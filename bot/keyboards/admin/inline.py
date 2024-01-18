from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardBuilder


def available_tables(rows) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for row in rows:
        builder.add(InlineKeyboardButton(text=row[0], callback_data=f'table_{row[0]}'))

    builder.adjust(1)

    return builder.as_markup()


def back_to_tables() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='◀️ Назад', callback_data='admin_back_to_tables'))

    builder.adjust()

    return builder.as_markup()
