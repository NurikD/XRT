from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def admin_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text='📊Статистика'))
    builder.add(KeyboardButton(text='👤База данных'))
    builder.add(KeyboardButton(text='🏡Главное меню'))

    builder.adjust(2, 1)

    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Выберите функцию"
    )
