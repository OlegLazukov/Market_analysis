from tvDatafeed import TvDatafeed, Interval
from Config import *
import pymysql.cursors


"""
Подключение к базе данных
"""
connection = pymysql.connect(
        host=host,
        port=3306,
        user=user,
        password=password_db,
        database=database,
        cursorclass=pymysql.cursors.DictCursor
)
"""
Создаем объект TvDatafeed
"""
tv = TvDatafeed(user_name, password)

"""
Функция обновления базы данных по запросу полученному от пользователя
"""
def summary_of_quotes(click_button):
    for item in lst_exchange:
        df_quotes = tv.get_hist(symbol=f"{click_button}",exchange=f"{item}",interval=Interval.in_daily,n_bars=10000)
        if df_quotes is None:
            continue
        with connection.cursor() as cursor:
                count = 0
                for index, row in df_quotes.iterrows():
                        name_quote = row['symbol'].replace(f"{item}" + ":", "")
                        count += 1
                        update_query = f"UPDATE IGNORE `Сurrency quotes` SET symbol = '{name_quote}', open = '{row['open']}', high = '{row['high']}', low = '{row['low']}', close = '{row['close']}', volume = '{row['volume']}', date = '{index}' WHERE id = '{count}';"
                        cursor.execute(update_query)
                        connection.commit()
        with connection.cursor() as cursor:
                insert_buy_sell = "UPDATE `Сurrency quotes` SET buy = 'None', sell = 'Day for sell' WHERE close < open;"
                cursor.execute(insert_buy_sell)
                connection.commit()
        with connection.cursor() as cursor:
                insert_buy_sell = "UPDATE `Сurrency quotes` SET buy = 'Day for buy', sell = 'None' WHERE close > open;"
                cursor.execute(insert_buy_sell)
                connection.commit()


# with connection.cursor() as cursor:
#     sql = "CREATE TABLE IF NOT EXISTS `Сurrency quotes` (id INT AUTO_INCREMENT PRIMARY KEY, symbol varchar(255), open FLOAT, high FLOAT, low FLOAT, close FLOAT, volume INT, date DATE);"
#     cursor.execute(sql)

# with connection.cursor() as cursor:
#     for index, row in df_eur_usd.iterrows():
#             insert_query = f"INSERT INTO `Сurrency quotes` (symbol, open, high, low, close, volume, date) VALUES ('EURUSD', '{row['open']}', '{row['high']}', '{row['low']}', '{row['close']}', '{row['volume']}', '{index}');"
#             cursor.execute(insert_query)
#             connection.commit()

# with connection.cursor() as cursor:
#         count = 0
#         for index, row in df_eur_usd.iterrows():
#                 count += 1
#                 update_query = f"UPDATE IGNORE `Quote_eur_usd` SET symbol = '{row['symbol']}', open = '{row['open']}', high = '{row['high']}', low = '{row['low']}', close = '{row['close']}', volume = '{row['volume']}', date = '{index}' WHERE id_eur_usd = '{count}';"
#                 cursor.execute(update_query)
#                 connection.commit()


# with connection.cursor() as cursor:
#         delete_query = "ALTER TABLE `Сurrency quotes` RENAME COLUMN id_eur_usd TO id;"
#         cursor.execute(delete_query)
#         connection.commit()

# with connection.cursor() as cursor:
#         add_column_buy_sell = "ALTER TABLE `Сurrency quotes` ADD buy varchar(255), ADD sell varchar(255);"
#         cursor.execute(add_column_buy_sell)
#         connection.commit()

# with connection.cursor() as cursor:
#         insert_buy_sell = "UPDATE `Сurrency quotes` SET buy = 'None', sell = 'Day for sell' WHERE close < open;"
#         cursor.execute(insert_buy_sell)
#         connection.commit()



"""
Функция для вычисления средней цены инструмента
"""
def average_value():
        with connection.cursor() as cursor:
                average_value = "SELECT AVG(HIGH - LOW) FROM `Сurrency quotes`;"
                cursor.execute(average_value)
                result = cursor.fetchone()['AVG(HIGH - LOW)']
                value = round(result, 6) * 1000000
        return value

"""
Функция для получения стоблцов дат (покупки и продажи), когда цена инструмента выше средней (соответственно дни более волатильные)
"""
def set_data():
        lst_buy, lst_sell = [], []
        with connection.cursor() as cursor:
                cursor.execute("SELECT date, buy, sell, high, low FROM `Сurrency quotes`;")
                for row in cursor.fetchall():
                        res = round(row['high'] - row['low'], 6) * 1000000
                        if res > average_value() and row['buy'] == 'Day for buy':
                                lst_buy.append(row['date'])
                        elif res > average_value() and row['sell'] == 'Day for sell':
                                lst_sell.append(row['date'])
        return lst_buy, lst_sell

"""
Функция для определения дня недели из списков дат
"""
def num_date_in_day():
        lst_day_buy, lst_day_sell = [], []
        dct_day = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница'}
        for item in set_data()[0]:
                if item.weekday() in dct_day.keys():
                        day = dct_day[item.weekday()]
                        lst_day_buy.append(day)
        for item in set_data()[1]:
                if item.weekday() in dct_day.keys():
                        day = dct_day[item.weekday()]
                        lst_day_sell.append(day)

        return lst_day_buy, lst_day_sell


"""
Функция для создания словарей с количеством покупок и продаж по дням недели
"""

def from_lst_to_dct():
        dct_data_buy, dct_data_sell = {}, {}
        lst_day = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
        for i in range(5):
                count_buy = num_date_in_day()[0].count(lst_day[i])
                count_sell = num_date_in_day()[1].count(lst_day[i])
                dct_data_buy[lst_day[i]] = count_buy
                dct_data_sell[lst_day[i]] = count_sell
        return dct_data_buy, dct_data_sell

from_lst_to_dct()

