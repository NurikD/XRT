from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    taking_full_name = State()
    choosing_role = State()

    taking_email = State()
    checking_email_code = State()

    taking_argus = State()
    taking_plots = State()
