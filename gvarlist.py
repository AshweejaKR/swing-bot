import datetime as dt

debugOn = False
instrument_list = None
client_id = None
api = None
waitTime = dt.time(8, 59)
startTime = dt.time(9, 16)
endTime = dt.time(15, 16)
sleepTime = 20
ratelimitsleepTime = 1
ltp = 0.0
count = 0
data_list = []
position_datafile = "default.json"

# config data for Trade
buy_p = 0.9985
sell_p = 1.002
tsl_P  = 1.004
amountPerTrade = 2000.00



