import logging
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage

from bot.misc.config import TgKeys

from bot.handlers.user import default_commands
from bot.handlers.user import applications, notifications, private_office, unknown_commands, help
from bot.handlers.user.register import main_register, continue_dispatcher, continue_executor

from bot.handlers.user.utils import sender_notice

from bot.handlers.admin import panel

from bot.database.models import *
from bot.database.methods.insert import add_statuses_name

from .misc.commands import set_commands


async def start_db() -> None:
    await create_statuses()
    await add_statuses_name()
    await create_data_array()
    await create_users()
    await create_notification_modes()


async def get_commands(bot: Bot) -> None:
    await set_commands(bot)


async def start_bot() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    bot = Bot(token=TgKeys.TOKEN, parse_mode='HTML')
    dp = Dispatcher(storage=MemoryStorage())

    # Принудительно настраиваем фильтр на работу только в чатах один-на-один с ботом
    dp.message.filter(F.chat.type == "private")

    # Создаем таблицы при запуске бота
    dp.startup.register(start_db)

    # Подгружаем объект кнопок с командами (меню)
    dp.startup.register(get_commands)

    # Регистрация роутеров с командами
    dp.include_router(default_commands.router)

    # Процесс регистрации пользователя
    dp.include_router(main_register.router)
    dp.include_router(continue_dispatcher.router)
    dp.include_router(continue_executor.router)

    # Инициализация пользовательского меню
    dp.include_router(applications.router)
    dp.include_router(help.router)
    dp.include_router(notifications.router)
    dp.include_router(private_office.router)

    # Инициализация админ-панели
    dp.include_router(panel.router)

    # Регистрация роутера с неизвестными командами
    dp.include_router(unknown_commands.router)

    asyncio.create_task(sender_notice())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    await bot.session.close()
