import json
import requests
import time
from datetime import datetime
import pdb
import urllib
import hashlib

SYMBOL_BTCCNY = 'BTC_CNY'
SYMBOL_LTCCNY = 'LTC_CNY'
SYMBOL_BTCUSD = 'BTC_USD'

class BtcLtcDataApi(object):
    KLINE_SYMBOL_URL = {
        SYMBOL_BTCCNY: 'http://api.huobi.com/staticmarket/btc_kline_[period]_json.js',
        SYMBOL_LTCCNY: 'http://api.huobi.com/staticmarket/ltc_kline_[period]_json.js',
        SYMBOL_BTCUSD: 'http://api.huobi.com/usdmarket/btc_kline_[period]_json.js'
    }   

    DEPTH_SYMBOL_URL = {
        SYMBOL_BTCCNY: 'http://api.huobi.com/staticmarket/depth_btc_json.js',
        SYMBOL_LTCCNY: 'http://api.huobi.com/staticmarket/depth_ltc_json.js',
        SYMBOL_BTCUSD: 'http://api.huobi.com/usdmarket/depth_btc_json.js'
    } 

    def __init__(self):
        pass

    def getKline(self, symbol, period, length=0):
        url = self.KLINE_SYMBOL_URL[symbol]
        url = url.replace('[period]', period)
        
        if length:
            url = url + '?length=' + str(length)
            
        try:
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()
                return data
        except Exception, e:
            print e
            return None

    def getDepth(self, symbol, level):
        url = self.DEPTH_SYMBOL_URL[symbol]
        url = url.replace('json', level)

        try:
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()
                return data
        except Exception, e:
            print e
            return None


HUOBI_TRADE_API = 'https://api.huobi.com/apiv3'

COINTYPE_BTC = 1
COINTYPE_LTC = 2


FUNCTIONCODE_GETACCOUNTINFO = 'get_account_info'
FUNCTIONCODE_GETORDERS = 'get_orders'
FUNCTIONCODE_ORDERINFO = 'order_info'
FUNCTIONCODE_BUY = 'buy'
FUNCTIONCODE_SELL = 'sell'
FUNCTIONCODE_BUYMARKET = 'buy_market'
FUNCTIONCODE_SELLMARKET = 'sell_market'
FUNCTIONCODE_CANCELORDER = 'cancel_order'
FUNCTIONCODE_GETNEWDEALORDERS = 'get_new_deal_orders'

class BtcLtcTradeApi(object):
    def __init__(self):
        self.accessKey = ''
        self.secretKey = ''

    def _signature(self, params):
        params = sorted(params.iteritems(), key=lambda d:d[0], reverse=False)
        message = urllib.urlencode(params)
    
        m = hashlib.md5()
        m.update(message)
        m.digest()

        sig=m.hexdigest()
        return sig    

    def _processRequest(self, method_, params_, optional=None):
        method = method_
        params = params_
        
        time_ = time.time()
        datetime_ = datetime.fromtimestamp(time_)
        params['created'] = long(time_)
        params['access_key'] = self.accessKey
        params['secret_key'] = self.secretKey
        params['method'] = method
        
        sign = self._signature(params)
        params['sign'] = sign
        del params['secret_key']
        
        if optional:
            params.update(optional)
        
        payload = urllib.urlencode(params)

        r = requests.post(HUOBI_TRADE_API, params=payload)
        if r.status_code == 200:
            data = r.json()
            return datetime_, data
        else:
            return datetime_, None        
    
    def getAccountInfo(self, market='cny'):
        method = FUNCTIONCODE_GETACCOUNTINFO
        params = {}
        
        optional = {'market': market}
        return self._processRequest(method, params, optional)

    def getOrders(self, coinType=COINTYPE_BTC, market='cny'):
        method = FUNCTIONCODE_GETORDERS
        params = {'coin_type': coinType}
        optional = {'market': market}
        return self._processRequest(method, params, optional)

    def getOrderInfo(self, id_, coinType=COINTYPE_BTC, market='cny'):
        method = FUNCTIONCODE_ORDERINFO
        params = {
            'coin_type': coinType,
            'id': id_
        }
        optional = {'market': market}
        return self._processRequest(method, params, optional)

    def buyLimit(self, price, quantity, coinType=COINTYPE_BTC, tradePassword='', tradeId = '', market='cny'):
        method = FUNCTIONCODE_BUY
        params = {
            'coin_type': coinType,
            'price': price,
            'amount': quantity
        }
        optional = {
            'trade_password': tradePassword,
            'trade_id': tradeId,
            'market': market
        }
        return self._processRequest(method, params, optional)

    def sellLimit(self, price, quantity, coinType=COINTYPE_BTC, tradePassword='', tradeId = '', market='cny'):
        method = FUNCTIONCODE_SELL
        params = {
            'coin_type': coinType,
            'price': price,
            'amount': quantity
        }
        optional = {
            'trade_password': tradePassword,
            'trade_id': tradeId,
            'market': market
        }
        return self._processRequest(method, params, optional)

    def buyMarket(self, quantity, coinType=COINTYPE_BTC, tradePassword='', tradeId = '', market='cny'):
        method = FUNCTIONCODE_BUYMARKET
        params = {
            'coin_type': coinType,
            'amount': quantity
        }
        optional = {
            'trade_password': tradePassword,
            'trade_id': tradeId,
            'market': market
        }
        return self._processRequest(method, params, optional) 
    
    def sellMarket(self, quantity, coinType=COINTYPE_BTC, tradePassword='', tradeId = '', market='cny'):
        method = FUNCTIONCODE_SELLMARKET
        params = {
            'coin_type': coinType,
            'amount': quantity
        }
        optional = {
            'trade_password': tradePassword,
            'trade_id': tradeId,
            'market': market
        }
        return self._processRequest(method, params, optional)      

    def cancelOrder(self, id_, coinType=COINTYPE_BTC, market='cny'):
        method = FUNCTIONCODE_CANCELORDER
        params = {
            'coin_type': coinType,
            'id': id_
        }
        optional = {'market': market}
        return self._processRequest(method, params, optional)    

    def getNewDealOrders(self, coinType=COINTYPE_BTC, market='cny'):
        method = FUNCTIONCODE_GETNEWDEALORDERS
        params = {
            'coin_type': coinType
        }
        optional = {'market': market}
        return self._processRequest(method, params, optional)

class BtcLtcTradeApiFake(object):
    def __init__(self):
        self.__orderIdTmp = None
        self.__orderTypeTmp = None
        self.__requestQuantityTmp = None
        self.__requestPriceTmp = None
        self.__commission = 0.002
        self.__fee = 0
        self.__cashTmp = 10000
        self.__isInPositionTmp = False
        self.__dateTime = None
        self.__data = BtcLtcDataApi()

    def getAccountInfo(self):
        #pdb.set_trace()
        if  self.__isInPositionTmp is True:
            curBar = self.__data.getKline(SYMBOL_LTCCNY, '001', 1)
            total = self.__cashTmp + self.__requestQuantityTmp * float(curBar[0][4]) - self.__fee
            share = self.__requestQuantityTmp
        else:
            total = self.__cashTmp
            share = 0

        ret = {'total':str(total), 
               'available_cny_display':str(self.__cashTmp), 
               'available_btc_display':str(share),
               'available_ltc_display':str(share)}

        return datetime.fromtimestamp(time.time()), ret

    def getOrderInfo(self, id_, coinType=COINTYPE_BTC):
        vot = self.__requestQuantityTmp * self.__requestPriceTmp
        total = vot
        ret = {'id':str(self.__orderIdTmp), 
               'type':str(self.__orderTypeTmp), 
               'order_price':str(self.__requestPriceTmp), 
               'order_amount':str(self.__requestQuantityTmp),
               'processed_price':str(self.__requestPriceTmp),
               'processed_amount':str(self.__requestQuantityTmp),
               'vot':str(vot),
               'fee':str(self.__fee),
               'total':str(total),
               'status':'2'}
        return self.__dateTime, ret

    def buyMarket(self, quantity, coinType=COINTYPE_BTC):
        #pdb.set_trace()
        curBar = self.__data.getKline(SYMBOL_LTCCNY, '001', 1)
        self.__isInPositionTmp = True
        self.__orderIdTmp = 1234
        self.__orderTypeTmp = 3
        self.__requestPriceTmp = float(curBar[0][4])
        self.__requestQuantityTmp = quantity
        cost = self.__requestPriceTmp * self.__requestQuantityTmp
        self.__fee = cost * self.__commission
        self.__cashTmp -= cost
        self.__dateTime = datetime.fromtimestamp(time.time())
        ret = {'result':'success', 'id':str(self.__orderIdTmp)}
        return self.__dateTime, ret

    def sellMarket(self, quantity, coinType=COINTYPE_BTC):
        curBar = self.__data.getKline(SYMBOL_LTCCNY, '001', 1)
        self.__isInPositionTmp = False
        self.__orderIdTmp = 1235
        self.__orderTypeTmp = 4
        self.__requestPriceTmp = float(curBar[0][4])
        self.__requestQuantityTmp = quantity
        cost = self.__requestPriceTmp * self.__requestQuantityTmp
        self.__fee = cost * self.__commission
        self.__cashTmp += cost - self.__fee
        self.__dateTime = datetime.fromtimestamp(time.time())
        ret = {'result':'success', 'id':str(self.__orderIdTmp)}
        return self.__dateTime, ret

    def buyLimit(self, price, quantity, coinType=COINTYPE_BTC):
        self.__isInPositionTmp = True
        self.__orderIdTmp = 1234
        self.__orderTypeTmp = 3
        self.__requestPriceTmp = price
        self.__requestQuantityTmp = quantity
        cost = self.__requestPriceTmp * self.__requestQuantityTmp
        self.__fee = cost * self.__commission
        self.__cashTmp -= cost
        self.__dateTime = datetime.fromtimestamp(time.time())
        ret = {'result':'success', 'id':str(self.__orderIdTmp)}
        return self.__dateTime, ret
        

    def sellLimit(self, price, quantity, coinType=COINTYPE_BTC):
        self.__isInPositionTmp = False
        self.__orderIdTmp = 1235
        self.__orderTypeTmp = 4
        self.__requestPriceTmp = price
        self.__requestQuantityTmp = quantity
        cost = self.__requestPriceTmp * self.__requestQuantityTmp
        self.__fee = cost * self.__commission
        self.__cashTmp += cost - self.__fee
        self.__dateTime = datetime.fromtimestamp(time.time())
        ret = {'result':'success', 'id':str(self.__orderIdTmp)}
        return self.__dateTime, ret

    def cancelOrder(self, id_, coinType=COINTYPE_BTC):
        ret = {'result':'success'}
        return datetime.fromtimestamp(time.time()), ret
