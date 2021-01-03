import requests
import pywaves as pw
import sql
import configparser
import time
import json
import datetime

config = configparser.RawConfigParser()
config.read('bot.cfg')

node_address = config.get('account', 'address')
node_private_key = config.get('account', 'private_key')
node_api = config.get('blockchain', 'node')
usdn_node_address = config.get('payments', 'usdn_node_address')
pw.setNode(node_api)


def check_usdn_payment(address, last_payments):
    txs = requests.get(node_api + "/transactions/address/" + address + "/limit/100").json()
    cur_date = datetime.datetime.now()
    counter = 0
    total_amount = 0
    for tx in txs[0]:
        if tx['sender'] == usdn_node_address:
            if counter == last_payments:
                break
            if counter == 0 and datetime.date.fromtimestamp(tx['timestamp']/1000).day == cur_date.day:
                total_amount += tx['transfers'][0]['amount']
                counter += 1
                continue
            total_amount += tx['transfers'][0]['amount']
            counter += 1
    return total_amount


def usdn_reinvest(address, amount):
    node = pw.Address(privateKey=node_private_key)
    sender = pw.Address(publicKey=sql.get_col("public_key", address, "address"))
    tx = sender.invokeScript("3PNikM6yp4NqcSU8guxQtmR5onr2D4e8yTJ", "lockNeutrino", [],
                             [{"amount": amount, "assetId": "DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p"}],
                             txFee=900000, signer=node)
    if 'error' not in tx:
        return True
    return False


def re_lease(address, amount):
    node = pw.Address(privateKey=node_private_key)
    leaser = pw.Address(publicKey=sql.get_col("public_key", address, "address"))
    tx = node.sendWaves(leaser, amount-200000)
    if 'error' not in tx:
        sql.update_col(address, "cur_reinvest", 0, "address")
        tx = leaser.lease(recipient=node, amount=amount-200000, txFee=500000, signer=node)
        if 'error' not in tx:
            if sql.get_col("language", address, "address") == "English":
                return "Successfully re-leased reinvested amount"
            else:
                return "Реинвест успешно защищён: " + tx['id']
        else:
            if sql.get_col("language", address, "address") == "English":
                return "Error during reinvest safety: " + str(tx)
            else:
                return "Ошибка при защите реинвеста " + str(tx)
    else:
        if sql.get_col("language", address, "address") == "English":
            return "Some error occurred when tried to send waves from node to you during reinvesting: " + str(tx)
        else:
            return "Возникла ошибка при защите реинвеста: " + str(tx)


def get_leasing_balance(address):
    lb = requests.get(url=node_api + '/leasing/active/' + address).json()
    if len(lb) == 0:
        return 0
    total = 0
    for x in lb:
        if x['recipient'] == node_address:
            total += x['amount']
    return total


def send_waves(recipient, amount, type):
    sa = 0 if sql.get_col("contract_address", sql.get_col("telegram_id", recipient, "address"), 'telegram_id') == '0' else pw.Address(
        address=sql.get_col("contract_address", sql.get_col("telegram_id", recipient, "address"), 'telegram_id')).balance()
    node = pw.Address(privateKey=node_private_key)
    if (type == "total" or type == "sa") and sa > 500000:
        tx = withdraw_sa(sql.get_col("public_key", recipient, "address"),
                sql.get_col("contract_private_key", recipient, "address"))
        if not tx:
            return False
    if type != "sa" and amount < 10*10**8:
        tx = node.sendWaves(recipient=pw.Address(recipient), amount=amount,
                            attachment="Withdraw leasing reward from @BoxiNodeBot")
    else:
        return False
    if "error" not in tx:
        if type == "cur_reward" or type == "total":
            sql.update_col(recipient, "cur_reward", 0, "address")
        if type == "cur_reinvest" or type == "total":
            sql.delete_reinvest_col(recipient, "address")
            sql.update_col(recipient, "cur_reinvest", 0, "address")
        return tx
    return False


def get_address(public_key):
    try:
        return pw.Address(publicKey=public_key)
    except:
        return False


def create_sa(public_key, amount):
    script_account = pw.Address()
    node = pw.Address(privateKey=node_private_key)
    script = '''{-# STDLIB_VERSION 3 #-}
    {-# CONTENT_TYPE EXPRESSION #-}
    {-# SCRIPT_TYPE ACCOUNT #-}

    let nodePublicKey = base58'G78wz69ifpAq6ALptTkPtVfbtVubeetj169dEEmsXBHH'
    let ownerPublicKey = base58''' + "'" + public_key + "'" + '''


    match (tx) {
        case ltx:LeaseTransaction|LeaseCancelTransaction =>
            sigVerify(ltx.bodyBytes, ltx.proofs[0], ownerPublicKey) || sigVerify(ltx.bodyBytes, ltx.proofs[0], nodePublicKey)
        case trtx:TransferTransaction =>
            trtx.recipient == addressFromPublicKey(ownerPublicKey) && (sigVerify(trtx.bodyBytes, trtx.proofs[0], nodePublicKey) ||  sigVerify(trtx.bodyBytes, trtx.proofs[0], ownerPublicKey))
        case _ =>
            false
     }'''
    tx = node.sendWaves(script_account, amount-100000, attachment="Deposit to Smart-Account of @BoxiNodeBot")
    if not tx or 'error' in tx:
        print(tx)
        return 'Error sending WAVES to SA' + json.dumps(tx)
    else:
        sql.update_col(public_key, "cur_reinvest", 0, "public_key")
        sql.update_col(public_key, "contract_address", script_account.address, "public_key")
        sql.update_col(public_key, "contract_private_key", script_account.privateKey, "public_key")
    i = 0
    sa = ['error']
    while 'error' in sa:
        sa = script_account.setScript(script, txFee=1000000)
        i += 1
        time.sleep(1)
        if not tx or i > 10:
            print(sa)
            return "Error while setting script: " + json.dumps(sa)
    i = 0
    tx = ['error']
    while 'error' in tx:
        tx = script_account.lease(node, script_account.balance() - 500000, signer=node, txFee=500000)
        i += 1
        time.sleep(1)
        if not tx or i > 10:
            print(tx)
            return "Error while start leasing: " + json.dumps(tx)
    if sql.get_col("language", public_key, "public_key") == "English":
        return "Successfully setup SA and start leasing, private key of SA: `" + script_account.privateKey + "`"
    return "Успешно создан Смарт-Аккаунт и начат лизинг с него, приватный ключ СА: `" + script_account.privateKey + "`"


def deposit_sa(public_key, contract_private_key, amount):
    script_account = pw.Address(privateKey=contract_private_key)
    node = pw.Address(privateKey=node_private_key)
    tx = node.sendWaves(script_account, amount-100000, attachment="Deposit to Smart-Account of @BoxiNodeBot")
    if not tx or 'error' in tx:
        print(tx)
        return 'Error sending Waves to SA: ' + json.dumps(tx)
    else:
        sql.update_col(public_key, "cur_reinvest", sql.get_col("cur_reinvest", public_key, "public_key") - amount, "public_key")
    i = 0
    tx = ['error']
    while 'error' in tx:
        tx = script_account.lease(node, script_account.balance() - 500000, signer=node, txFee=500000)
        print(tx)
        i += 1
        time.sleep(1)
        if not tx or i > 10:
            print(tx)
            return "Error starting lease: " + json.dumps(tx)
    if sql.get_col("language", public_key, "public_key") == "English":
        return "Reinvest amount successful transfer to SA and leasing started"
    return "Средства с реинвестирования успешно отправлены на СА и начат лизинг"


def withdraw_sa(public_key, contract_private_key):
    script_account = pw.Address(privateKey=contract_private_key)
    node = pw.Address(privateKey=node_private_key)
    owner = pw.Address(address=sql.get_col("address", public_key, "public_key"))
    leasings = requests.get(url=node_api + '/leasing/active/' + sql.get_col("contract_address", public_key, "public_key")).json()
    for lease in leasings:
        tx = script_account.leaseCancel(leaseId=lease['id'], signer=node, txFee=500000)
        if 'error' not in tx:
            continue
        else:
            return "Error cancel lease: " + json.dumps(tx)
    tx = ['error']
    i = 0
    while 'error' in tx:
        tx = script_account.sendWaves(owner, script_account.balance()-500000, txFee=500000, signer=node, attachment="Withdraw from Smart-Account of @BoxiNodeBot")
        i += 1
        time.sleep(1)
        if not tx or i > 10:
            print(tx)
            return "Error withdraw: " + json.dumps(tx)
    return True
