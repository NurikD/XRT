from datetime import datetime

from bot.database.main import connect_pg


async def set_notice_mode(user_id: int, notification_key: str) -> None:
    """Устанавливаем уведомления пользователя по отправленной кнопке"""
    connection = await connect_pg()
    async with connection.transaction():
        # Проверяем наличие данных в таблице
        if notification_key.startswith('bot'):
            if notification_key == 'bot_all':
                await connection.execute(
                    """
                    UPDATE notification_modes 
                    SET 
                        bot_all = CASE WHEN $1 = 'bot_all' THEN NOT bot_all ELSE bot_all END,
                        bot_new_request = FALSE,
                        bot_request_change = FALSE,
                        bot_change_interval = FALSE
                    WHERE fk_user_id = $2
                    """,
                    notification_key, user_id
                )
            else:
                # Получаем текущее состояние параметра уведомления и инвертируем его
                current_state = await connection.fetchval(
                    f"SELECT {notification_key} FROM notification_modes WHERE fk_user_id = $1", user_id
                )
                # Обновляем значение параметра в таблице
                await connection.execute(
                    f"UPDATE notification_modes SET {notification_key} = $1 WHERE fk_user_id = $2", not current_state,
                    user_id
                )

                # Устанавливаем bot_all в False при выборе любого другого режима
                await connection.execute(
                    f"UPDATE notification_modes SET bot_all = False WHERE fk_user_id = $1", user_id
                )

                await connection.execute(
                    """
                    UPDATE notification_modes
                    SET
                        bot_all = True,
                        bot_new_request = False,
                        bot_request_change = False,
                        bot_change_interval = False
                    WHERE fk_user_id = $1
                        AND bot_new_request = True
                        AND bot_request_change = True
                        AND bot_change_interval = True
                    """,
                    user_id
                )

        elif notification_key.startswith('email'):
            if notification_key == 'email_all':
                await connection.execute(
                    """
                    UPDATE notification_modes 
                    SET 
                        email_all = CASE WHEN $1 = 'email_all' THEN NOT email_all ELSE email_all END,
                        email_new_request = FALSE,
                        email_request_change = FALSE,
                        email_change_interval = FALSE
                    WHERE fk_user_id = $2
                    """,
                    notification_key, user_id
                )

            else:
                # Получаем текущее состояние параметра уведомления и инвертируем его
                current_state = await connection.fetchval(
                    f"SELECT {notification_key} FROM notification_modes WHERE fk_user_id = $1", user_id
                )
                # Обновляем значение параметра в таблице
                await connection.execute(
                    f"UPDATE notification_modes SET {notification_key} = $1 WHERE fk_user_id = $2", not current_state,
                    user_id
                )

                # Устанавливаем email_all в False при выборе любого другого режима
                await connection.execute(
                    f"UPDATE notification_modes SET email_all = False WHERE fk_user_id = $1", user_id
                )

                await connection.execute(
                    """
                    UPDATE notification_modes
                    SET
                        email_all = True,
                        email_new_request = False,
                        email_request_change = False,
                        email_change_interval = False
                    WHERE fk_user_id = $1
                        AND email_new_request = True
                        AND email_request_change = True
                        AND email_change_interval = True
                    """,
                    user_id
                )


async def disable_all_notice(user_id: int, notification_key: str) -> None:
    """Полностью отключает уведомления по переданному notification_key"""
    connection = await connect_pg()
    async with connection.transaction():
        if notification_key.startswith('bot'):
            await connection.execute(
                """UPDATE notification_modes
                SET 
                    bot_all = false, 
                    bot_new_request = false, 
                    bot_request_change = false, 
                    bot_change_interval = false 
                WHERE fk_user_id = $1""",
                user_id)
        elif notification_key.startswith('email'):
            await connection.execute(
                """UPDATE notification_modes 
                SET email_all = false, 
                    email_new_request = false,
                    email_request_change = false, 
                    email_change_interval = false 
                WHERE fk_user_id = $1""",
                user_id)


async def change_user_email(user_id: int, email: str) -> None:
    """Изменяет почту пользователя"""
    connection = await connect_pg()
    async with connection.transaction():
        await connection.execute(
            """UPDATE users SET email = $1 WHERE user_id = $2""",
            email, user_id
        )


# функция добавления Логина Аргуса в БД
async def update_argus_login(user_id: int, login: str) -> None:
    connection = await connect_pg()
    async with connection.transaction():
        await connection.execute(
            """UPDATE users SET login = $1 WHERE user_id = $2""",
            login, user_id
        )


async def latest_activity(user_id: int) -> None:
    connection = await connect_pg()
    current_time = datetime.now()
    async with connection.transaction():
        await connection.execute(
            """UPDATE users SET request_time = $1 WHERE user_id = $2""",
            current_time, user_id
        )


async def change_array(data) -> None:
    connection = await connect_pg()
    async with connection.transaction():
        await connection.execute(
            """UPDATE data_table 
            SET worksite_short_name = $1, 
                assignee_name = $2, 
                close_ki = $3 
            WHERE crm = $4
            """,
            data['WORKSITE_SHORT_NAME'], data['ASSIGNEE_NAME'],
            data.get('CLOSE_KI'), data['CRM']
        )
