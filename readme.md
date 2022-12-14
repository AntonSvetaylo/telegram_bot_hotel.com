                                            **TooEasyTravel_Svet_Bot**

Данная инструкция предназначения для настройки Telegram-bot **TooEasyTravel_Svet_Bot** к сайту
Hotels.com.

Структура кода:
- config_data
- database
- debugs
- handlers
- keyboards
- states
- utils

Так в корневой папке находятся следующие файлы:
- .env.template
- .gitignore
- loader.py
- mine.py
- Requirements.txt


                                                **Настройка бота**
Перед началом работы необходимо установить пакет **Requirements.txt**.
В данном пакете содержатся все необходимые зависимости для дальнейшей работы.
Установку пакета возможно произвести командой:

**pip install -r Requirements.txt**

Следующим шагом необходимо создать файл **.env**, в котором будет содержаться 
конфиденциальная информация (токен бота и токен API), согласно файла-примера
**.env.template**.

Настройка бота завершена.


                                                **Структура бота**
**loader.py** - В данной файле содержатся следующие объекты: экземпляр бота, headers,
список url-адресов для запроса и другие.

**mine.py** - Данным файлом производится запуск бота.

**Requirements.txt** - Файл со списком зависимостей.

**config_data** - В данной папке содержится файл **config.py**, в котором содержатся
объекты конфигурации бота (бот-токен, API-токен, кнопки).

**database** - В данной папке содержится файл **bot_db.py**. В рамках данного файла создается БД Telegram бота.

**handlers** - В данной папке содержится подпапка **default_handlers**, в которой, в свою очередь, 
содержатся файлы с обработчиками сообщений: **message_handlers.py** и **callback_handlers.py**

**debugs** - Данная папка создается после первого запуска бота. В данной папке будут храниться логи.

**keyboards** - Данная папка предназначается для создания Inline и Reply кнопок. 
В данной версии бота не используется.

**states** - В данной папке содержится файл **User_cls.py**, в котором прописаны классы
**User** и **Order**.

**utils** - В данной папке содержатся файлы: 
- **main_scripts.py** - файл с основной структурой бота.
- **additional_scripts.py** - файл с дополнительными функциями.
- **set_bot_commands.py** - файл-загрузчик команд бота.