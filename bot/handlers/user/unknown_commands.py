from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.database.methods.get import user_exists
from bot.keyboards.user.reply import main_menu
from .register.main_register import start_user_register

router = Router()


@router.message(F.text)
async def unknown_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if await user_exists(user_id) is False:
        await start_user_register(message, state)

    else:
        await message.answer(
            text="⚠️Неизвестная команда, возвращаю в главное меню!",
            reply_markup=main_menu()
        )
