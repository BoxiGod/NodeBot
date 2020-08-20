import requests
import base58
import sql

node = 'https://nodes.wavesnodes.com'


def registration(telegram_id):
    txs = requests.get(node + '/transactions/address/3P2cC7cwEwnz4z6RFyx7DWnWCtTHBcaL53P/limit/10').json()
    for tx in txs[0]:
        if tx['type'] == 4 and tx['recipient'] == '3P2cC7cwEwnz4z6RFyx7DWnWCtTHBcaL53P':
            try:
                if int(base58.b58decode(tx['attachment'])) == telegram_id:
                    if not sql.get_col("address", tx['sender'], "address"):
                        sql.update_col(telegram_id, "address", tx['sender'], 'telegram_id')
                    else:
                        sql.update_col(tx['sender'], "telegram_id", telegram_id + telegram_id, "address")
                        sql.update_col(tx['sender'], "cur_payment_ratio_fees", 95, "address")
                        sql.update_col(tx['sender'], "cur_payment_ratio_block_reward", 95, "address")
                        sql.update_col(tx['sender'], "language",
                                       sql.get_col("language", telegram_id, "telegram_id"), "address")
                        sql.delete_col("telegram_id", telegram_id, "address", "")
                        sql.update_col(telegram_id + telegram_id, "telegram_id", telegram_id, "telegram_id")
                    return True
            except ValueError:
                print("error")
                continue
    return False
