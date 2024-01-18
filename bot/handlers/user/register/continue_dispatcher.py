from aiogram import F, html, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from .main_register import save_user_data
from .fsm_states import Form

from bot.app.sender import register_mail


router = Router()


# Этап отправки проверочного письма #

@router.message(Form.taking_email, F.text.contains('rt.ru'))
async def email_taken(message: Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    data = {
        'email': None,
    }
    entities = message.entities or []

    for item in entities:
        if item.type in data.keys():
            data[item.type] = item.extract_from(message.text)

    if data['email'] is None:
        await email_incorrectly(message)

    if data['email'] == user_data.get('old_email'):
        await same_mail(message)
        return

    send_code = register_mail(data['email'])
    if send_code is False:
        await email_incorrectly(message)

    else:
        await state.update_data(email=data['email'], email_code=str(send_code))
        await message.answer(
            f"🕊Мы отправили письмо с кодом на {html.quote(data['email'])}\n\n"
            f"Введите код:"
        )

        await state.set_state(Form.checking_email_code)

# Этап проверки корректности ввода почты #


@router.message(Form.taking_email)
async def email_incorrectly(message: Message) -> None:
    await message.answer(
        "<b>❌Некорректный e-mail адрес</b>\n\n"
        "Введите еще раз!",
    )


async def same_mail(message: Message) -> None:
    await message.answer(
        "<b>❌Новый e-mail адрес не должен повторяться с прошлым!</b>\n\n"
        "Введите еще раз!",
    )


# Этап проверки кода от пользователя #

@router.message(Form.checking_email_code)
async def email_checking_code(message: Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    if user_data['email_code'] == message.text:
        await save_user_data(message, user_data)
        await state.clear()

    else:
        await email_code_incorrectly(message)


@router.message(Form.checking_email_code)
async def email_code_incorrectly(message: Message) -> None:
    await message.answer(
        "<b>❌Код введен неверно</b>\n\n"
        "Введите еще раз!"
    )
