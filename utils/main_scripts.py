# -*- coding: utf-8 -*-
import json
import sqlite3
import datetime
from loader import my_bot, headers, url, cities, logger
from telebot import types
from states.User_cls import User
from telegram_bot_calendar import DetailedTelegramCalendar
from utils.additional_scripts import request_to_api, check_string, hotel_for_list, is_digit, \
    to_float_or_not_to_float, convert_str


bot_db = sqlite3.connect('database/telegram_bot_db', check_same_thread=False)
cursor = bot_db.cursor()


@logger.catch
def introduce(message) -> None:
    """
     Функция-приветствие для новых пользователей.
     :param message: сообщение от пользователя в чате-боте.
     """
    logger.debug("Пользователь {} ввел представился - {}".format(message.chat.id, message.text))
    cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", (message.from_user.id, message.text))
    bot_db.commit()
    my_bot.send_message(message.chat.id, 'Приятно познакомиться, {}!'
                                         '\n↙А теперь откройте меню и выберите команду.'.format(message.text))


@logger.catch
def rename(message) -> None:
    """
     Функция изменяет имя пользователя в БД.
     :param message: сообщение от пользователя в чате-боте.
     """
    logger.debug("Пользователь {} изменил имя на {}".format(message.chat.id, message.text))
    cursor.execute("""UPDATE users
                            SET user_name = :name
                            WHERE bot_user_id = :user_id""", {'name': message.text, 'user_id': message.chat.id})
    bot_db.commit()
    my_bot.send_message(message.chat.id, 'Имя изменено👍\n'
                                         '↙Теперь откройте меню и выберите следующую команду')


@logger.catch
def stop_command(message):
    query = User.users[message.chat.id].get_query()
    logger.debug("Пользователь {} остановил команду {}".format(message.chat.id, query.command))
    my_bot.send_message(message.chat.id, 'Команда {} остановлена.\n'
                                         '↙Выберите следующую команду'.format(query.command))


@logger.catch
def city_choice(message) -> None:
    """
    В рамках данной функции производиться выбор города.
    :param message: сообщение от пользователя в чате-боте.
    """
    if message.text == '/stop':
        stop_command(message)
    else:
        logger.debug("Пользователь {} указал город {}".format(message.chat.id, message.text))
        querystring = {'query': message.text.lower(), 'locale': 'ru_RU'}
        response = request_to_api(url=url[0], headers=headers, querystring=querystring)
        data = json.loads(response.text)
        city_list = data['suggestions'][0]['entities']
        markup = types.InlineKeyboardMarkup()
        item_back = types.InlineKeyboardButton('Отменить команду', callback_data="city_none")
        if len(city_list) > 0:
            for i in city_list:
                city = convert_str(my_str=i['caption'])
                cities[i['destinationId']] = city
                city_item = types.InlineKeyboardButton(city, callback_data=f"city{i['destinationId']}")
                markup.add(city_item)
            markup.add(item_back)
            my_bot.send_message(message.chat.id, 'Выберите город из списка ниже', reply_markup=markup)
        else:
            logger.debug("Введенный пользователем {} город {} не найден.".format(message.chat.id, message.text))
            my_bot.send_message(message.chat.id, 'Упс! Я не нашел такой город!')


@logger.catch
def currency(message) -> None:
    """
    В рамках данной функции производиться выбор валюты.
    :param message: сообщение от пользователя в чате-боте.
    """
    logger.debug("Пользователь {} производит выбор валюту.".format(message.chat.id))

    markup = types.InlineKeyboardMarkup(row_width=2)
    usd_item = types.InlineKeyboardButton(text="USD", callback_data='USD')
    eur_item = types.InlineKeyboardButton(text='EUR', callback_data='EUR')
    item_back = types.InlineKeyboardButton('Отменить команду', callback_data="city_none")
    markup.add(usd_item, eur_item, item_back)
    my_bot.send_message(message.chat.id, 'В какой валюте будем считать стоимость?', reply_markup=markup)


@logger.catch
def adults(message) -> None:
    """
    В рамках данной функции выбирается количество взрослых для проживания в одном номере.
    :param message: сообщение от пользователя в чате-боте.
    """
    logger.debug("Пользователь {} выбирает количество взрослых, "
                 "которые будут проживать в одном номере".format(message.chat.id))
    markup = types.InlineKeyboardMarkup(row_width=4)
    item_back = types.InlineKeyboardButton('Отменить команду', callback_data="city_none")
    items = []
    for n in range(4):
        items.append(types.InlineKeyboardButton(n+1, callback_data=f'adult{n+1}'))
    markup.add(items[0], items[1], items[2], items[3], item_back)
    my_bot.send_message(message.chat.id,  'Далее, укажите количество взрослых, которые будут проживать в номере.',
                        reply_markup=markup)


@logger.catch
def children(message) -> None:
    """
    В рамках данной функции уточняется, будут ли проживать в номере дети.
    :param message: сообщение от пользователя в чате-боте.
    """
    logger.debug("Пользователь {} уточняет, будут ли проживать в номере дети.".format(message.chat.id))
    markup = types.InlineKeyboardMarkup(row_width=2)
    yes_item = types.InlineKeyboardButton('Да', callback_data='yes')
    no_item = types.InlineKeyboardButton('Нет', callback_data='no')
    item_back = types.InlineKeyboardButton('Отменить команду', callback_data="city_none")
    markup.add(yes_item, no_item, item_back)
    my_bot.send_message(message.chat.id, 'Дети будут проживать в номере?', reply_markup=markup)


@logger.catch
def children_age(message) -> None:
    """
    В рамках данной функции проверяется и добавляется возраст детей к экземпляру класса.
    :param message: сообщение от пользователя в чате-боте.
    """
    logger.debug("Пользователь {} указал возраст ребенка/детей.".format(message.chat.id))
    user = User.users[message.chat.id]
    query = user.get_query()
    ages = check_string(my_str=message.text)
    if len(ages) == 0:
        logger.debug("Пользователь {} неверно указал возраст ребенка/детей.".format(message.chat.id))
        my_bot.send_message(message.chat.id, 'Нужно указать либо одно число,\n'
                                             'Либо несколько числе через запятую')
        children(message)
    elif len(ages) > 1:
        query.children = ', '.join(ages)
        my_bot.send_message(message.chat.id, 'Количество детей - {}'.format(len(ages)))
        checkin_date(message)
    else:
        query.children = ages[0]
        my_bot.send_message(message.chat.id, 'Количество детей - {}'.format(len(ages)))
        checkin_date(message)


@logger.catch
def checkin_date(message) -> None:
    """
    В рамках данной функции указывается дата заезда.
    :param message: сообщение от пользователя в чате-боте.
    """
    logger.debug("Пользователь {} вводит дату заезда в отель.".format(message.chat.id))
    my_bot.send_message(message.chat.id, 'Теперь переходим к датам заезда и выезда')
    date = datetime.date.today()
    my_calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=date).build()
    my_bot.send_message(message.chat.id, 'Выберите дату заезда.', reply_markup=my_calendar)


@logger.catch
def checkout_date(message) -> None:
    """
    В рамках данной функции указывается дата заезда.
    :param message: сообщение от пользователя в чате-боте.
    """
    logger.debug("Пользователь {} вводит дату выезда из отеля.".format(message.chat.id))
    user = User.users[message.chat.id]
    query = user.get_query()
    date = (datetime.datetime.strptime(str(query.check_in), "%Y-%m-%d") + datetime.timedelta(days=1)).date()
    my_calendar, step = DetailedTelegramCalendar(calendar_id=2, locale='ru', min_date=date).build()
    my_bot.send_message(message.chat.id, 'Укажите дату выезда.', reply_markup=my_calendar)


@logger.catch
def price(message) -> None:
    """
    В данной функции указывается диапазон цен, в рамках которых производится поиск.
    :param message: сообщение от пользователя в чате-боте.
    """
    logger.debug("Пользователь {} указывает диапазон приемлемых цен.".format(message.chat.id))
    msg = my_bot.send_message(message.chat.id, 'В каком диапазоне цен будем искать отели? '
                                               '(укажите числами: мин.цена - макс.цена)')
    my_bot.register_next_step_handler(msg, intermediate_step)


@logger.catch
def intermediate_step(message) -> None:
    """
    Промежуточная функция, в рамках которой производится проверка введенных пользователем цен.
    :param message: сообщение от пользователя в чате-боте.
    """
    try:
        if message.text == '/stop':
            stop_command(message)
        else:
            result = check_string(my_str=message.text)
            if int(result[0]) > int(result[1]):
                logger.debug("Пользователь {} неверно указал цены. "
                             "Минимальная цена больше максимальной.".format(message.chat.id))
                my_bot.send_message(message.chat.id, 'Минимальная цена не может быть больше максимальной цены.')
                price(message)
            elif len(result) > 2:
                logger.debug("Пользователь {} неверно указал цены (больше двух чисел)".format(message.chat.id))
                my_bot.send_message(message.chat.id, 'Укажите диапазон из двух цен.')
                price(message)
            else:
                logger.debug("Пользователь {} верно указал цены.".format(message.chat.id))
                user = User.users[message.chat.id]
                query = user.get_query()
                query.minprice = int(result[0])
                query.maxprice = int(result[1])
                distance_to_center(message)
    except IndexError:
        logger.debug("Пользователь {} неверно указал цены. Вместо цифр указан текст.".format(message.chat.id))
        my_bot.send_message(message.chat.id, '❗❗❗Диапазон цен нужно указать числами❗❗❗')
        price(message)


@logger.catch
def distance_to_center(message) -> None:
    """
    В рамках данной функции указывается максимальное расстояние до центра.
    :param message: сообщение от пользователя в чате-боте.
    """
    logger.debug("Пользователь {} указывает дистанцию до центра города.".format(message.chat.id))
    msg = my_bot.send_message(message.chat.id, 'Далее укажите максимальное расстояние от центра в км.')
    my_bot.register_next_step_handler(msg, intermediate_step_two)


@logger.catch
def intermediate_step_two(message) -> None:
    """
    Промежуточная функция, в рамках которой производится проверка указанного пользователем расстояния до центра.
    :param message: сообщение от пользователя в чате-боте.
    """
    if message.text == '/stop':
        stop_command(message)
    else:
        user_distance = to_float_or_not_to_float(message.text)
        if is_digit(string=user_distance):
            logger.debug("Пользователь {} верно указал расстояние до центра города.".format(message.chat.id))
            user = User.users[message.chat.id]
            query = user.get_query()
            query.max_distance = float(message.text)
            adults(message)
        else:
            logger.debug("Пользователь {} неверно указал расстояние до центра.".format(message.chat.id))
            my_bot.send_message(message.chat.id, 'Неверно указано максимальное расстояние до центра. '
                                                 'Нужно указать число')
            distance_to_center(message)


@logger.catch
def photo(message) -> None:
    """
    В рамках данной функции запрашивается потребность фотографий к отелям.
    :param message: сообщение от пользователя в чате-боте.
    """
    logger.debug("Пользователь {} уточняет потребность в выгрузке фото.".format(message.chat.id))
    markup = types.InlineKeyboardMarkup(row_width=2)
    yes_item = types.InlineKeyboardButton(text='да', callback_data='photo:yes')
    no_item = types.InlineKeyboardButton(text='нет', callback_data='photo:no')
    item_back = types.InlineKeyboardButton('Отменить команду', callback_data="city_none")
    markup.add(yes_item, no_item, item_back)
    my_bot.send_message(message.chat.id, 'Выгрузить фотографии?', reply_markup=markup)


def query_to_api(message) -> None:
    """
    В рамках данной функции 'собирается' запрос к API Hotels.com,
    на основании, указанных пользователем, далее производится запрос к API,
    после чего выводится результат.
    :param message: сообщение от пользователя в чате-боте.
    """
    try:
        logger.debug("Производится выгрузка из API по запросу пользователя {}.".format(message.chat.id))
        user = User.users[message.chat.id]
        query = user.get_query()
        querystring = {"destinationId": query.destinationid,
                       "pageNumber": "1",
                       "pageSize": "25",
                       "checkIn": query.check_in,
                       "checkOut": query.check_out,
                       "adults1": query.adults,
                       "sortOrder": query.sortorder,
                       "locale": "ru_RU",
                       "currency": query.currency}
        if query.children != '':
            querystring["children1"] = query.children

        response = request_to_api(url=url[1], headers=headers, querystring=querystring)
        data = json.loads(response.text)

        hotels = []
        if query.command == 'lowprice':

            for h in data['data']['body']['searchResults']['results'][:5]:
                hotel = hotel_for_list(api_hotel=h, chat_id=message.chat.id)
                hotels.append(hotel)
        elif query.command == 'highprice':
            for h in data['data']['body']['searchResults']['results'][-5::1]:
                hotel = hotel_for_list(api_hotel=h, chat_id=message.chat.id)
                hotels.append(hotel)
        elif query.command == 'bestdeal':
            for h in data['data']['body']['searchResults']['results']:
                distance_to_center_api = h['landmarks'][0]['distance'].split()
                distance_to_center_api[0] = distance_to_center_api[0].replace(',', '.')
                if query.minprice <= round(h['ratePlan']['price']['exactCurrent']) <= query.maxprice\
                        and float(distance_to_center_api[0]) <= query.max_distance:
                    hotel = hotel_for_list(api_hotel=h, chat_id=message.chat.id)
                    hotels.append(hotel)
                if len(hotels) == 5:
                    break

        query.result = hotels

        if len(hotels) == 0:
            logger.debug("По запросу пользователя {} не найдено ни одного отеля.".format(message.chat.id))
            my_bot.send_message(message.chat.id, 'Не найдено ни одного подходящего отеля 😞')
        else:
            logger.debug("Запросу пользователя {} выполнен успешно.".format(message.chat.id))
            for hotel in hotels:
                cursor.execute("""INSERT INTO user_query(bot_user_id,
                                user_command,
                                hotel_name,
                                hotel_address,
                                hotel_price,
                                currency,
                                hotel_distance,
                                URL_hotel) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (
                                                                message.chat.id,
                                                                query.command,
                                                                hotel['name'],
                                                                hotel['address'],
                                                                hotel['price'],
                                                                query.currency,
                                                                hotel['distance'],
                                                                hotel['url']
                                                                ))
                bot_db.commit()

                if query.photo > 0:
                    photos = []
                    for photo in hotel['photo']:
                        photos.append(types.InputMediaPhoto(photo))
                    my_bot.send_media_group(message.chat.id, photos)
                my_bot.send_message(message.chat.id, ''
                                                     'Наименование: {hotel_name}\n'
                                                     'Адрес: {address}\n'
                                                     'Цена за сутки: {price_per_day} '
                                                     '{currency}\n'
                                                     'Расстояние до центра: {distance}\n'
                                                     'URL: {url}'.format(
                                                                                hotel_name=hotel['name'],
                                                                                address=hotel['address'],
                                                                                price_per_day=hotel['price'],
                                                                                currency=query.currency,
                                                                                distance=hotel['distance'],
                                                                                url=hotel['url']
                                                     ), disable_web_page_preview=True
                                    )
            cursor.execute("""INSERT INTO user_commands VALUES (NULL, ?, ?, ?)""",
                           (message.chat.id, query.command, datetime.datetime.now()))

            cursor.execute("""UPDATE user_query
                                    SET user_query_id = (
                                                            SELECT user_query_id
                                                            FROM user_commands
                                                            WHERE user_commands.command_name = user_query.user_command
                                                                AND user_commands.bot_user_id = user_query.bot_user_id
                                                            ORDER BY user_commands.command_date DESC
                                                            LIMIT 1
                                                            )
                                    WHERE user_query_id IS NULL
                                    """)
            bot_db.commit()
            my_bot.send_message(message.chat.id, '=' * 20)
        my_bot.send_message(message.chat.id, 'Поиск завершен. Можно выбирать другую команду.')
    except Exception as e:
        my_bot.send_message(message.chat.id, 'Что-то пошло не так😖\n'
                                             'Мне жаль, но придется повторить запрос😔\n'
                                             '↙Выдерите команду еще раз.')
        logger.debug(e)
