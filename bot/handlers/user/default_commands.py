from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters.command import CommandStart

from bot.database.methods.update import latest_activity
from bot.database.methods.get import user_exists

from bot.keyboards.user.reply import *

from .register.main_register import start_user_register

router = Router()


@router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    if await user_exists(user_id) is False:
        await start_user_register(message, state)

    else:
        await state.clear()
        await message.answer(
            text=f"🏜Добро пожаловать, <b>{message.from_user.first_name}!</b>",
            reply_markup=main_menu()
        )

    await latest_activity(user_id)


@router.message(Command('cancel'))
@router.message(F.text.lower() == 'отмена')
async def command_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Действие отменено"
    )


@router.message(Command('user_id'))
async def get_user_id(message: Message):
    await message.answer(
        f"Ваш id: <code>{message.from_user.id}</code>"
    )