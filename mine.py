from loader import my_bot, logger
import handlers
from utils.set_bot_commands import set_default_commands
from database.bot_db import create_db

create_db()

if __name__ == '__main__':
    try:
        set_default_commands(my_bot)
        my_bot.infinity_polling()
    except Exception as e:
        logger.debug(e)
        
