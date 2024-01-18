from os import getenv
from typing import Final
from dotenv import load_dotenv


class TgKeys:
    load_dotenv()
    TOKEN: Final = getenv('TOKEN_API')
