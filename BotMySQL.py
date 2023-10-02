import logging
import random
#import time
import mysql.connector
import numpy as np
import threading

from mysql.connector import Error

from threading import Timer
from time import sleep, time
from functools import wraps

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, bot, ParseMode, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Chat
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Вход в БД
def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

# Соединение с БД
connection = create_connection("<HOST NAME>", "<USER NAME>", "<PASSWORD>", "<DATABASE NAME>")



def mult_threading(func):
     """Декоратор для запуска функции в отдельном потоке"""
     @wraps(func)
     def wrapper(*args_, **kwargs_):
         import threading
         func_thread = threading.Thread(target=func,
                                        args=tuple(args_),
                                        kwargs=kwargs_)
         func_thread.start()
         return func_thread
     return wrapper


@mult_threading
def connn(update, connection):
    print('Connected')
    while True:
        sleep(200)
        #print('Connected')
        cursor = connection.cursor()
        cursor.execute(f"""UPDATE users SET adm = 1 WHERE userid = 593433853 """)
        connection.commit()
        cursor.execute(f"""UPDATE users SET adm = 2 WHERE userid = 593433853 """)
        connection.commit()

#==================================================================================================================================#

# Таблица рулетки
def tablerulet(update, connection):
    cursor = connection.cursor()
    chat = update.effective_chat
    chatid = chat.id * chat.id // 500000
    cursor.execute(f"""
CREATE TABLE IF NOT EXISTS betinchat{chatid} (
  id INT AUTO_INCREMENT,
  username VARCHAR(20),
  userid INT,
  bet INT,
  field VARCHAR(20),
  Pwin INT,
  coment VARCHAR(50),
  PRIMARY KEY (id)
) ENGINE = InnoDB
""")
    cursor.execute (f"""
CREATE TABLE IF NOT EXISTS log{chatid} (
  id INT AUTO_INCREMENT,
  num INT,
  color VARCHAR(15),
  PRIMARY KEY (id)
) ENGINE = InnoDB
""")
    cursor.execute (f"""
CREATE TABLE IF NOT EXISTS trash{chatid} (
  id INT AUTO_INCREMENT,
  msgid INT,
  PRIMARY KEY (id)
) ENGINE = InnoDB
""")


# Рулетка/меню
def StolRuletki(update, context, connection):
    cursor = connection.cursor()
    chat = update.effective_chat
    chatid = chat.id * chat.id // 500000
    keyboard = [[InlineKeyboardButton("⛔️", callback_data='27'),
                 InlineKeyboardButton("1стр", callback_data='1'),
                 InlineKeyboardButton("1-3", callback_data='14'),
                 InlineKeyboardButton("10-12", callback_data='15'),
                 InlineKeyboardButton("19-21", callback_data='16'),
                 InlineKeyboardButton("28-30", callback_data='17')],

                [InlineKeyboardButton("💚", callback_data='13'),
                 InlineKeyboardButton("2стр", callback_data='2'),
                 InlineKeyboardButton("4-6", callback_data='18'),
                 InlineKeyboardButton("13-15", callback_data='19'),
                 InlineKeyboardButton("22-24", callback_data='20'),
                 InlineKeyboardButton("31-33", callback_data='21')],

                [InlineKeyboardButton("💰", callback_data='28'),
                 InlineKeyboardButton("3стр", callback_data='3'),
                 InlineKeyboardButton("7-9", callback_data='22'),
                 InlineKeyboardButton("16-18", callback_data='23'),
                 InlineKeyboardButton("25-27", callback_data='24'),
                 InlineKeyboardButton("34-36", callback_data='25')],

                [InlineKeyboardButton("1st 12", callback_data='4'),
                 InlineKeyboardButton("2nd 12", callback_data='5'),
                 InlineKeyboardButton("3rd 12", callback_data='6')],

                [InlineKeyboardButton("1/2", callback_data='7'),
                 InlineKeyboardButton("EVEN", callback_data='8'),
                 InlineKeyboardButton("🔴", callback_data='11'),
                 InlineKeyboardButton("⚫️", callback_data='12'),
                 InlineKeyboardButton("ODD", callback_data='9'),
                 InlineKeyboardButton("2/2", callback_data='10')],

                [InlineKeyboardButton("Крутить", callback_data='26')]]


    reply_markup = InlineKeyboardMarkup(keyboard)
    msgr = update.message.reply_text('''
🎰🎰🎲🎲Рулетка🎲🎲🎰🎰
✅Нажмите на поле, чтобы поставить 10000
🎱Также ставки принимаются текстом.
📜Описание рулетки: /desc
📊Формат ставки:
📱ставка поле/число
📝Примеры:
🧾1000 1стр | 500 ч | 3 ODD |15 1/3|
''', reply_markup=reply_markup)

    msgid = int(msgr.message_id)
   # sleep (10)
   # context.bot.delete_message(chat_id=chat.id, message_id=msg.message_id)
    cursor.execute(f"INSERT INTO trash{chatid} (msgid) VALUES ({msgid})")
    connection.commit()
    delmsg(update, context)



# Описание
def descr(update, context):
    msg = update.message.reply_text("""
Поле выглядит так:
💚💚💚 0 💚💚💚
🔴1       ⚫2       🔴3
⚫4       🔴5       ⚫6
🔴7       ⚫8       🔴9
⚫10     ⚫11     🔴12
⚫13     🔴14     ⚫15
🔴16     ⚫17     🔴18
🔴19     ⚫20     🔴21
⚫22     🔴23     ⚫24
🔴25     ⚫26     🔴27
⚫28     ⚫29     🔴30
⚫31     🔴32     ⚫33
🔴34     ⚫35     🔴36
💚💚💚 0 💚💚💚

Описание кнопок/коэффициент выигрыша:

💰 - Проверить баланс
⛔️- отменить ставки

1стр - Первый ряд чисел|x3
2стр - Второй ряд чисел|x3
3стр - Третий ряд чисел|x3

ODD - Нечётные числа|x2
EVEN - Чётные числа|x2

1/3 - Первая треть чисел (1-12)|x3
2/3 - Вторая терть чисел (13-24)|x3
3/3 - Третья треть чисел (25-36)|x3
1/2 - Первая половина чисел (1-18)|x2
2/2 - Вторая половина чисел (19-36)|x2

⚫ - Чёрные|x2
🔴 - Красные|x2
💚 - Зеро|x14
    """)

#=================================================================================================#


#РАЗВЛЕЧЕНИЯ
def razvlecheniya():
    keyboard = [
        [
            KeyboardButton('🔮 Шар'),
            KeyboardButton('⚖ Выбери '),
        ],
        [
            KeyboardButton('◀ В главное меню'),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard = keyboard, resize_keyboard=True,)

#🚀 Игры
def gamesklava():
    keyboard = [
        [
            KeyboardButton('🎲 Кубик'),
            KeyboardButton('🎰 Казино'),
        ],
        [
            KeyboardButton('🔫 Рулетка'),
        ],
        [
            KeyboardButton('◀ В главное меню'),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard = keyboard, resize_keyboard=True,)





#    🎲 🎲 🎲
def kubicklava():
    keyboard = [
        [
            KeyboardButton('🎲 1'),
            KeyboardButton('🎲 2'),
            KeyboardButton('🎲 3'),
        ],
        [
            KeyboardButton('🎲 4'),
            KeyboardButton('🎲 5'),
            KeyboardButton('🎲 6'),
        ],
        [
            KeyboardButton('💵 Баланс'),
        ],
        [
            KeyboardButton('◀ В главное меню'),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard = keyboard, resize_keyboard=True,)

# Казино
def kazinoklava():

    keyboard = [
        [
            KeyboardButton('🎰 1000'),
            KeyboardButton('🎰 2000'),
            KeyboardButton('🎰 5000'),
        ],
        [
            KeyboardButton('🎰 10000'),
            KeyboardButton('🎰 20000'),
            KeyboardButton('🎰 50000'),
        ],
        [
            KeyboardButton('💵 Баланс'),
        ],
        [
            KeyboardButton('◀ В главное меню'),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard = keyboard, resize_keyboard=True,)




def klavamenu():
    keyboard = [
        [
            KeyboardButton('📒 Профиль'),
            KeyboardButton('💵 Баланс'),
        ],
        [
            KeyboardButton('🎉 Развлечения'),
            KeyboardButton('🚀 Игры'),
        ],
        [
            KeyboardButton('❓ Помощь'),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard = keyboard, resize_keyboard=True,)



#=================================================================================================#

def StolRR6(update):
    text = update.message.text
    a = (text.split(' ', 2))
    txt = np.array(a)
    bet = txt[2]
    user = update.effective_user
    name = user.first_name
    keyboard = [[InlineKeyboardButton(f"{name}", callback_data='1st')],

                [InlineKeyboardButton("2-стул", callback_data='2nd')],

                [InlineKeyboardButton("3-стул", callback_data='3rd')],

                [InlineKeyboardButton("4-стул", callback_data='4th')],

                [InlineKeyboardButton("5-стул", callback_data='5th')],

                [InlineKeyboardButton("6-стул", callback_data='6th')],

                [InlineKeyboardButton("Отмена", callback_data='8th')]]
                # InlineKeyboardButton("Отмена", callback_data='8th')]]


    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f'''
🔫🔫🔫Русская рулетка 🔫🔫🔫
6 Игроков
📜Описание рулетки: /descRR
Стоимость входа: {bet} монет
⏳Ожидаю игроков...
''', reply_markup=reply_markup)

def StolRR4(update):
    text = update.message.text
    a = (text.split(' ', 2))
    txt = np.array(a)
    bet = txt[2]
    user = update.effective_user
    name = user.first_name
    keyboard = [[InlineKeyboardButton(f"{name}", callback_data='1st')],

                [InlineKeyboardButton("2-стул", callback_data='2nd')],

                [InlineKeyboardButton("3-стул", callback_data='3rd')],

                [InlineKeyboardButton("4-стул", callback_data='4th')],

                [InlineKeyboardButton("Отмена", callback_data='8th')]]
                # InlineKeyboardButton("Отмена", callback_data='8th')]]


    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f'''
🔫🔫🔫Русская рулетка 🔫🔫🔫
4 игрока
📜Описание рулетки: /descRR
Стоимость входа: {bet} монет
⏳Ожидаю игроков...
''', reply_markup=reply_markup)

def StolRR2(update):
    text = update.message.text
    a = (text.split(' ', 2))
    txt = np.array(a)
    bet = txt[2]
    user = update.effective_user
    name = user.first_name
    keyboard = [[InlineKeyboardButton(f"{name}", callback_data='1st')],

                [InlineKeyboardButton("2-стул", callback_data='2nd')],

                [InlineKeyboardButton("Отмена", callback_data='8th')]]
               #  InlineKeyboardButton("Отмена", callback_data='8th')]]


    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f'''
🔫🔫🔫Русская рулетка 🔫🔫🔫
1 на 1
📜Описание рулетки: /descRR
Стоимость входа: {bet} монет
⏳Ожидаю игроков...
''', reply_markup=reply_markup)

def descRR(update, context):
    update.message.reply_text("""
Начало:
Создаётся комната на 2/4/6 человек.
Начальная ставка задаётся зачинщиком.
Ставка может быть начинаться с 10т. монет.
Лимит 500млн за игру.

Игровой процесс:
В комнату садятся 2/4/6 человек, друг на против друга.
В середине комнаты лежит 6-ти зарядный пистолет, в котором заряжена одна пуля.
Каждый по очереди берёт пистолет, крутит барабан, подносит дуло пистолета к виску и нажимает курок.
Процедура повторяется до тех пор, пока один из игроков не застрелит себя.
После этого остальным участникам будет предоставлен выбор, поделить деньги проигравшего или продолжить играть до следущего выстрела.
Игра может продолжаться до последнего везунчика, который заберёт весь куш.

Запуск игры:
Чтобы запустить игру напишите->
Русскаярулетка/РР/RR, количество игроков(2/4/6) и ставку.

Примеры:
Русскаярулетка 4 20000
RR 2 50000
РР 6 500000
""")


def updatemsg(update):
    keyboard = [[InlineKeyboardButton(f"ТЫ", callback_data='1st')],

                [InlineKeyboardButton(";", callback_data='2nd')],

                [InlineKeyboardButton("Саси", callback_data='8th')]]
               #  InlineKeyboardButton("Отмена", callback_data='8th')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    query = update.callback_query
    query.answer()
    query.edit_message_text(text = f'''
🔫🔫🔫Русская рулетка 🔫🔫🔫
1 на 1
📜Описание рулетки: /descRR
Стоимость входа: -123 монет
⏳Ожидаю игроков...
''', reply_markup=reply_markup)



def updategamer2(connection, update):
    query = update.callback_query
    query.answer()
    chat = update.effective_chat
    chatid = chat.id * chat.id // 500000
    cursor = connection.cursor()
    name1 = "1-стул"
    name2 = "2-стул"
    cursor.execute(f"""SELECT COUNT(*) FROM RR{chatid}""")
    K = np.array(cursor.fetchall())
    k = 0
    cursor.execute(f"""SELECT * FROM RR{chatid}""")
    N = np.array(cursor.fetchall())
    while k < K:
        M = N[k]
        idd = M[0]
        if int(idd) == 1:
            name1 = M[1]
        if int(idd) == 2:
            name2 = M[1]
        k = k + 1

    keyboard = [[InlineKeyboardButton(f"{name1}", callback_data='1st')],

                [InlineKeyboardButton(f"{name2}", callback_data='2nd')],

                [InlineKeyboardButton("Отмена", callback_data='8th')]]
               #  InlineKeyboardButton("Отмена", callback_data='8th')]]


    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(f'''
🔫🔫🔫Русская рулетка 🔫🔫🔫
1 на 1
📜Описание рулетки: /descRR
Стоимость входа: ? монет
⏳Ожидаю игроков...
''', reply_markup=reply_markup)


def addgamer(connection, update, Bot):
    cd = update.callback_query.data
    cdid = update.callback_query.id
    user = update.effective_user
    username = str(user.first_name)
    userid = user.id
    cursor = connection.cursor()
    chat = update.effective_chat
    chatid = chat.id * chat.id // 500000
    if cd == '1st':
        pos = 1
    if cd == '2nd':
        pos = 2
    if cd == '3rd':
        pos = 3
    if cd == '4th':
        pos = 4
    if cd == '5th':
        pos = 5
    if cd == '6th':
        pos = 6
    try:
        sql = f"INSERT INTO RR{chatid} (id ,username, userid) VALUES (%s, %s, %s)"
        val = (pos, username, userid)
        cursor = connection.cursor()
        cursor.execute(sql, val)
        connection.commit()
        updategamer2(connection, update)
    except Error:
        print(cdid)
        Bot.answerCallbackQuery(callback_query_id=cdid, text="Этот стул уже занят :о", show_alert=True)





def RoomRR(connection, update):
    text = update.message.text
    a = (text.split(' ', 2))
    txt = np.array(a)
    #com = txt[0]
    #num = txt[1]
    bet = txt[2]
    user = update.effective_user
    #name = str(user.first_name) + str(user.last_name)
    username = str(user.first_name)
    userid = user.id
    cursor = connection.cursor()
    chat = update.effective_chat
    chatid = chat.id * chat.id // 500000
    cursor.execute(f"""
CREATE TABLE IF NOT EXISTS RR{chatid} (
  id INT UNIQUE,
  username VARCHAR(20),
  userid INT,
  PRIMARY KEY (id)
) ENGINE = InnoDB
""")
    cursor.execute (f"""
CREATE TABLE IF NOT EXISTS logRR{chatid} (
  id INT AUTO_INCREMENT,
  username VARCHAR(20),
  bet INT,
  typegame VARCHAR(20),
  win INT,
  PRIMARY KEY (id)
) ENGINE = InnoDB
""")
    sql = f"INSERT INTO RR{chatid} (id ,username, userid) VALUES (%s, %s, %s)"
    val = ('1', username, userid)
    cursor = connection.cursor()
    cursor.execute(sql, val)
    connection.commit()
   # cursor.execute(f"""UPDATE users SET balance = balance - {bet} WHERE userid = {userid} """)
   # connection.commit()

# Помощь
def help(update, context):
    update.message.reply_text("""Введите /Command чтобы посмотреть список команд""")


#'Русскаярулетка/РР/RR' - Запустить русскую рулетку

# команды
def commands(update, context):
    update.message.reply_text("""
    Команды:


    '!рулетка/Рулетка' - Запустить рулетку
    '!Профиль/П' - Посмотреть профиль
    '!Баланс/Б' - Посмотреть баланс
    'Го/Крутить' - Запустить рулетку
    'Лог/лог' - Посмотреть последние 11 выпавших чисел
    '!Лог/!лог' - Посмотреть последние 20 выпавших чисел
    '+ (число)' - передать монетки
    'Бонус' - Если у вас меньше 2500
    /desc - Описание рулетки
    /help - Помощь
    /CommandA - Команды для админов
    """)

def commandsA(update, context):
    update.message.reply_text("""
    {Для использования отметьте сообщение игрока}
    Команды:
    '+A' - Выдать админку
    '-A' - Отобрать админку
    '+б' - Посмотреть баланс игрока
    '++ (число)' - Выдать монетки
    '-- (число)' - Забрать монетки
    '+! (текст)' - Выдать префикс
    """)

# Профиль
@mult_threading
def profile(update, context):
    chat = update.effective_chat
    user = update.effective_user
    name = user.first_name
    userid = user.id
    cursor = connection.cursor()
    cursor.execute(f'''SELECT * FROM users WHERE userid = {userid}''')
    try:
        row = np.array(cursor.fetchone())
        balance = row[4]
        prefix = row[5]
    except IndexError:
        print('ERROR PROFILE')
    msg = update.message.reply_text(f"""
    Ваш профиль:

Имя: {name}
Префикс : {prefix}
Баланс: {balance}

<В разработке>
Максимальный выигрыш:
Максимальная ставка:

    """)
    sleep (10)
    context.bot.delete_message(chat_id=chat.id, message_id=msg.message_id)
    delmsg(update, context)

# Отмена ставки
@mult_threading
def cancelbet(update, connection, context):
    user = update.effective_user
    chat = update.effective_chat
    userid = user.id
    chatid = chat.id * chat.id // 500000
    cursor = connection.cursor()
    cursor.execute(f"""SELECT COUNT(*) FROM betinchat{chatid} WHERE userid = {userid}""")
    M = np.array(cursor.fetchall())
    k = 0
    cursor.execute(f"""SELECT bet FROM betinchat{chatid} WHERE userid = {userid}""")
    com = np.array(cursor.fetchall())
    while k < M:
        winer = com[k]
        wernul = winer[0]
        cursor.execute(f"""UPDATE users SET balance = balance + {wernul} WHERE userid = {userid} """)
        connection.commit()
        k = k + 1

    cursor.execute(f'''DELETE FROM betinchat{chatid} WHERE userid = {userid} ''')
    connection.commit()
    username = str(user.username)
    name1 = str(user.first_name)
    name2 = str(user.first_name) + str(user.last_name)
    if username == Nonee:
        if str(user.last_name) == str(Nonee):
            msg = update.message.reply_text(f'{name1} Вы отменили свои ставки')
        else:
            msg = update.message.reply_text(f'{name2} Вы отменили свои ставки')
    else:
        msg = update.message.reply_text(f'@{username} Вы отменили свои ставки')

    sleep(5)
    context.bot.delete_message(chat_id=chat.id, message_id=msg.message_id)
    delmsg(update, context)


#=============================================================================#

def sharik(update):
    text =  update.message.text
    strs = (text.split(' ', 1))
    word = np.array(strs)
    RN = random.randint(0, 8)
    if RN == 1:
        update.effective_message.reply_text(f'''🔮 Определённо''')
    if RN == 3:
        update.effective_message.reply_text(f'''🔮 Предрешено''')
    if RN == 4:
        update.effective_message.reply_text(f'''🔮 Сконцентрируйся и спроси опять''')
    if RN == 2:
        update.effective_message.reply_text(f'''🔮 Мой ответ - «нет»''')
    if RN == 5:
        update.effective_message.reply_text(f'''🔮 Пока не ясно''')
    if RN == 6:
        update.effective_message.reply_text(f'''🔮 Знаки говорят - «Да»''')
    if RN == 7:
        update.effective_message.reply_text(f'''🔮 Весьма сомнительно''')
    if RN == 8:
        update.effective_message.reply_text(f'''🔮 Перспективы не очень хорошие''')
    if RN == 0:
        update.effective_message.reply_text(f'''🔮 Спроси позже''')

#Выбор
def viberi(update):
    text =  update.message.text
    strs = (text.split(' ', 3))
    word = np.array(strs)
    word1 = word[1]
    word2 = word[3]
    RN = random.randint(0, 8)
    RW = random.randint(0, 1)
    if RN == 0:
        if RW == 0:
            words = word1
        else:
            words = word2
        update.effective_message.reply_text(f'''⚖ Определённо «{words}»''')
    if RN == 1:
        if RW == 0:
            words = word1
        else:
            words = word2
        update.effective_message.reply_text(f'''⚖ Думаю что «{words}» лучше''')
    if RN == 2:
        if RW == 0:
            update.effective_message.reply_text(f'''⚖ «{word1}» конечно хорошо, но «{word2}» лучше ''')
        else:
            update.effective_message.reply_text(f'''⚖ «{word2}» конечно хорошо, но «{word1}» лучше ''')
    if RN == 3:
        if RW == 0:
            update.effective_message.reply_text(f'''⚖ Думаю «{word1}» лучше чем «{word2}»''')
        else:
            update.effective_message.reply_text(f'''⚖ Думаю «{word2}» лучше чем «{word1}»''')
    if RN == 4:
        if RW == 0:
            words = word1
        else:
            words = word2
        update.effective_message.reply_text(f'''⚖ Скорее всего «{words}»''')
    if RN == 5:
        if RW == 0:
            update.effective_message.reply_text(f'''⚖ Как по мне, «{word1}» лучше, но «{word2}» тоже неплохо''')
        else:
            update.effective_message.reply_text(f'''⚖ Как по мне, «{word2}» лучше, но «{word1}» тоже неплохо''')
    if RN == 6:
        if RW == 0:
            words = word1
        else:
            words = word2
        update.effective_message.reply_text(f'''⚖ Я не уверен, но выберу «{words}»''')
    if RN == 7:
        if RW == 0:
            words = word1
        else:
            words = word2
        update.effective_message.reply_text(f'''⚖ 100% «{words}» намного лучше ''')
    if RN == 8:
        if RW == 0:
            words = word1
        else:
            words = word2
        update.effective_message.reply_text(f'''⚖ Нет ничего лучше «{words}» ''')


#----------------------------------------------------------------------------------#


#-------------------------------------ИГРЫ-----------------------------------------#

#РАЗВЛЕЧЕНИЯ
def razvlmenu(update):
    chat = update.effective_chat
    chattype = chat.type
    #if chattype == 'private':
     #   update.effective_message.reply_text(f'''🎉 Раздел: Развлечения''', reply_markup=razvlecheniya(),)
    #else:
    update.effective_message.reply_text(f'''
🎉 Раздел: Развлечения
    🔮 Шар [фраза]
 ⠀⚖ Выбери [фраза] или [фраза2]
 ⠀⠀''')

#ГЕЙММЕНЮ
def gamemenu(update):
    chat = update.effective_chat
    chattype = chat.type
    if chattype == 'private':
        update.effective_message.reply_text(f'''🚀 Раздел: Игры''', reply_markup=gamesklava(),)
    else:
        update.effective_message.reply_text(f'''
🚀 Раздел: Игры

    🔫 Рулетка
 ⠀⠀🎲 Кубик [1-6]
 ⠀⠀🎰 Казино [сумма]''')


#КУБИК
def kubikmenu(update):
    chat = update.effective_chat
    chattype = chat.type
    if chattype == 'private':
        update.effective_message.reply_text(f'''Игра: 🎲Кубик\nВыберите число от «1» до «6»\nУгадав число вы получите приз ''', reply_markup=kubicklava(),)
    else:
        update.effective_message.reply_text(f'''Игра: 🎲Кубик\nВыберите число от «1» до «6»\nУгадав число вы получите приз\nПример: Кубик 3 ''')


def kubic(update):
    chat = update.effective_chat
    chattype = chat.type
    cursor = connection.cursor()
    user = update.effective_user
    userid = user.id
    text =  update.message.text
    strs = (text.split(' ', 3))
    word = np.array(strs)
    word1 = word[1]
    RN = random.randint(1, 6)
    RW = random.randint(1000, 10000)
   # print(chattype)
    if int(word1) < 7 and int(word1) > 0:
        if chattype == 'private':
            if int(RN) == int(word1):
                update.effective_message.reply_text(f'''Поздравляю\n💸 Приз: {RW}''', reply_markup=kubicklava(),)
                cursor.execute(f"""UPDATE users SET balance = balance + {RW} WHERE userid = {userid} """)
                connection.commit()
            else:
                update.effective_message.reply_text(f'''Неправильно, это было число {RN} ☹''', reply_markup=kubicklava(),)
        else:
            if int(RN) == int(word1):
                update.effective_message.reply_text(f'''Поздравляю\n💸 Приз: {RW}''',)
                cursor.execute(f"""UPDATE users SET balance = balance + {RW} WHERE userid = {userid} """)
                connection.commit()
            else:
                update.effective_message.reply_text(f'''Неправильно, это было число {RN} ☹''',)
    else:
        update.effective_message.reply_text(f'''Введите число от «1» до «6» ''',)



#КАЗИНО МЕНЮ
def kazinomenu(update):
    chat = update.effective_chat
    chattype = chat.type
    if chattype == 'private':
        update.effective_message.reply_text(f'''
Игра: 🎰 Казино
Поставь деньги!!!
Выбей три в ряд!!!
Получи выйгрыш (х30) от ставки!!!
Пример: Казино 3000


''', reply_markup=kazinoklava(),)
    else:
        update.effective_message.reply_text(f'''
Игра: 🎰 Казино
Поставь деньги!!!
Выбей три в ряд!!!
Получи выйгрыш (х30) от ставки!!!
Пример: Казино 3000


''')


#🍋
#💰
#🍒
#🍓
#КАЗИНО      🍋 🍒 🍓      🎰
def kazino(update):
    chat = update.effective_chat
    chattype = chat.type
    cursor = connection.cursor()
    user = update.effective_user
    name1 = user.first_name
    userid = user.id
    text = update.message.text
    a = (text.split(' ', 1))
    txt = np.array(a)
    bet = int(txt[1])
    bet30 = bet * 30


    c = [0, 0 ,0]
    com = ''
    b = 0
    cursor.execute(f"""SELECT balance FROM users WHERE userid = {userid} """)
    balans = np.array(cursor.fetchone())
    DBalans = balans
    if bet > DBalans:
        update.effective_message.reply_text(f'''❌[{name1}](tg://user?id={userid}), вы не можете поставить ставку превышающую ваш баланс!!!''',
parse_mode=ParseMode.MARKDOWN,)
    else:
        while b < 3:
            num = random.randint(1, 3)
            if num == 1:
                c[b] = 1
                com = f'{com}'+'🍋'
            if num == 2:
                c[b] = 2
                com = f'{com}'+'🍒'
            if num == 3:
                c[b] = 3
                com = f'{com}'+'🍓'
            b = b + 1
        #update.effective_message.reply_text(f'''🎰Казино: {com}''')
        if chattype == 'private':
            if c[0] == c[1] and c[0] == c[2]:
                update.effective_message.reply_text(f'''🎰Казино: {com}\nВы выйграли: {bet30}$ (x30)💰''', reply_markup=kazinoklava(),)
                cursor.execute(f"""UPDATE users SET balance = balance + {bet30} WHERE userid = {userid} """)
                connection.commit()
            else:
                update.effective_message.reply_text(f'''🎰Казино: {com}\nВы проиграли: {bet}$ 🙁''', reply_markup=kazinoklava(),)
                cursor.execute(f"""UPDATE users SET balance = balance - {bet} WHERE userid = {userid} """)
                connection.commit()
        else:
            if c[0] == c[1] and c[0] == c[2]:
                update.effective_message.reply_text(f'''🎰Казино: {com}\nВы выйграли: {bet30}$ (x30)💰''',)
                cursor.execute(f"""UPDATE users SET balance = balance + {bet30} WHERE userid = {userid} """)
                connection.commit()
            else:
                update.effective_message.reply_text(f'''🎰Казино: {com}\nВы проиграли: {bet}$ 🙁''',)
                cursor.execute(f"""UPDATE users SET balance = balance - {bet} WHERE userid = {userid} """)
                connection.commit()




def monetka(update):
    user = update.effective_user
    name1 = user.first_name
    userid = user.id
    num = random.randint(1, 2)
    if num==1:
        update.effective_message.reply_text(f'''Орёл''')
    else:
         update.effective_message.reply_text(f'''Решка''')




#=========================================================================================================================================#


def helpm(update):
    user = update.effective_user
    name = str(user.first_name) + str(user.last_name)
    username = user.username
    userid = user.id
    update.effective_message.reply_text(f'''
[{name}](tg://user?id={userid}), мои команды:

🎉 Развлекательные:
  🔮 Шар [фраза]
 ⠀⚖ Выбери [фраза] или [фраза2]

🚀 Игры:

 ⠀⠀🔫 Рулетка
 ⠀⠀🎲 Кубик [1-6]
 ⠀⠀🎰 Казино [сумма]
 ''',
parse_mode=ParseMode.MARKDOWN,)

def menues(update, context):
    chat = update.effective_chat
    chattype = chat.type
    if chattype == 'private':
        update.effective_message.reply_text(f'''Главное меню''', reply_markup=klavamenu(),)
    else:
        update.effective_message.reply_text(f'''Чтобы посмотреть список команд\nВведите: помощь''')

@mult_threading
def createtop(connection, update, context):
    cursor = connection.cursor()
    cursor.execute(f"""SELECT name, username, userid, balance FROM users WHERE balance >= 0""")
    top = np.array(cursor.fetchall())
    cursor.execute(f'''SELECT COUNT(*) FROM users''')
    userscount = np.array(cursor.fetchone())
    chatid = update.effective_chat.id
    if chatid < 0:
        chatid1 = chatid * -1
        cursor.execute (f"""
CREATE TABLE IF NOT EXISTS top{chatid1} (
  id INT AUTO_INCREMENT,
  name VARCHAR(30),
  userid INT UNIQUE,
  balance INT,
  PRIMARY KEY (id)
) ENGINE = InnoDB
""")
    else:
        cursor.execute (f"""
CREATE TABLE IF NOT EXISTS top{chatid} (
  id INT AUTO_INCREMENT,
  name VARCHAR(30),
  userid INT UNIQUE,
  balance INT,
  PRIMARY KEY (id)
) ENGINE = InnoDB
""")
    connection.commit()
    b=0
    while b<userscount:
        try:
            userid = top[b]
            balance=userid[3]
            user=context.bot.get_chat_member(chatid, userid[2])
            if user.status != 'left':
                if user.status != 'kicked':
                    if chatid < 0:
                        try:
                            fullname=user.user.first_name + ' ' + user.user.last_name
                            sql = f"""INSERT INTO top{chatid1} (name, userid, balance) VALUES (%s, %s, %s)"""
                            val = (fullname, userid[2], int(balance))
                            cursor.execute(sql, val)
                            connection.commit()
                        except Exception:
                            sql = f"""INSERT INTO top{chatid1} (name, userid, balance) VALUES (%s, %s, %s)"""
                            val = (user.user.first_name, userid[2], int(balance))
                            cursor.execute(sql, val)
                            connection.commit()
                    else:
                        try:
                            fullname=user.user.first_name + ' ' + user.user.last_name
                            sql = f"""INSERT INTO top{chatid} (name, userid, balance) VALUES (%s, %s, %s)"""
                            val = (fullname, userid[2], int(balance))
                            cursor.execute(sql, val)
                            connection.commit()
                        except Exception:
                            sql = f"""INSERT INTO top{chatid} (name, userid, balance) VALUES (%s, %s, %s)"""
                            val = (user.user.first_name, userid[2], int(balance))
                            cursor.execute(sql, val)
                            connection.commit()
                else:
                    none = 'none'
                    b=b+1
            #balans = np.array(cursor.fetchone())
            #print(top)
            #print(userscount)
                b=b+1
                #print(user)
            else:
                none = 'none'
                b=b+1
        except Exception:
            #print(Exception)
            #print(user.status)
            #print(user.user.first_name)
            b=b+1

    if chatid < 0:
        cursor.execute(f"""SELECT name, userid, balance FROM top{chatid1}""")
    else:
        cursor.execute(f"""SELECT name, userid, balance FROM top{chatid}""")
    a = np.array(cursor.fetchall())
    n = 1
    t = 1
    #print(a)
    #print((a[0])[1])
    b = np.array(sorted(a, key=lambda i: int(i[2]), reverse=1))
    #print(b)
    if chatid < 0:
        cursor.execute(f'''SELECT COUNT(*) FROM top{chatid1}''')
    else:
        cursor.execute(f'''SELECT COUNT(*) FROM top{chatid}''')
    N = np.array(cursor.fetchone())
    n=0
    com1 = "#📜Топ чата:\n\n"
    while n < N:
        com = f"[{(b[n])[0]}](tg://user?id={b[n][1]}) - [{(b[n])[2]}]"
        com1 =str(com1)+ str(com) + '\n'
        n = n + 1
    context.bot.send_message(chatid, com1, parse_mode=ParseMode.MARKDOWN,)
    #cursor.execute(f"""DROP TABLE top{chatid1}""")
    connection.commit()
    delmsg(update, context)


def updatetop(connection, update, context):
    chat = update.effective_chat
    chatusername = chat.username
    cursor = connection.cursor()
    chatid = int(chat.id)
    if chatid < 0:
        chatid1 = chatid * -1
    context.bot.get_chat_members_count(chatid)
    countchat = np.array(cursor.fetchone())
    if chatid < 0:
        cursor.execute(f'''SELECT COUNT(*) FROM top{chatid1}''')
    else:
        cursor.execute(f'''SELECT COUNT(*) FROM top{chatid}''')
    counttop= np.array(cursor.fetchone())

    print(chatid)
    print(countchat)
    print(counttop)


def CheckTOP(connection, update, context):
    chat = update.effective_chat
    cursor = connection.cursor()
    chatid = chat.id
    if chatid < 0:
        chatid1 = chatid * -1
    cursor.execute(f"SHOW TABLES LIKE 'top{chatid}'")
    try:
        row = np.array(cursor.fetchone())
        PC = row[0]
    except IndexError:
        PC = 0
    kk = f'top{chatid}'
    if kk == PC:
        updatetop(connection, update, context)
    else:
        createtop(connection, update, context)


def razdachanaspawne(connection, update, context):
    chat = update.effective_chat
    cursor = connection.cursor()
    chatid = chat.id
    user = update.effective_user
    name = str(user.first_name) + str(user.last_name)
    userid = user.id
    if chatid<0:
        chatid = chatid * -1
    cursor.execute (f"""
CREATE TABLE IF NOT EXISTS razdacha{chatid} (
  id INT AUTO_INCREMENT,
  name VARCHAR(30),
  userid INT UNIQUE,
  bet INT,
  PRIMARY KEY (id)
) ENGINE = InnoDB
""")
    connection.commit()
    sql = f"""INSERT INTO razdacha{chatid} (name, userid, bet) VALUES (%s, %s, %s)"""
    val = (user.user.first_name, userid[2], int(balance))
    cursor.execute(sql, val)
    connection.commit()
    update.effective_message.reply_text(f'''{name}''')



# "Для новых функций"
def msg1(update, context):
    update.message.reply_text("В разработке")

# Команды. Переменные
start_rulet = '!рулетка'
start_rulet1 = '!р'
start_rulet2 = 'Рулетка'
profile1 = '!профиль'
profile2 = 'П'
profile3 = 'Профиль'
Balance1 = 'Баланс'
Balance2 = '!баланс'
Balance3 = 'Б'
log1 = 'лог'
log11 = 'Лог'
log2 = '!Лог'
log21 = '!лог'
go = 'Го'
goo = 'го'
gooo = 'go'
go1 = 'Крутить'
Cancel = 'Отмена'
Cancel1 = '!отмена'
Nonee = "None"
RR = "Русскаярулетка"
RR1 = "RR"
RR2 = "РР"
#-----------------------
admbalanc = '+б'


# Команды\marker. Добавляет пользователя если он ещё не добавлен. Проверяет текст ставки.
def com(update, context):
    user = update.effective_user
    name = str(user.first_name) + str(user.last_name)
    username = user.username
    userid = user.id
    try:
        cursor = connection.cursor()
        try:
            sql = f"INSERT IGNORE INTO users (name ,username, userid, balance, prefix, adm) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (name, username, userid, '10000', 'Игрок', '0', 'Безработный')
            cursor = connection.cursor()
            cursor.execute(sql, val)
            connection.commit()
        except Error:
            username = 'None'
            sql = f"INSERT IGNORE INTO users (name ,username, userid, balance, prefix, adm) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (name, username, userid, '10000', 'Игрок', '0', 'Безработный')
            cursor = connection.cursor()
            cursor.execute(sql, val)
            connection.commit()
    except Error:
        none = "none"

    try:
        text =  update.message.text
        a = (text.split(' ', 1))
        bet = np.array(a)
        num = int(bet[0])
        fld = bet[1]
        if type(num) == int:
            #print(num)
            #print(fld)
            if fld == '0' or fld == '1' or fld == '2' or fld == '3' or fld == '4' or fld == '5' or fld == '6' or fld == '7' or fld == '8' or fld == '9' or fld == '10' or fld == '11' or fld == '11' or fld == '12' or fld == '13' or fld == '14' or fld == '15' or fld == '16' or fld == '17' or fld == '18' or fld == '19' or fld == '20' or fld == '21' or fld == '22' or fld == '23' or fld == '24' or fld == '25' or fld == '26' or fld == '27' or fld == '28' or fld == '29' or fld == '30' or fld == '31' or fld == '32' or fld == '33' or fld == '34' or fld == '35' or fld == '36':
                stavkaint(update, connection, context)
            else:
                stavka(update, connection, context)
    except ValueError:
        num = 'None'
    try:
        text = update.message.text
        a = (text.split(' ', 2))
        txt = np.array(a)
        com = txt[0]
        num = txt[1]
        bet = txt[2]
        minn = '10000'
        maxx = '500000000'
    #    if com == 'RR' or com == 'РР' or com == 'Русскаярулетка':
    #        if num == '2' or num == '4' or num == '6':
    #            if int(bet) >= int(minn) and int(bet) <= int(maxx):
    #                if num == '2':
    #                   # msg1(update, context)
    #                    #rrcheckt(update, connection)

    #                if num == '4':
    #                  #  msg1(update, context)
    #                    #rrcheckf(update, connection)
    #                if num == '6':
    #                  #  msg1(update, context)
    #                    #rrchecks(update, connection)
    #            else:
    #              #  update.effective_message.reply_text(f'''Ставка меньше 10к или больше 500кк''')
    #        else:
    #          #  update.effective_message.reply_text(f'''Доступны комнаты только с 2/4/6 местами''')
    except IndexError:
        none = 1
    try:
        text =  update.message.text
        strs = (text.split(' ', 3))
        word = np.array(strs)
        if word[0] == 'Выбери' and word[2] == 'или':
            viberi(update)
        if word[0] == 'выбери' and word[2] == 'или':
            viberi(update)
    except IndexError:
        print('error')

    try:
        text =  update.message.text
        wrd = (text.split(' ', 1))
        word = np.array(wrd)
        if word[0] == 'Шар' or word[0] == 'шар':
            sharik(update)
    except IndexError:
        print('error')

    try:
        text =  update.message.text
        wrd = (text.split(' ', 1))
        word = np.array(wrd)
        try:
            num = int(word[1])
            if word[0] == 'Кубик' or word[0] == 'кубик':
                if type(num) == int:
                    kubic(update)
                else:
                    update.effective_message.reply_text(f'''Введите число''')
        except ValueError:
            none = 1

        if text == '🎲 1' or text == '🎲 2' or text == '🎲 3' or text == '🎲 4' or text == '🎲 5' or text == '🎲 6':
            kubic(update)

    except IndexError:
        none = 1

    try:
        text =  update.message.text
        wrd = (text.split(' ', 1))
        word = np.array(wrd)
        try:
            num = int(word[1])
            if word[0] == 'Казино' or word[0] == 'казино':
                if type(num) == int:
                    kazino(update)
                else:
                    update.effective_message.reply_text(f'''Введите число''')
        except ValueError:
            none = 1
    except IndexError:
        none = 1

    if text == '🎰 1000' or text == '🎰 2000' or text == '🎰 5000' or text == '🎰 10000' or text == '🎰 20000' or text == '🎰 50000':
        kazino(update)


    try:
        text = update.message.text
        a = (text.split(' ', 1))
        txt = np.array(a)
        num1 = txt[0]
        #    print(num1)
        if num1 == '+':
            money(update, connection)
        if num1 == '++':
            admmoney(update, connection, context)
        if num1 == '—':
            admmoney(update, connection, context)
        if num1 == '--':
            admmoney(update, connection, context)
        if num1 == '+!':
            admmoney(update, connection, context)
        if num1 == '-A':
            admmoney(update, connection, context)
        if num1 == '+A':
            admmoney(update, connection, context)
        if num1 == '+б':
            admmoney(update, connection, context)
    except IndexError:
        none = 1



    if update.message.text == 'u' or update.message.text == 'U':
        updatetop(connection, update, context)
    if update.message.text == 'Топ' or update.message.text == 'топ' or update.message.text == '!топ':
        createtop(connection, update, context)
    if update.message.text == 'Монетка' or update.message.text == 'монетка':
        monetka(update)
    if update.message.text == '◀ В главное меню':
        menues(update, context)
    if update.message.text == '🎉 Развлечения' or update.message.text == 'Развлечения' or update.message.text == 'развлечения':
        razvlmenu(update)
    if update.message.text == '🚀 Игры' or update.message.text == 'игры' or update.message.text == 'Игры':
        gamemenu(update)
    if update.message.text == '🎲 Кубик' or update.message.text == 'кубик' or update.message.text == 'Кубик':
        kubikmenu(update)
    if update.message.text == '🎰 Казино' or update.message.text == 'Казино' or update.message.text == 'казино':
        kazinomenu(update)
    if update.message.text == 'starts':
        delmsg(update, context)
        connn(update, connection)
    if update.message.text == 'Бонус':
        bonus(update, connection, context)
    if update.message.text == start_rulet or update.message.text == 'рулетка':
        query_with_fetchone(connection, update, context)
    if update.message.text == start_rulet1:
        query_with_fetchone(connection, update, context)
    if update.message.text == '🔫 Рулетка':
        query_with_fetchone(connection, update, context)
    if update.message.text == start_rulet2:
        query_with_fetchone(connection, update, context)
    if update.message.text == profile1:
        profile(update, context)
    if update.message.text == profile2:
        profile(update, context)
    if update.message.text == profile3:
        profile(update, context)
    if update.message.text == '📒 Профиль':
        profile(update, context)
    if update.message.text == Balance1:
        balance(update, context)
    if update.message.text == Balance2:
        balance(update, context)
    if update.message.text == Balance3:
        balance(update, context)
    if update.message.text == "💵 Баланс":
        balance(update, context)
    if update.message.text == 'Помощь' or update.message.text == '❓ Помощь':
        helpm(update)
    if update.message.text == 'лог':
        log(update, connection, context)
    if update.message.text == log11:
        log(update, connection, context)
    if update.message.text == log2:
        log1(update, connection, context)
    if update.message.text == log21:
        log1(update, connection, context)
    if update.message.text == go:
        randomrulet(connection, update, context)
    if update.message.text == goo:
        randomrulet(connection, update, context)
    if update.message.text == gooo:
        randomrulet(connection, update, context)
    if update.message.text == go1:
        randomrulet(connection, update, context)
    if update.message.text == Cancel:
        cancelbet(update, connection)
    if update.message.text == Cancel1:
        cancelbet(update, connection)
    #if update.message.text == RR:
    #    msg1(update, context)
    #if update.message.text == RR1:
    #    msg1(update, context)
    #    #StolRR6(update)
    #if update.message.text == RR2:
    #    msg1(update, context)



@mult_threading
def bonus(update, connection, context):
    chat = update.effective_chat
    chatid = chat.id * chat.id // 500000
    user = update.effective_user
    userid = int(user.id)
    name1 = user.first_name
    name2 = str(user.first_name) + str(user.last_name)
    cursor = connection.cursor()
    cursor.execute(f"""SELECT balance FROM users WHERE userid = {userid} """)
    balans = np.array(cursor.fetchone())
    MinBalans = 2500
    if balans > MinBalans:
        msg = update.effective_message.reply_text(f'''❌[{name1}](tg://user?id={userid}), у вас больше 2500 монет на руках!!!''',
parse_mode=ParseMode.MARKDOWN,)
    else:
        cursor.execute(f"""UPDATE users SET balance = 10000 WHERE userid = {userid} """)
        connection.commit()
        msg = update.effective_message.reply_text(f'''✅[{name1}](tg://user?id={userid}), ваш баланс 10000''',
parse_mode=ParseMode.MARKDOWN,)
    sleep(5)
    context.bot.delete_message(chat_id=chat.id, message_id=msg.message_id)
    delmsg(update, context)


# Ставка текст числа
@mult_threading
def stavkaint(update, connection, context):
    chat = update.effective_chat
    cursor = connection.cursor()
    chatid = chat.id * chat.id // 500000
    cursor.execute(f"SHOW TABLES LIKE 'betinchat{chatid}'")
    try:
        row = np.array(cursor.fetchone())
        PC = row[0]
    except IndexError:
        PC = 0
    kk = f'betinchat{chatid}'
    if kk == PC:
        text = update.message.text
        a = (text.split(' ', 1))
        txt = np.array(a)
        bet = int(txt[0])
        fld = str(txt[1])
        if fld == '0' or fld == '1' or fld == '2' or fld == '3' or fld == '4' or fld == '5' or fld == '6' or fld == '7' or fld == '8' or fld == '9' or fld == '10' or fld == '11' or fld == '11' or fld == '12' or fld == '13' or fld == '14' or fld == '15' or fld == '16' or fld == '17' or fld == '18' or fld == '19' or fld == '20' or fld == '21' or fld == '22' or fld == '23' or fld == '24' or fld == '25' or fld == '26' or fld == '27' or fld == '28' or fld == '29' or fld == '30' or fld == '31' or fld == '32' or fld == '33' or fld == '34' or fld == '35' or fld == '36':

            if fld == '0':
                fld = 'Zero'
                Pwin = bet * 14
            else:
                Pwin = bet * 10

            user = update.effective_user
            chat = update.effective_chat
            chatid = chat.id * chat.id // 500000
            userid = int(user.id)
            name1 = user.first_name
            name2 = str(user.first_name) + str(user.last_name)
            cursor = connection.cursor()
            cursor.execute(f"""SELECT balance FROM users WHERE userid = {userid} """)
            balans = np.array(cursor.fetchone())
            DBalans = balans
            if bet > DBalans:
                update.effective_message.reply_text(f'''❌[{name1}](tg://user?id={userid}), вы не можете поставить ставку превышающую ваш баланс!!!''',
parse_mode=ParseMode.MARKDOWN,)
            else:
                cursor.execute(f"""UPDATE users SET balance = balance - {bet} WHERE userid = {userid} """)
                connection.commit()
                coment = f'{name1} {bet} на [{fld}]'

                sql = f"INSERT INTO betinchat{chatid} ( username, userid, bet, field, Pwin, coment) VALUES ( %s, %s, %s, %s, %s, %s)"
                val = (name1, userid, bet, fld, Pwin, coment)
                cursor.execute(sql, val)
                connection.commit()
                msg = update.effective_message.reply_text(f'''
📝Ставка принята:
💰{coment}
✅Выигрыш составит: {Pwin}
        ''')
        sleep(5)
        context.bot.delete_message(chat_id=chat.id, message_id=msg.message_id)
        delmsg(update, context)

# Ставка/чат
@mult_threading
def stavka(update, connection, context):
    chat = update.effective_chat
    cursor = connection.cursor()
    chatid = chat.id * chat.id // 500000
    cursor.execute(f"SHOW TABLES LIKE 'betinchat{chatid}'")
    try:
        row = np.array(cursor.fetchone())
        PC = row[0]
    except IndexError:
        PC = 0
    kk = f'betinchat{chatid}'
    if kk == PC:
        text = update.message.text
        a = (text.split(' ', 1))
        txt = np.array(a)
        bet = int(txt[0])
        fld = str(txt[1])
        if fld == 'к' or fld == 'ч' or fld == 'odd' or fld == 'even' or fld == '1/2' or fld == '2/2' or fld == '1/3' or fld == '2/3' or fld == '3/3' or fld == '2стр'  or fld == '1стр'  or fld == '3стр' :

           # or int(fld) >= 0 and int(fld) < 37

            if fld == 'к':
                fld = 'Red'
                Pwin = bet * 2
            if fld == 'ч':
                fld = 'Black'
                Pwin = bet * 2
            if fld == 'odd':
                fld = 'ODD'
                Pwin = bet * 2
            if fld == 'even':
                fld = 'EVEN'
                Pwin = bet * 2
            if fld == '1/2':
                Pwin = bet * 2
            if fld == '2/2':
                Pwin = bet * 2
            if fld == '1/3':
                Pwin = bet * 3
            if fld == '2/3':
                Pwin = bet * 3
            if fld == '3/3':
                Pwin = bet * 3
            if fld == '1стр':
                Pwin = bet * 3
            if fld == '2стр':
                Pwin = bet * 3
            if fld == '3стр':
                Pwin = bet * 3
        #    if int(fld) >= 1 and int(fld) <= 36:
        #        Pwin = bet * 6
        #    if int(fld) == 0:
        #        Pwin = bet * 14

            user = update.effective_user
            chat = update.effective_chat
            chatid = chat.id * chat.id // 500000
            userid = int(user.id)
            name1 = user.first_name
            name2 = str(user.first_name) + str(user.last_name)
            cursor = connection.cursor()
            cursor.execute(f"""SELECT balance FROM users WHERE userid = {userid} """)
            balans = np.array(cursor.fetchone())
            DBalans = balans
            if bet > DBalans:
                update.effective_message.reply_text(f'''❌[{name1}](tg://user?id={userid}), вы не можете поставить ставку превышающую ваш баланс!!!''',
parse_mode=ParseMode.MARKDOWN,)
            else:
                cursor.execute(f"""UPDATE users SET balance = balance - {bet} WHERE userid = {userid} """)
                connection.commit()
                coment = f'{name1} {bet} на [{fld}]'

                sql = f"INSERT INTO betinchat{chatid} ( username, userid, bet, field, Pwin, coment) VALUES ( %s, %s, %s, %s, %s, %s)"
                val = (name1, userid, bet, fld, Pwin, coment)
                cursor.execute(sql, val)
                connection.commit()
                msg = update.effective_message.reply_text(f'''
📝Ставка принята:
💰{coment}
✅Выигрыш составит: {Pwin}
        ''')
        sleep(5)
        try:
            context.bot.delete_message(chat_id=chat.id, message_id=msg.message_id)
            delmsg(update, context)
        except Exception:
            none = "none"

# Баланс
@mult_threading
def balance(update, context):
    chat = update.effective_chat
    user = update.effective_user
    name = user.first_name
    userid = user.id
    cursor = connection.cursor()
    cursor.execute(f'''SELECT * FROM users WHERE userid = {userid}''')
    try:
        row = np.array(cursor.fetchone())
        balance = row[4]
    except IndexError:
        balance = 0
    msg = update.effective_message.reply_text(f'[{name}](tg://user?id={userid})\nБаланс: {balance}',parse_mode=ParseMode.MARKDOWN,)
    sleep (10)
    context.bot.delete_message(chat_id=chat.id, message_id=msg.message_id)
    delmsg(update, context)



@mult_threading
def balance1(update, context):
    chat = update.effective_chat
    user = update.effective_user
    name = user.first_name
    userid = user.id
    cursor = connection.cursor()
    cursor.execute(f'''SELECT * FROM users WHERE userid = {userid}''')
    try:
        row = np.array(cursor.fetchone())
        balance = row[4]
    except IndexError:
        balance = 0
    msg = update.effective_message.reply_text(f'[{name}](tg://user?id={userid})\nБаланс: {balance}',parse_mode=ParseMode.MARKDOWN,)
    sleep (10)
    context.bot.delete_message(chat_id=chat.id, message_id=msg.message_id)

# Лог последних 10 выпавших чисел
@mult_threading
def log(update, connection, context):
    chat = update.effective_chat
    chatid = chat.id * chat.id // 500000
    cursor = connection.cursor()
    cursor.execute(f'''SELECT COUNT(*) FROM log{chatid}''')
    a = np.array(cursor.fetchone())
    b = a[0] - 10
    com2 = ' '
    if b < 0:
        b = 0
    cursor.execute(f'''SELECT * FROM log{chatid} WHERE id <= {a[0]} AND id > {b}''')
    while b < a:
        com = np.array(cursor.fetchone())
        color = str(com[2])
        if color == 'Red':
            Vcolor = '🔴'
        if color == 'Black':
            Vcolor = '⚫'
        if color == 'Zero':
            Vcolor = '💚'
        com2 =str(com2)+ str(Vcolor) + str(com[1]) + '\n'
        b = b + 1

    msg = update.effective_message.reply_text(f'{com2}')
    sleep(5)
    context.bot.delete_message(chat_id=chat.id, message_id=msg.message_id)
    delmsg(update, context)

# Последние 20 чисел
@mult_threading
def log1(update, connection, context):
    chat = update.effective_chat
    chatid = chat.id * chat.id // 500000
    cursor = connection.cursor()
    cursor.execute(f'''SELECT COUNT(*) FROM log{chatid}''')
    a = np.array(cursor.fetchone())
    b = a[0] - 20
    com2 = ' '
    if b < 0:
        b = 0
    cursor.execute(f'''SELECT * FROM log{chatid} WHERE id <= {a[0]} AND id > {b}''')
    while b < a:
        com = np.array(cursor.fetchone())
        color = str(com[2])
        if color == 'Red':
            Vcolor = '🔴'
        if color == 'Black':
            Vcolor = '⚫'
        if color == 'Zero':
            Vcolor = '💚'
        com2 =str(com2)+ str(Vcolor) + str(com[1]) + '\n'
        b = b + 1

    msg = update.effective_message.reply_text(f'{com2}')
    sleep(5)
    context.bot.delete_message(chat_id=chat.id, message_id=msg.message_id)
    delmsg(update, context)

# Выплаты победителям
def payday(update, connection):
    chat = update.effective_chat
    chatid = chat.id * chat.id // 500000
    cursor = connection.cursor()
    cursor.execute(f"""SELECT COUNT(*) FROM winers{chatid}""")
    M = np.array(cursor.fetchall())
    k = 0
    cursor.execute(f"""SELECT userid , Pwin FROM winers{chatid}""")
    com = np.array(cursor.fetchall())
    while k < M:
        winer = com[k]
        cursor.execute(f"""UPDATE users SET balance = balance + {winer[1]} WHERE userid = {winer[0]} """)
        connection.commit()
        k = k + 1


# Проверка всего чего можно для запуска рулетки
@mult_threading
def randomrulet(connection, update, context):
    user = update.effective_user
    username = str(user.username)
    name1 = str(user.first_name)
    name2 = str(user.first_name) + str(user.last_name)
    chat = update.effective_chat
    chatid = chat.id * chat.id // 500000
    cursor = connection.cursor()

    cursor.execute(f"SHOW TABLES LIKE 'betinchat{chatid}'")
    kk = f'betinchat{chatid}'
    try:
        row = np.array(cursor.fetchone())
        PC = row[0]
    except IndexError:
        PC = 0
    if kk == PC:
        cursor.execute(f"""SELECT COUNT(*) FROM betinchat{chatid}""")
        N = np.array(cursor.fetchone())
        if N == 0:
            update.effective_message.reply_text(f'''Сделайте ставки!''')
        else:
            if username == Nonee:
                if str(user.last_name) == str(Nonee):
                    msg = update.effective_message.reply_text(f'{name1} крутит рулетку через 10 секунд')
                    sendgif(update, context)
                else:
                   msg = update.effective_message.reply_text(f'{name2} крутит рулетку через 10 секунд')
                   sendgif(update, context)
            else:
                msg = update.effective_message.reply_text(f'@{username} крутит рулетку через 10 секунд')
                sendgif(update, context)
            sleep(10)
            context.bot.delete_message(chat_id=chat.id, message_id=msg.message_id)
            vin(connection, update, context)
    else:
        msg = update.effective_message.reply_text('Запустите рулетку')
        sleep(3)
        context.bot.delete_message(chat_id=chat.id, message_id=msg.message_id)

# Определение победителей
def vin(connection, update, context):
    chat = update.effective_chat
    chatid = chat.id * chat.id // 500000
    cursor = connection.cursor()
    cursor.execute(f"""
CREATE TABLE IF NOT EXISTS winers{chatid} (
  id INT AUTO_INCREMENT,
  username VARCHAR(20),
  userid INT,
  bet INT,
  field VARCHAR(20),
  Pwin INT,
  coment VARCHAR(50),
  PRIMARY KEY (id)
) ENGINE = InnoDB
""")
    user = update.effective_user
    chat = update.effective_chat
    chatid = chat.id * chat.id // 500000
    username = user.username
    RN = random.randint(0, 36)
    cursor.execute(f"SELECT * FROM rulet WHERE num = {RN}")
    row = np.array(cursor.fetchone())
    num = row[1]
    color = str(row[2])
    EO = str(row[3])
    ster = str(row[4])
    thirds = str(row[5])
    half = str(row[6])
    PN = str(row[7])
    if color == 'Red':
        Vcolor = '🔴'
    if color == 'Black':
        Vcolor = '⚫'
    if color == 'Zero':
        Vcolor = '💚'


    cursor.execute(f"""SELECT COUNT(*) FROM betinchat{chatid}""")
    N = np.array(cursor.fetchone())
    n = 0
    i = ' '
    a = 0
    com1 = ' '

    cursor.execute(f"""INSERT INTO winers{chatid} SELECT * FROM betinchat{chatid} WHERE field = "{color}" OR field = "{EO}" OR field = "{ster}" OR field = "{thirds}" OR field = "{half}" OR field = "{num}" OR field = "{PN}" """)
    connection.commit()

    cursor.execute(f"""SELECT coment FROM betinchat{chatid}""")

    while n < N:
        com = np.array(cursor.fetchone())
        com1 =str(com1)+ str(com[0]) + '\n'
        n = n + 1

    cursor.execute(f"""SELECT COUNT(*) FROM winers{chatid}""")
    j = np.array(cursor.fetchone())
    if j == 0:
        i = 'Победителей нет'
    else:
        cursor.execute(f"""SELECT username, userid , Pwin FROM winers{chatid}""")
        while a < j:
            com = np.array(cursor.fetchone())
            i = str(i)+ str(com[0]) + ' выиграл ' + str(com[2]) + '\n'
            a = a + 1

    payday(update, connection)

    context.bot.send_message(chat.id, f'''
Рулетка: {Vcolor}{RN}
[{EO}][{ster}][{thirds}][{half}][{PN}]

Результаты:
{com1}
-------------------------
{i}
''')

    cursor.execute(f"""SELECT msgid FROM trash{chatid}""")
    msg = np.array(cursor.fetchone())
    #print(msg)
    #print(msg[0])
    #print(chat.id)
    try:
        context.bot.delete_message(chat_id=chat.id, message_id=int(msg[0]))
    except Exception:
        none = "none"
    cursor.execute(f"""DROP TABLES trash{chatid}""")

    cursor.execute(f"""DROP TABLES betinchat{chatid}""")
    cursor.execute(f"""DROP TABLES winers{chatid}""")
    sql = f"INSERT INTO log{chatid} ( num, color) VALUES( %s, %s)"
    val = (int(num), str(color))
    cursor.execute(sql, val)
    connection.commit()
    #.delmsg(update, context)


# Проверка на создание таблицы/создание таблицы
def query_with_fetchone(connection, update, context):
    chat = update.effective_chat
    cursor = connection.cursor()
    chatid = chat.id * chat.id // 500000

    cursor.execute(f"SHOW TABLES LIKE 'betinchat{chatid}'")
    try:
        row = np.array(cursor.fetchone())
        PC = row[0]
    except IndexError:
        PC = 0
    kk = f'betinchat{chatid}'
    if kk == PC:
        update.effective_message.reply_text('Рулетка уже запущена')
    else:
        tablerulet(update, connection)
        StolRuletki(update, context, connection)


def rrcheckt(update, connection):
    chat = update.effective_chat
    cursor = connection.cursor()
    chatid = chat.id * chat.id // 500000

    cursor.execute(f"SHOW TABLES LIKE 'RR{chatid}'")
    try:
        row = np.array(cursor.fetchone())
        PC = row[0]
    except IndexError:
        PC = 0
    kk = f'RR{chatid}'
    if kk == PC:
        update.effective_message.reply_text('Русская рулетка уже запущена')
    else:
        StolRR2(update)
        RoomRR(connection, update)

def rrcheckf(update, connection):
    chat = update.effective_chat
    cursor = connection.cursor()
    chatid = chat.id * chat.id // 500000

    cursor.execute(f"SHOW TABLES LIKE 'RR{chatid}'")
    try:
        row = np.array(cursor.fetchone())
        PC = row[0]
    except IndexError:
        PC = 0
    kk = f'RR{chatid}'
    if kk == PC:
        update.effective_message.reply_text('Русская рулетка уже запущена')
    else:
        StolRR4(update)
        RoomRR(connection, update)

def rrchecks(update, connection):
    chat = update.effective_chat
    cursor = connection.cursor()
    chatid = chat.id * chat.id // 500000

    cursor.execute(f"SHOW TABLES LIKE 'RR{chatid}'")
    try:
        row = np.array(cursor.fetchone())
        PC = row[0]
    except IndexError:
        PC = 0
    kk = f'RR{chatid}'
    if kk == PC:
        update.effective_message.reply_text('Русская рулетка уже запущена')
    else:
        StolRR6(update)
        RoomRR(connection, update)

# Ставка через панель
@mult_threading
def stavka10000(update, connection, context):
    user = update.effective_user
    bet = 10000
    cd = update.callback_query.data
    if cd == '1':
        Scd = '1стр'
        Pwin = bet * 3
    if cd == '2':
        Scd = '2стр'
        Pwin = bet * 3
    if cd == '3':
        Scd = '3стр'
        Pwin = bet * 3
    if cd == '4':
        Scd = '1/3'
        Pwin = bet * 3
    if cd == '5':
        Scd = '2/3'
        Pwin = bet * 3
    if cd == '6':
        Scd = '3/3'
        Pwin = bet * 3
    if cd == '7':
        Scd = '1/2'
        Pwin = bet * 2
    if cd == '8':
        Scd = 'EVEN'
        Pwin = bet * 2
    if cd == '9':
        Scd = 'ODD'
        Pwin = bet * 2
    if cd == '10':
        Scd = '2/2'
        Pwin = bet * 2
    if cd == '11':
        Scd = 'Red'
        Pwin = bet * 2
    if cd == '12':
        Scd = 'Black'
        Pwin = bet * 2
    if cd == '13':
        Scd = 'Zero'
        Pwin = bet * 14
    if cd == '14':
        Scd = '1-3'
        Pwin = bet * 6
    if cd == '15':
        Scd = '10-12'
        Pwin = bet * 6
    if cd == '16':
        Scd = '19-21'
        Pwin = bet * 6
    if cd == '17':
        Scd = '28-30'
        Pwin = bet * 6
    if cd == '18':
        Scd = '4-6'
        Pwin = bet * 6
    if cd == '19':
        Scd = '13-15'
        Pwin = bet * 6
    if cd == '20':
        Scd = '22-24'
        Pwin = bet * 6
    if cd == '21':
        Scd = '31-33'
        Pwin = bet * 6
    if cd == '22':
        Scd = '7-9'
        Pwin = bet * 6
    if cd == '23':
        Scd = '16-18'
        Pwin = bet * 6
    if cd == '24':
        Scd = '25-27'
        Pwin = bet * 6
    if cd == '25':
        Scd = '34-36'
        Pwin = bet * 6
    chat = update.effective_chat
    cdid = update.callback_query.id
    chatid = chat.id * chat.id // 500000
    userid = int(user.id)
    name1 = user.first_name
    name2 = str(user.first_name) + str(user.last_name)
    cursor = connection.cursor()
    try:
        cursor.execute(f"""SELECT balance FROM users WHERE userid = {userid} """)
        balans = np.array(cursor.fetchone())
        DBalans = balans
        if bet > DBalans:
            context.bot.answerCallbackQuery(callback_query_id=cdid, text="У вас нет столько денег", show_alert=False)#True
            #update.effective_message.reply_text(f'''❌{name1} вы не можете поставить ставку превышающую 90% вашего баланса!!!''')
        else:
            cursor.execute(f"""UPDATE users SET balance = balance - {bet} WHERE userid = {userid} """)
            connection.commit()
            coment = f'{name1} {bet} на [{Scd}]'

            sql = f"INSERT INTO betinchat{chatid} ( username, userid, bet, field, Pwin, coment) VALUES ( %s, %s, %s, %s, %s, %s)"
            val = (name1, userid, bet, Scd, Pwin, coment)
            cursor.execute(sql, val)
            connection.commit()
            #context.bot.answerCallbackQuery(callback_query_id=cdid, text="Ставка принята", show_alert=True)
            msg = update.effective_message.reply_text(f'''
📝Ставка принята:
💰{coment}
✅Выигрыш составит: {Pwin}
        ''')
        sleep(10)
        context.bot.delete_message(chat_id=chat.id, message_id=msg.message_id)

    except OperationalError:
        cursor.execute(f"""\r""")
        connection.commit()


# Кнопки. Ответ.
def button(update, context):
    callback_data = update.callback_query.data

    if callback_data > '0' and callback_data != '26' and callback_data != '27' and callback_data != '28' and callback_data != '1st' and callback_data != '2nd' and callback_data != '3rd' and callback_data != '4th' and callback_data != '5th' and callback_data != '6th' and callback_data != '7th' and callback_data != '8th':
        stavka10000(update, connection,context)

    if callback_data == '28':
        balance1(update, context)

    if callback_data == '27':
        cancelbet(update, connection, context)

    if callback_data == '26':
        randomrulet(connection, update, context)

    if callback_data == '1st':
        addgamer(connection, update, Bot)
    if callback_data == '2nd':
        addgamer(connection, update, Bot)
    if callback_data == '3rd':
        addgamer(connection, update, Bot)
    if callback_data == '4th':
        addgamer(connection, update, Bot)
    if callback_data == '5th':
        addgamer(connection, update, Bot)
    if callback_data == '6th':
        addgamer(connection, update, Bot)
    if callback_data == '7th':
        descRR(update, context)
    if callback_data == '8th':
        updatemsg(update)

# Передача деняг
def money(update, connection):
    cursor = connection.cursor()
    text = update.message.text
    a = (text.split(' ', 1))
    txt = np.array(a)
    summ = int(txt[1])
    user = update.effective_user
    user1 = update.message.reply_to_message.from_user
    name1 = user.first_name
    name2 = user1.first_name
    userid1 = user.id
    userid2 = user1.id

    cursor.execute(f"""SELECT balance FROM users WHERE userid = {userid1} """)
    balans = np.array(cursor.fetchone())
    if summ > int(balans):
        update.effective_message.reply_text(f'''❌{name1} недостаточно средств!!!''')
    else:
        update.effective_message.reply_text(f'{name1} передал {summ} монеток {name2}')
        cursor.execute(f"""UPDATE users SET balance = balance - {summ} WHERE userid = {userid1} """)
        connection.commit()
        cursor.execute(f"""UPDATE users SET balance = balance + {summ} WHERE userid = {userid2} """)
        connection.commit()

# Админские штучки
def admmoney(update, connection, context):
    cursor = connection.cursor()
    text = update.message.text
    try:
        a = (text.split(' ', 1))
        txt = np.array(a)
        summ = txt[1]
    except IndexError:
        summ = 0
    chatid = update.effective_chat.id
    user = update.effective_user
    user1 = update.message.reply_to_message.from_user
    name1 = user.first_name
    name2 = user1.first_name
    userid1 = user.id
    userid2 = user1.id
    Padm = '1'
    Sadm = '2'
    cursor.execute(f"""SELECT adm FROM users WHERE userid = {userid1} """)
    adm = np.array(cursor.fetchone())
   # if int(adm) >= int(Padm) and userid1 == '593433853':
   #     update.effective_message.reply_text(f'Низя тебе, но админка то есть))')
    if int(adm) >= int(Padm):
        if txt[0] == '++':
            #msg = update.effective_message.reply_text(f'{name1} добавил {summ} монеток {name2}')
            res = context.bot.send_message(chatid, f'[{name1}](tg://user?id={userid1}) добавил {summ} монеток [{name2}](tg://user?id={userid2})',
parse_mode=ParseMode.MARKDOWN,)
            cursor.execute(f"""UPDATE users SET balance = balance + {summ} WHERE userid = {userid2} """)
            connection.commit()
        if txt[0] == '—' or txt[0] == '--':
            res = context.bot.send_message(chatid, f'[{name1}](tg://user?id={userid1}) забрал у [{name2}](tg://user?id={userid2}), {summ} монеток',
parse_mode=ParseMode.MARKDOWN,)
            cursor.execute(f"""UPDATE users SET balance = balance - {summ} WHERE userid = {userid2} """)
            connection.commit()
        if txt[0] == '+!':
            #context.bot.set_chat_administrator_custom_title(chatid, userid2, str(summ))
            res = context.bot.send_message(chatid, f'[{name1}](tg://user?id={userid1}) выдал префикс {summ} игроку [{name2}](tg://user?id={userid2})',
parse_mode=ParseMode.MARKDOWN,)
            cursor.execute(f"""UPDATE users SET prefix = '{summ}' WHERE userid = {userid2} """)
            connection.commit()
        if txt[0] == '+б':
            cursor.execute(f"""SELECT balance FROM users WHERE userid = {userid2} """)
            bal = np.array(cursor.fetchone())
            bals = bal[0]
            update.effective_message.reply_text(f'Баланс игрока [{name2}](tg://user?id={userid2}): {bals} ',
parse_mode=ParseMode.MARKDOWN,)

    if int(adm) == int(Sadm):
        if txt[0] == '+A':
            update.effective_message.reply_text(f'[{name1}](tg://user?id={userid1}) выдал админку игроку [{name2}](tg://user?id={userid2})',
parse_mode=ParseMode.MARKDOWN,)
            cursor.execute(f"""UPDATE users SET adm = '1' WHERE userid = {userid2} """)
            connection.commit()
        if txt[0] == '-A':
            update.effective_message.reply_text(f'[{name1}](tg://user?id={userid1}) забрал админку у игрока [{name2}](tg://user?id={userid2})',
parse_mode=ParseMode.MARKDOWN,)
            cursor.execute(f"""UPDATE users SET adm = '0' WHERE userid = {userid2} """)
            connection.commit()


    if int(adm) < 1 :
        update.effective_message.reply_text(f'''❌[{name1}](tg://user?id={userid1}) вы не администратор бота!!''',
parse_mode=ParseMode.MARKDOWN,)
    delmsg(update, context)
   # sleep(2)
   # context.bot.delete_message(chat_id=chatid, message_id=res.message_id)



#Гифка рулетки при запуске
@mult_threading
def sendgif(update, context):
    chatid = update.effective_chat.id
    link = ["https://media.giphy.com/media/1DEJwfwdknKZq/giphy.gif", "https://media.giphy.com/media/l2Sq8INNsCDnEULM4/giphy.gif", "https://media.giphy.com/media/26uf2YTgF5upXUTm0/giphy.gif", "https://media.giphy.com/media/xT9DPi61MmrDLzVFzq/giphy.gif"]
    r = random.randint(0, 3)
    res = context.bot.send_animation(chatid, link[r])
    sleep(10)
    context.bot.delete_message(chat_id=chatid, message_id=res.message_id)
    delmsg(update, context)


# Удаление сообщения пользователя
def delmsg(update, context):
    chatid = update.effective_chat.id
    msgid = update.effective_message.message_id
    #sleep(1)
    context.bot.delete_message(chat_id=chatid, message_id=msgid)


# Ошибки
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# Основа
def main():
    print('started')

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("<TG BOT TOKEN>", use_context=True)

    # Обработчики комманд
    updater.dispatcher.add_handler(CommandHandler('command', commands))
    updater.dispatcher.add_handler(CommandHandler('commanda', commandsA))
    #updater.dispatcher.add_handler(CommandHandler('start', conn))
    updater.dispatcher.add_handler(CommandHandler('desc', descr))
    #updater.dispatcher.add_handler(CommandHandler('descRR', descRR))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, com))
    updater.dispatcher.add_error_handler(error)


    # Start the Bot
    updater.start_polling()
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()

