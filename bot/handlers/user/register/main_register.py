from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from bot.database.methods.update import change_user_email, changer_role
from bot.database.methods.insert import add_new_user

from bot.keyboards.user.reply import *

from bot.misc.const import AVAILABLE_ROLES

from .fsm_states import Form


router = Router()


# Этап заполнения ФИО #

async def start_user_register(message: Message, state: FSMContext) -> None:
    await message.answer(
        text="<b>Привет!👋</b>\n\n"
             "Прежде, чем мы начнем, мне потребуется, чтобы вы прошли процесс регистрации.\n\n"
             "Для начала введите свое ФИО",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(Form.taking_full_name)


# Этап выбора роли #

@router.message(Form.taking_full_name, F.text.len() >= 15)
async def fullname_taken(message: Message, state: FSMContext):
    await state.update_data(
        user_id=message.from_user.id,
        nickname=message.from_user.username,
        full_name=message.text.title()
    )
    await message.answer(
        text="Спасибо! Теперь выберите роль:",
        reply_markup=get_roles()
    )

    await state.set_state(Form.choosing_role)


@router.message(Form.taking_full_name)
async def fullname_incorrectly(message: Message):
    await message.answer(
        "<b>❌Некорректное ФИО</b>\n\n"
        "Попробуйте ввести еще раз!"
    )


# Этап отображения сводной информации у пользователя #

@router.message(Form.choosing_role, F.text.in_(list(AVAILABLE_ROLES.keys())))
async def fullname_and_role_taken(message: Message, state: FSMContext):
    await state.update_data(role=AVAILABLE_ROLES[message.text])
    if message.text == 'Диспетчер':
        await message.answer(
            text="📥Теперь укажите адрес <b>рабочей</b> электронной почты\n\n"
                 "🤖Бот автоматически проверит адрес на корректность ввода "
                 "и в случае не валидности, выдаст ошибку\n\n"
                 "<i>Пример: example@rt.ru</i>",
            reply_markup=ReplyKeyboardRemove()
        )

        await state.set_state(Form.taking_email)

    elif message.text == 'Исполнитель':
        await message.answer(
            text="📲Теперь отправьте мне свой АРГУС\n\n"
                 "<i>Пример: HM_BEDILO-OV</i>",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(Form.taking_argus)


@router.message(Form.choosing_role)
async def role_incorrectly(message: Message):
    await message.answer(
        text="<b>❌Такой роли еще нет</b>\n\n"
             "Пожалуйста, выберите роль из списка ниже:",
        reply_markup=get_roles()
    )


async def save_user_data(message: Message, user_data):
    if user_data.get('change_role'):
        await changer_role(
            change_role=user_data['change_role'],
            user_id=message.from_user.id,
            login=user_data.get('login'),
            plots=user_data.get('plots'),
            email=user_data.get('email')
        )

        await message.answer(
            text="🤝Данные изменены",
            reply_markup=main_menu()
        )

    elif user_data.get('change_email'):
        await change_user_email(message.from_user.id, user_data['email'])
        await message.answer(
            text="📬Почта изменена",
            reply_markup=main_menu()
        )

    else:
        await add_new_user(
            user_id=user_data['user_id'],
            nickname=user_data['nickname'],
            full_name=user_data['full_name'],
            fk_role=user_data['role'],
            login=user_data.get('login'),
            email=user_data.get('email'),
            plots=user_data.get('plots')
        )

        await message.answer(
            text="✅Регистрация завершена!",
            reply_markup=main_menu()
        )
