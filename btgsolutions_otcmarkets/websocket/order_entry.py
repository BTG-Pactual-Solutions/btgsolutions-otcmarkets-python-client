
from typing import Optional, List
from ..rest import Authenticator
from ..config import BASE_WS_URL, MAX_WS_RECONNECT_RETRIES
from .websocket_default_functions import _on_open, _on_message, _on_error, _on_close
import websocket 
import json
import ssl
import threading

def _default_callback_exec_report(msg):
    print('new execution report:')
    print(msg)

def _default_callback_acknowledgement(msg):
    print('new message acknowledgement:')
    print(msg)


class OrderEntry:
    """
    This class connects with OTC Markets Order Entry WebSocket, providing an easy way to send orders.

    * Main use case:

    >>> from btgsolutions_otcmarkets import OrderEntry
    >>> order_entry = OrderEntry(
    >>>     api_key='YOUR_API_KEY',
    >>>     investor_id='YOUR_INVESTOR_ID',
    >>> )

    >>> order_entry.run()

    >>> order_entry.create_new_order(
        order_temp_id='123',
        ticker='ZTEST01',
        rate=10.6,
        qty=11000,
        side='sell',
        req_id='1',
    )
    
    >>> order_entry.replace_order(
        external_id='9ef1d212-5daf-439b-b51e-9801d8e492be',
        rate=6.72,
        qty=100,
        req_id='12',
    )
    
    >>> order_entry.cancel_order(
        external_id='9ef1d212-5daf-439b-b51e-9801d8e492be',
        req_id='123',
    )
    
    >>> order_entry.close()

    Parameters
    ----------------
    api_key: str
        User identification key.
        Field is required.

    investor_id: str
        - Investor ID.
        - Field is required.

    ssl: bool
        Enable or disable ssl configuration.
        Field is not required. Default: True (enable).
    """
    def __init__(
        self,
        api_key:str,
        investor_id:str,
        ssl:Optional[bool] = True,
        **kwargs,
    ):
        if not isinstance(investor_id, str):
            raise Exception("'investor_id' parameter must be a string")

        self.api_key = api_key
        self.investor_id = investor_id
        self.ssl = ssl

        self.__authenticator = Authenticator(self.api_key)
        self.__nro_reconnect_retries = 0

        self.url = BASE_WS_URL + "/stream/v1/btg-otc-mkts/order-entry"

        self.websocket_cfg = kwargs
    
    def run(
        self,
        on_exec_report=None,
        on_acknowledgement=None,
        on_open=None,
        on_error=None,
        on_close=None,
        reconnect=True,
    ):
        """
        Initializes a connection to websocket and starts to receive high frequency news.

        Parameters
        ----------        
        on_exec_report: function
            - Called every time it receives an order execution report message.
            - Arguments:
                1. Execution report message.
            - Field is not required.
            - Default: print message.

        on_acknowledgement: function
            - Called every time it receives an acknowledgement message. An acknowledgement message is a feedback message sent from server, whenever a client sends a message to it.
            - Arguments:
                1. Execution report message.
            - Field is not required.
            - Default: print message.

        on_open: function
            - Called at opening connection to websocket.
            - Field is not required. 
            - Default: prints 'open connection', in case of success.

        on_error: function
            - Called when a error occurs.
            - Arguments: 
                1. Exception object.
            - Field is not required. 
            - Default: prints error.

        on_close: function
            - Called when connection is closed.
            - Arguments: 
                1. close_status_code.
                2. close_msg.
            - Field is not required. 
            - Default: prints 'closed connection'.

        reconnect: bool
            Try reconnect if connection is closed.
            Field is not required.
            Default: True.
        """

        if on_exec_report is None:
            on_exec_report = _default_callback_exec_report
        if on_acknowledgement is None:
            on_acknowledgement = _default_callback_acknowledgement
        if on_open is None:
            on_open = _on_open
        if on_error is None:
            on_error = _on_error
        if on_close is None:
            on_close = _on_close

        def intermediary_on_message(ws, data):
            msg = json.loads(data)

            if msg["message"] == "execution report":
                on_exec_report(msg)
            elif msg.get("req_id"):
                on_acknowledgement(msg)
            else:
                print(msg)

        def intermediary_on_open(ws):
            on_open()
            self.__nro_reconnect_retries = 0

        def intermediary_on_error(ws, error):
            on_error(error)

        def intermediary_on_close(ws, close_status_code, close_msg):
            on_close(close_status_code, close_msg)
            
            if reconnect:
                if self.__nro_reconnect_retries == MAX_WS_RECONNECT_RETRIES:
                    print(f"### Fail retriyng reconnect")
                    return
                self.__nro_reconnect_retries +=1
                print(f"### Reconnecting.... Attempts: {self.__nro_reconnect_retries}/{MAX_WS_RECONNECT_RETRIES}")
                self.run(on_exec_report, on_acknowledgement, on_open, on_error, on_close, reconnect)

        self.ws = websocket.WebSocketApp(
            url=self.url,
            on_open=intermediary_on_open,
            on_message=intermediary_on_message,
            on_error=intermediary_on_error,
            on_close=intermediary_on_close,
            header={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
                "Sec-WebSocket-Protocol": self.__authenticator.token,
            }
        )

        ssl_conf = {} if self.ssl else {"sslopt": {"cert_reqs": ssl.CERT_NONE}}
        wst = threading.Thread(target=self.ws.run_forever, kwargs=ssl_conf)
        wst.daemon = True
        wst.start()

        while True:
            if self.ws.sock is not None and self.ws.sock.connected:
                break
            pass

    def __send(self, data):
        """
        Class method to be used internally. Sends data to websocket.
        """
        if not isinstance(data, str):
            data = json.dumps(data)   
        print(f'Sending data: {data}')
        return self.ws.send(data)
    
    def close(self):
        """
        Closes connection with websocket.
        """
        self.ws.close()
    
    def create_new_order(
        self,
        order_temp_id: str,
        ticker: str,
        rate: float,
        qty: int,
        side: str,
        req_id: str = '1',
    ):
        """
        Create a new DMA order.

        Parameters
        ----------        
        order_temp_id: str
            - Temporary order ID. The temporary order ID will be used to identify the order requested by the client untill the same receives an Execution Report message informing the permanent order ID 'external_id'.
            - Field is required.
        
        ticker: str
            - Asset ticker symbol.
            - Field is required.
        
        rate: float
            - Order rate.
            - Field is required.
        
        qty: int
            - Order quantity.
            - Field is required.
        
        side: str
            - Order side.
            - Field is required.
            - Available values: 'buy', 'sell'.
        
        req_id: str
            - Message request ID.
            - Field is not required.
            - Default value: '1'
        """
        new_order = {
            'type': 'NewOrder',
            'req_id': req_id,
            'params': [
                {
                    'investor_id': self.investor_id,
                    'tmp_ext_id': order_temp_id,
                    'symbol': ticker,
                    'rate': rate,
                    'qty': qty,
                    'side': side,
                    'order_type': 'limit',
                }
            ]
        }

        self.__send(new_order)
    
    def replace_order(
        self,
        external_id: str,
        rate: float,
        qty: int,
        req_id: str = '1',
    ):
        """
        Replace a DMA order.

        Parameters
        ----------        
        external_id: str
            - Order External ID, that remains throughout the order lifecycle.
            - Field is required.
        
        rate: float
            - Order rate.
            - Field is not required.
        
        qty: int
            - Order quantity.
            - Field is not required.
        
        req_id: str
            - Message request ID.
            - Field is not required.
            - Default value: '1'
        """
        replace_order = {
            'type': 'ReplaceOrder',
            'req_id': req_id,
            'params': [
                {
                    'investor_id': self.investor_id,
                    'external_id': external_id,
                    'rate': rate,
                    'qty': qty,
                }
            ]
        }

        self.__send(replace_order)

    def cancel_order(
        self,
        external_id: str,
        req_id: str = '1',
    ):
        """
        Cancel a DMA order.

        Parameters
        ----------        
        external_id: str
            - Order External ID, that remains throughout the order lifecycle.
            - Field is required.

        req_id: str
            - Message request ID.
            - Field is not required.
            - Default value: '1'
        """
        cancel_order = {
            'type': 'CancelOrder',
            'req_id': req_id,
            'params': [
                {
                    'investor_id': self.investor_id,
                    'external_id': external_id,
                }
            ]
        }

        self.__send(cancel_order)