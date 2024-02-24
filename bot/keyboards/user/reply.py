from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_roles() -> ReplyKeyboardMarkup:
    kb = [
        [
            KeyboardButton(text='Диспетчер'),
            KeyboardButton(text='Исполнитель')
        ],
    ]

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )

    return keyboard


def main_menu() -> ReplyKeyboardMarkup:
    """Кнопки основной панели пользователя"""
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text='📥Все'))
    builder.add(KeyboardButton(text='🔔Уведомления'))
    builder.add(KeyboardButton(text='🆘Помощь'))
    builder.add(KeyboardButton(text='💻Личный кабинет'))

    builder.adjust(2, 2, 1)
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Выберите функцию"
    )


def settings_menu() -> ReplyKeyboardMarkup:
    """Кнопки личного кабинета"""
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text='Логин Аргус'))
    builder.add(KeyboardButton(text='🏘Участки'))
    builder.add(KeyboardButton(text='◀️ Назад'))

    builder.adjust(2, 1, 1)
    return builder.as_markup(resize_keyboard=True)
