from logger import *
from angelib import *
from tradelib import *

import gvarlist

initialize_logger()

# This is for testing the API Only

login()

params = {
    "datatype":"PercOIGainers",
    "expirytype":"NEAR" 
}
gainersLosers = gvarlist.api.gainersLosers(params)
print(gainersLosers)

for i in gainersLosers:
    print(i)

logout()
