import time
import mysql.connector
import requests
import sql
import pywaves as pw
import json
import configparser
import telebot
import chain
from datetime import datetime
import logging

# logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('blocks.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# config setup
config = configparser.RawConfigParser()
config.read('bot.cfg')

node_address = config.get('account', 'address')
user = config.get('database', 'user')
password = config.get('database', 'password')
node = config.get('blockchain', 'node')
boxinode_token_fee = config.get('payments', 'boxinode_token_fee')
boxinode_token_minimum = config.get('payments', 'boxinode_token_minimum')
boxinode_per_block_reward = config.get('payments', 'boxinode_per_block_reward')

mydb = mysql.connector.connect(
    host="localhost",
    user=user,
    password=password,
    auth_plugin='mysql_native_password',
    database="NodeBot"
)

mycursor = mydb.cursor()

if config.getint('main', 'production'):
    bot = telebot.TeleBot('894215970:AAHPnGjDjBKOmMxHNIZorsWWeVmEjGERdcg')
    group_id_eng = config.get('payments', 'group_id_eng')
    group_id_ru = config.get('payments', 'group_id_ru')
else:
    bot = telebot.TeleBot('1129543819:AAHAz2aGokUfAeSgE_uSHQnT9zGsWfFmmaM')
    group_id_eng = -1001206932432
    group_id_ru = -1001206932432

# mycursor.execute("CREATE DATABASE IF NOT EXISTS PaymentBot")
mycursor.execute("CREATE TABLE IF NOT EXISTS Blocks (block INT PRIMARY KEY, generator VARCHAR(60), fees INT)")
mydb.commit()


def notify_groups(lease_payment, total_leasers, lease_amount, cursor):
    sql.cursor = cursor
    bot.send_message(group_id_eng, "Leasers! Weekly payment was done today\nTotal WAVES: *" + str('{:.2f}'.format(lease_payment / 10**8))
                     + " WAVES*\nLeasers: *" + str(total_leasers)
                     + "*\nNode Balance: *" + str('{:.2f}'.format(lease_amount / 10**8)) + "*",
                     parse_mode='Markdown')
    bot.send_message(group_id_ru, "Лизеры! Еженедельная выплата была сделана сегодня\nВсего WAVES: *"
                     + str('{:.2f}'.format(lease_payment / 10**8)) + " WAVES*\nЛизеров: *"
                     + str(total_leasers) + "*\nБаланс Ноды: *" + str('{:.2f}'.format(lease_amount / 10**8)) + "*",
                     parse_mode='Markdown')
    now = datetime.now()
    date_today = now.strftime('%Y-%m-%d %H:%M:%S')
    sql.insert_stats(date_today, total_leasers, lease_amount, lease_payment, lease_payment/lease_amount*52)


def notify_payment(address, amount, cursor):
    sql.cursor = cursor
    tg_id = sql.get_col("telegram_id", address, "address")
    if tg_id:
        if sql.get_col("language", tg_id, "telegram_id") == "English":
            bot.send_message(tg_id, "Payment was done, you got *" + str('{:.8f}'.format(amount / 10**8)) + " WAVES*",
                             parse_mode='Markdown')
        else:
            bot.send_message(tg_id,
                             "Выплата сделана, вы получили *" + str('{:.8f}'.format(amount / 10**8)) + " WAVES*",
                             parse_mode='Markdown')


def notify_block(amount, reinvest, leaser, total_lease, total_reward):
    tg_id = sql.get_col("telegram_id", leaser.address, "address")
    if tg_id:
        if sql.get_col("language", tg_id, "telegram_id") == "English":
            bot.send_message(tg_id, "New block! *" + str(
                int(total_reward) / 10 ** 8) + " WAVES*. \nNode balance = *" + str(
                '{:.1f}'.format(int(total_lease) / 10 ** 8)) + "* WAVES, your share = *" + str('{:.5f}'.format(leaser.share))
                             + " %*. \nYou got *" + str(
                '{:.8f}'.format(int(amount) / 10 ** 8)) + " WAVES*, where *"
                             + str(reinvest) + "%* goes to reinvest",
                             parse_mode='Markdown')
        else:
            bot.send_message(tg_id, "Новый блок! *" + str(
                int(total_reward) / 10 ** 8) + " WAVES*. \nБаланс ноды = *" + str(
                '{:.1f}'.format(int(total_lease) / 10 ** 8)) + "* WAVES, ваша доля = *" + str('{:.5f}'.format(leaser.share))
                             + " %*. \nВы получили *" + str(
                '{:.8f}'.format(int(amount) / 10 ** 8)) + " WAVES*, где *"
                             + str(reinvest) + "%* ушло в реинвестирование",
                             parse_mode='Markdown')


def insert_block(block, generator, fees, cursor):
    sql = "INSERT INTO Blocks (block, generator, fees) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE block=block"
    val = (block, generator, fees)
    cursor.execute(sql, val)


def get_last_block(mycursor):
    sql = "SELECT Max(block) FROM Blocks"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    try:
        return myresult[0][0]
    except IndexError:
        return myresult


def update_leases(height):
    sql.mydb = mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        auth_plugin='mysql_native_password',
        database="NodeBot"
    )
    sql.cursor = sql.mydb.cursor()
    lease_amount = {}
    print("update leases for block " + str(height))
    list_of_leasers = requests.get(url=node + "/leasing/active/3P2cC7cwEwnz4z6RFyx7DWnWCtTHBcaL53P").json()
    leaser_address_list = []
    for leaser in list_of_leasers:
        leaser_address_list.append(leaser['sender'])
    sql_command = "SELECT * FROM Users"
    sql.cursor = sql.mydb.cursor()
    my_cursor = sql.mydb.cursor()
    my_cursor.execute(sql_command)
    for val in my_cursor.fetchall():  # Null if canceled
        if val[0] not in leaser_address_list:
                sql.update_col(val[0], "leased", 0, "address")
                sql.update_col(val[0], "pendingLease", 0, "address")
        if val[15] not in leaser_address_list:
                sql.update_col(val[15], "contract_lease", 0, "contract_address")
                sql.update_col(val[15], "contract_pending_lease", 0, "contract_address")
    for leaser in list_of_leasers:  # Null all pending, before check pending
        if sql.get_col("contract_address", leaser['sender'], "contract_address"):
            sql.update_col(leaser['sender'], "contract_pending_lease", 0, "contract_address")
        else:
            sql.update_col(leaser['sender'], "pendingLease", 0, "address")
    for leaser in list_of_leasers:  # Check pending
        if int(leaser['height']) + 1000 > height:
            if leaser['sender'] not in lease_amount:
                lease_amount[leaser['sender']] = leaser['amount']
            else:
                lease_amount[leaser['sender']] = lease_amount[leaser['sender']] + leaser['amount']
    for x in lease_amount:
        if sql.get_col("contract_address", x, "contract_address"):
            sql.update_col(x, "contract_pending_lease", lease_amount.get(x, ""), "contract_address")
        else:
            sql.update_col(x, "pendingLease", lease_amount.get(x, ""), "address")
    lease_amount = {}
    for leaser in list_of_leasers:
        if int(leaser['height']) + 1000 < height:
            if leaser['sender'] not in lease_amount:
                lease_amount[leaser['sender']] = leaser['amount']
            else:
                lease_amount[leaser['sender']] = lease_amount[leaser['sender']] + leaser['amount']
    for x in lease_amount:
        if sql.get_col("contract_address", x, "contract_address"):
            sql.update_col(x, "contract_lease", lease_amount.get(x, ""), "contract_address")
        else:
            sql.update_col(x, "leased", lease_amount.get(x, ""), "address")
    sql.cursor.close()
    sql.mydb.close()


def check_blocks_sequence():
    mydb = mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        auth_plugin='mysql_native_password',
        database="NodeBot"
    )
    mycursor = mydb.cursor()
    print("start check blocks")
    current_block = 2186190
    last_block = requests.get(url=node + "/blocks/last").json()['height'] - 1
    print(last_block)
    while current_block <= last_block:
        if not block_exist(current_block, mycursor):
            url = node + "/blocks/seq/" + str(current_block) + '/' + str(current_block + 50)
            blocks = requests.get(url=url).json()
            i = 0
            while i < len(blocks):
                if not block_exist(blocks[i]['height'], mycursor):
                    insert_block(blocks[i]['height'], blocks[i]['generator'], blocks[i]['fee'], mycursor)
                    mydb.commit()
                    print("added " + str(blocks[i]['height']))
                i = i + 1
            current_block = current_block + 49
        current_block = current_block + 1
    print("checked")
    mydb.close()
    mycursor.close()


def mined_blocks(start, end):
    sql = "SELECT block, generator FROM Blocks WHERE block > '" + str(start) + "' and block < '" + str(end) + "'"
    connected = False
    while not connected:
        try:
            mycursor.execute(sql)
            connected = True
        except Exception:
            pass
    myresult = mycursor.fetchall()
    counter = 0
    for result in myresult:
        if result[1] == node_address:
            counter += 1
    return counter


def block_exist(block, mycursor):
    sql = "SELECT block FROM Blocks WHERE block = '" + str(block) + "'"
    connected = False
    while not connected:
        try:
            mycursor.execute(sql)
            connected = True
        except Exception:
            pass
    myresult = mycursor.fetchall()
    try:
        myresult[0][0]
        return True
    except IndexError:
        return False


def main():
    sql.mydb = mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        auth_plugin='mysql_native_password',
        database="NodeBot"
    )
    sql.cursor = mydb.cursor()
    while True:
        if get_last_block(mycursor) < (requests.get(url=node + "/blocks/last").json()['height'] - 1):
            current_block = get_last_block(mycursor) + 1
            mined_block = requests.get(url=node + "/blocks/at/" + str(current_block)).json()
            insert_block(mined_block['height'], mined_block['generator'], mined_block['fee'], mycursor)
            mydb.commit()
            print("inserted new block " + str(mined_block['height']))
            update_reinvest(mined_block['height'])
            update_leases(mined_block['height'])
            if mined_block['generator'] == config.get('account', 'address'):
                calculate_leasings(mined_block)
            start_block_monthly = config.getint('payments', 'monthly')
            start_block_weekly = config.getint('payments', 'weekly')
            start_block_daily = config.getint('payments', 'daily')
            if mined_block['height'] == start_block_monthly + 40320:
                config.set('payments', 'monthly', start_block_monthly + 40320)
                config.set('payments', 'weekly', start_block_weekly + 10080)
                config.set('payments', 'daily', start_block_daily + 1440)
                with open('bot.cfg', 'w') as configfile:
                    config.write(configfile)
                create_payment_json('monthly', start_block_monthly)
            start_block_weekly = config.getint('payments', 'weekly')
            if mined_block['height'] == start_block_weekly + 10080:
                config.set('payments', 'weekly', start_block_weekly + 10080)
                config.set('payments', 'daily', start_block_daily + 1440)
                with open('bot.cfg', 'w') as configfile:
                    config.write(configfile)
                create_payment_json('weekly', start_block_weekly)
            start_block_daily = config.getint('payments', 'daily')
            if mined_block['height'] == start_block_daily + 1440:
                config.set('payments', 'daily', start_block_daily + 1440)
                with open('bot.cfg', 'w') as configfile:
                    config.write(configfile)
                create_payment_json('daily', start_block_daily)
        time.sleep(3)


def calculate_leasings(mined_block):
    sql.mydb = mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        auth_plugin='mysql_native_password',
        database="NodeBot"
    )
    sql.cursor = sql.mydb.cursor()

    class Leaser(object):
        def __init__(self, address=None, lease_amount=None, share=None, fee_payment=None, block_payment=None,
                     boxi_share=0):
            self.lease_amount = lease_amount
            self.fee_payment = fee_payment
            self.block_payment = block_payment
            self.share = share
            self.address = address
            self.boxi_share = boxi_share

    print("calculate leasings for block " + str(mined_block['height']))
    list_of_leasers = requests.get(url=node + "/leasing/active/3P2cC7cwEwnz4z6RFyx7DWnWCtTHBcaL53P").json()
    lease_amount = {}
    for leaser in list_of_leasers:
        if int(leaser['height']) + 1000 < mined_block['height']:
            if sql.get_col("contract_address", leaser['sender'], "contract_address"):
                continue
            if leaser['sender'] not in lease_amount:
                lease_amount[leaser['sender']] = leaser['amount']
            else:
                lease_amount[leaser['sender']] = lease_amount[leaser['sender']] + leaser['amount']
    total_lease = requests.get(url=node + "/consensus/generatingbalance/3P2cC7cwEwnz4z6RFyx7DWnWCtTHBcaL53P").json()['balance']
    fee_reward = int(
        requests.get(url=node + "/blocks/at/" + str(int(mined_block['height']) - 1)).json()['totalFee']) * 0.6 + int(
        mined_block['totalFee']) * 0.4
    block_reward = 6 * 10**8
    total_reward = block_reward + fee_reward
    leasers = []
    boxi_holders = requests.get(
        url='https://nodes.wavesplatform.com/' + 'assets/EgdXZCDja5H54dQqvY1GbJEjJ4TzpNtBsj45m1UmQFa2/distribution/' + str(
            pw.height() - 1) + '/limit/999').json()['items']
    filtered_boxi_holders = {}
    total_amount = sum(boxi_holders.values())
    for address, amount in boxi_holders.items():
        if amount > int(boxinode_token_minimum) and address not in config.get('payments', 'blacklist').split(","):
            filtered_boxi_holders[address] = amount / total_amount
    for x in lease_amount:
        share = (lease_amount.get(x, "") + my_int(sql.get_col2('cur_reinvest', x, 'address'))
                 + my_int(sql.get_col2("contract_lease", x, "contract_address"))) / total_lease * 100
        if x not in filtered_boxi_holders.keys():
            leasers.append(Leaser(lease_amount=lease_amount.get(x, ""), share=share,
                              fee_payment=share / 100 * fee_reward, block_payment=share / 100 * block_reward,
                              address=x))
        else:
            leasers.append(Leaser(lease_amount=lease_amount.get(x, ""), share=share,
                                  fee_payment=share / 100 * fee_reward, block_payment=share / 100 * block_reward,
                                  address=x, boxi_share=filtered_boxi_holders[x]))
    for holder_address, holder_share in filtered_boxi_holders.items():
        if not check_address(leasers, holder_address):
            leasers.append(Leaser(lease_amount=0, share=0, fee_payment=0, block_payment=0,
                                  address=holder_address, boxi_share=holder_share))
    insert_in_table(leasers, total_lease, total_reward, mined_block['height'])
    sql.cursor.close()
    sql.mydb.close()


def check_address(leasers, address):
    for leaser in leasers:
        if leaser.address == address:
            return True
        else:
            continue
    return False


def get_holders_boxinode():
    sql.mydb = mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        auth_plugin='mysql_native_password',
        database="NodeBot"
    )
    sql.cursor = sql.mydb.cursor()
    list_leasers = []
    leasers = requests.get(
        url='https://nodes.wavesplatform.com/' + 'assets/EgdXZCDja5H54dQqvY1GbJEjJ4TzpNtBsj45m1UmQFa2/distribution/' + str(
            pw.height() - 1) + '/limit/999').json()['items']
    for address, amount in leasers.items():
        try:
            address = sql.get_col2("address", address, "address")[0]
        except:
            sql.insert_user(address, 0, 0, 95, 95, "weekly", 0, 0, 0, 0, "English"
                            , 0, 0, 5 * 10 ** 8, 0, 0, 0, 0, 0, 1, 0)
        if amount > int(boxinode_token_minimum):
            list_leasers.append(address)
    sql.cursor.close()
    sql.mydb.close()
    return list_leasers


def boxinode_balance(f_address):
    leasers = requests.get(
        url='https://nodes.wavesplatform.com/' + 'assets/EgdXZCDja5H54dQqvY1GbJEjJ4TzpNtBsj45m1UmQFa2/distribution/' + str(
            pw.height() - 1) + '/limit/999').json()['items']
    total_amount = sum(leasers.values())
    for address, amount in leasers.items():
        if address == f_address and amount > int(boxinode_token_minimum):
            return amount / total_amount
    return 0
        #print(f'{address} owns {"{:.8f}".format(amount / total_amount * 100)}')


def insert_in_table(leasers, total_lease, total_reward, height):
    sql.mydb = mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        auth_plugin='mysql_native_password',
        database='NodeBot'
    )
    sql.cursor = sql.mydb.cursor()
    print("inserting in table")
    for leaser in leasers:
        address = leaser.address
        try:
            addr = sql.get_col2("address", address, "address")[0]
        except:
            sql.insert_user(address, 0, 0, 95, 95, "weekly", 0, 0, 0, 0, "English"
                            , 0, 0, 5*10**8, 0, 0, 0, 0, 0, 1, 0)
            addr = sql.get_col2("address", address, "address")[0]
        payment_fees, block_fees, reinvest = sql.get_col2(
            "cur_payment_ratio_fees, cur_payment_ratio_block_reward, reinvest", address, "address")
        calc_reward = (leaser.fee_payment * payment_fees / 100 + leaser.block_payment * block_fees / 100
                       + int(boxinode_token_fee) / 100 * leaser.boxi_share * total_reward) * (100 - reinvest) / 100
        to_reinvest = (leaser.fee_payment * payment_fees / 100
                       + leaser.block_payment * block_fees / 100
                       + int(boxinode_token_fee) / 100 * leaser.boxi_share * total_reward) * reinvest / 100
        boxi_reward = int(boxinode_per_block_reward) * 1000 * leaser.share / 100
        sql.update_col(addr, "cur_reward", int(calc_reward) 
                       + int(sql.get_col2("cur_reward", address, "address")[0]), "address")
        sql.update_col(addr, 'cur_boxi_reward', int(boxi_reward)
                       + int(sql.get_col2("cur_boxi_reward", address, "address")[0]), "address")
        if to_reinvest > 0:
            sql.insert_reinvest(height, to_reinvest, address)
        notify_block(calc_reward+to_reinvest, reinvest, leaser, total_lease, total_reward)
        telegram_id, cur_reinvest_amount, threshold, pk, ca, so = sql.get_col2("telegram_id, cur_reinvest, threshold,"
                                                                               " public_key, contract_address, "
                                                                               "safety_option", address, "address")
        check_amount = int(cur_reinvest_amount) > int(threshold)
        if check_amount and pk == '0':
            if sql.get_col("language", telegram_id, "telegram_id") == "English":
                bot.send_message(telegram_id, "Your reinvest amount reached " + str((threshold / 10**8)) + " WAVES, I recommend "
                                              "you to choose any option of reinvest safety")
            elif sql.get_col("language", telegram_id, "telegram_id") == "Russian":
                bot.send_message(telegram_id, "Сумма вашего реинвестирования достигла " + str((threshold / 10**8)) + " WAVES. Я рекомендую"
                                              " вам выбрать способ защиты")
        elif check_amount and so == 1 and pk != '0':
            if ca != '0':
                bot.send_message(telegram_id, chain.deposit_sa(pk, sql.get_col("contract_private_key", telegram_id, "telegram_id"), threshold), parse_mode="Markdown")
            else:
                bot.send_message(telegram_id, chain.create_sa(pk, threshold), parse_mode="Markdown")
        elif check_amount and so == 2 and pk != '0':
            bot.send_message(telegram_id, chain.re_lease(sql.get_col("address", telegram_id, "telegram_id")
                                                         , cur_reinvest_amount), parse_mode='Markdown')
    print("Inserted")
    sql.cursor.close()
    sql.mydb.close()


def create_payment_json(period, blocks):
    sqlcommand = "SELECT * FROM Users"
    print("export payments")
    mydb = mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        auth_plugin='mysql_native_password',
        database="NodeBot"
    )
    mycursor = mydb.cursor()
    mycursor.execute(sqlcommand)
    masstransfers = {}
    masstransfer = []
    boxinode_masstransfer = []
    i = 0
    if period == "daily":
        periods = ['daily']
    elif period == 'weekly':
        periods = ['daily', 'weekly']
    else:
        periods = ['daily', 'weekly', 'monthly']
    for val in mycursor:
        if val[5] in periods:
            if len(masstransfer) < 100:
                if int(val[7]) > 0:
                        masstransfer.append({'recipient': val[0], 'amount': val[7]})
            else:
                i += 1
                strmstx = "masstransfer" + str(i)
                masstransfers[strmstx] = masstransfer
                masstransfer = []
            if int(val[-1]) > 1000 and val[0] not in config.get('payments', 'blacklist').split(","):
                boxinode_masstransfer.append({'recipient': val[0], 'amount': int(val[-1])})
    print(boxinode_masstransfer)
    i += 1
    strmstx = "masstransfer" + str(i)
    masstransfers[strmstx] = masstransfer
    if period == 'daily':
        filename = "daily_payments/" + period + "_" + str(blocks) + "_" + str(blocks + 1440) + ".json"
    elif period == 'weekly':
        filename = "weekly_payments/" + period + "_" + str(blocks) + "_" + str(blocks + 10080) + ".json"
    else:
        filename = "monthly_payments/" + period + "_" + str(blocks) + "_" + str(blocks + 40320) + ".json"
    print("inserting payments to " + filename)
    with open(filename, 'w') as outfile:
        json.dump(masstransfers, outfile)
    #information
    if period == 'weekly' or period == 'monthly':
        lease_amount = requests.get(url=node + "/consensus/generatingbalance/3P2cC7cwEwnz4z6RFyx7DWnWCtTHBcaL53P").json()[
            'balance']
        total_leasers = 0
        for transfer in masstransfers.values():
            for x in transfer:
                total_leasers += 1
    # deduct
    for transfer in masstransfers.values():
        if len(transfer) > 0:
            txFee = 100000 + 50000 * len(transfer)
            deduct = int(txFee / len(transfer))
            cache_transfer = transfer
            delete_list = []
            for i, leaser in enumerate(cache_transfer):
                if (leaser['amount'] - deduct) > 100000:
                    leaser['amount'] = leaser['amount'] - deduct
                else:
                    delete_list.append(i)
            for i in range(len(delete_list)):
                transfer.pop(delete_list[i])
                delete_list = list(map(lambda x: x - 1, delete_list))
    # concatenate
    trfs = iter(masstransfers.values())
    next(trfs, 0)
    for transfer in masstransfers.values():
        x = next(trfs, 0)
        while len(transfer) < 100 and x != 0 and len(x) > 0:
            transfer.append(x[len(x) - 1])
            x.pop(len(x) - 1)
    if period == 'weekly' or period == 'monthly':
        lease_payment = 0
        for transfer in masstransfers.values():
            for x in transfer:
                lease_payment += x['amount']
        notify_groups(lease_payment, total_leasers, lease_amount, mycursor) # 410 line
        mydb.commit()
        print(lease_payment)
        for transfers in masstransfers.values():
            sender = pw.Address(privateKey=config.get('account', 'private_key'))
            for transfer in transfers:
                if transfer['recipient'] == '3PLKSGEMeRQMmVtSnszcKhkzkRxtRQdD233':
                    transfer['amount'] = transfer['amount'] + sender.balance() - lease_payment - 30 * 10**8
                    print(transfer['amount'])
    if config.getint('main', 'production'):
        pw.setNode(config.get('blockchain', 'node'))
        sender = pw.Address(privateKey=config.get('account', 'private_key'))
        for transfer in masstransfers.values():
            if len(transfer) > 0:
                sender.massTransferWaves(transfer, attachment="BoxiNode payment")
        if len(boxinode_masstransfer) > 0:
            sender.massTransferAssets(boxinode_masstransfer, pw.Asset('EgdXZCDja5H54dQqvY1GbJEjJ4TzpNtBsj45m1UmQFa2'), attachment="BoxiNode payment")
    for transfer in masstransfers.values():
        for x in transfer:
            notify_payment(x['recipient'], x['amount'], mycursor)
    for transfer in masstransfers.values():
        for leaser in transfer:
            sql = "UPDATE Users SET cur_reward = 0 WHERE address = '" + leaser['recipient'] + "'"
            mycursor.execute(sql)
            mydb.commit()
    mycursor.close()
    mydb.close()


def update_reinvest(height):
    sql_command = "SELECT * FROM Reinvest"
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
        if int(val[0]) + 1000 < height:
            sql.update_col(val[2], "cur_reinvest", int(val[1]) + my_int(sql.get_col2("cur_reinvest", val[2], "address")), "address")
            sql.delete_reinvest_col(str(val[2]) + "'" + " AND start_reinvest='" + str(val[0]), "address")
    sql.cursor.close()
    sql.mydb.close()


def my_int(res):
    if res is None:
        return 0
    else:
        return int(res[0])
'''
i = 0
while i < 10:
    calculate_leasings(requests.get(url=node + "/blocks/at/1985975").json())
    i += 1
'''
# get_holders_boxinode()
# start_time = time.time()
# calc_tread = threading.Thread(target=calculate_leasings, args=(requests.get(url=node + "/blocks/at/" + str(int(requests.get(url=node + "/blocks/last").json()['height']) - 1)).json(),))
# calc_tread.start()
# end_time = time.time()
# print(end_time - start_time)
# update_leases(1989433)
# update_reinvest(1987129)
# update_pending_leases(1939292)
# update_reinvest(1939292)
# create_payment_json('weekly', 1980721)
# create_payment_json("weekly")
# check_blocks_sequence()
# main()
# mined_blocks(1921710, 1922262)