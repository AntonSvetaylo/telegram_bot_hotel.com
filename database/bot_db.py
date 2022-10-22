import sqlite3


def create_db():
    with sqlite3.connect('database/telegram_bot_db', check_same_thread=False) as bot_db:
        cursor = bot_db.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                                bot_user_id INT,
                                user_name TEXT
                                )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS user_query (
                                user_query_id INT,
                                bot_user_id INT,
                                user_command TEXT,
                                hotel_name TEXT,
                                hotel_address TEXT,
                                hotel_price FLOAT,
                                currency TEXT,
                                hotel_distance TEXT,
                                URL_hotel TEXT
                                )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS user_commands (
                                user_query_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                bot_user_id INT,
                                command_name TEXT,
                                command_date  DATETIME
                                )""")

        bot_db.commit()
