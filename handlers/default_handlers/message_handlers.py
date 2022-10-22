import sqlite3
from loader import my_bot, history_result, logger
from states.User_cls import User
from utils.main_scripts import introduce, city_choice, rename


bot_db = sqlite3.connect('database/telegram_bot_db', check_same_thread=False)
cursor = bot_db.cursor()


@logger.catch
@my_bot.message_handler(commands=['start'])
def start_command(message) -> None:
    """
    Функция, отвечающая за команду START.
    Функция:
        - проверяет пользователя в БД. По результату проверка в БД предлагаетЖ
            - либо представиться;
            - либо выбрать команду.
    :param message: сообщение-команда от пользователя в чате-боте.
    """
    logger.debug("Пользователь {} ввел команду start".format(message.chat.id))
    cursor.execute("""SELECT *
                            FROM users
                            WHERE bot_user_id = :ID""", {'ID': message.chat.id})
    user = cursor.fetchone()
    bot_db.commit()
    if user is not None:
        my_bot.send_message(message.chat.id, 'С возвращением, {name}👋!\n'
                                             '↙Открой меню и выбери команду!'.format(name=user[1]))
    else:
        my_bot.send_message(message.chat.id, 'Приветствую, странник 👋'
                                             '\nЯ бот сайта Hotels.com'
                                             '\nЯ помогу тебе выбрать и забронировать '
                                             'отель в любой стране.')
        msg = my_bot.send_message(message.chat.id, 'Как я могу к тебе обращаться?')
        my_bot.register_next_step_handler(msg, introduce)


@logger.catch
@my_bot.message_handler(commands=['history'])
def history_command(message) -> None:
    """
    Функция, отвечающая за команду HISTORY.
    Функция выгружает из БД:
        - пять последних команд пользователя;
        - дату команды;
        - список отелей.
    :param message: сообщение-команда от пользователя в чате-боте.
    """
    logger.debug("Пользователь {} ввел команду history".format(message.chat.id))
    history_result[message.chat.id] = dict()
    cursor.execute("""SELECT uq.user_command,
                                       us.command_date,
                                       uq.hotel_name
                            FROM user_query uq
                            JOIN (SELECT user_query_id,
                                               command_date
                                    FROM user_commands
                                    WHERE bot_user_id = :ID
                                    ORDER BY user_query_id DESC 
                                    LIMIT 5) us ON uq.user_query_id = us.user_query_id""", {'ID': message.chat.id})

    for elem in cursor:
        if elem[1] in history_result[message.chat.id].keys() and \
                elem[0] in history_result[message.chat.id][elem[1]].keys():
            history_result[message.chat.id][elem[1]][elem[0]].append(elem[2])
        elif elem[1] in history_result[message.chat.id].keys() and \
                elem[0] not in history_result[message.chat.id][elem[0]].keys():
            history_result[message.chat.id][elem[1]][elem[0]] = []
            history_result[message.chat.id][elem[1]][elem[0]].append(elem[2])
        else:
            history_result[message.chat.id][elem[1]] = {elem[0]: []}
            history_result[message.chat.id][elem[1]][elem[0]].append(elem[2])

    for date, h_value in history_result[message.chat.id].items():
        for h_com, hotels in h_value.items():
            my_bot.send_message(message.chat.id,
                                'Команда: {command}\n'
                                'Дата: {command_date}\n'
                                'Отели:\n   {hotels}'.format(
                                    command=h_com,
                                    command_date=date,
                                    hotels='\n   '.join(hotels)
                                ))
    bot_db.commit()


@logger.catch
@my_bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def city_requests(message) -> None:
    """
    Функция для запроса города.
    :param message: сообщение-команда от пользователя в чате-боте.
    """
    logger.debug("Пользователь {} ввел команду {}".format(message.chat.id, message.text))
    User(message.chat.id)
    user = User.users[message.chat.id]
    query = user.get_query()
    query.command = message.text[1::]
    msg = my_bot.send_message(message.chat.id, 'Укажите город (любой, кроме русских городов... санкции🤷🤷‍♀)')
    my_bot.register_next_step_handler(msg, city_choice)


@logger.catch
@my_bot.message_handler(commands=['rename'])
def rename_command(message) -> None:
    """
    Функция запрашивает новое имя пользователя для корректировки в БД.
    :param message: сообщение-команда от пользователя в чате-боте.
    """
    logger.debug("Пользователь {} ввел команду rename".format(message.chat.id))
    msg = my_bot.send_message(message.chat.id, 'Укажите новое имя.')
    my_bot.register_next_step_handler(msg, rename)
