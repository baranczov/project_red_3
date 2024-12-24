import logging
import os
from dotenv import dotenv_values

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DOTENV_PATH = os.path.join(BASE_DIR, ".env")

config = dotenv_values(DOTENV_PATH) if os.path.exists(DOTENV_PATH) else {}


def env(key):
    """Получает значение переменной окружения по ключу."""
    return config.get(key)


DEBUG = eval(env("DEBUG"))
API_KEY = env("API_KEY")

LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
