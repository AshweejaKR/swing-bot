import datetime as dt

debugOn = False
instrument_list = None
client_id = None
api = None
waitTime = dt.time(8, 59)
startTime = dt.time(9, 16)
endTime = dt.time(15, 16)
sleepTime = 0.5
ltp = 0.0
count = 0
buy_p = 0.9939
sell_p = 1.011
tsl_P  = 1.016
amountPerTrade = 1000.00
data_list = []
filename = "position_data.json"



