import urllib
from SmartApi import SmartConnect
from pyotp import TOTP
import time
import pandas as pd
import datetime as dt

from logger import *

# global variables here
import gvarlist

def login():
    try:
        key_secret = open("key.txt", "r").read().split()
        gvarlist.client_id = key_secret[2]

        gvarlist.api = SmartConnect(api_key = key_secret[0])
        data = gvarlist.api.generateSession(gvarlist.client_id, key_secret[3], TOTP(key_secret[4]).now())
        lg.debug('data: %s ' % data)
        if(data['status'] and data['message'] == 'SUCCESS'):
            lg.info('Login success ... !')
            send_to_telegram("Login success ... !")
        else:
            lg.error('Login failed ... !')
            send_to_telegram('Login failed ... !')
            logout()
            sys.exit()
    except Exception as err:
        template = "An exception of type {0} occurred. error message:{1!r}"
        message = template.format(type(err).__name__, err.args)
        lg.error(message)
        send_to_telegram(message)
        logout()
        sys.exit()

def logout():
    try:
        data = gvarlist.api.terminateSession(gvarlist.client_id)
        lg.debug('logout: %s ' % data)
        if(data['status'] and data['message'] == 'SUCCESS'):
            lg.info('Logout success ... !')
            send_to_telegram("Logout success ... !")
        else:
            lg.error('Logout failed ... !')
    except Exception as err:
        template = "An exception of type {0} occurred. error message:{1!r}"
        message = template.format(type(err).__name__, err.args)
        lg.error(message)
        send_to_telegram(message)
        lg.error('Logout failed ... !')
        send_to_telegram('Logout failed ... !')

def token_lookup(ticker, exchange = "NSE"):
    try:
        for instrument in gvarlist.instrument_list:
            if instrument["symbol"] == ticker and instrument["exch_seg"] == exchange and instrument["symbol"].split('-')[-1] == "EQ":
                return instrument["token"]
    except Exception as err:
        template = "An exception of type {0} occurred. error message:{1!r}"
        message = template.format(type(err).__name__, err.args)
        lg.error(message)
        send_to_telegram(message)

def symbol_lookup(token, exchange = "NSE"):
    for instrument in gvarlist.instrument_list:
        if instrument["token"] == token and instrument["exch_seg"] == exchange:
            return instrument["symbol"][:-3]

def submit_order(ticker, sharesQty, buy_sell, exchange = 'NSE'):
    lg.info('Submitting %s Order for %s, Qty = %d ' % (buy_sell, ticker, sharesQty))
    orderID = None

    try:
        params = {
                    "variety" : "NORMAL",
                    "tradingsymbol" : "{}".format(ticker),
                    "symboltoken" : token_lookup(ticker),
                    "transactiontype" : buy_sell,
                    "exchange" : exchange,
                    "ordertype" : "MARKET",
                    "producttype" : "CARRYFORWARD",
                    "duration" : "DAY",
                    "quantity" : sharesQty
                    }
        
        lg.info('params: %s ' % params)
        orderID = gvarlist.api.placeOrder(params)
        lg.info('orderID: %s ' % orderID)
    except Exception as err:
        template = "An exception of type {0} occurred. error message:{1!r}"
        message = template.format(type(err).__name__, err.args)
        lg.error(message)
        send_to_telegram(message)
        lg.error('%s order NOT submitted!' % buy_sell)
        send_to_telegram('{} order NOT submitted!'.format(buy_sell))
        logout()
        sys.exit()
    return orderID
    
def get_oder_status(orderID):
    status = 'NA'
    # For Test
    # return 'completed'
    # End test
    
    time.sleep(gvarlist.sleepTime)
    order_history_response = gvarlist.api.orderBook()  
    try:
        for i in order_history_response['data']:
            if(i['orderid'] == orderID):
                lg.debug(str(i))
                status = i['status'] # completed/rejected/open/cancelled
                break
    except Exception as err:
        template = "An exception of type {0} occurred. error message:{1!r}"
        message = template.format(type(err).__name__, err.args)
        lg.error(message)
        send_to_telegram(message)
        
    return status

def hist_data(ticker, exchange = "NSE"):
    interval = 'ONE_DAY'
    duration = 10
    token = token_lookup(ticker, exchange)
    if token is None:
        lg.error("Not a VALID ticker")
        df_data = pd.DataFrame(columns = ["date", "open", "high", "low", "close", "volume"])
        return df_data
    params = {
             "exchange" : exchange,
             "symboltoken" : token,
             "interval" : interval,
             "fromdate" : (dt.date.today() - dt.timedelta(duration)).strftime('%Y-%m-%d %H:%M'),
             "todate" : dt.date.today().strftime('%Y-%m-%d %H:%M')  
             }
    data = gvarlist.api.getCandleData(params)

    df_data = pd.DataFrame(data["data"],
                           columns = ["date", "open", "high", "low", "close", "volume"])
    df_data.set_index("date", inplace = True)
    df_data.index = pd.to_datetime(df_data.index)
    df_data.index = df_data.index.tz_localize(None)
    return df_data

def get_current_price(ticker, exchange = 'NSE'):
    # Only For Test/Debug
    if(gvarlist.debugOn):
        ltp = float(input("Enter LTP:\n"))
        return ltp
    # End Test

    time.sleep(gvarlist.sleepTime)
    data = "NO DATA RECEIVED"
    try:
        data = gvarlist.api.ltpData(exchange = exchange, tradingsymbol = ticker, symboltoken = token_lookup(ticker))
        if(data['status'] and (data['message'] == 'SUCCESS')):
            ltp = float(data['data']['ltp'])
            gvarlist.ltp = ltp
        else:
            template = "An ERROR occurred. error message : {0!r}"
            message = template.format(data['message'])
            lg.error(message)
            send_to_telegram(message)
            ltp = gvarlist.ltp
    except Exception as err:
        template = "An exception of type {0} occurred. error message:{1!r}"
        message = template.format(type(err).__name__, err.args)
        lg.error(message)
        lg.error("DATA RECEIVED: {}".format(data))
        ltp = gvarlist.ltp

    return ltp

def get_shares_amount(cur_price):
    return 1
