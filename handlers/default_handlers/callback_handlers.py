import datetime
from telebot import types
from loader import my_bot, ru_step, cities, logger
from states.User_cls import User
from utils.main_scripts import adults, children, checkin_date, checkout_date, currency, \
    children_age, price, photo, query_to_api
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP


@logger.catch
@my_bot.callback_query_handler(func=lambda call: call.data.startswith('city'))
def city_answer(call):
    """
    Колбэк функция к функции выбора Города.
    Вносит ID города в экземпляр класса пользователя.
    """
    user = User.users[call.message.chat.id]
    query = user.get_query()
    if call.data == 'city_none':
        my_bot.send_message(call.message.chat.id, '↙Откройте меню и новую выберите команду.')
        logger.debug("Пользователь {} отменил команду {}.".format(call.message.chat.id, query.command))

    else:
        city_id = ''.join([n for n in call.data[4:]])
        query.destinationid = city_id

        my_bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Вы выбрали - {}'.format(cities[call.data[4:]]), reply_markup=None)
        logger.debug("Пользователь {} выбрал город {}.".format(call.message.chat.id, cities[call.data[4:]]))
        currency(call.message)


@logger.catch
@my_bot.callback_query_handler(func=lambda call: call.data in ['USD', 'EUR'])
def currency_answer(call):
    """
    Колбэк функция к функции выбора Валюты.
    Вносит валюту в экземпляр класса пользователя.
    """
    user = User.users[call.message.chat.id]
    query = user.get_query()
    query.currency = call.data
    my_bot.edit_message_text(chat_id=call.message.chat.id,
                             message_id=call.message.message_id,
                             text='Выбрали валюту - {}'.format(query.currency),
                             reply_markup=None)

    logger.debug("Пользователь {} выбрал валюту {}.".format(call.message.chat.id, query.currency))

    if query.command == 'bestdeal':
        price(call.message)
    else:
        adults(call.message)


@logger.catch
@my_bot.callback_query_handler(func=lambda call: call.data.startswith('adult'))
def adult_answer(call):
    """
    Колбэк функция к функции выбора количества взрослых в одном номере.
    Вносит количество взрослых в экземпляр класса пользователя.
    """
    user = User.users[call.message.chat.id]
    query = user.get_query()
    query.adults = call.data[-1]
    my_bot.edit_message_text(chat_id=call.message.chat.id,
                             message_id=call.message.message_id,
                             text='Количество взрослых - {}'.format(query.adults),
                             reply_markup=None)
    logger.debug("Пользователь {} указал кол-во взрослых {}.".format(call.message.chat.id, query.adults))
    children(call.message)


@logger.catch
@my_bot.callback_query_handler(func=lambda call: call.data in ['yes', 'no'])
def children_answer(call):
    """
    Колбэк функция к функции уточнения проживания детей в одном номере.
    В зависимости от ответа происходит переход либо на функцию уточнения возраста детей,
    либо на функцию уточнения даты заезда в отель.
    """
    if call.data == 'yes':

        logger.debug("Пользователь {} указывает возраст детей.".format(call.message.chat.id))

        msg_yes = my_bot.edit_message_text(chat_id=call.message.chat.id,
                                           message_id=call.message.message_id,
                                           text='Укажите возраст детей через запятую, пробел '
                                                'или любой другой разделитель.',
                                           reply_markup=None)
        my_bot.register_next_step_handler(msg_yes, children_age)

    elif call.data == 'no':
        logger.debug("Пользователь {} указал проживание в номере без детей.".format(call.message.chat.id))
        my_bot.edit_message_text(chat_id=call.message.chat.id,
                                 message_id=call.message.message_id,
                                 text='Количество детей - 0',
                                 reply_markup=None)
        checkin_date(call.message)


@logger.catch
@my_bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def cal(c):
    """
    Колбэк функция к функции уточнения даты заезда в отель.
    """
    date = datetime.date.today()
    result, key, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=date).process(c.data)
    if not result and key:
        my_bot.edit_message_text(f"Выберите {ru_step[LSTEP[step]]}",
                                 c.message.chat.id,
                                 c.message.message_id,
                                 reply_markup=key)
    elif result:
        user = User.users[c.message.chat.id]
        query = user.get_query()
        query.check_in = result
        logger.debug("Пользователь {} указал дату заезда - {}.".format(c.message.chat.id, query.check_in))

        my_bot.edit_message_text(f"Указали дату заезда: {result}",
                                 c.message.chat.id,
                                 c.message.message_id)
        checkout_date(c.message)


@logger.catch
@my_bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def cal(c):
    """
    Колбэк функция к функции уточнения даты выезда из отеля.
    """
    user = User.users[c.message.chat.id]
    query = user.get_query()
    date = (datetime.datetime.strptime(str(query.check_in), "%Y-%m-%d") + datetime.timedelta(days=1)).date()
    result, key, step = DetailedTelegramCalendar(calendar_id=2, locale='ru', min_date=date).process(c.data)
    if not result and key:
        my_bot.edit_message_text(f"Выберите {ru_step[LSTEP[step]]}",
                                 c.message.chat.id,
                                 c.message.message_id,
                                 reply_markup=key)
    elif result:
        query.check_out = result
        logger.debug("Пользователь {} указал дату выезда - {}.".format(c.message.chat.id, query.check_out))

        my_bot.edit_message_text(f"Указали дату выезда: {result}",
                                 c.message.chat.id,
                                 c.message.message_id)
        photo(c.message)


@logger.catch
@my_bot.callback_query_handler(func=lambda call: call.data.startswith('photo'))
def photo_answer(call):
    """
    Колбэк функция к функции выгрузки фотографий отеля.
    """
    if call.data == 'photo:yes':
        logger.debug("Пользователь {} выбирает количество фотографий "
                     "каждого отеля для выгрузки.".format(call.message.chat.id))
        markup = types.InlineKeyboardMarkup(row_width=5)
        item_back = types.InlineKeyboardButton('Отменить команду', callback_data="city_none")
        items = []
        for n in range(5):
            items.append(types.InlineKeyboardButton(n + 1, callback_data=f'p_num{n + 1}'))
        markup.add(items[0], items[1], items[2], items[3], items[4], item_back)
        my_bot.send_message(call.message.chat.id, 'Сколько фотографий выгрузить?', reply_markup=markup)
    else:
        logger.debug("Пользователь {} выбрал выгрузку без фотографий.".format(call.message.chat.id))
        my_bot.edit_message_text(chat_id=call.message.chat.id,
                                 message_id=call.message.message_id,
                                 text='Выгружаю...',
                                 reply_markup=None)
        query_to_api(call.message)


@logger.catch
@my_bot.callback_query_handler(func=lambda call: call.data.startswith('p_num'))
def photo_num(call):
    """
    Колбэк функция для функции выше.
    Добавляет в экземпляр класса количество фото для последующего запроса.
    """
    user = User.users[call.message.chat.id]
    query = user.get_query()
    query.photo = int(call.data[-1])
    logger.debug("Пользователь {} выбрал по {} фотографий к каждому отелю.".format(call.message.chat.id, query.photo))
    my_bot.edit_message_text(chat_id=call.message.chat.id,
                             message_id=call.message.message_id,
                             text='Выгружаю...',
                             reply_markup=None)
    query_to_api(call.message)
