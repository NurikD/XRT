from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hide_link

from bot.database.methods.get import dispatcher_exists, get_user_mail, get_user_role
from bot.database.methods.update import latest_activity

from bot.handlers.user.utils import deadline_message
from bot.handlers.user.register.fsm_states import Form

from bot.keyboards.user.reply import *
from bot.keyboards.user.inline import *


router = Router()

# Вывод функций который может изменить пользователь #


@router.message(F.text == '💻Личный кабинет')
async def settings(message: Message):
    is_dispatcher = await dispatcher_exists(message.from_user.id)
    await message.answer(
        text=f"{hide_link('https://telegra.ph/file/2e8bf0a6bd744d44231bc.png')}"
             "В данном разделе, вы можете изменить существующий адрес электронной почты на новый, "
             "<i>(если вы являетесь диспетчером)</i> "
             "а также роль пользователя 📲\n\n"
             "Нажмите на параметр ниже, который хотите изменить 👇",
        reply_markup=settings_menu(is_dispatcher))

    await latest_activity(message.from_user.id)


@router.message(F.text == '🏘Участки')
async def plots(message: Message):
    await message.answer("<i>Функция в режиме апробации...</i>⏰")


# Вывод почты пользователя, с возможностью ее изменить #


@router.message(F.text == '📬Почта')
async def user_email(message: Message):
    is_dispatcher = await dispatcher_exists(message.from_user.id)
    if is_dispatcher is True:
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

# Вывод роли пользователя, с возможностью ее изменить #


@router.message(F.text == '🎩Роль')
async def user_role(message: Message):
    role = await get_user_role(message.from_user.id)

    if role == 'Диспетчер':
        await message.answer(
            text=f"👨‍💻Ваша роль сейчас: <b>{role}</b>\n\n"
                 "Вы можете сменить роль на <i><b>\"Исполнитель\"</b></i>, "
                 "но вам будут недоступны уведомления по почте!",
            reply_markup=btn_change_role(role)
        )

    elif role == 'Исполнитель':
        await message.answer(
            text=f"👨‍💻Ваша роль сейчас: {role}\n\n"
                 "Вы можете сменить роль на <i><b>\"Диспетчер\"</b></i>, "
                 "тогда вам откроется возможность получать уведомления по почте",
            reply_markup=btn_change_role(role)
        )


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
