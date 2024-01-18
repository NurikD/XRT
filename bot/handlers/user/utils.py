import asyncio
from datetime import datetime, timedelta, timezone
from os import getenv
import requests

from aiogram.types import CallbackQuery

from bot.database.methods.get import get_notifications_info

from bot.app.array_filter import new_lines
from bot.app.sender import send_notification_mail


async def deadline_message(call: CallbackQuery) -> bool:
    current_time = datetime.now(timezone.utc)  # Устанавливаем часовой пояс UTC

    # Получаем время отправки сообщения из метаданных
    message_time = call.message.date.replace(tzinfo=timezone.utc)  # Устанавливаем часовой пояс UTC
    time_difference = current_time - message_time

    if time_difference > timedelta(minutes=1):
        await call.answer(
            text="🗑Кнопки устарели, вызовите новую клавиатуру!",
            show_alert=True
        )
        return True
    return False


async def generate_message_text(line):
    """Генерация сообщения с заголовком"""

    if line['MESSAGE_TYPE'] == 'new_request':
        caption = "<b>✈️Новая заявка\n\n</b>"
    elif line['MESSAGE_TYPE'] == 'request_change':
        caption = "<b>🗿Изменение в заявке</b>\n\n"
    else:
        caption = "<b>🌵Изменить интервал</b>\n\n"

    fields = ""
    fields += (
        f"🏠<i>Участок:</i> <b>{line['WORKSITE_SHORT_NAME']}</b><br>\n"
        f" ├– 🏝<i>Номер заявки:</i> <b>{line['CRM']}</b><br>\n"
        f" ‍├– 🏃‍♂️<i>Исполнитель:</i> <b>{line['ASSIGNEE_NAME']}</b><br>\n"
        f" ├– ⏰<i>Дата создания:</i> <b>{line['CREATE_KI']}</b><br>\n"
        f" ├– 🏀<i>КС 3 ЛТП:</i> <b>{line['KS_3']}</b><br>\n"
        f" ├– 🎾<i>КС 2+3:</i> <b>{line['KS_23']}</b><br>\n"
        f" ├– 🎱<i>Интервал согласованный:</i> <b>{line['INTERVAL']}</b><br>\n"
    )

    if line['STATUS'] == 1:
        fields += " └– ✅<i>Статус:</i> <u>Нормально</u>"
    elif line['STATUS'] == 2:
        fields += " └– 🌄<i>Статус:</i> <u>Изменить интервал</u>"
    elif line['STATUS'] == 3:
        fields += " └– 📲<i>Статус:</i> <u>Назначить исполнителя</u>"

    return caption, fields


async def sender_notice() -> None:
    while True:
        try:
            await asyncio.sleep(60)
            line = await new_lines()
            if line and getenv('SEND_NOTIFICATION') == 'ON':
                caption, message = await generate_message_text(line)
                notifications = await get_notifications_info()
                modes = [dict(notice) for notice in notifications]

                for mode in modes:
                    if mode['bot_all']:
                        if line['MESSAGE_TYPE'] == 'new_request':  # Новое сообщение
                            await send_request(int(mode['fk_user_id']), caption + message.replace('<br>', ''))

                    if mode['email_all']:
                        if line['MESSAGE_TYPE'] == 'new_request':  # Новое сообщение
                            if mode['email']:
                                send_notification_mail(mode['email'], caption, message)

                    if mode['bot_new_request']:
                        if line['MESSAGE_TYPE'] == 'new_request':  # Новое сообщение
                            await send_request(int(mode['fk_user_id']), caption + message.replace('<br>', ''))

                    if mode['email_new_request']:
                        if line['MESSAGE_TYPE'] == 'new_request':  # Новое сообщение
                            if mode['email']:
                                send_notification_mail(mode['email'], caption, message)

                    if mode['bot_request_change']:
                        if line['MESSAGE_TYPE'] == 'request_change':  # Изменение в сообщении
                            await send_request(int(mode['fk_user_id']), caption + message.replace('<br>', ''))

                    if mode['email_request_change']:
                        if line['MESSAGE_TYPE'] == 'request_change':  # Изменение в сообщении
                            if mode['email']:
                                send_notification_mail(mode['email'], caption, message)

                    if mode['bot_change_interval']:
                        if line['MESSAGE_TYPE'] == 'change_interval':  # Изменить интервал
                            await send_request(int(mode['fk_user_id']), caption + message.replace('<br>', ''))

                    if mode['email_change_interval']:
                        if line['MESSAGE_TYPE'] == 'change_interval':  # Изменить интервал
                            if mode['email']:
                                send_notification_mail(mode['email'], caption, message)

        except ValueError as ex_:
            print(f'Decoding JSON has failed: {ex_}')
        except asyncio.TimeoutError:
            print('Operation timed out, will retry...')
        except Exception as ex:
            print(f'An unexpected error occurred: {ex}')


async def send_request(user_id: int, text: str) -> None:
    response = requests.post(
        f"https://api.telegram.org/bot{getenv('TOKEN_API')}/sendMessage?chat_id={user_id}&parse_mode=html&text={text}"
    )

    print(response.text)
