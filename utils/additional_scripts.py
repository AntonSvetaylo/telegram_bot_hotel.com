import re
import requests
import json
from typing import List, Dict
from states.User_cls import User
from loader import my_bot, headers, url, logger


@logger.catch
def convert_str(my_str: str) -> str:
    """
    Функция конвертирует строку - наименование города. Убирает лишнее.
    :param my_str: str - строка до конвертации.
    :return result: str - строка после конвертации.
    """
    patterns = [r"<span class='\w+'>", r"(</span>)"]
    result = my_str
    for pattern in patterns:
        result = re.sub(pattern, '', result)
    return result


def request_to_api(url: str, headers: dict, querystring: dict):
    """
    Функция производит непосредственный запрос к API и возвращает ответ API, е
    сли запрос был успешным.
    :param url: str - url-адрес БД в API, к которому производится запрос.
    :param headers: dict - Токен и Хост API.
    :param querystring: dict - Параметры запроса пользователя.

    :return response - результат запроса.
    """
    try:
        response = requests.request('GET', url, headers=headers, params=querystring, timeout=150)
        if response.status_code == requests.codes.ok:
            return response
    except Exception as e:
        logger.debug(e)
        return None


@logger.catch
def check_string(my_str: str) -> List:
    """
    Функция формирует список из чисел, указанных в запросе пользователя.
    :param my_str: str - сообщение пользователя.
    :return: result - список чисел.
    """
    pattern = r"\d+"
    result = re.findall(pattern, my_str)
    return result


@logger.catch
def is_digit(string: str) -> bool:
    """
    Функция проверяет, что символы в строке - это число (целое или с плавающей точкой).
    :param string: str - строка пользователя.
    :return: return - True или False.
    """
    if string.isdigit():
        return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False


@logger.catch
def to_float_or_not_to_float(string: str) -> str:
    """
    Функция заменяет запятую на точку в строке.
    :param string: str - строка пользователя.
    :return: обновленная строка.
    """
    if ',' in string:
        string = string.replace(',', '.')
    return string


@logger.catch
def hotel_for_list(api_hotel: dict, chat_id: int) -> Dict:
    """
    В рамках функции выгружается информация по отелю в результате запроса к API.
    :param api_hotel: dict - данные отеля из API.
    :param chat_id: int - ID пользователя.
    :return: hotel - информация по одному из пяти искомых отелей.
    """
    try:
        user = User.users[chat_id]
        query = user.get_query()
        hotel = dict()
        hotel['id'] = api_hotel['id']
        hotel['name'] = api_hotel['name']
        hotel['distance'] = api_hotel['landmarks'][0]['distance']

        querystring = {"id": api_hotel['id'], "locale": "ru_RU"}
        response = request_to_api(url=url[3], headers=headers, querystring=querystring)
        data = json.loads(response.text)
        hotel['address'] = data['data']['body']['propertyDescription']['address']['fullAddress']

        hotel['price'] = round(api_hotel['ratePlan']['price']['exactCurrent'])
        hotel['url'] = 'https://hotels.com/ho{hotel_id}'.format(hotel_id=api_hotel['id'])
        if query.photo > 0:
            hotel['photo'] = photo(hotel_id=hotel['id'], chat_id=chat_id)
        return hotel
    except Exception as e:
        logger.debug(e)
        my_bot.send_message(chat_id, 'Что-то пошло не так😖\n'
                                     'Мне жаль, но придется повторить запрос😔\n'
                                     '↙Выдерите команду еще раз.')


@logger.catch
def photo(hotel_id: int, chat_id: int) -> List:
    """
    Функция для выгрузки фотографий.
    :param hotel_id: int - ID отеля.
    :param chat_id: int - ID пользователя.
    :return: photo_list - список фотографий.
    """
    try:
        user = User.users[chat_id]
        query = user.get_query()
        querystring = {"id": hotel_id}
        response = request_to_api(url=url[2], headers=headers, querystring=querystring)
        p_data = json.loads(response.text)
        photo_list = []

        for p in p_data['hotelImages'][0:query.photo]:
            photo_list.append(p['baseUrl'].format(size='z'))
        return photo_list
    except Exception as e:
        logger.debug(e)
        my_bot.send_message(chat_id, 'Что-то пошло не так😖\n'
                                     'Мне жаль, но придется повторить запрос😔\n'
                                     '↙Выдерите команду еще раз.')
