from os import getenv

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.types import FSInputFile

from bot.database.methods.get import *

from bot.handlers.user.utils import deadline_message

from bot.keyboards.admin.reply import *
from bot.keyboards.admin.inline import *
from bot.keyboards.user.reply import main_menu

router = Router()


ADMINS = [int(admin_id) for admin_id in getenv('ADMINS').split(',')]


@router.message(F.from_user.id.in_(ADMINS) & (F.text == '/admin'))
async def admin_panel(message: Message):
    await message.answer(
        text="Добро пожаловать, в админ-панель",
        reply_markup=admin_menu()
    )


@router.message(F.from_user.id.in_(ADMINS) & F.text == '📊Статистика')
async def user_statistics(message: Message):
    user_count = await number_of_users()
    active_users, today, week, month = await get_user_statistics()

    await message.answer(f"📊Статистика бота RTX\n\n"
                         f"┌⛩Всего пользователей: {user_count}\n"
                         f"└👤Активных пользователей: {active_users}\n\n"
                         f"┌📮Количество подписок\n"
                         f"├🗻за сегодня: +{today}\n"
                         f"├🏔за неделю: +{week}\n"
                         f"└🌋за месяц: +{month}")


@router.message(F.from_user.id.in_(ADMINS) & F.text == '👤База данных')
async def database_models(message: Message):
    tables = await table_names()
    await message.answer(
        text="Ваши таблицы: ",
        reply_markup=available_tables(tables)
    )


@router.callback_query(F.from_user.id.in_(ADMINS) & F.data.startswith('table_'))
async def get_table(call: CallbackQuery):
    if await deadline_message(call) is False:
        await call.message.delete()

        file_name = await save_table_data(call.data)
        file_path = FSInputFile(f"bot/downloads/admin_requests/{file_name}")

        await call.message.answer_document(
            file_path,
            reply_markup=back_to_tables()
        )

    await call.answer()


@router.callback_query(F.from_user.id.in_(ADMINS) & F.data.startswith('admin_back_'))
async def btn_back(call: CallbackQuery):
    if await deadline_message(call) is False:
        await call.message.delete()
        await database_models(call.message)

    await call.answer()


@router.message(F.from_user.id.in_(ADMINS) & F.text == '🏡Главное меню')
async def back_to_user_panel(message: Message):
    await message.answer(
        text="Возвращаю в главное меню!",
        reply_markup=main_menu()
    )
