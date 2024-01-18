from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hide_link

from bot.database.methods.update import set_notice_mode, disable_all_notice, latest_activity
from bot.database.methods.get import dispatcher_exists, get_user_role
from bot.database.methods.get import notifications_exists

from bot.handlers.user.utils import deadline_message

from bot.keyboards.user.reply import *
from bot.keyboards.user.inline import *


router = Router()


# Выбор режима настройки уведомлений #

@router.message(F.text == '🔔Уведомления')
async def notice_modes(message: types.Message):
    user_role = await get_user_role(message.from_user.id)
    await message.answer(text=f"{hide_link('https://telegra.ph/file/4c3eec48f6538e097ba9e.png')}"
                              "Выберите способ отправки уведомлений, нажав на соответсвующую кнопку ниже 👇",
                         reply_markup=notifications_settings(user_role))

    await latest_activity(message.from_user.id)  # Записывает время активности


# Настройка уведомлений для бота #


@router.callback_query(F.data == 'notice_in_bot')
async def bot_mode(call: CallbackQuery):
    notifications = await notifications_exists(call.from_user.id)

    if await deadline_message(call) is False:
        await call.message.edit_text(
            text="Выберите режим отправки уведомлений для бота:",
            reply_markup=notice_selection_options(notifications, 'bot')
        )

    await call.answer()


# Настройка уведомлений для почты #


@router.callback_query(F.data == 'notice_in_mail')
async def mail_mode(call: CallbackQuery):
    if await deadline_message(call) is False:
        if await dispatcher_exists(call.from_user.id) is True:
            notifications = await notifications_exists(call.from_user.id)
            await call.message.edit_text(
                text="Выберите режим отправки уведомлений для почты: ",
                reply_markup=notice_selection_options(notifications, 'email')
            )

    await call.answer()


# Ловим выбранный режим и заносим его в БД #


@router.callback_query(F.data.startswith('set_'))
async def set_mode(call: CallbackQuery):
    notification_key = call.data.split('set_')[1]
    user_id = call.from_user.id

    await set_notice_mode(user_id, notification_key)

    if notification_key.startswith('bot'):
        await bot_mode(call)

    else:
        await mail_mode(call)

    await call.answer()


# Кнопка назад возвращает в меню выбора уведомлений #


@router.callback_query(F.data.startswith('back_'))
async def back_to_main(call: CallbackQuery):
    user_role = await get_user_role(call.from_user.id)
    if await deadline_message(call) is False:
        await call.message.edit_text(
            text=f"{hide_link('https://telegra.ph/file/4c3eec48f6538e097ba9e.png')}"
                 "Выберите способ отправки уведомлений, нажав на соответсвующую кнопку ниже 👇",
            reply_markup=notifications_settings(user_role)
        )

    await call.answer()


# Отключает полностью уведомления для бота/почты #


@router.callback_query(F.data.startswith('disable'))
async def disable_notifications(call: CallbackQuery):
    notification_key = call.data.split('_')[1]
    user_id = call.from_user.id
    await disable_all_notice(user_id, notification_key)

    if notification_key.startswith('bot'):
        await bot_mode(call)

    else:
        await mail_mode(call)

    await call.answer()
