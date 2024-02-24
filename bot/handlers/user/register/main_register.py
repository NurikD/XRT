from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from bot.database.methods.update import change_user_email
from bot.database.methods.insert import add_new_user

from bot.keyboards.user.reply import *
from .fsm_states import Form


router = Router()


# Этап заполнения контакта #

async def start_user_register(message: Message, state: FSMContext) -> None:
    button = KeyboardButton(text="Отправить контакт", request_contact=True)
    markup = ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True, one_time_keyboard=True)

    await message.answer(
        text="<b>Привет!👋</b>\n\n"
             "Прежде, чем мы начнем, мне потребуется, чтобы вы прошли процесс регистрации.\n\n"
             "Для начала отправьте свой контакт, нажав на кнопку 'Отправить контакт'.",
        reply_markup=markup,
    )
    await state.set_state(Form.taking_phone_number)


# Запрос email пользователя #

async def email_checking_code(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()
    await state.update_data(user_id=user_id)
    await save_user_data(message, user_data)


@router.message(Form.taking_phone_number, F.text | F.contact)
async def phone_number_taken(message: Message, state: FSMContext):
    if message.contact:
        phone_number = message.contact.phone_number
    else:
        phone_number = message.text

    await state.update_data(phone_number=phone_number)

    await message.answer(
        text="Отлично! Теперь введите свой email текстом.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(Form.taking_email)


async def save_user_data(message: Message, user_data):
    user_id = message.from_user.id
    nickname = message.from_user.username or 'No nickname'

    if user_data.get('change_email'):
        await change_user_email(user_id, user_data['email'])
        await message.answer(
            text="📬Почта изменена",
            reply_markup=main_menu()
        )
    else:
        await add_new_user(
            user_id=user_id,
            nickname=nickname,
            phone_number=user_data['phone_number'],
            login=user_data.get('login'),
            email=user_data.get('email'),
            plots=user_data.get('plots')
        )

        await message.answer(
            text="✅Регистрация завершена!",
            reply_markup=main_menu()
        )