import sqlite3
import datetime
import logging

from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = '6108816898:AAHaeWbJtoUyJIgunkaSGkd0eHmHRyBO2tk'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)

dp = Dispatcher(bot)

conn = sqlite3.connect('example.db')
now = datetime.datetime.now()
c = conn.cursor()

def pars(data_list):
    return [str(i[0]) + '  ' + str(i[1]) for i in data_list]

def check(data_list):
    return len(data_list) >= 1



c.execute("""CREATE TABLE IF NOT EXISTS Expensesss(
   da_y INT,
   mo_nth INT,
   ye_ar INT,
   much INT,
   reason TEXT,
   da_te TEXT
   );""");

# c.execute('SELECT * FROM Expensesss')
# c.execute('DROP TABLE Expensesss;')
# conn.commit()                   # Для удаления данных из таблицы

def auth(func):
    async def wrapeer(message):
        """if(message['from']['id']) != 576133865:
            return await message.reply("Sorry not you day",reply=False)"""
        return await func(message)

    return wrapeer




@dp.message_handler(commands=['start', 'info'])
@auth
async def welcome(message: types.Message):
    await message.reply(
        "Этот бот предназначен для учета финансов\n\n"
        "Для того, чтобы посмотреть это сообщение с коммандами еще раз, введите: /info\n\n"
        "Добавить расход: просто напишите \n\n1)Сумму 2)Категорию, вашей траты \n\n"
        "Для того, чтобы посмотреть траты за день /day\n\n"
        "Для того, чтобы посмотреть траты за месяц /month\n\n"
        "Для того, чтобы посмотреть траты за год /year\n\n"
        "Для просмотра категорий /category\n"
        ,
        reply=False
        # context = dp.current_state(chat=message.chat.id)

    )



@dp.message_handler(commands=['day'])
@auth
async def day_s(message: types.Message):
    q = ("SELECT SUM(much) FROM Expensesss WHERE da_te = ?")
    prov = ("SELECT * FROM Expensesss WHERE da_te = ?")
    a = c.execute(prov, ((str(datetime.date.today())),))


    if (check(a.fetchall())):
        a = c.execute(q, ((str(datetime.date.today())),))
        ans = int(a.fetchall()[0][0])
        # await message.reply((int((c.fetchall()[0][0]))))
        q = ("SELECT reason,much FROM Expensesss WHERE da_te = ?")
        c.execute(q, ((str(datetime.date.today())),))
        ans_2 = pars(c.fetchall())
        ans_message = f"Ваши траты за день {ans} руб \nКатегории трат {ans_2}."

        # await message.reply('Причины ваших трат:',c.fetchall(),'\n Сумма затрат за день\n',ans)
        await message.reply(ans_message)
    else:
        await message.reply('У вас пока что не было трат за этот день')



@dp.message_handler(commands=['month'])
@auth
async def mon_s(message: types.Message):
    q = ("SELECT SUM(much) FROM Expensesss WHERE mo_nth = ? AND ye_ar = ?")
    prov = ("SELECT * FROM Expensesss WHERE mo_nth = ? AND ye_ar = ?")
    c.execute(prov, ((now.month, now.year)))
    if(check(c.fetchall())):
        c.execute(q,((now.month, now.year)))
        summa = int(c.fetchall()[0][0])
        qq = ("SELECT reason, SUM(much) AS total FROM Expensesss WHERE mo_nth = ? AND ye_ar = ? GROUP BY reason ")
        c.execute(qq, ((now.month, now.year)))
        await message.reply(f'Всего потрачено за месяц {summa}\nКатегории трат \n{pars(c.fetchall())}')
    else:
        await message.reply('За этот месяц вы еще ничего не потратили')


@dp.message_handler(commands=['year'])
@auth
async def year(message: types.Message):
    q = ("SELECT SUM(much) FROM Expensesss WHERE ye_ar = ?")
    prov = ("SELECT * FROM Expensesss WHERE ye_ar = ?")
    c.execute(prov, ((now.year,)))
    if(check(c.fetchall())):
        c.execute(q, ((now.year,)))
        summa = int(c.fetchall()[0][0])
        qq = ("SELECT reason, SUM(much) AS total FROM Expensesss WHERE ye_ar = ? GROUP BY reason ")
        c.execute(qq, ((now.year,)))
        await message.reply(f'Всего потрачено за год {summa}\nКатегории трат \n{pars(c.fetchall())}')
    else:
        await message.reply('За этот год вы еще ничего не потратили')


@dp.message_handler(commands=['category'])
@auth
async def cat(message: types.Message):
    q = """
    SELECT reason, SUM(much) AS total FROM Expensesss GROUP BY reason
    """
    result = c.execute(q).fetchall()
    if(check(result)):
        await message.reply(pars(result))
    else:
        await message.reply('Для того, чтобы вывести категории, вы должны ввести свои траты')


@dp.message_handler()
@auth
async def process_message(message: types.Message):
    # Получение текста сообщения
    text = message.text.split()
    if text[0][0] == '-':
        prow = text[0][1:].isdigit()
    else:
        prow = text[0].isdigit()

    # Запись сообщения в базу данных SQLite
    if prow and type(text[1]) == str:
        c.execute(f"INSERT INTO Expensesss VALUES(?, ?, ?, ?, ?, ?)",
                  (now.day, now.month, now.year, int(text[0]), text[1].lower(), str(datetime.date.today())))
        conn.commit()
        query = "SELECT * FROM Expensesss WHERE da_te = ?;"
        c.execute(query, ((str(datetime.date.today())),))

        #result = c.fetchall()

        await message.reply("Ваша трата записана")
    else:
        await message.reply("Пожалуйста введите сообщение в формате \n1)Сумма 2)Категоия \n Пример: 500 Самокат")



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
