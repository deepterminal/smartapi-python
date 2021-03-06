from six.moves.urllib.parse import urljoin
import sys

sys.path.append('c:\AngelSmartApi\SmartApi')
import csv
import json
import dateutil.parser
import hashlib
import logging
import datetime
import smartapi.smartExceptions as ex
import requests
from requests import get
import re, uuid
import socket

from smartapi.version import __version__, __title__

log = logging.getLogger(__name__)


class SmartConnect(object):
    #_rootUrl = "https://openapisuat.angelbroking.com"
    _rootUrl="https://apiconnect.angelbroking.com" #prod endpoint
    #_login_url ="https://smartapi.angelbroking.com/login"
    _login_url="https://smartapi.angelbroking.com/publisher-login" #prod endpoint
    _default_timeout = 7  # In seconds
    # Products
    PRODUCT_MIS = "MIS"

    PRODUCT_CNC = "CNC"
    PRODUCT_NRML = "NRML"
    PRODUCT_CO = "CO"
    PRODUCT_BO = "BO"

    # Order types
    ORDER_TYPE_MARKET = "MARKET"
    ORDER_TYPE_LIMIT = "LIMIT"
    ORDER_TYPE_SLM = "SL-M"
    ORDER_TYPE_SL = "SL"

    # Varities
    VARIETY_REGULAR = "regular"
    VARIETY_BO = "bo"
    VARIETY_CO = "co"
    VARIETY_AMO = "amo"

    # Transaction type
    TRANSACTION_TYPE_BUY = "BUY"
    TRANSACTION_TYPE_SELL = "SELL"

    # Validity
    VALIDITY_DAY = "DAY"
    VALIDITY_IOC = "IOC"

    # Exchanges
    EXCHANGE_NSE = "NSE"
    EXCHANGE_BSE = "BSE"
    EXCHANGE_NFO = "NFO"
    EXCHANGE_CDS = "CDS"
    EXCHANGE_BFO = "BFO"
    EXCHANGE_MCX = "MCX"
    EXCHANGE_NCDEX="NCDEX"

    # Status constants
    STATUS_COMPLETE = "COMPLETE"
    STATUS_REJECTED = "REJECTED"
    STATUS_CANCELLED = "CANCELLED"

    _routes = {
        "api.login":"/rest/auth/angelbroking/user/v1/loginByPassword",
        "api.logout":"/rest/secure/angelbroking/user/v1/logout",
        "api.token": "/rest/auth/angelbroking/jwt/v1/generateTokens",
        "api.refresh": "/rest/auth/angelbroking/jwt/v1/generateTokens",
        "api.user.profile": "/rest/secure/angelbroking/user/v1/getProfile",

        "api.order.place": "/rest/secure/angelbroking/order/v1/placeOrder",
        "api.order.modify": "/rest/secure/angelbroking/order/v1/modifyOrder",
        "api.order.cancel": "/rest/secure/angelbroking/order/v1/cancelOrder",
        "api.order.book":"/rest/secure/angelbroking/order/v1/getOrderBook",
        
        "api.ltp.data": "/rest/secure/angelbroking/order/v1/getLtpData",
        "api.trade.book": "/rest/secure/angelbroking/order/v1/getTradeBook",
        "api.rms.limit": "/rest/secure/angelbroking/user/v1/getRMS",
        "api.holding": "/rest/secure/angelbroking/portfolio/v1/getHolding",
        "api.position": "/rest/secure/angelbroking/order/v1/getPosition",
        "api.convert.position": "/rest/secure/angelbroking/order/v1/convertPosition"
    }

    def __init__(self, api_key=None, access_token=None, refresh_token=None, userId=None, root=None, debug=False, timeout=None, proxies=None, pool=None, disable_ssl=False):
        self.debug = debug
        self.api_key = api_key
        self.session_expiry_hook = None
        self.disable_ssl = disable_ssl
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.userId = userId
        self.proxies = proxies if proxies else {}
        self.root = root or self._loginUrl
        self.timeout = timeout or self._default_timeout

        if pool:
            self.reqsession = requests.Session()
            reqadapter = requests.adapters.HTTPAdapter(**pool)
            self.reqsession.mount("https://", reqadapter)
            print("in pool")
        else:
            self.reqsession = requests

        # disable requests SSL warning
        requests.packages.urllib3.disable_warnings()

    def setSessionExpiryHook(self, method):
        if not callable(method):
            raise TypeError("Invalid input type. Only functions are accepted.")
        self.session_expiry_hook = method
    
    def getUserId():
        return userId;

    def setUserId(self,id):
        self.userId=id

    def setAccessToken(self, access_token):

        self.access_token = access_token

    def setRefreshToken(self, refresh_token):

        self.refresh_token = refresh_token
    
    def login_url(self):
        """Get the remote login url to which a user should be redirected to initiate the login flow."""
        return "%s?api_key=%s" % (self._login_url, self.api_key)
    
    def _request(self, route, method, parameters=None):
        """Make an HTTP request."""
        params = parameters.copy() if parameters else {}
       
        uri =self._routes[route].format(**params)
        print(uri)
        url = urljoin(self.root, uri)
        print(url)
        hostname = socket.gethostname() 
        clientLocalIP=socket.gethostbyname(hostname)
        clientPublicIP=get('https://api.ipify.org').text
        macAddress = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        privateKey = "test"
        accept = "application/json"
        userType = "USER"
        sourceID = "WEB"

        # Custom headers
        headers = {
            #"X-SmartApi-Version": "", 
            #"User-Agent": self._user_agent()
            "Content-type":accept,
            "X-ClientLocalIP": clientLocalIP,
            "X-ClientPublicIP": clientPublicIP,
            "X-MACAddress": macAddress,
            "Accept": accept,
            "X-PrivateKey": privateKey,
            "X-UserType": userType,
            "X-SourceID": sourceID
        }

        #if self.api_key and self.access_token:
        if self.access_token:
            # set authorization header
        
            auth_header = self.access_token
            headers["Authorization"] = "Bearer {}".format(auth_header)

        if self.debug:
            log.debug("Request: {method} {url} {params} {headers}".format(method=method, url=url, params=params, headers=headers))
    
        try:
            r = requests.request(method,
                                        url,
                                        data=json.dumps(params) if method in ["POST", "PUT"] else None,
                                        params=json.dumps(params) if method in ["GET", "DELETE"] else None,
                                        headers=headers,
                                        verify=not self.disable_ssl,
                                        allow_redirects=True,
                                        timeout=self.timeout,
                                        proxies=self.proxies)
            print("The Response Content",r.content)
        except Exception as e:
            raise e

        if self.debug:
            log.debug("Response: {code} {content}".format(code=r.status_code, content=r.content))

        # Validate the content type.
        if "json" in headers["Content-type"]:
            try:
                data = json.loads(r.content.decode("utf8"))
             
            except ValueError:
                raise ex.DataException("Couldn't parse the JSON response received from the server: {content}".format(
                    content=r.content))

            # api error
            if data.get("error_type"):
                # Call session hook if its registered and TokenException is raised
                if self.session_expiry_hook and r.status_code == 403 and data["error_type"] == "TokenException":
                    self.session_expiry_hook()

                # native errors
                exp = getattr(ex, data["error_type"], ex.GeneralException)
                raise exp(data["message"], code=r.status_code)

            return data
        elif "csv" in headers["Content-type"]:
            return r.content
        else:
            raise ex.DataException("Unknown Content-type ({content_type}) with response: ({content})".format(
                content_type=headers["Content-type"],
                content=r.content))
        
    def _deleteRequest(self, route, params=None):
        """Alias for sending a DELETE request."""
        return self._request(route, "DELETE", params)
    def _putRequest(self, route, params=None):
        """Alias for sending a PUT request."""
        return self._request(route, "PUT", params)
    def _postRequest(self, route, params=None):
        """Alias for sending a POST request."""
        return self._request(route, "POST", params)
    def _getRequest(self, route, params=None):
        """Alias for sending a GET request."""
        return self._request(route, "GET", params)

    def generateSession(self,clientCode,password):
        
        params={"clientcode":clientCode,"password":password}
        loginResultObject=self._postRequest("api.login",params)
        jwtToken=loginResultObject['data']['jwtToken']
        self.setAccessToken(jwtToken)
        refreshToken=loginResultObject['data']['refreshToken']
        self.setRefreshToken(refreshToken)
        user=self.getProfile(refreshToken)
    
        id=user['data']['clientcode']
        #id='D88311'
        print(id)

        self.setUserId(id)
        user['data']['jwtToken']="Bearer "+jwtToken
        user['data']['refreshToken']=refreshToken
        print("USER",user)
        return user
    
    def terminateSession(self,clientCode):
        logoutResponseObject=self._postRequest("api.logout",{"clientcode":clientCode})
        return logoutResponseObject

    def generateToken(self,refresh_token):
        response=self._postRequest('api.token',{"refreshToken":refresh_token})
        jwtToken=response['data']['jwtToken']
        self.setAccessToken(jwtToken)
        return response

    def renewAccessToken(self):

        # h = hashlib.sha256(self.api_key.encode("utf-8") + refresh_token.encode("utf-8") + access_token.encode("utf-8"))
        # checksum = h.hexdigest()

        response =self._postRequest('api.refresh', {
            "jwtToken": self.access_token,
            "refreshToken": self.refresh_token,
            #"checksum": checksum
        })
       
        tokenSet={}

        if "jwtToken" in response:
            tokenSet['jwtToken']=response['data']['jwtToken']
<<<<<<< HEAD
        tokenSet['clientcode']=self. userId   
=======
        tokenSet['clientcode']=self.userId
>>>>>>> d8cd1ced0e9e79452791072bec4213ec85e370b1
        tokenSet['refreshToken']=response['data']["refreshToken"]
       
        return tokenSet

    def getProfile(self,refreshToken):
        user=self._getRequest("api.user.profile",{"refreshToken":refreshToken})
        print("USER PROFILE",user)
        return user
    
    def placeOrder(self,orderparams):
        #params = {"exchange":orderparams.exchange,"symbolToken":orderparams.symboltoken,"transactionType":orderparams.transactionType,"quantity":orderparams.quantity,"price":orderparams.price,"productType":orderparams.producttype,"orderType":orderparams.ordertype,"duration":orderparams.duration,"variety":orderparams.variety,"tradingSymbol":orderparams.tradingsymbol,"triggerPrice":orderparams.trigger_price,"squareoff":orderparams.squareoff,"stoploss":orderparams.stoploss,"trailingStoploss":orderparams.trailing_stoploss,"tag":orderparams.tag}
        params=orderparams
       
        for k in list(params.keys()):
            if params[k] is None :
                del(params[k])
        
        orderResponse= self._postRequest("api.order.place", params)['data']['orderid']

        return orderResponse
    
    def modifyOrder(self,orderparams):
        params = orderparams

        for k in list(params.keys()):
            if params[k] is None:
                del(params[k])

        orderResponse= self._postRequest("api.order.modify", params)
        #order=Order(orderResponse)
        #order['orderId']=orderResponse['data']['orderid']
        return orderResponse
    
    def cancelOrder(self, order_id,variety):
        orderResponse= self._postRequest("api.order.cancel", {"variety": variety,"orderid": order_id})
        return orderResponse

    def ltpData(self,exchange,tradingsymbol,symboltoken):
        params={
            "exchange":exchange,
            "tradingsymbol":tradingsymbol,
            "symboltoken":symboltoken
        }
        ltpDataResponse= self._postRequest("api.ltp.data",params)
        return ltpDataResponse
    
    def orderBook(self):
        orderBookResponse=self._getRequest("api.order.book")
        return orderBookResponse
        

    def tradeBook(self):
        tradeBookResponse=self._getRequest("api.trade.book")
        return tradeBookResponse
    
    def rmsLimit(self):
        rmsLimitResponse= self._getRequest("api.rms.limit")
        return rmsLimitResponse
    
    def position(self):
        positionResponse= self._getRequest("api.position")
        return positionResponse

    def holding(self):
        holdingResponse= self._getRequest("api.holding")
        return holdingResponse
    
    def convertPosition(self,positionParams):
        params=positionParams
        for k in list(params.keys()):
            if params[k] is None:
                del(params[k])
        convertPositionResponse= self._postRequest("api.convert.position",params)

        return convertPositionResponse

    def _user_agent(self):
        return (__title__ + "-python/").capitalize() + __version__   

