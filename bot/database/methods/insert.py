import datetime

from bot.database.main import connect_pg


async def add_statuses_name() -> None:
    """Добавляет статусы заявок в таблицу при первом запуске бота"""
    connection = await connect_pg()

    # Проверяем наличие данных в таблице
    rows = await connection.fetch(
        """SELECT status_name FROM statuses"""
    )

    if not rows:
        async with connection.transaction():
            await connection.execute(
                """INSERT INTO statuses (status_name) VALUES ($1)""", 'Нормально'
            )
            await connection.execute(
                """INSERT INTO statuses (status_name) VALUES ($1)""", 'Изменить интервал'
            )

            await connection.execute(
                """INSERT INTO statuses (status_name) VALUES ($1)""", 'Назначить исполнителя'
            )

        print('[INFO] Insert data from func - {add_statuses_name} successfully')


async def add_roles_name() -> None:
    """Добавляет роли в таблицу при первом запуске бота"""
    connection = await connect_pg()

    # Проверяем наличие данных в таблице
    rows = await connection.fetch(
        """SELECT role_name FROM roles"""
    )

    if not rows:
        async with connection.transaction():
            await connection.execute(
                """INSERT INTO roles (role_name) VALUES ($1)""", 'Диспетчер'
            )
            await connection.execute(
                """INSERT INTO roles (role_name) VALUES ($1)""", 'Исполнитель'
            )

            print('[INFO] Insert data from func - {add_roles_name} successfully')


async def add_new_user(**kwargs) -> None:
    """Добавляет нового пользователя в таблицу users,
    если его не существует"""
    connection = await connect_pg()
    async with connection.transaction():
        await connection.execute(
            """INSERT INTO users 
            (user_id, nickname, full_name, fk_role, login, email, plots, register_time) 
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""",
            kwargs['user_id'], kwargs.get('nickname'),
            kwargs['full_name'], kwargs['fk_role'], kwargs.get('login'), kwargs.get('email'),
            ', '.join(kwargs.get('plots', [])) if kwargs.get('plots') else None,
            datetime.datetime.now()
        )

        row = await connection.fetchrow(
            """SELECT fk_user_id FROM notification_modes WHERE fk_user_id = $1""",
            kwargs['user_id']
        )
        if row is None:
            await connection.execute(
                """INSERT INTO notification_modes (fk_user_id) VALUES ($1)""",
                kwargs['user_id']
            )


async def insert_new_array(data) -> None:
    connection = await connect_pg()
    async with connection.transaction():
        await connection.execute(
            """
            INSERT INTO data_table (
            crm, city, worksite_short_name, assignee_name, 
            open_date, create_ki, start_ki, stop_ki, 
            close_ki, ks_3, ks_23, interval, fk_status, 
            status_time, commentary, login, date_close
            ) 
            VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, 
            $10, $11, $12, $13, $14, $15, $16, $17
            )
            """,
            data['CRM'], data['CITY'], data['WORKSITE_SHORT_NAME'], data['ASSIGNEE_NAME'],
            data.get('OPEN_DATE'), data.get('CREATE_KI'), data.get('START_KI'),
            data.get('STOP_KI'), data.get('CLOSE_KI'), data.get('KS_3'), data['KS_23'],
            data['INTERVAL'], data['STATUS'], data.get('STATUS_TIME'), data['COMMENTARY'],
            data['LOGIN'], data.get('DATE_CLOSE')
        )
