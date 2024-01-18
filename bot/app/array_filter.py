from collections import defaultdict
from datetime import datetime, timedelta

import pandas as pd

from bot.app.oracle_data import get_data
from bot.database.methods.insert import insert_new_array
from bot.database.methods.update import change_array
from bot.database.methods.get import get_array_data


async def parse_datetime(date_str) -> datetime:
    """Изменяет формат времени"""
    return datetime.strptime(date_str, '%d.%m.%Y %H:%M:%S')


async def filter_api(rows: list):
    api_data = []
    for row in rows:
        create_ki = await parse_datetime(row['CREATE_KI'])
        open_date = await parse_datetime(row['OPEN_DATE'])
        start_ki = await parse_datetime(row['START_KI'])
        stop_ki = await parse_datetime(row['STOP_KI'])

        ks_3 = create_ki + timedelta(hours=20)
        current_date = datetime.now()

        row['KS_3'] = ks_3
        row['KS_23'] = open_date + timedelta(hours=24)
        row['INTERVAL'] = f"{start_ki}-{stop_ki.strftime('%H:%M:%S')}"

        try:
            if row['DATE_CLOSE']:
                date_close = datetime.strptime(row['DATE_CLOSE'], '%Y-%m-%d %H:%M:%S')
                row['DATE_CLOSE'] = date_close
        except Exception as ex_:
            row['DATE_CLOSE'] = None
            print(f'Err: {ex_}')

        if row['ASSIGNEE_NAME'] is None:
            row['STATUS'], row['STATUS_TIME'] = 3, current_date - create_ki  # Назначить исполнителя

        elif stop_ki < ks_3:
            row['STATUS'] = 1  # Нормально

        elif stop_ki > ks_3:
            row['STATUS'], row['STATUS_TIME'] = 2, stop_ki - ks_3  # Изменить интервал

        api_data.append(row)

    return api_data


async def target_line(api_data: list):
    rows = await get_array_data()
    db_data = [dict(row) for row in rows]

    # Проверка вхождения по CRM
    crm_ids = []
    for db_row in db_data:
        crm_ids.append(db_row['crm'])

    # Делаем все ключи из БД в верхнем регистре
    db_data = [{key.upper(): value for key, value in data.items()} for data in db_data]

    # Обработчик новых заявок + изменить интервал
    for api_row in api_data:
        date_fields = ['OPEN_DATE', 'CREATE_KI', 'START_KI', 'STOP_KI', 'CLOSE_KI']
        for field in date_fields:
            if api_row[field]:
                api_row[field] = await parse_datetime(api_row[field])

        if api_row['CRM'] not in crm_ids:
            if api_row['STATUS'] == 2:
                api_row['MESSAGE_TYPE'] = 'change_interval'
            else:
                api_row['MESSAGE_TYPE'] = 'new_request'

            await insert_new_array(api_row)
            return api_row

    # Обработчик измененных заявок
    my_keys = ['WORKSITE_SHORT_NAME', 'ASSIGNEE_NAME', 'CLOSE_KI']
    for api_row in api_data:
        for db_row in db_data:
            if api_row['CRM'] == db_row['CRM']:
                if not all(api_row[key] == db_row[key] for key in my_keys):
                    api_row['MESSAGE_TYPE'] = 'request_change'
                    await change_array(api_row)
                    return api_row


async def enter_data(format_type, json_data):
    """Форматирует данные из JSON и заносит их в Excel"""
    try:
        my_list = []

        if format_type == 'all':
            columns = ['CRM', 'WORKSITE_SHORT_NAME', 'CREATE_KI', 'OPEN_DATE', 'START_KI', 'STOP_KI', 'ASSIGNEE_NAME']

        elif format_type == 'non_executor':
            for data in json_data:
                if data['ASSIGNEE_NAME'] is None:
                    my_list.append(data)
            columns = ['CRM', 'WORKSITE_SHORT_NAME', 'CREATE_KI', 'OPEN_DATE', 'START_KI', 'STOP_KI', 'COMMENTARY']

        else:
            raise ValueError("Invalid message type")

        df = pd.DataFrame(json_data, columns=columns)

        file_name = f'{format_type}_{datetime.now().strftime("%d%m%Y_%H%M%S")}.xlsx'
        file_path = f'bot/downloads/user_requests/{file_name}'
        df.to_excel(file_path, index=False)

        return file_path

    except Exception as e:
        raise Exception(f"Err: {e}")


async def app_by_city(json_data) -> str:
    """Считает кол-во заявок по городам и время между заявками"""

    city_stats = defaultdict(lambda: {'today': 0, 'more_2_days': 0, 'more_7_days': 0})
    for data in json_data:
        create_date = await parse_datetime(data['CREATE_KI'])
        current_date = datetime.now()
        time_difference = current_date - create_date

        if time_difference.days == 0:
            city_stats[data['CITY']]['today'] += 1
        elif time_difference.days > 7:
            city_stats[data['CITY']]['more_7_days'] += 1
        else:
            city_stats[data['CITY']]['more_2_days'] += 1

    result_text = ""
    for city, stats in city_stats.items():
        total = stats['today'] + stats['more_2_days'] + stats['more_7_days']
        result_text += f"Город: {city} | Кол-во заявок: {total}\n"
        result_text += f"1. Новых сегодня - {stats['today']} шт\n"
        result_text += f"2. Более 2 дня- {stats['more_2_days']} шт\n"
        result_text += f"3. Более 7 дней - {stats['more_7_days']} шт\n\n"

    return result_text


async def records() -> list:
    """Фильтрует сырой массив и возвращает отфильтрованный"""
    data_array = await get_data()
    if data_array:
        filtered_array = await filter_api(data_array)

        return filtered_array


async def new_lines() -> dict:
    """Отслеживает записи в API"""
    filtered_array = await records()
    if filtered_array:
        lines = await target_line(filtered_array)

        return lines


async def convert_to_excel(format_type):
    """Заносит данные из API в Excel Документ"""
    filtered_array = await records()
    if filtered_array:
        file_path = await enter_data(format_type, filtered_array)
        counted_apps = await app_by_city(filtered_array)

        return file_path, counted_apps
