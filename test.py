from logger import *
from angelib import *
from tradelib import *

import gvarlist

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

initialize_logger()

initialize_bot()
# This is for testing the API Only

login()

params = {
    "datatype":"PercOIGainers",
    "expirytype":"NEAR" 
}
# gainersLosers = gvarlist.api.gainersLosers(params)
# print(gainersLosers)

# for i in gainersLosers:
    # print(i)

ticker = "NIFTYBEES-EQ"
exchange = 'NSE'
#Estimate Charges
params = {
    "orders": [
        {
            "product_type": "DELIVERY",
            "transaction_type": "SELL",
            "quantity": "10",
            "price": "200",
            "exchange": "NSE",
            "symbol_name": ticker,
            "token": token_lookup(ticker, exchange)
        }
    ]
}
estimateCharges = gvarlist.api.estimateCharges(params)
print("estimateCharges: {} \n".format(estimateCharges))

data = estimateCharges['data']['summary']
for i in data:
    print(i, '  :  ', data[i])

params = {
    "isin":"INE528G01035",
    "quantity":"1"
}
# verifyDis = gvarlist.api.verifyDis(params)
# print("verifyDis: {} \n".format(verifyDis))

params = {
    "dpId":"33200",
    "ReqId":"2351614738654050",
    "boid":"1203320018563571",
    "pan":"JZTPS2255C"
}
# generateTPIN = gvarlist.api.generateTPIN(params)
# print("generateTPIN: {} \n".format(generateTPIN))

logout()
