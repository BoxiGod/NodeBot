import mysql.connector
import configparser

config = configparser.RawConfigParser()
config.read('bot.cfg')

user = config.get('database', 'user')
password = config.get('database', 'password')

mydb = mysql.connector.connect(
    host="localhost",
    user=user,
    password=password,
    auth_plugin='mysql_native_password',
    database="NodeBot"
)


cursor = mydb.cursor()
# TODO turn on/off notifications
cursor.execute("CREATE DATABASE IF NOT EXISTS NodeBot")
cursor.execute("CREATE TABLE IF NOT EXISTS Users (address CHAR(50), leased BIGINT, "
               "pendingLease BIGINT, cur_payment_ratio_fees INT, "
               "cur_payment_ratio_block_reward INT, payment_period CHAR(15), "
               "reinvest INT, cur_reward BIGINT, cur_reinvest BIGINT, boxinode_balance INT, "
               "language CHAR(20), telegram_id INT, step INT, threshold BIGINT, public_key CHAR(50), "
               "contract_address CHAR(50), contract_lease BIGINT, "
               " contract_pending_lease BIGINT, contract_private_key CHAR(50), safety_option INT, "
               "cur_boxi_reward BIGINT)")
cursor.execute("CREATE TABLE IF NOT EXISTS Reinvest (start_reinvest INT, amount_reinvest BIGINT, address CHAR(50))")
cursor.execute("CREATE TABLE IF NOT EXISTS NodeStats (date_today DATE, total_leasers BIGINT, "
               "lease_amount BIGINT, lease_payment BIGINT, apr FLOAT)")
mydb.commit()
mydb.close()
cursor.close()



'''
mydb = mysql.connector.connect(
    host="localhost",
    user="BoxiGod",
    password="89103020017Zas",
    auth_plugin='mysql_native_password',
    database='NodeBot'
)
'''


def insert_reinvest(start_reinvest, amount_reinvest, address):
    sql = "INSERT INTO Reinvest (start_reinvest, amount_reinvest, address) VALUES (%s, %s, %s)"
    val = (str(start_reinvest), str(amount_reinvest), str(address))
    cursor.execute(sql, val)
    mydb.commit()


def get_reinvest_col(select_column, column, search_column):
    cursor.itersize = 1
    sql = "SELECT " + str(select_column) + " FROM Reinvest WHERE " + str(search_column) + " = '" + str(column) + "'"
    cursor.execute(sql)
    result = cursor.fetchall()
    try:
        return result
    except IndexError:
        return result


def delete_reinvest_col(user_id, set_col):
    sql = "DELETE FROM Reinvest WHERE " + str(set_col) + "='" + str(user_id) + "'"
    cursor.execute(sql)
    mydb.commit()


def delete_col(col, condition, col2, condition2):
    sql = "DELETE From Users WHERE " + str(col) + "='" + str(condition) + "' AND " + str(col2) + "='" + str(condition2) + "'"
    cursor.execute(sql)
    mydb.commit()


def update_col(user_id, col, new_val, set_col):
    sql = "UPDATE Users SET " + str(col) + "= '" + str(new_val) + "' WHERE " + str(set_col) + "='" + str(user_id) + "'"
    cursor.execute(sql)
    mydb.commit()


def insert_user(address, leased, pendingLease, cur_payment_ratio_fees, cur_payment_ratio_block_reward,
                payment_period, reinvest, cur_reward, cur_reinvest, boxinode_balance,
                language, tg_id, step, threshold, public_key,
                contract_address, contract_lease, contract_pending_lease, contract_private_key, safety_option, cur_boxi_reward):
    sql = "INSERT INTO Users (address, leased, pendingLease, cur_payment_ratio_fees, " \
          "cur_payment_ratio_block_reward, " \
          "payment_period, reinvest, cur_reward, cur_reinvest, boxinode_balance, " \
          "language, telegram_id, step, threshold, public_key, " \
          "contract_address, contract_lease, contract_pending_lease, " \
          "contract_private_key, safety_option, cur_boxi_reward) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (address, str(leased), str(pendingLease), str(cur_payment_ratio_fees),
           str(cur_payment_ratio_block_reward), payment_period, str(reinvest), str(cur_reward),
           str(cur_reinvest), str(boxinode_balance), language, str(tg_id), str(step), str(threshold),
           str(public_key), str(contract_address), str(contract_lease)
           , str(contract_pending_lease), str(contract_private_key), str(safety_option), str(cur_boxi_reward))
    cursor.execute(sql, val)
    mydb.commit()


def get_col(select_column, column, search_column):
    cursor.itersize = 1
    sql = "SELECT " + str(select_column) + " FROM Users WHERE " + str(search_column) + " = '" + str(column) + "'"
    cursor.execute(sql)
    result = cursor.fetchall()
    try:
        return result[0][0]
    except IndexError:
        return result


def get_col2(select_column, column, search_column):
    cursor.itersize = 1
    sql = "SELECT " + str(select_column) + " FROM Users WHERE " + search_column + " = '" + str(column) + "'"
    cursor.execute(sql)
    result = cursor.fetchone()
    try:
        return result
    except IndexError:
        return result


def insert_stats(date_today, total_leasers, lease_amount, lease_payment, apr):
    sql = "INSERT INTO NodeStats (date_today, total_leasers, lease_amount, lease_payment, apr) VALUES (%s, %s, %s, %s, %s)"
    val = (date_today, str(total_leasers), str(lease_amount), str(lease_payment), str(apr))
    cursor.execute(sql, val)
