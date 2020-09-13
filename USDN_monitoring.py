import mysql.connector
import sql
import configparser
import datetime
import chain

config = configparser.RawConfigParser()
config.read('bot.cfg')

user = config.get('database', 'user')
password = config.get('database', 'password')


def usdn_reinvest():
    sql_command = "SELECT * FROM USDN_Staking;"
    sql.mydb = mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        auth_plugin='mysql_native_password',
        database="NodeBot"
    )
    sql.cursor = sql.mydb.cursor()
    my_cursor = sql.mydb.cursor()
    my_cursor.execute(sql_command)
    for val in my_cursor.fetchall():
        days = sql.get_col("period_days", val[0], "address", table="USDN_Staking")
        amount = chain.check_usdn_payment(val[0], days)
        cur_date = datetime.datetime.now()
        if amount > 0 and (datetime.date(cur_date.year, cur_date.month, cur_date.day) - val[-1]).days == days:
            if chain.usdn_reinvest(val[0], amount):
                sql.update_col(val[0], "start_date", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "address")


def main():
    while True:
        usdn_reinvest()


main()
