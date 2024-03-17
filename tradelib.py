import json
import time

from logger import *
from angelib import *

# global variables here
import gvarlist

# Function to write data to a JSON file
def write_to_json(data):
    with open(gvarlist.filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Function to read data from a JSON file
def read_from_json():
    data = []
    try:
        with open(gvarlist.filename, 'r') as json_file:
            data = json.load(json_file)
    except Exception as err:
        pass
    return data

class Trader():
    def __init__(self, ticker):
        self.ticker = ticker
        self.prevPrice = 0.0

        stock_data = hist_data(self.ticker)
        self.prevPrice = max(stock_data.iloc[-1]['close'], stock_data.iloc[-2]['close'])
        self.prevPrice = 1025.00

        self.cur_price = get_current_price(self.ticker)
        self.sharesQty = int(gvarlist.amountPerTrade / self.cur_price)

        lg.info('Trade is initialized with ticker %s ...!!' % (self.ticker))
        lg.info("Current price of {} is {} and Trading Qty {}".format(self.ticker, self.cur_price, self.sharesQty))
    
    def trail_SL(self):
        if(self.cur_price > self.triggerTSL):
            self.stoploss = self.target
            self.target = (gvarlist.sell_p * self.cur_price)
            self.triggerTSL = (gvarlist.tsl_P * self.cur_price)

    def exit_pos(self):
        global data_list
   
        if(len(data_list) > 0):
            temp = data_list[-1]
            self.sharesQty = temp['quantity']
            self.target = temp['target_price']
            self.triggerTSL = temp['trigger_price']
            self.stoploss = temp['stoploss_price']

            self.trail_SL()

            temp['target_price'] = self.target
            temp['trigger_price'] = self.triggerTSL
            temp['stoploss_price'] = self.stoploss

            lg.debug("\n-----------------------------------------")
            lg.debug("self.cur_price: {} ".format(self.cur_price))
            lg.debug("self.target: {} ".format(self.target))
            lg.debug("self.stoploss: {} ".format(self.stoploss))
            lg.debug("self.triggerTSL: {} ".format(self.triggerTSL))
            lg.debug("-----------------------------------------\n\n")

            lg.info('SL %.2f <-- %.2f --> %.2f TP' % (self.stoploss, self.cur_price, self.target))
            if((self.cur_price > self.target) or (self.cur_price < self.stoploss)):
                buy_sell = "SELL"
                #####
                # orderID = submit_order(self.ticker, self.sharesQty, buy_sell)
                orderID = 'orderID'
                count = 0
                while (get_oder_status(orderID) == 'open'):
                    lg.info('Buy order is in open, waiting ... %d ' % (count))
                status = get_oder_status(orderID)
                if(status == 'completed'):
                    lg.info('Submitting {} Order for {}, Qty = {} at price: {}'.format(buy_sell, self.ticker, self.sharesQty, self.cur_price))
                    send_to_telegram('Submitting {} Order for {}, Qty = {} at price: {}'.format(buy_sell, self.ticker, self.sharesQty, self.cur_price))
                    data_list.remove(data_list[-1])
                else:
                    lg.error('Sell order NOT submitted, aborting trade!')
                    send_to_telegram('Sell order NOT submitted, aborting trade!')
            write_to_json(data_list)
    
    def run(self):
        global data_list
        data_list = read_from_json()
        success = True

        try:
            while True:
                lg.info('Running trade for %s ... !' % (self.ticker))
                lg.info("self.cur_price = {} <= (gvarlist.buy_p * self.prevPrice) = {} ... ".format(self.cur_price, (gvarlist.buy_p * self.prevPrice)))

                cur_time = dt.datetime.now(pytz.timezone("Asia/Kolkata")).time()
                if(cur_time < gvarlist.startTime or cur_time > gvarlist.endTime):
                    lg.info('Market is closed. ')
                    send_to_telegram('Market is closed. ')
                    break

                self.cur_price = get_current_price(self.ticker)
                self.sharesQty = int(gvarlist.amountPerTrade / self.cur_price)

                if(self.cur_price <= gvarlist.buy_p * self.prevPrice):
                    buy_sell = 'BUY'
                    #####
                    # orderID = submit_order(self.ticker, self.sharesQty, buy_sell)
                    orderID = 'orderID'
                    self.target = (gvarlist.sell_p * self.cur_price)
                    self.stoploss = 10.00 #(0.995 * self.cur_price)
                    self.triggerTSL = (gvarlist.tsl_P * self.cur_price)
                    count = 0
                    while (get_oder_status(orderID) == 'open'):
                        lg.info('Buy order is in open, waiting ... %d ' % (count))
                    status = get_oder_status(orderID)
                    if(status == 'completed'):
                        buy_data = {"buy_price" : self.cur_price, "orderID" : orderID, "quantity" : self.sharesQty, "target_price" : self.target, "trigger_price" : self.triggerTSL, "stoploss_price" : self.stoploss}
                        data_list.append(buy_data)
                        self.prevPrice = self.cur_price
                        lg.info('Submitting {} Order for {}, Qty = {} at price: {}'.format(buy_sell, self.ticker, self.sharesQty, self.cur_price))
                        send_to_telegram('Submitting {} Order for {}, Qty = {} at price: {}'.format(buy_sell, self.ticker, self.sharesQty, self.cur_price))
                    else:
                        lg.error('Buy order NOT submitted, aborting trade!')
                        send_to_telegram('Buy order NOT submitted, aborting trade!')
                    write_to_json(data_list)
                self.exit_pos()
        except Exception as err:
            write_to_json(data_list)
            template = "An exception of type {0} occurred. error message:{1!r}"
            message = template.format(type(err).__name__, err.args)
            lg.error(message)
            send_to_telegram(message)
            success = False

        write_to_json(data_list)
        return success
