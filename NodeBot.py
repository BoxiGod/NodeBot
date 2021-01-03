import mysql.connector
# from datetime import datetime
import telebot
# import requests
# import config
import sql
from verif import registration
import chain
import configparser
import cherrypy
# import time
import pywaves as pw

config = configparser.RawConfigParser()
config.read('bot.cfg')

user = config.get('database', 'user')
password = config.get('database', 'password')

if config.getint('main', 'production'):
    bot = telebot.TeleBot('894215970:AAHPnGjDjBKOmMxHNIZorsWWeVmEjGERdcg')
else:
    bot = telebot.TeleBot('1310913628:AAE9B0lkqEbuWjdc7DDQfXbdZyM2vm5r3dQ')

WEBHOOK_HOST = '5.189.131.138'
WEBHOOK_PORT = 443
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_SSL_CERT = 'webhook_cert.pem'
WEBHOOK_SSL_PRIV = 'webhook_pkey.pem'

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % ('')


class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                'content-type' in cherrypy.request.headers and \
                cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)


remove_keyboard = telebot.types.ReplyKeyboardRemove(selective=False)
keyboard_language = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
non_registered_keyboard_english = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
non_registered_keyboard_russian = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard_russian = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard_english = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
staking_settings_english = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
staking_settings_russian = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
payment_english = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
payment_russian = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
reinvest_safety_keyboard_russian = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
reinvest_safety_keyboard_english = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
sent_keyboard_english = telebot.types.InlineKeyboardMarkup()
sent_keyboard_russian = telebot.types.InlineKeyboardMarkup()
choose_period_russian = telebot.types.InlineKeyboardMarkup()
choose_period_english = telebot.types.InlineKeyboardMarkup()
withd_leas_english = telebot.types.InlineKeyboardMarkup()
withd_leas_russian = telebot.types.InlineKeyboardMarkup()
withd_sa_english = telebot.types.InlineKeyboardMarkup()
withd_sa_russian = telebot.types.InlineKeyboardMarkup()
withd_total_english = telebot.types.InlineKeyboardMarkup()
withd_total_russian = telebot.types.InlineKeyboardMarkup()
withd_reinvest_english = telebot.types.InlineKeyboardMarkup()
withd_reinvest_russian = telebot.types.InlineKeyboardMarkup()
restaking_russian = telebot.types.InlineKeyboardMarkup()
restaking_english = telebot.types.InlineKeyboardMarkup()
markup = telebot.types.ForceReply(selective=False)

key_russian = telebot.types.KeyboardButton(text='English')
key_english = telebot.types.KeyboardButton(text='Русский')
key_register_english = telebot.types.KeyboardButton(text='Register')
key_register_russian = telebot.types.KeyboardButton(text='Регистрация')
key_withd_lease_yes_english = telebot.types.InlineKeyboardButton(text='Yes', callback_data="withd_leas_yes_eng")
key_reinv_bal_yes_english = telebot.types.InlineKeyboardButton(text='Yes', callback_data="reinv_bal_yes_eng")
key_sa_yes_english = telebot.types.InlineKeyboardButton(text='Yes', callback_data="withd_sa_yes_eng")
key_total_yes_english = telebot.types.InlineKeyboardButton(text='Yes', callback_data="withd_total_yes_eng")
key_reinv_bal_no_english = telebot.types.InlineKeyboardButton(text='No', callback_data="reinv_bal_no_eng")
key_withd_lease_no_english = telebot.types.InlineKeyboardButton(text='No', callback_data="withd_leas_no_eng")
key_sa_no_english = telebot.types.InlineKeyboardButton(text='No', callback_data="reinv_sa_no_eng")
key_total_no_english = telebot.types.InlineKeyboardButton(text='No', callback_data="withd_total_no_eng")
key_withd_lease_yes_russian = telebot.types.InlineKeyboardButton(text='Да', callback_data="withd_leas_yes_rus")
key_reinv_bal_yes_russian = telebot.types.InlineKeyboardButton(text='Да', callback_data="reinv_bal_yes_rus")
key_sa_yes_russian = telebot.types.InlineKeyboardButton(text='Да', callback_data="withd_sa_yes_rus")
key_total_yes_russian = telebot.types.InlineKeyboardButton(text='Да', callback_data="withd_total_yes_rus")
key_reinv_bal_no_russian = telebot.types.InlineKeyboardButton(text='Нет', callback_data="reinv_bal_no_rus")
key_withd_lease_no_russian = telebot.types.InlineKeyboardButton(text='Нет', callback_data="withd_leas_no_rus")
key_sa_no_russian = telebot.types.InlineKeyboardButton(text='Нет', callback_data="reinv_sa_no_rus")
key_total_no_russian = telebot.types.InlineKeyboardButton(text='Нет', callback_data="withd_total_no_rus")
key_sent_english = telebot.types.InlineKeyboardButton(text='Sent', callback_data="sent")
key_sent_russian = telebot.types.InlineKeyboardButton(text='Отправил', callback_data="sent_rus")
key_daily_russian = telebot.types.InlineKeyboardButton(text='Раз в день', callback_data="daily_rus")
key_weekly_russian = telebot.types.InlineKeyboardButton(text='Раз в неделю', callback_data="weekly_rus")
key_monthly_russian = telebot.types.InlineKeyboardButton(text='Раз в месяц', callback_data="monthly_rus")
key_daily_english = telebot.types.InlineKeyboardButton(text='Once a day', callback_data="daily_eng")
key_weekly_english = telebot.types.InlineKeyboardButton(text='Once a week', callback_data="weekly_eng")
key_monthly_english = telebot.types.InlineKeyboardButton(text='Once a month', callback_data="monthly_eng")
key_check_main_staking_information_russian = telebot.types.KeyboardButton(text='Информация по лизингу')
key_check_main_staking_information_english = telebot.types.KeyboardButton(text='staking information')
key_payment_period_russian = telebot.types.KeyboardButton(text='Частота выплат')
key_payment_period_english = telebot.types.KeyboardButton(text='Payment period')
key_reinvest_russian = telebot.types.KeyboardButton(text='Реинвестирование')
key_reinvest_english = telebot.types.KeyboardButton(text='Reinvest')
key_staking_settings_russian = telebot.types.KeyboardButton(text='Настройки выплат')
key_staking_settings_english = telebot.types.KeyboardButton(text='Payment settings')
key_back_english = telebot.types.KeyboardButton(text='Back')
key_back_russian = telebot.types.KeyboardButton(text='Назад')
key_withdraw_reward_russian = telebot.types.KeyboardButton(text='Награду за лизинг')
key_withdraw_reward_english = telebot.types.KeyboardButton(text='staking reward')
key_withdraw_reinvest_russian = telebot.types.KeyboardButton(text='Реинвестированное')
key_withdraw_reinvest_english = telebot.types.KeyboardButton(text='Reinvest balance')
key_withdraw_sa_russian = telebot.types.KeyboardButton(text='Смарт-Аккаунт')
key_withdraw_sa_english = telebot.types.KeyboardButton(text='Smart-Account')
key_withdraw_total_russian = telebot.types.KeyboardButton(text='Всё')
key_withdraw_total_english = telebot.types.KeyboardButton(text='Total')
key_payment_english = telebot.types.KeyboardButton(text='Immediate withdraw')
key_payment_russian = telebot.types.KeyboardButton(text='Мгновенный вывод')
key_reinvest_safety_english = telebot.types.KeyboardButton(text='Reinvest safety')
key_reinvest_safety_russian = telebot.types.KeyboardButton(text='Защита реинвеста')
key_info_reinvest_safety_russian = telebot.types.KeyboardButton(text='Информация')
key_info_reinvest_safety_english = telebot.types.KeyboardButton(text='Information')
key_reinvest_threshold_russian = telebot.types.KeyboardButton(text='Порог WAVES')
key_reinvest_threshold_english = telebot.types.KeyboardButton(text='WAVES threshold')
key_security_setup_russian = telebot.types.KeyboardButton(text='Установка безопасности')
key_security_setup_english = telebot.types.KeyboardButton(text='Security setup')
key_usdn_staking_russian = telebot.types.KeyboardButton(text="USDN рестейкинг")
key_usdn_staking_english = telebot.types.KeyboardButton(text="USDN re-staking")
key_usdn_yes_russian = telebot.types.InlineKeyboardButton(text='Да', callback_data="yes_usdn")
key_usdn_no_russian = telebot.types.InlineKeyboardButton(text='Нет', callback_data="no_usdn")
key_usdn_yes_english = telebot.types.InlineKeyboardButton(text='Yes', callback_data="yes_usdn")
key_usdn_no_english = telebot.types.InlineKeyboardButton(text='No', callback_data="no_usdn")

staking_settings_english.add(key_payment_period_english, key_reinvest_english)
staking_settings_english.add(key_back_english)
staking_settings_russian.add(key_payment_period_russian, key_reinvest_russian)
staking_settings_russian.add(key_back_russian)
reinvest_safety_keyboard_russian.add(key_info_reinvest_safety_russian, key_reinvest_threshold_russian)
reinvest_safety_keyboard_russian.add(key_security_setup_russian, key_usdn_staking_russian)
reinvest_safety_keyboard_russian.add(key_back_russian)
reinvest_safety_keyboard_english.add(key_info_reinvest_safety_english, key_reinvest_threshold_english)
reinvest_safety_keyboard_english.add(key_security_setup_english, key_usdn_staking_english)
reinvest_safety_keyboard_english.add(key_back_english)
choose_period_russian.add(key_daily_russian, key_weekly_russian)
choose_period_russian.add(key_monthly_russian)
choose_period_english.add(key_daily_english, key_weekly_english)
choose_period_english.add(key_monthly_english)
non_registered_keyboard_russian.add(key_register_russian)
non_registered_keyboard_english.add(key_register_english)
keyboard_language.add(key_english, key_russian)
sent_keyboard_english.add(key_sent_english)
sent_keyboard_russian.add(key_sent_russian)
main_keyboard_russian.add(key_check_main_staking_information_russian, key_staking_settings_russian)
main_keyboard_russian.add(key_payment_russian, key_reinvest_safety_russian)
main_keyboard_english.add(key_check_main_staking_information_english, key_staking_settings_english)
main_keyboard_english.add(key_payment_english, key_reinvest_safety_english)
payment_english.add(key_withdraw_reinvest_english, key_withdraw_reward_english)
payment_english.add(key_withdraw_sa_english, key_withdraw_total_english)
payment_english.add(key_back_english)
payment_russian.add(key_withdraw_reinvest_russian, key_withdraw_reward_russian)
payment_russian.add(key_withdraw_sa_russian, key_withdraw_total_russian)
payment_russian.add(key_back_russian)
withd_leas_english.add(key_withd_lease_yes_english, key_withd_lease_no_english)
withd_leas_russian.add(key_withd_lease_yes_russian, key_withd_lease_no_russian)
withd_sa_english.add(key_sa_yes_english, key_sa_no_english)
withd_sa_russian.add(key_sa_yes_russian, key_sa_no_russian)
withd_total_english.add(key_total_yes_english, key_total_no_english)
withd_total_russian.add(key_total_yes_russian, key_total_no_russian)
withd_reinvest_english.add(key_reinv_bal_yes_english, key_reinv_bal_no_english)
withd_reinvest_russian.add(key_reinv_bal_yes_russian, key_reinv_bal_no_russian)
restaking_russian.add(key_usdn_yes_russian, key_usdn_no_russian)
restaking_english.add(key_usdn_yes_english, key_usdn_no_english)


def check_language(telegram_id):
    if sql.get_col("language", telegram_id, "telegram_id") == "Russian":
        return True
    else:
        return False


def registered(telegram_id):
    if sql.get_col('Address', telegram_id, 'telegram_id') and sql.get_col('telegram_id', telegram_id, 'telegram_id'):
        return True
    return False


def translate(period):
    if period == 'weekly':
        return 'раз в неделю'
    if period == 'daily':
        return 'раз в день'
    if period == 'monthly':
        return 'раз в месяц'


def process_reinvest_security_step(message):
    sql.mydb = mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        auth_plugin='mysql_native_password',
        database='NodeBot'
    )
    sql.cursor = sql.mydb.cursor()
    if message.text == "0":
        if sql.get_col("language", message.chat.id, "telegram_id") == "Russian":
            bot.send_message(message.chat.id, "Вы отменили изменение", reply_markup=reinvest_safety_keyboard_russian)
        else:
            bot.send_message(message.chat.id, "You canceled changes", reply_markup=reinvest_safety_keyboard_english)
        return
    elif message.text == '1':
        sql.update_col(message.chat.id, 'safety_option', 1, 'telegram_id')
        if sql.get_col("language", message.chat.id, "telegram_id") == "Russian":
            if not sql.get_col("public_key", message.chat.id, "telegram_id"):
                msg = bot.send_message(message.chat.id, "Вы выбрали первый способ реинвестирования,"
                                                        " укажите ваш публичный ключ ниже:")
                bot.register_next_step_handler(msg, process_public_key_step)
            else:
                bot.send_message(message.chat.id, "Вы выбрали первый способ реинвестирования.", reply_markup=main_keyboard_russian)
        else:
            if not sql.get_col("public_key", message.chat.id, "telegram_id"):
                msg = bot.send_message(message.chat.id, "You chose first method of reinvest, write "
                                                        "your public key below please:")
                bot.register_next_step_handler(msg, process_public_key_step)
            else:
                bot.send_message(message.chat.id, "You chose first method of reinvest.", reply_markup=main_keyboard_english)
    elif message.text == '2':
        sql.update_col(message.chat.id, 'safety_option', 2, 'telegram_id')
        script = '''`{-# STDLIB_VERSION 3 #-}
        {-# CONTENT_TYPE EXPRESSION #-}
        {-# SCRIPT_TYPE ACCOUNT #-}

        let nodePublicKey = base58'G78wz69ifpAq6ALptTkPtVfbtVubeetj169dEEmsXBHH'


        match (tx) {
            case ltx:LeaseTransaction|LeaseCancelTransaction =>
                sigVerify(ltx.bodyBytes, ltx.proofs[0], nodePublicKey) || sigVerify(ltx.bodyBytes, ltx.proofs[0], ltx.senderPublicKey)
            case _ => sigVerify(tx.bodyBytes, tx.proofs[0], tx.senderPublicKey)
        }`
        '''
        if sql.get_col("language", message.chat.id, "telegram_id") == "Russian":
            bot.send_message(message.chat.id, "Вы выбрали второй способ реинвестирования, вам "
                                              "нужно установить следующий скрипт на ваш аккаунт:")
        else:
            bot.send_message(message.chat.id, "You chose second method of reinvest, "
                                              "you need to setup following script to your account:")
        bot.send_message(message.chat.id, script, parse_mode='Markdown')
        if sql.get_col("language", message.chat.id, "telegram_id") == "Russian":
            msg = bot.send_message(message.chat.id, "Заключительный шаг - установка вашего публичного ключа:")
        else:
            msg = bot.send_message(message.chat.id, "And final step - you need to setup your public key:")
        bot.register_next_step_handler(msg, process_public_key_step)
    else:
        if sql.get_col("language", message.chat.id, "telegram_id") == "Russian":
            bot.send_message(message.chat.id, "Вы отменили изменение", reply_markup=reinvest_safety_keyboard_russian)
        else:
            bot.send_message(message.chat.id, "You canceled the changes", reply_markup=reinvest_safety_keyboard_english)
    sql.cursor.close()
    sql.mydb.close()


def process_public_key_step(message):
    sql.mydb = mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        auth_plugin='mysql_native_password',
        database='NodeBot'
    )
    sql.cursor = sql.mydb.cursor()
    if message.text == "0":
        if sql.get_col("language", message.chat.id, "telegram_id") == "Russian":
            bot.send_message(message.chat.id, "Вы отменили изменения", reply_markup=reinvest_safety_keyboard_russian)
        if sql.get_col("language", message.chat.id, "telegram_id") == "English":
            bot.send_message(message.chat.id, "You canceled changes" + str(int(message.text))
                             + " WAVES ", reply_markup=reinvest_safety_keyboard_english)
        return
    address = chain.get_address(message.text)
    if address:
        pass
    else:
        if sql.get_col("language", message.chat.id, "telegram_id") == "English":
            bot.send_message(message.chat.id, "Please enter valid public key!",
                             reply_markup=reinvest_safety_keyboard_english)
            return
        else:
            bot.send_message(message.chat.id, "Пожалуйста, вводите валидный публичный ключ!",
                             reply_markup=reinvest_safety_keyboard_russian)
            return
    if sql.get_col("address", message.chat.id, "telegram_id") == address.address:
        sql.update_col(message.chat.id, 'public_key', message.text, 'telegram_id')
        if sql.get_col("language", message.chat.id, "telegram_id") == "Russian":
            bot.send_message(message.chat.id, "Вы установили, что ваш публичный ключ,: "
                                              "" + message.text, reply_markup=reinvest_safety_keyboard_russian)
        else:
            bot.send_message(message.chat.id, "You set up your public key: " + message.text
                             , reply_markup=reinvest_safety_keyboard_english)
    else:
        if sql.get_col("language", message.chat.id, "telegram_id") == "Russian":
            bot.send_message(message.chat.id, "Этот публичный ключ не от вашего адреса: " +
                             sql.get_col("address", message.chat.id, "telegram_id")
                             , reply_markup=reinvest_safety_keyboard_russian)
        else:
            bot.send_message(message.chat.id, "This public key doesn't belong to your address: "
                             + sql.get_col("address", message.chat.id, "telegram_id")
                             , reply_markup=reinvest_safety_keyboard_english)
    sql.cursor.close()
    sql.mydb.close()


def process_threshold_step(message):
    sql.mydb = mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        auth_plugin='mysql_native_password',
        database='NodeBot'
    )
    sql.cursor = sql.mydb.cursor()
    if message.text == "0":
        if sql.get_col("language", message.chat.id, "telegram_id") == "Russian":
            bot.send_message(message.chat.id, "Вы отменили изменения", reply_markup=reinvest_safety_keyboard_russian)
        else:
            bot.send_message(message.chat.id, "You canceled changes" + str(int(message.text))
                             + " WAVES ", reply_markup=reinvest_safety_keyboard_english)
        return
    if message.text.isnumeric():
        sql.update_col(message.chat.id, 'threshold', int(message.text) * 10**8, 'telegram_id')
        if sql.get_col("language", message.chat.id, "telegram_id") == "Russian":
            bot.send_message(message.chat.id, "Вы выбрали, что WAVES безопасно реинвестируются при "
                                              "достижении " + str(int(message.text))
                                              + " WAVES в реинвестировании",
                             reply_markup=reinvest_safety_keyboard_russian)
        else:
            bot.send_message(message.chat.id, "You chose resend WAVES to reinvest as "
                                              "only reinvest amount reached " + str(int(message.text))
                                              + " WAVES ", reply_markup=reinvest_safety_keyboard_english)
    else:
        if sql.get_col("language", message.chat.id, "telegram_id") == "Russian":
            bot.send_message(message.chat.id, "Вы отменили изменение", reply_markup=reinvest_safety_keyboard_russian)
        else:
            bot.send_message(message.chat.id, "You canceled the changes", reply_markup=reinvest_safety_keyboard_english)
    sql.cursor.close()
    sql.mydb.close()


def days_usdn_staking(message):
    sql.mydb = mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        auth_plugin='mysql_native_password',
        database='NodeBot'
    )
    sql.cursor = sql.mydb.cursor()
    if message.text == "0":
        if sql.get_col("language", message.chat.id, "telegram_id") == "Russian":
            bot.send_message(message.chat.id, "Вы отменили изменения", reply_markup=reinvest_safety_keyboard_russian)
        else:
            bot.send_message(message.chat.id, "You canceled changes" + str(int(message.text))
                             + " WAVES ", reply_markup=reinvest_safety_keyboard_english)
        return
    if message.text.isnumeric():
        if not sql.get_col("address", sql.get_col("address", message.chat.id, "telegram_id"),
                           "address", table="USDN_Staking"):
            sql.insert_usdn_staking(sql.get_col("address", message.chat.id, "telegram_id"), period_days=message.text)
        if sql.get_col("language", message.chat.id, "telegram_id") == "Russian":
            bot.send_message(message.chat.id, "Вы выбрали, что USDN ре-стейкается раз в "
                             + str(int(message.text)) + "(дни)", reply_markup=reinvest_safety_keyboard_russian)
        else:
            bot.send_message(message.chat.id, "You chose that USDN will be re-staking once a "
                             + str(int(message.text)) + "(days)", reply_markup=reinvest_safety_keyboard_english)

    else:
        if check_language(message.chat.id):
            bot.send_message(message.chat.id, "Вы отменили изменение", reply_markup=reinvest_safety_keyboard_russian)
        else:
            bot.send_message(message.chat.id, "You canceled the changes", reply_markup=reinvest_safety_keyboard_english)
    if check_language(message.chat.id):
        if sql.get_col("public_key", message.chat.id, "telegram_id") == '0':
            msg = bot.send_message(message.chat.id, "Заключительный шаг - укажите ваш "
                                                    "публичный ключ ниже:", reply_markup=markup)
            bot.register_next_step_handler(msg, process_public_key_step)
    else:
        if sql.get_col("public_key", message.chat.id, "telegram_id") == '0':
            msg = bot.send_message(message.chat.id, "Final step - provide public key from your account:", reply_markup=markup)
            bot.register_next_step_handler(msg, process_public_key_step)
    sql.cursor.close()
    sql.mydb.close()


def process_reinvest_step(message):
    sql.mydb = mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        auth_plugin='mysql_native_password',
        database='NodeBot'
    )
    sql.cursor = sql.mydb.cursor()
    if message.text.isnumeric():
        if 100 >= int(message.text) >= 0:
            sql.update_col(message.chat.id, 'reinvest', message.text, 'telegram_id')
            if sql.get_col("language", message.chat.id, "telegram_id") == "Russian":
                bot.send_message(message.chat.id, "Вы выбрали " + message.text
                                 + "% реинвестировать в лизинг", reply_markup=staking_settings_russian)
            if sql.get_col("language", message.chat.id, "telegram_id") == "English":
                bot.send_message(message.chat.id, "You chose " + message.text
                                 + "% reinvest in staking", reply_markup=staking_settings_english)
        else:
            if sql.get_col("language", message.chat.id, "telegram_id") == "Russian":
                bot.send_message(message.chat.id, "Введите число больше 0 и меньше 100", reply_markup=markup)
            else:
                bot.send_message(message.chat.id, "Enter the number between 0 and 100",
                                 reply_markup=markup)
            bot.register_next_step_handler(message, process_reinvest_step)
    else:
        if sql.get_col("language", message.chat.id, "telegram_id") == "Russian":
            bot.send_message(message.chat.id, "Вы отменили изменение", reply_markup=staking_settings_russian)
        else:
            bot.send_message(message.chat.id, "You canceled the changes", reply_markup=staking_settings_english)
    sql.cursor.close()
    sql.mydb.close()


def reinvest_sum(address):
    sql_command = "SELECT * FROM Reinvest"
    sql.cursor = sql.mydb.cursor()
    my_cursor = sql.mydb.cursor()
    my_cursor.execute(sql_command)
    adr_sum = 0
    for val in my_cursor.fetchall():
        if val[2] == address:
            adr_sum += val[1]
    return adr_sum


@bot.message_handler(commands=['start', 'register'])
def start_message(message):
    if message.chat.id < 0:
        return
    sql.mydb = mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        auth_plugin='mysql_native_password',
        database='NodeBot'
    )
    sql.cursor = sql.mydb.cursor()
    if message.text == '/register':
        if sql.get_col("language", message.chat.id, "telegram_id") == "English":
            bot.send_message(message.chat.id, "To register in bot send any transaction to "
                                              "\n`3P2cC7cwEwnz4z6RFyx7DWnWCtTHBcaL53P`\n\nIn description "
                                              "write: "
                                              "\n`" + str(message.chat.id) +
                             "`\n\nAs only you will send, "
                             "press "
                             "button 'Sent'", reply_markup=sent_keyboard_english, parse_mode='Markdown')
            return
        else:
            bot.send_message(message.chat.id, "Для регистрации отправьте любую транзакцию на адрес "
                                              "\n`3P2cC7cwEwnz4z6RFyx7DWnWCtTHBcaL53P`\n\nВ описании "
                                              "транзакции укажите: \n`"
                                              "" + str(message.chat.id) +
                             "`\n\nКак только отправите, "
                             "нажмите кнопку 'отправил'"
                             "", reply_markup=sent_keyboard_russian, parse_mode='Markdown')
            return
    if not sql.get_col("telegram_id", message.chat.id, 'telegram_id'):
        bot.send_message(message.chat.id, "Hi! Firstly choose your language by pressing button below:\n"
                                          "Привет! Для начала выбери язык бота, нажав "
                                          "на кнопку снизу: ", reply_markup=keyboard_language)
    elif sql.get_col('Address', message.chat.id, "telegram_id"):
        if sql.get_col("language", message.chat.id, "telegram_id") == "English":
            bot.send_message(message.chat.id, "Menu", reply_markup=main_keyboard_english)
        else:
            bot.send_message(message.chat.id, "Меню", reply_markup=main_keyboard_russian)
    elif sql.get_col("language", message.chat.id, "telegram_id") == "English":
        bot.send_message(message.chat.id, "Welcome! Firstly I recommend to "
                                          "register with /register command",
                         reply_markup=main_keyboard_english, parse_mode='Markdown')
    elif sql.get_col("language", message.chat.id, "telegram_id") == "Russian":
        bot.send_message(message.chat.id, "Добро пожаловать! Для начала я "
                                          "рекомендую зарегестрироваться с командой /register",
                         reply_markup=main_keyboard_russian, parse_mode='Markdown')
    sql.cursor.close()
    sql.mydb.close()


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    sql.mydb = mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        auth_plugin='mysql_native_password',
        database='NodeBot'
    )
    sql.cursor = sql.mydb.cursor()
    telegram_id = call.message.chat.id
    bot.delete_message(telegram_id, call.message.message_id)
    if call.data == "sent":
        if registration(telegram_id):
            bot.send_message(telegram_id, "You registered. \nPayments by default: "
                                                   "95% from block fee, 95% from block "
                                                   "reward, weekly\nstaking address: "
                                                   "`3P2cC7cwEwnz4z6RFyx7DWnWCtTHBcaL53P` "
                                                   "or alias: `boxinode`", reply_markup=main_keyboard_english, parse_mode='Markdown')
        else:
            bot.send_message(telegram_id, "Transaction not found, "
                                                   "try again", reply_markup=sent_keyboard_english)
    if call.data == "sent_rus":
        if registration(telegram_id):
            bot.send_message(telegram_id, "Вы зарегестрированы. \nВаши выплаты по умолчанию: "
                                                   "95% от комисии, 95% от награды "
                                                   "за блок, еженедельная\nАдрес для лизинга: "
                                                   "`3P2cC7cwEwnz4z6RFyx7DWnWCtTHBcaL53P` или алиас: `boxinode`"
                                                   "", reply_markup=main_keyboard_russian, parse_mode='Markdown')
        else:
            bot.send_message(telegram_id, "Транзакция не найдена, "
                                          "попробуйте снова", reply_markup=sent_keyboard_russian)
    if call.data == "no_usdn":
        if check_language(telegram_id):
            bot.send_message(telegram_id, "Отмена", reply_markup=main_keyboard_russian)
        else:
            bot.send_message(telegram_id, "Cancel", reply_markup=main_keyboard_english)
    if call.data == "yes_usdn":
        if not sql.get_col("address", telegram_id, "telegram_id"):
            if not check_language(telegram_id):
                bot.send_message(telegram_id, "Fitstly you need to /register", reply_markup=main_keyboard_english)
                return
            else:
                bot.send_message(telegram_id, "Сначала нужно зарегестрироваться: /register", reply_markup=main_keyboard_russian)
                return
        script = '''{-# STDLIB_VERSION 3 #-}
{-# CONTENT_TYPE EXPRESSION #-}
{-# SCRIPT_TYPE ACCOUNT #-}

let dappFunc = "lockNeutrino"
let dappAddress = "3PNikM6yp4NqcSU8guxQtmR5onr2D4e8yTJ"
let botPublicKey = base58'G78wz69ifpAq6ALptTkPtVfbtVubeetj169dEEmsXBHH'

match (tx) {
    case i:InvokeScriptTransaction =>
        sigVerify(tx.bodyBytes, tx.proofs[0], tx.senderPublicKey) || {
            let rightInvoke = (
                i.function == dappFunc
                && addressFromRecipient(i.dApp) == addressFromString(dappAddress)
            )
            rightInvoke && sigVerify(tx.bodyBytes, tx.proofs[0], botPublicKey) 
        }
    case _ => sigVerify(tx.bodyBytes, tx.proofs[0], tx.senderPublicKey)
}'''
        if check_language(telegram_id):
            bot.send_message(telegram_id, "Вам нужно установить следующий скрипт на ваш аккаунт:")
            bot.send_message(telegram_id, script)
            msg = bot.send_message(telegram_id, "Как часто хотите рестейкать? Введите число(дни): ", reply_markup=markup)
            bot.register_next_step_handler(msg, days_usdn_staking)
        else:
            bot.send_message(telegram_id, "You need to setup following script to your account:", reply_markup=markup)
            bot.send_message(telegram_id, script)
            msg = bot.send_message(telegram_id, "How often do you want to re-stake?(days): ", reply_markup=markup)
            bot.register_next_step_handler(msg, days_usdn_staking)
    if call.data == "withd_leas_yes_eng" or call.data == "withd_leas_yes_rus":
        tx = chain.send_waves(sql.get_col("address", telegram_id, "telegram_id"),
                              sql.get_col("cur_reward", telegram_id, "telegram_id") - 200000, "cur_reward")
        if tx and sql.get_col("language", telegram_id, "telegram_id") == "English":
            bot.send_message(telegram_id, "Payment done, tx id = `" + tx['id'] + "`",
                             reply_markup=main_keyboard_english, parse_mode='Markdown')
        elif tx and sql.get_col("language", telegram_id, "telegram_id") == "Russian":
            bot.send_message(telegram_id, "Выплата сделана, id транзакции = `" + tx['id'] + "`",
                             reply_markup=main_keyboard_russian, parse_mode='Markdown')
        else:
            bot.send_message(telegram_id, "Some error occured, please contact admin @BoxiGod",
                             reply_markup=main_keyboard_russian, parse_mode='Markdown')
    if call.data == "withd_total_yes_eng" or call.data == "withd_total_yes_rus":
        tx = chain.send_waves(sql.get_col("address", telegram_id, "telegram_id"),
                              sql.get_col("cur_reinvest", telegram_id, "telegram_id") + reinvest_sum(
                                  sql.get_col("address", telegram_id, 'telegram_id')) +
                              sql.get_col("cur_reward", telegram_id, "telegram_id") - 200000, "total")
        if tx and sql.get_col("language", telegram_id, "telegram_id") == "English":
            bot.send_message(telegram_id, "Payment done, tx id = `" + tx['id'] + "`",
                             reply_markup=main_keyboard_english, parse_mode='Markdown')
        elif tx and sql.get_col("language", telegram_id, "telegram_id") == "Russian":
            bot.send_message(telegram_id, "Выплата сделана, id транзакции = `" + tx['id'] + "`",
                             reply_markup=main_keyboard_russian, parse_mode='Markdown')
    if call.data == "withd_sa_yes_eng" or call.data == "withd_sa_yes_rus":
        tx = chain.send_waves(sql.get_col("address", telegram_id, "telegram_id"),
                              0, "sa")
        if tx and sql.get_col("language", telegram_id, "telegram_id") == "English":
            bot.send_message(telegram_id, "Succesfully canceled all staking and withdraw from SA",
                             reply_markup=main_keyboard_english, parse_mode='Markdown')
        elif tx and sql.get_col("language", telegram_id, "telegram_id") == "Russian":
            bot.send_message(telegram_id, "Успешно отменены все лизинги и выведены средства с СА",
                             reply_markup=main_keyboard_russian, parse_mode='Markdown')
    if call.data == "reinv_bal_yes_eng" or call.data == "reinv_bal_yes_rus":
        tx = chain.send_waves(sql.get_col("address", telegram_id, "telegram_id"),
                              sql.get_col("cur_reinvest", telegram_id, "telegram_id") + reinvest_sum(
                sql.get_col("address", telegram_id, 'telegram_id')) - 200000, "cur_reinvest")
        if tx and sql.get_col("language", telegram_id, "telegram_id") == "English":
            bot.send_message(telegram_id, "Payment done, tx id = `" + tx['id'] + "`",
                             reply_markup=main_keyboard_english, parse_mode='Markdown')
        elif tx and sql.get_col("language", telegram_id, "telegram_id") == "Russian":
            bot.send_message(telegram_id, "Выплата сделана, id транзакции = `" + tx['id'] + "`",
                             reply_markup=main_keyboard_russian, parse_mode='Markdown')
    if "_no_" in call.data:
        if sql.get_col("language", telegram_id, "telegram_id") == "English":
            bot.send_message(telegram_id, "You canceled the withdraw",
                             reply_markup=main_keyboard_english, parse_mode='Markdown')
        else:
            bot.send_message(telegram_id, "Вы отменили вывод",
                             reply_markup=main_keyboard_russian, parse_mode='Markdown')
    if call.data == "daily_rus":
        sql.update_col(telegram_id, 'payment_period', 'daily', "telegram_id")
        bot.send_message(telegram_id, "Вы выбрали ежедневную выплату", reply_markup=staking_settings_russian)
    if call.data == "weekly_rus":
        sql.update_col(telegram_id, 'payment_period', 'weekly', "telegram_id")
        bot.send_message(telegram_id, "Вы выбрали еженедельную выплату", reply_markup=staking_settings_russian)
    if call.data == "monthly_rus":
        sql.update_col(telegram_id, 'payment_period', 'monthly', "telegram_id")
        bot.send_message(telegram_id, "Вы выбрали ежемесячную выплату", reply_markup=staking_settings_russian)
    if call.data == "daily_eng":
        sql.update_col(telegram_id, 'payment_period', 'daily', "telegram_id")
        bot.send_message(telegram_id, "You chose daily payment", reply_markup=staking_settings_english)
    if call.data == "weekly_eng":
        sql.update_col(telegram_id, 'payment_period', 'weekly', "telegram_id")
        bot.send_message(telegram_id, "You chose weekly payment", reply_markup=staking_settings_english)
    if call.data == "monthly_eng":
        sql.update_col(telegram_id, 'payment_period', 'monthly', "telegram_id")
        bot.send_message(telegram_id, "You chose monthly payment", reply_markup=staking_settings_english)
    sql.cursor.close()
    sql.mydb.close()


@bot.message_handler(content_types=['text'])
def begin(message):
    if message.chat.id < 0:
        return
    sql.mydb = mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        auth_plugin='mysql_native_password',
        database='NodeBot'
    )
    sql.cursor = sql.mydb.cursor()
    if not sql.get_col("telegram_id", message.chat.id, 'telegram_id'):
        if message.text.lower() == "русский":
            sql.insert_user("", 0, 0, 95, 95, "weekly", 0, 0, 0, 0, "Russian"
                            , message.chat.id, 0, 5*10**8, 0, 0, 0, 0, 0, 1, 0)
            bot.send_message(message.chat.id, "Вы выбрали русский язык", reply_markup=remove_keyboard)
            bot.send_message(message.chat.id, "Для просмотра своего баланса и управления выплатами "
                                              "вам нужно будет зарегистрироваться, "
                                              "сделать это можно по "
                                              "команде /register", reply_markup=main_keyboard_russian)
        elif message.text.lower() == "english":
            sql.insert_user("", 0, 0, 95, 95, "weekly", 0, 0, 0, 0, "English"
                            , message.chat.id, 0, 5*10**8, 0, 0, 0, 0, 0, 1, 0)
            bot.send_message(message.chat.id, "You chose English language", reply_markup=remove_keyboard)
            bot.send_message(message.chat.id, "To look your balance and manage your payments "
                                              ", you will need to register, you c"
                                              "an do it via /register command", reply_markup=main_keyboard_english)
        else:
            bot.send_message(message.chat.id, "Hi! Firstly choose your language by pressing button below:\n"
                                              "Привет! Для начала выбери язык бота, нажав "
                                              "на кнопку снизу: ", reply_markup=keyboard_language)
    else:
        step = sql.get_col('step', message.chat.id, "telegram_id")
        config.read('bot.cfg')
        if message.text.lower() == "информация по лизингу":
            # TODO add year yield
            height = chain.pw.height()
            payment_period = sql.get_col('payment_period', message.chat.id, 'telegram_id')
            pl = sql.get_col("pendingLease", message.chat.id, "telegram_id")
            pr = sql.get_reinvest_col("amount_reinvest", sql.get_col("address", message.chat.id, 'telegram_id'), "address")
            clb = sql.get_col("contract_lease", message.chat.id, "telegram_id")
            cplb1 = sql.get_col("contract_pending_lease", message.chat.id, "telegram_id")
            cplb2 = " " if cplb1 == 0 else "(" + str(cplb1 / 10**8) + " WAVES)"
            pending_lease = " " if pl == 0 else "(" + str('{:.8f}'.format(pl / 10**8)) + ") "
            pending_reinvest = " " if not pr else "(" + str('{:.8f}'.format(sum(map(sum, pr)) / 10**8)) + ") "
            next_payment_in = config.getint('payments', 'daily') + 1440 - height if payment_period == 'daily' else config.getint('payments', 'weekly') + 10800 - height if payment_period == 'weekly' else config.getint('payments', 'monthly') + 43200 - height
            sa_balance = " " if clb == 0 and cplb1 == 0 else "\nБаланс СА: *" + str(clb / 10 ** 8) + " WAVES*" + cplb2
            g_address = sql.get_col("address", message.chat.id, 'telegram_id')
            address = "`" + g_address + "`" if g_address != "" else "Нужно зарегестрироваться /register"
            bot.send_message(message.chat.id, "Ваш адрес: " + str(
                address) + "\nБаланс в лизинге: *"
                             + str(
                '{:.8f}'.format(sql.get_col("leased", message.chat.id, 'telegram_id') / 10 ** 8))
                             + pending_lease + "WAVES*\nТекущая награда = *" + str('{:.8f}'.format(
                sql.get_col("cur_reward", message.chat.id,
                            'telegram_id') / 10 ** 8)) + " WAVES*" + sa_balance + "\nРеинвестировано = *" + str('{:.8f}'.format(
                sql.get_col("cur_reinvest", message.chat.id,
                            'telegram_id') / 10 ** 8)) + pending_reinvest + "WAVES*\nСледующая выплата через: *" + str(
                next_payment_in) +
                             " блоков*" + "\nПериодичность выплат: *"
                             + translate(sql.get_col("payment_period", message.chat.id, 'telegram_id'))
                             + "*\nРеинвест = *" + str(sql.get_col("reinvest", message.chat.id, 'telegram_id'))
                             + " %*\nВыплата от комиссии за блок = *"
                             + str(sql.get_col("cur_payment_ratio_fees", message.chat.id, 'telegram_id'))
                             + " %*\nВыплата от награды за блок = *"
                             + str(sql.get_col("cur_payment_ratio_block_reward", message.chat.id, 'telegram_id'))
                             + " %*\n", reply_markup=main_keyboard_russian, parse_mode='Markdown')
        elif message.text.lower() == "staking information":
            g_address = sql.get_col("address", message.chat.id, 'telegram_id')
            height = chain.pw.height()
            payment_period = sql.get_col('payment_period', message.chat.id, 'telegram_id')
            pl = sql.get_col("pendingLease", message.chat.id, "telegram_id")
            pr = sql.get_reinvest_col("amount_reinvest", g_address, "address")
            clb = sql.get_col("contract_lease", message.chat.id, "telegram_id")
            cplb1 = sql.get_col("contract_pending_lease", message.chat.id, "telegram_id")
            cplb2 = " " if cplb1 == 0 else "(" + str(cplb1 / 10**8) + " WAVES)"
            pending_lease = " " if pl == 0 else "(" + str(
                '{:.8f}'.format(pl / 10 ** 8)) + ") "
            pending_reinvest = " " if not pr else "(" + str('{:.8f}'.format(sum(map(sum, pr)) / 10**8)) + ") "
            next_payment_in = config.getint('payments', 'daily') + 1440 - height if payment_period == 'daily' else config.getint('payments', 'weekly') + 10800 - height if payment_period == 'weekly' else config.getint('payments', 'monthly') + 43200 - height
            sa_balance = " " if clb == 0 and cplb1 == 0 else "\nSA balance: *" + str(clb / 10**8) + " WAVES*" + cplb2
            address = "`" + g_address + "`" if g_address != "" else "You need to /register first"
            restaking_status = "Active" if sql.get_col("active", g_address, "address", table="USDN_Staking") and \
                                           sql.get_col("public_key", g_address, "address") else "Disable"
            bot.send_message(message.chat.id, "Your address: " + str(address
                ) + "\nstaking Balance: *"
                             + str(
                '{:.8f}'.format(sql.get_col("leased", message.chat.id, 'telegram_id') / 10 ** 8))
                             + pending_lease + "WAVES*\nHold reward = *" + str('{:.8f}'.format(
                sql.get_col("cur_reward", message.chat.id,
                            'telegram_id') / 10 ** 8)) + " WAVES*"+ sa_balance + "\nReinvested = *" + str(
                '{:.8f}'.format(sql.get_col("cur_reinvest", message.chat.id, 'telegram_id') / 10 ** 8)) +
                             pending_reinvest + "WAVES*\nNext payment in: *" + str(next_payment_in) +
                             " blocks*" + "\nPayment period = *"
                             + str(sql.get_col("payment_period", message.chat.id, 'telegram_id'))
                             + "*\nReinvest ratio = *" +
                             str(sql.get_col("reinvest", message.chat.id, 'telegram_id')) + "* %\nFee payment = *"
                             + str(sql.get_col("cur_payment_ratio_fees", message.chat.id, 'telegram_id'))
                             + " %*\nBlock reward payment = *" +
                             str(sql.get_col("cur_payment_ratio_block_reward", message.chat.id, 'telegram_id'))
                             + " %*\n"
                             + "USDN restaking: " + restaking_status, reply_markup=main_keyboard_english, parse_mode='Markdown')
        elif message.text.lower() == "настройки выплат":
            sql.update_col(message.chat.id, 'step', 1, "telegram_id")
            bot.send_message(message.chat.id, "Настройки выплат", reply_markup=staking_settings_russian)
        elif message.text.lower() == "payment settings":
            sql.update_col(message.chat.id, 'step', 1, "telegram_id")
            bot.send_message(message.chat.id, "Payment settings", reply_markup=staking_settings_english)
        elif message.text.lower() == "immediate withdraw":
            sql.update_col(message.chat.id, 'step', 2, "telegram_id")
            cur_reward = sql.get_col("cur_reward", message.chat.id, 'telegram_id') / 10 ** 8
            cur_reinvest = sql.get_col("cur_reinvest", message.chat.id, 'telegram_id') / 10 ** 8 + reinvest_sum(
                sql.get_col("address", message.chat.id, 'telegram_id')) / 10 ** 8
            sa = 0 if sql.get_col("contract_address", message.chat.id, 'telegram_id') else pw.Address(
                address=sql.get_col("contract_address", message.chat.id, 'telegram_id')).balance() / 10**8
            bot.send_message(message.chat.id, "What do you want to withdraw?" + "\nstaking: *"
                             + str(cur_reward) + "*\nReinvest: *" + str(cur_reinvest)
                             + "*\nSmart-Account: *" + str(sa) + "*\nTotal: " + str('{:.8f}'.format(cur_reward + cur_reinvest + sa)),
                             reply_markup=payment_english, parse_mode='Markdown')
        elif message.text.lower() == "мгновенный вывод":
            sql.update_col(message.chat.id, 'step', 2, "telegram_id")
            cur_reward = sql.get_col("cur_reward", message.chat.id, 'telegram_id') / 10 ** 8
            cur_reinvest = '{:.8f}'.format(sql.get_col("cur_reinvest", message.chat.id, 'telegram_id') / 10 ** 8 + reinvest_sum(
                sql.get_col("address", message.chat.id, 'telegram_id')) / 10 ** 8)
            sa = 0 if sql.get_col("contract_address", message.chat.id, 'telegram_id') else pw.Address(
                address=sql.get_col("contract_address", message.chat.id, 'telegram_id')).balance() / 10**8
            bot.send_message(message.chat.id, "Что вы хотите вывести?" + "\nНаграда за лизинг: *"
                             + str(cur_reward) + "*\nРеинвестированное: *" + str(cur_reinvest)
                             + "*\nСмарт-Аккаунт: *" + str(sa) + "*\nВсего: " + str('{:.8f}'.format(cur_reward + float(cur_reinvest) + sa)),
                             reply_markup=payment_russian, parse_mode='Markdown')
        elif message.text.lower() == "защита реинвеста":
            sql.update_col(message.chat.id, 'step', 3, "telegram_id")
            bot.send_message(message.chat.id, "Защита реинвеста", reply_markup=reinvest_safety_keyboard_russian)
        elif message.text.lower() == "reinvest safety":
            sql.update_col(message.chat.id, 'step', 3, "telegram_id")
            bot.send_message(message.chat.id, "Reinvest safety", reply_markup=reinvest_safety_keyboard_english)
        elif step == 1 and message.text.lower() == "частота выплат":
            bot.send_message(message.chat.id, "Частота выплат", reply_markup=choose_period_russian)
        elif step == 1 and message.text.lower() == "payment period":
            bot.send_message(message.chat.id, "Payment period", reply_markup=choose_period_english)
        elif step == 1 and message.text.lower() == "reinvest":
            msg = bot.send_message(message.chat.id, "Enter the reinvest ratio you want(%): ", reply_markup=markup)
            bot.register_next_step_handler(msg, process_reinvest_step)
        elif step == 1 and message.text.lower() == "реинвестирование":
            msg = bot.send_message(message.chat.id, "Введите значение реинвестирования, "
                                                    "которое вы хотите установить(%): ", reply_markup=markup)
            bot.register_next_step_handler(msg, process_reinvest_step)
        elif step == 2 and message.text.lower() == "реинвестированное":
            if sql.get_col("cur_reinvest", message.chat.id, 'telegram_id') + reinvest_sum(sql.get_col("address", message.chat.id, 'telegram_id')) > 200000:
                bot.send_message(message.chat.id, "Вы уверены, что хотите вывести: *"
                                 + str((sql.get_col("cur_reinvest", message.chat.id, 'telegram_id') + reinvest_sum(sql.get_col("address", message.chat.id, 'telegram_id'))) / 10**8)
                                 + " WAVES*?\n*Внимание*: комиссия за вывод составит 0.002 WAVES",
                                 reply_markup=withd_reinvest_russian, parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, "Недостаточно средств, минимум: *0.002 WAVES*",
                                 reply_markup=payment_russian, parse_mode='Markdown')
        elif step == 2 and message.text.lower() == "награду за лизинг":
            if sql.get_col("cur_reward", message.chat.id, 'telegram_id') > 200000:
                bot.send_message(message.chat.id, "Вы уверены, что хотите вывести: *"
                                 + str(sql.get_col("cur_reward", message.chat.id, 'telegram_id') / 10**8)
                                 + " WAVES*?\n*Внимание*: комиссия за вывод составит 0.002 WAVES",
                                 reply_markup=withd_leas_russian, parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, "Недостаточно средств, минимум: *0.002 WAVES*",
                                 reply_markup=payment_russian, parse_mode='Markdown')
        elif step == 2 and message.text.lower() == "смарт-аккаунт":
            sa = 0 if sql.get_col("contract_address", message.chat.id, 'telegram_id') else pw.Address(
                address=sql.get_col("contract_address", message.chat.id, 'telegram_id')).balance() / 10**8
            if sa * 10**8 > 200000:
                bot.send_message(message.chat.id, "Вы уверены, что хотите вывести: *"
                                 + str(sa)
                                 + " WAVES* cо Смарт-Аккаунта?",
                                 reply_markup=withd_sa_russian, parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, "Недостаточно средств, минимум: *0.002 WAVES*",
                                 reply_markup=payment_russian, parse_mode='Markdown')
        elif step == 2 and message.text.lower() == "всё":
            sql.update_col(message.chat.id, 'step', 2, "telegram_id")
            cur_reward = sql.get_col("cur_reward", message.chat.id, 'telegram_id') / 10**8
            cur_reinvest = sql.get_col("cur_reinvest", message.chat.id, 'telegram_id') / 10**8 + reinvest_sum(
                sql.get_col("address", message.chat.id, 'telegram_id')) / 10**8
            sa = 0 if sql.get_col("contract_address", message.chat.id, 'telegram_id') else pw.Address(
                address=sql.get_col("contract_address", message.chat.id, 'telegram_id')).balance() / 10**8
            if (cur_reward + cur_reinvest + sa) * 10**8 > 200000:
                bot.send_message(message.chat.id, "Вы уверены, что хотите вывести: *"
                                 + str('{:.8f}'.format(cur_reward + cur_reinvest + sa))
                                 + " WAVES*?\n*Внимание*: комиссия за вывод составит 0.002 WAVES",
                                 reply_markup=withd_total_russian, parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, "Недостаточно средств, минимум: *0.002 WAVES*",
                                 reply_markup=payment_russian, parse_mode='Markdown')
        elif step == 2 and message.text.lower() == "total":
            sql.update_col(message.chat.id, 'step', 2, "telegram_id")
            cur_reward = sql.get_col("cur_reward", message.chat.id, 'telegram_id') / 10**8
            cur_reinvest = sql.get_col("cur_reinvest", message.chat.id, 'telegram_id') / 10 ** 8 + reinvest_sum(
                sql.get_col("address", message.chat.id, 'telegram_id')) / 10 ** 8
            sa = 0 if sql.get_col("contract_address", message.chat.id, 'telegram_id') else pw.Address(
                address=sql.get_col("contract_address", message.chat.id, 'telegram_id')).balance() / 10**8
            if (cur_reward + cur_reinvest + sa) * 10**8 > 200000:
                bot.send_message(message.chat.id, "Are you sure that you want to withdraw: *"
                                 + str('{:.8f}'.format(cur_reward + cur_reinvest + sa))
                                 + " WAVES*?\n*Attention*: comission for withdraw is 0.002 WAVES",
                                 reply_markup=withd_total_english, parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, "Not enough funds, minimum: *0.002 WAVES*",
                                 reply_markup=payment_english, parse_mode='Markdown')
        elif step == 2 and message.text.lower() == "reinvest balance":
            if sql.get_col("cur_reinvest", message.chat.id, 'telegram_id') + reinvest_sum(sql.get_col("address", message.chat.id, 'telegram_id')) > 200000:
                bot.send_message(message.chat.id, "Are you sure that you want to withdraw: *"
                                 + str((sql.get_col("cur_reinvest", message.chat.id, 'telegram_id') + reinvest_sum(sql.get_col("address", message.chat.id, 'telegram_id'))) / 10**8)
                                 + " WAVES*?\n*Attention*: commission for withdraw is 0.002 WAVES",
                                 reply_markup=withd_reinvest_english, parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, "Not enough funds, minimum: *0.002 WAVES*",
                                 reply_markup=payment_english, parse_mode='Markdown')
        elif step == 2 and message.text.lower() == "staking reward":
            if sql.get_col("cur_reward", message.chat.id, 'telegram_id') > 200000:
                bot.send_message(message.chat.id, "Are you sure that you want to withdraw: *"
                                 + str(sql.get_col("cur_reward", message.chat.id, 'telegram_id') / 10 ** 8)
                                 + " WAVES*?\n*Attention*: commission for withdraw is *0.002 WAVES*",
                                 reply_markup=withd_leas_english, parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, "Not enough funds, minimum: *0.002 WAVES*",
                                 reply_markup=payment_english, parse_mode='Markdown')
        elif step == 2 and message.text.lower() == "smart-account":
            sa = 0 if sql.get_col("contract_address", message.chat.id, 'telegram_id') else pw.Address(
                address=sql.get_col("contract_address", message.chat.id, 'telegram_id')).balance() / 10**8
            if sa * 10**8 > 200000:
                bot.send_message(message.chat.id, "Are you sure that you want to withdraw: *"
                                 + str(sa)
                                 + " WAVES*?\n*Attention*: commission for withdraw is 0.002 WAVES",
                                 reply_markup=withd_sa_english, parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, "Not enough funds, minimum: *0.002 WAVES*",
                                 reply_markup=payment_english, parse_mode='Markdown')
        elif step == 3 and message.text.lower() == "порог waves":
            bot.send_message(message.chat.id, "*Внимание*, комисии за установку смарт-аккаунта(0.01 WAVES, один раз) и "
                                              "транзакции перевода и лизинга"
                                              "(0.005+0.005 = 0.01 WAVES, при каждом достижении порога) "
                                              "будут вычитаться из ваших наград. К тому же, при каждом "
                                              "переводе на смарт-аккаунт будет задержка в 1000 блоков перед майнингом."
                                              "Поэтому установите оптимальный порог для вас! ", parse_mode='Markdown')
            msg = bot.send_message(message.chat.id, "Установите при достижении какого количества WAVES "
                                                    "они будут переводиться на смарт-аккаунт(текущий порог: " + str(sql.get_col("threshold", message.chat.id, "telegram_id") / 10**8) + " WAVES):\nДля отмены изменений введите 0", reply_markup=markup)
            bot.register_next_step_handler(msg, process_threshold_step)
        elif step == 3 and message.text.lower() == "waves threshold":
            bot.send_message(message.chat.id, "*Attention*, comission for setup a smart-account(0.01 WAVES, once) and "
                                              "transfer and staking transactions"
                                              "(0.005+0.005 = 0.01 WAVES, every time threshold is reached) "
                                              "will be deducted from your balance. Moreover, remember about "
                                              "that before mining 1000 blocks must pass. "
                                              "So, setup an optimal threshold for you!"
                                              " ", parse_mode='Markdown')
            msg = bot.send_message(message.chat.id, "Set up the threshold of WAVES "
                                                    "to send to Smart-Account(current: " + str(sql.get_col("threshold", message.chat.id, "telegram_id") / 10**8) + " WAVES):\nTo cancel changes enter 0", reply_markup=markup)
            bot.register_next_step_handler(msg, process_threshold_step)
        elif step == 3 and message.text.lower() == "установка безопасности":
            msg = bot.send_message(message.chat.id, "Выберите вариант защиты(напишите: '1' или '2')", reply_markup=markup)
            bot.register_next_step_handler(msg, process_reinvest_security_step)
        elif step == 3 and message.text.lower() == "security setup":
            msg = bot.send_message(message.chat.id, "Choose way of security(write: '1' or '2')", reply_markup=markup)
            bot.register_next_step_handler(msg, process_reinvest_security_step)
        elif step == 3 and message.text.lower() == "информация":
            bot.send_message(message.chat.id, "Для увелечения безопасности реинвестирования, "
                                              "рекомендуется при достижении определённого "
                                              "порога WAVES в реинвестировании, "
                                              "выполнить одно из действий: "
                                              "\n\n1. Разрешить(предоставить ваш "
                                              "публичный ключ) ноде создать отдельный "
                                              "смарт-аккаунт. На смарт-аккаунте нода будет "
                                              "управлять лизингами и трансферами, но "
                                              "возможность вывода средств будет только на ваш адрес."
                                              "Для того, чтобы установить данный "
                                              "смарт-аккаунт требуется публичный ключ вашего аккаунта."
                                              "\n\n2. Установить скрипт на ваш аккаунт. "
                                              "Ваш аккаунт станет смарт-аккаунтом и нода "
                                              "сможет управлять лизингами вашего аккаунта."
                                              "Все остальные типы транзакций будут недоступны для ноды. "
                                              "Для выбора варианта нажмите 'Установка безопасности'",
                             reply_markup=reinvest_safety_keyboard_russian)
        elif step == 3 and message.text.lower() == "information":
            bot.send_message(message.chat.id, "To increase the safety of reinvest it's highly "
                                              "recommended to go by one of the two ways: "
                                              "\n\n1. Set up a separated Smart-Account(SA). In this "
                                              "SA node will be able to manage staking and"
                                              "transfers, but withdraw will be available only"
                                              "to your account.\n\n2. Set up a script on your account."
                                              " In this case your account become Smart-Account and node"
                                              "will be able to manage staking on your account. All"
                                              "other transactions will not be available for the node."
                                              "To choose one of the ways press 'Security setup'",
                             reply_markup=reinvest_safety_keyboard_english)
        elif step == 3 and message.text.lower() == "usdn re-staking":
            bot.send_message(message.chat.id, "Do you want to enable USDN re-staking?",
                             reply_markup=restaking_english)
        elif step == 3 and message.text.lower() == "usdn рестейкинг":
            bot.send_message(message.chat.id, "Хотите включить USDN рестейкинг на своём аккаунте?",
                             reply_markup=restaking_russian)
        elif (step >= 1) and message.text.lower() == "назад":
            bot.send_message(message.chat.id, "Назад", reply_markup=main_keyboard_russian)
            sql.update_col(message.chat.id, 'step', 0, "telegram_id")
        elif (step >= 1) and message.text.lower() == "back":
            sql.update_col(message.chat.id, 'step', 0, "telegram_id")
            bot.send_message(message.chat.id, "Back", reply_markup=main_keyboard_english)
        else:
            if sql.get_col("language", message.chat.id, "telegram_id") == "English":
                bot.send_message(message.chat.id, "Unknown message, try again", reply_markup=main_keyboard_english)
            else:
                bot.send_message(message.chat.id, "Неизвестное сообщение", reply_markup=main_keyboard_russian)
    sql.cursor.close()
    sql.mydb.close()


if config.getint('main', 'production'):
    bot.remove_webhook()

    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))
    cherrypy.config.update({
        'server.socket_host': WEBHOOK_LISTEN,
        'server.socket_port': WEBHOOK_PORT,
        'server.ssl_module': 'builtin',
        'server.ssl_certificate': WEBHOOK_SSL_CERT,
        'server.ssl_private_key': WEBHOOK_SSL_PRIV
    })

    cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
else:
    bot.polling()