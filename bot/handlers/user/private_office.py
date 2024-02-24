from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hide_link
import re
from bot.database.methods.get import get_user_mail, get_argus_login
from bot.database.methods.update import latest_activity, update_argus_login

from bot.handlers.user.utils import deadline_message
from bot.handlers.user.register.fsm_states import Form

from bot.keyboards.user.reply import *
from bot.keyboards.user.inline import *

router = Router()


# Вывод функций который может изменить пользователь #


@router.message(F.text == '💻Личный кабинет')
async def settings(message: Message):
    # is_dispatcher = await dispatcher_exists(message.from_user.id)
    await message.answer(
        text=f"{hide_link('https://telegra.ph/file/2e8bf0a6bd744d44231bc.png')}"
             "В данном разделе, вы можете добавить или изменить логин Аргус и участок, "
             "Нажмите на параметр ниже, который хотите изменить 👇",
        # reply_markup=settings_menu(is_dispatcher))
        reply_markup=settings_menu())  # добавлено

    await latest_activity(message.from_user.id)


@router.message(F.text == '🏘Участки')
async def plots(message: Message):
    await message.answer("<i>Функция в режиме апробации...</i>⏰")


@router.message(F.text == 'Логин Аргус')
async def argus_login_command(message: types.Message):
    await message.answer("Введите свой АРГУС:\n\n"
                         "Пример - Логин: FM_ARGUS")


@router.message(lambda message: message.text and re.match(r"^Логин:\s+", message.text))
async def process_argus_login(message: types.Message):
    try:
        # Используем регулярное выражение для извлечения логина
        match = re.match(r"^Логин:\s+(\S+)", message.text)
        if match:
            login = match.group(1).strip()

            # Проверка, существует ли логин Аргуса в базе данных
            existing_login = await get_argus_login(message.from_user.id)
            if existing_login:
                await message.answer(f"У вас уже установлен логин Аргус: {existing_login}")
            else:
                await update_argus_login(message.from_user.id, login)
                await message.answer(f"Логин Аргус успешно сохранен: {login}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")


# Вывод почты пользователя, с возможностью ее изменить #

@router.message(F.text == '📬Почта')
async def user_email(message: Message):
    # is_dispatcher = await dispatcher_exists(message.from_user.id)
    # if is_dispatcher is True:
    user_mail = await get_user_mail(message.from_user.id)
    await message.answer(text=f"Ваш адрес сейчас: {user_mail}\n\n"
                              "Если вы хотите изменить адрес на новый, то нажмите на кнопку ниже",
                         reply_markup=btn_change_email())


@router.callback_query(F.data == 'change_email')
async def change_email(call: CallbackQuery, state: FSMContext):
    user_mail = await get_user_mail(call.from_user.id)
    await state.update_data(change_email=True, old_email=user_mail)
    if await deadline_message(call) is False:
        await call.message.edit_text(
            'Введите новый адрес эл.почты:'
        )

        await state.set_state(Form.taking_email)



@router.callback_query(F.data == 'change_dispatcher_to_executor')
async def change_to_executor(call: CallbackQuery, state: FSMContext):
    await state.update_data(change_role='to_executor')
    if await deadline_message(call) is False:
        await call.message.edit_text(
            "Введите свой АРГУС:",
        )

        await state.set_state(Form.taking_argus)


@router.callback_query(F.data == 'change_executor_to_dispatcher')
async def change_to_dispatcher(call: CallbackQuery, state: FSMContext):
    await state.update_data(change_role='to_dispatcher')
    if await deadline_message(call) is False:
        await call.message.edit_text(
            "Введите адрес эл.почты:",
        )

        await state.set_state(Form.taking_email)


@router.message(F.text == '◀️ Назад')
async def back_to_main(message: Message):
    await message.answer(
        text="Возвращаю в главное меню!",
        reply_markup=main_menu()
    )
