from aiogram import F, Router
from aiogram.utils.markdown import hide_link
from aiogram.filters import Command

from bot.database.methods.update import latest_activity

from bot.keyboards.user.reply import *
from bot.keyboards.user.inline import *

router = Router()


@router.message(Command('help'))
@router.message(F.text == '🆘Помощь')
async def help_the_user(message: types.Message):
    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(
        text="Написать менеджеру",
        url="tg://resolve?domain=marselnet")
    )

    await message.answer(
        text=f"{hide_link('https://telegra.ph/file/638e9b0477dc5b4b30130.png')}"
        "🚑Если у вас возникли вопросы или проблемы по боту, то вы можете "
        "обратиться к нашему менеджеру @marselnet. "
        "Мы постараемся ответить, как можно скорее!\n\n"
        "🌉Ваш комфорт — является нашим приоритетом.",
        reply_markup=builder.as_markup()
    )

    await latest_activity(message.from_user.id)  # Записывает время активности
