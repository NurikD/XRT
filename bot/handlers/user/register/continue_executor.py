from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from .main_register import save_user_data
from .fsm_states import Form


router = Router()


# Этап отправки АРГУСА #

@router.message(Form.taking_argus, F.text.contains('_'))
async def argus_taken(message: Message, state: FSMContext) -> None:
    await state.update_data(login=message.text.upper())
    await message.answer(
        "🏘Введите свои участки\n\n"
        "<i>Пример:\n"
        "ХТ_ИНСТ. + 3 ЛТП_Нефтеюганск\n"
        "УТУ_Пойковский</i>"
    )

    await state.set_state(Form.taking_plots)


@router.message(Form.taking_argus)
async def argus_incorrectly(message: Message) -> None:
    await message.answer(
        "<b>❌Некорректный АРГУС</b>\n\n"
        "Введите еще раз!",
    )


@router.message(Form.taking_plots, F.text.contains('_'))
async def plots_taken(message: Message, state: FSMContext) -> None:
    input_lines = set(message.text.strip().split('\n'))
    await state.update_data(plots=input_lines)
    user_data = await state.get_data()

    await save_user_data(message, user_data)
    await state.clear()


@router.message(Form.taking_plots)
async def plots_incorrectly(message: Message) -> None:
    await message.answer(
        "<b>❌Некорректный ввод участков!</b>\n\n"
        "Введите еще раз!",
    )
