from datetime import datetime
from os import path

import pandas as pd

from bot.database.main import connect_pg
from bot.misc.const import AVAILABLE_ROLES


# POSTGRESQL

async def user_exists(user_id: int) -> bool:
    """Проверка на существование пользователя"""
    connection = await connect_pg()
    user_is_reg = await connection.fetchrow(
        """SELECT user_id FROM users WHERE user_id = $1""", user_id
    )

    if user_is_reg:
        return True
    return False



async def get_user_mail(user_id: int) -> str:
    """Возвращает email-адрес пользователя"""
    connection = await connect_pg()
    user_mail = await connection.fetchval(
        """SELECT email FROM users WHERE user_id = $1""", user_id
    )

    return user_mail


async def notifications_exists(user_id: int) -> dict:
    connection = await connect_pg()
    notification_modes = await connection.fetchrow(
        """SELECT * FROM notification_modes WHERE fk_user_id = $1""", user_id
    )

    return notification_modes


async def number_of_users() -> str:
    """Получить общее кол-во пользователей в боте"""
    connection = await connect_pg()
    async with connection.transaction():
        user_count = await connection.fetchval(
            """SELECT COUNT(*) FROM users"""
        )

    return user_count


async def table_names() -> list:
    """Получить названия всех таблиц, которые существуют в БД"""
    connection = await connect_pg()
    async with connection.transaction():
        tables = await connection.fetch(
            """SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE';
            """)

    return tables


async def save_table_data(table_name) -> str:
    table_name = table_name.replace('table_', '')

    current_datetime = datetime.now()
    timestamp = current_datetime.strftime('%d%m%Y_%H%M%S')
    xlsx_filename = f'{table_name}_{timestamp}.xlsx'
    xlsx_filepath = path.join('bot/downloads/admin_requests', xlsx_filename)

    connection = await connect_pg()
    async with connection.transaction():
        query = f"SELECT * FROM {table_name}"
        result = await connection.fetch(query)

        column_names = result[0].keys() if result else []
        df = pd.DataFrame(result, columns=column_names)

        # Сохраняем DataFrame в XLSX-файл с названиями столбцов
        df.to_excel(xlsx_filepath, index=False, engine='openpyxl')

    return xlsx_filename


async def get_user_statistics():
    """Получаем общее кол-во пользователей в боте, подписки, активность"""
    connection = await connect_pg()
    today_time = datetime.now()
    async with connection.transaction():
        time_of_reg = await connection.fetch(
            """SELECT request_time, register_time FROM users"""
        )

    # Извлекаем значения дат из результатов запроса и добавляем их в список
    registration_dates = [record['register_time'] for record in time_of_reg]
    requests_times = [record['request_time'] for record in time_of_reg]

    active_users = 0
    for request_time in requests_times:
        difference = today_time - request_time
        if difference.days == 0:
            active_users += 1

    today, week, month = 0, 0, 0
    for reg_date in registration_dates:
        difference = today_time - reg_date
        if difference.days == 0:
            today += 1
        elif difference.days <= 7:
            week += 1
        elif difference.days <= 30:
            month += 1

    return active_users, today, week, month


async def get_array_data():
    connection = await connect_pg()
    async with connection.transaction():
        data = await connection.fetch(
            """SELECT * FROM data_table"""
        )

        return data


async def get_notifications_info():
    connection = await connect_pg()
    async with connection.transaction():
        notices = await connection.fetch("""
            SELECT users.email, notification_modes.* FROM users 
            JOIN notification_modes ON notification_modes.fk_user_id=users.user_id;
        """)

        return notices


# получаем данные о логине с БД #
async def get_argus_login(user_id: int) -> str:
    """Получить логин Аргуса пользователя"""
    connection = await connect_pg()
    argus_login = await connection.fetchval(
        """SELECT login FROM users WHERE user_id = $1""", user_id
    )

    return argus_login

# ORACLE DB
