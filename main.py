import sys
import json

from logger import *
from angelib import *
from tradelib import *

import gvarlist

# initialize bot for trading account
def initialize_bot():
    filename = 'instrument_list.json'
    try:
        with open(filename) as f:
            gvarlist.instrument_list = json.load(f)
    except FileNotFoundError:
        instrument_url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        response = urllib.request.urlopen(instrument_url)
        gvarlist.instrument_list = json.loads(response.read())
        with open(filename, "w") as f:
            f.write(json.dumps(gvarlist.instrument_list))
    except Exception as err:
        template = "An exception of type {0} occurred. error message:{1!r}"
        message = template.format(type(err).__name__, err.args)
        lg.error(message)

    lg.info('Trading Bot initialized')
    send_to_telegram('Trading Bot initialized')

def main():
    
    if(len(sys.argv) > 1):
        if("debug".lower() == sys.argv[1].lower()):
            print("DEBUG ON")
            gvarlist.debugOn = True
            gvarlist.endTime = dt.time(23, 50)


    # initialize the logger (imported from logger)
    initialize_logger()

    # initialize bot
    initialize_bot()

    login()

    ticker = "NIFTYBEES-EQ"
    ltp = 0.0
    gvarlist.count = 0
    while ltp <= 1.0:
        gvarlist.count += 1
        ltp = get_current_price(ticker)
        if((gvarlist.count % 300) == 0):
            lg.info("Current price of {} is {} ... \n".format(ticker, ltp))

    cur_time = dt.datetime.now(pytz.timezone("Asia/Kolkata")).time()
    if(cur_time > gvarlist.waitTime and cur_time < gvarlist.startTime):
        lg.info("Market is NOT opened waiting ... !")
        time.sleep(gvarlist.sleepTime)

    gvarlist.count = 0
    while True:
        gvarlist.count += 1
        cur_time = dt.datetime.now(pytz.timezone("Asia/Kolkata")).time()
        if(cur_time > gvarlist.endTime):
            lg.info('Market is closed. \n')
            send_to_telegram('Market is closed...')
            logout()
            sys.exit()

        if(cur_time > gvarlist.startTime):
            break

        if((gvarlist.count % 300) == 0):
            lg.info("Market is NOT opened waiting ... !")
        time.sleep(gvarlist.sleepTime)
        
    lg.info("Current price of {} is {} ... \n".format(ticker, ltp))

    obj = Trader(ticker)
    success = obj.run()
    obj.report()

    logout()

    if not success:
        lg.info('Trading was not successful, locking asset')
        send_to_telegram('Trading was not successful, locking asset')
    else:
        lg.info('Trading was successful!')
        send_to_telegram('Trading was successful!')

    lg.info('Trading Bot finished ... ')
    send_to_telegram('Trading Bot finished ... ')

if __name__ == '__main__':
    main()
