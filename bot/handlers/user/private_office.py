from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hide_link
from bot.database.methods.update import latest_activity

from bot.handlers.user.utils import deadline_message
from bot.handlers.user.register.fsm_states import Form

from bot.keyboards.user.reply import *


router = Router()


# Вывод функций, которые может изменить пользователь #


@router.message(F.text == '💻Личный кабинет')
async def settings(message: Message):
    await message.answer(
        text=f"{hide_link('https://telegra.ph/file/2e8bf0a6bd744d44231bc.png')}"
             "В данном разделе, вы можете изменить существующий адрес электронной почты на новый"
             "Нажмите на параметр ниже, который хотите изменить 👇",
        reply_markup=settings_menu())

    await latest_activity(message.from_user.id)


@router.callback_query(F.data == 'change_dispatcher_to_executor')
async def change_to_executor(call: CallbackQuery, state: FSMContext):
    await state.update_data(change_role='to_executor')
    if await deadline_message(call) is False:
        await call.message.edit_text(
            "Введите свой АРГУС:",
        )

        await state.set_state(Form.taking_argus)


@router.message(F.text == '🏘Участки')
async def plots(message: Message):
    await message.answer("<i>Функция в режиме апробации...</i>⏰")


@router.message(F.text == '◀️ Назад')
async def back_to_main(message: Message):
    await message.answer(
        text="Возвращаю в главное меню!",
        reply_markup=main_menu()
    )
