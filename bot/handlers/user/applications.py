from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.types import Message, FSInputFile

from bot.database.methods.update import latest_activity

from bot.handlers.user.utils import deadline_message

from bot.keyboards.user.reply import *
from bot.keyboards.user.inline import *

from bot.app.array_filter import convert_to_excel

router = Router()

# Глобальные переменные для хранения file_path и counted_apps
global file_path, counted_apps


# Вывод всех заявок #

@router.message(F.text == '📥Все')
async def all_requests(message: types.Message):
    await send_document_by_request('all', message)

    await latest_activity(message.from_user.id)  # Записывает время активности


# Вывод заявок без исполнителя #

@router.message(F.text == '📤Без исполнителя')
async def non_executor_requests(message: Message):
    await send_document_by_request('non_executor', message)

    await latest_activity(message.from_user.id)  # Записывает время активности


async def send_document_by_request(request_type, message: Message) -> None:
    global file_path, counted_apps
    try:
        file_path, counted_apps = await convert_to_excel(request_type)
        generated_file = FSInputFile(file_path)

        await message.answer_document(
            generated_file,
            reply_markup=btn_app_by_city()
        )
    except TypeError:
        await message.answer('⛔️Нет данных для вывода. Пожалуйста, подождите.')


# Вывод кол-ва заявок по городам #

@router.callback_query(F.data == 'data_by_city')
async def requests_by_city(call: CallbackQuery):
    if await deadline_message(call) is False:
        global file_path, counted_apps  # Объявляем глобальные переменные

        await call.message.delete()
        await call.message.answer(
            text=counted_apps,
            reply_markup=btn_back_to_excel()
        )

    await call.answer()


@router.callback_query(F.data == 'back_to_excel')
async def back_to_file(call: CallbackQuery):
    if await deadline_message(call) is False:
        global file_path, counted_apps  # Объявляем глобальные переменные
        generated_file = FSInputFile(file_path)

        await call.message.delete()
        await call.message.answer_document(
            generated_file,
            reply_markup=btn_app_by_city()
        )

    await call.answer()
