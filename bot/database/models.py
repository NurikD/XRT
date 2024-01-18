from .main import connect_pg


async def create_statuses() -> None:
    """Статусы наименования заявок"""
    connection = await connect_pg()
    async with connection.transaction():
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS statuses (
                id serial PRIMARY KEY,
                status_name varchar (30)
            );
        """)


async def create_data_array() -> None:
    """Массив данных"""
    connection = await connect_pg()
    async with connection.transaction():
        await connection.execute("""      
            CREATE TABLE IF NOT EXISTS data_table (
                crm text,
                city text,
                worksite_short_name text,
                assignee_name varchar,
                open_date timestamp,
                create_ki timestamp,
                start_ki timestamp,
                stop_ki timestamp,
                close_ki timestamp,
                ks_3 timestamp,
                ks_23 timestamp,
                interval varchar,
                fk_status int REFERENCES statuses(id),
                status_time interval,
                commentary text,
                login text,
                date_close timestamp
            );   
            """)

    print('[INFO] Table - {data_table} created successfully')


async def create_roles() -> None:
    """Пользовательские роли"""
    connection = await connect_pg()
    async with connection.transaction():
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id serial PRIMARY KEY,
                role_name varchar (30)
            );
            """)

    print('[INFO] Table - {roles} created successfully')


async def create_users() -> None:
    """Основная информация о пользователе"""
    connection = await connect_pg()
    async with connection.transaction():
        await connection.execute("""   
            CREATE TABLE IF NOT EXISTS users (
                user_id bigint UNIQUE,
                nickname varchar (32),
                full_name varchar (64),
                fk_role int REFERENCES roles(id),
                login varchar (32),
                email varchar (64),
                plots varchar,
                request_time timestamp,
                register_time timestamp
            );   
            """)

    print('[INFO] Table - {users} created successfully')


async def create_notification_modes() -> None:
    """Настройки уведомлений пользователя"""
    connection = await connect_pg()
    async with connection.transaction():
        await connection.execute("""   
            CREATE TABLE IF NOT EXISTS notification_modes (
                fk_user_id bigint REFERENCES users(user_id),
                bot_all BOOLEAN DEFAULT true,
                bot_new_request BOOLEAN DEFAULT false,
                bot_request_change BOOLEAN DEFAULT false,
                bot_change_interval BOOLEAN DEFAULT false,
                email_all BOOLEAN DEFAULT false,
                email_new_request BOOLEAN DEFAULT false,
                email_request_change BOOLEAN DEFAULT false,
                email_change_interval BOOLEAN DEFAULT false
            );   
            """)

    print('[INFO] Table - {notification_modes} created successfully')
