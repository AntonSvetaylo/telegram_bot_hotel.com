from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config
from loguru import logger
from os import path
from database.bot_db import create_db

storage = StateMemoryStorage()
my_bot = TeleBot(token=config.bot_token, state_storage=storage)

headers = {
    'X-RapidAPI-Key': config.rapid_api_key,
    'X-RapidAPI-Host': 'hotels4.p.rapidapi.com'
}

ru_step = {'year': 'год', 'month': 'месяц', 'day': 'день'}

url = [
    "https://hotels4.p.rapidapi.com/locations/v2/search",
    "https://hotels4.p.rapidapi.com/properties/list",
    "https://hotels4.p.rapidapi.com/properties/get-hotel-photos",
    "https://hotels4.p.rapidapi.com/properties/get-details"
]

logger.add("debugs/debug.log", format="{time} {level} {message}", level="DEBUG",
           rotation="100 MB", compression="zip")

cities = {}

history_result = {}
