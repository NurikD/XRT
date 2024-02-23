from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hide_link
from bot.database.methods.get import get_argus_login
from bot.database.methods.update import latest_activity, update_argus_login

from bot.handlers.user.utils import deadline_message
from bot.handlers.user.register.fsm_states import Form

from bot.keyboards.user.reply import *
from bot.keyboards.user.inline import *

router = Router()

# Глобальные переменные для хранения file_path и counted_apps
global file_path, counted_apps

# Вывод функций, которые может изменить пользователь #

@router.message(F.text == '💻Личный кабинет')
async def settings(message: Message):
    await message.answer(
        text=f"{hide_link('https://telegra.ph/file/2e8bf0a6bd744d44231bc.png')}"
             "В данном разделе, вы можете изменить существующий адрес электронной почты на новый. "
             "Нажмите на параметр ниже, который хотите изменить 👇",
        reply_markup=settings_menu())

    await latest_activity(message.from_user.id)


@router.message(F.text == '🏘Участки')
async def plots(message: Message):
    await message.answer("<i>Функция в режиме апробации...</i>⏰")


# Добавление логина Аргуса в БД
@router.message(F.text == 'Логин Аргус')
async def argus_login(message: Message):
    await message.answer("Введите свой логин АРГУС:")


@router.message(F.text.lower())
async def argus_login_command(message: Message, state: FSMContext):
    try:
        login = message.text.strip()

        # Проверка, существует ли логин Аргуса в базе данных
        existing_login = await get_argus_login(message.from_user.id)
        if existing_login:
            await message.answer(f"У вас уже установлен логин Аргус: {existing_login}")
        else:
            await update_argus_login(message.from_user.id, login)
            await message.answer(f"Логин Аргус успешно сохранен: {login}")
        await state.finish()

    except Exception as e:
        print(f"Произошла ошибка: {e}")


@router.callback_query(F.data == 'change_executor_to_dispatcher')
async def change_to_dispatcher(call: CallbackQuery, state: FSMContext):
    await state.update_data(change_role='to_dispatcher')
    if await deadline_message(call) is False:
        await call.message.edit_text(
            "Введите адрес эл.почты:"
        )

        await state.set_state(Form.taking_email)


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
