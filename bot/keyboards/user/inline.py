from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardBuilder


def notifications_settings(role) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='В боте', callback_data='notice_in_bot'))
    if role == 'Диспетчер':
        builder.add(InlineKeyboardButton(text='На почте', callback_data='notice_in_mail'))

    builder.adjust()

    return builder.as_markup()


def btn_change_email() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text='✏️Сменить почту',
                callback_data='change_email'
            )
        ]
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=kb
    )

    return keyboard


def btn_change_role(role) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    text = '👤Сменить роль'
    if role == 'Диспетчер':
        builder.add(InlineKeyboardButton(text=text, callback_data='change_dispatcher_to_executor'))
    elif role == 'Исполнитель':
        builder.add(InlineKeyboardButton(text=text, callback_data='change_executor_to_dispatcher'))

    builder.adjust()

    return builder.as_markup()


def btn_notifications_back() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text='◀️ Назад',
                callback_data='back_common'
            )
        ]
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=kb
    )

    return keyboard


def btn_back_to_excel() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='◀️ Назад', callback_data='back_to_excel'))
    builder.adjust()

    return builder.as_markup()


def notice_selection_options(notification_modes: dict, method: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    buttons = {
        'Все': f'{method}_all',
        'Новая заявка': f'{method}_new_request',
        'Изменение в заявке': f'{method}_request_change',
        'Изменить интервал': f'{method}_change_interval',
    }

    # Ищем хотя бы одно значение True и если оно существует добавляем кнопку "❌Отключить все"
    check_data = list(notification_modes.items())

    my_list = []
    for key, value in check_data:
        if method in key:
            if value is True:
                my_list.append(value)
                break

    for text, key in buttons.items():
        checked = notification_modes.get(key, False)
        button_text = f"{'✅ ' if checked else ''}{text}"  # Добавить эмодзи, где значение кнопки True
        builder.row(InlineKeyboardButton(text=button_text, callback_data=f'set_{key}'))

    if my_list:
        builder.row(InlineKeyboardButton(text='❌Отключить все', callback_data=f'disable_{method}_all'))

    builder.row(InlineKeyboardButton(text='◀️ Назад', callback_data='back_options'))

    builder.adjust(1, 2, 1)
    return builder.as_markup()


def btn_app_by_city() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='🏙Заявки по городам', callback_data='data_by_city'))
    builder.adjust()

    return builder.as_markup()
