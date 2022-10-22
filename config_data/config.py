from decouple import config
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()


bot_token = config('token')
rapid_api_key = config('X-RapidAPI-Key')
default_commands = (
    ('start', 'Запустить/перезапустить бот'),
    ('highprice', 'Найти отели с максимальной ценой'),
    ('lowprice', 'Найти отели с минимальной ценой'),
    ('bestdeal', 'Найти отели с лучшей ценой'),
    ('history', 'Вывести последние пять команд с результатами поиска'),
    ('stop', 'Остановить ввода запроса на любом шаге'),
    ('rename', 'Изменить имя пользователя')
)
