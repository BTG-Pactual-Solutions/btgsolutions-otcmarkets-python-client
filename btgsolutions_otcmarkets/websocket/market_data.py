
from typing import Optional, List
from ..rest import Authenticator
from ..config import BASE_WS_URL, MAX_WS_RECONNECT_RETRIES
from .websocket_default_functions import _on_open, _on_message, _on_error, _on_close
import websocket 
import json
import ssl
import threading

def _default_callback_market_status(msg):
    message = msg["message"]
    status = message["status"]
    market_type = message["market"]
    print(f'Market is {status} for {market_type} orders')

def _default_callback_top_of_book_update(msg):
    tob = msg["message"]
    
    headers = ["Symbol", "Qty. Bid", "Vol. Bid", "Bid", "Offer", "Vol. Offer", "Qty. Offer", "Datetime"]
    data = [
        tob['symbol'],
        tob['size_buy'] if tob.get('size_buy') else 'N/A',
        round(tob['pu_buy'] * tob['size_buy'], 1) if tob.get('pu_buy') and tob.get('size_buy') else 'N/A',
        tob['rate_buy'] if tob.get('rate_buy') else 'N/A',
        tob['rate_sell'] if tob.get('rate_sell') else 'N/A',
        round(tob['pu_sell'] * tob['size_sell'], 1) if tob.get('pu_sell') and tob.get('size_sell') else 'N/A',
        tob['size_sell'] if tob.get('size_sell') else 'N/A',
        tob['timestamp'] if tob.get('timestamp') else 'N/A',
    ]

    col_widths = [max(len(header), len(str(value))) for header, value in zip(headers, data)]
    separator = "+" + "+".join('-' * (w + 2) for w in col_widths) + "+"

    print('Top Of Book update:')
    print(separator)
    print("| " + " | ".join(f"{header:{w}}" for header, w in zip(headers, col_widths)) + " |")
    print(separator)
    print("| " + " | ".join(f"{value:{w}}" for value, w in zip(data, col_widths)) + " |")
    print(separator)


class MarketDataStream:
    """
    This class connects with OTC Markets Market Data WebSocket, providing an easy way to access our real time market data feed.

    * Main use case:

    >>> from btgsolutions_otcmarkets import MarketDataStream
    >>> ws = MarketDataStream(
    >>>     api_key='YOUR_API_KEY',
    >>> )
    
    >>> ws.run()

    >>> ws.subscribe(['ZTEST01','ZTEST02'])
    
    >>> ws.unsubscribe(['ZTEST01'])

    >>> ws.close()

    Parameters
    ----------------
    api_key: str
        User identification key.
        Field is required.

    ssl: bool
        Enable or disable ssl configuration.
        Field is not required. Default: True (enable).
    """
    def __init__(
        self,
        api_key:str,
        ssl:Optional[bool] = True,
        **kwargs,
    ):
        self.api_key = api_key
        self.ssl = ssl

        self.__authenticator = Authenticator(self.api_key)
        self.__nro_reconnect_retries = 0

        self.url = BASE_WS_URL + "/stream/v1/btg-otc-mkts/mktdata"

        self.websocket_cfg = kwargs
    
    def run(
        self,
        on_tob_update=None,
        on_market_status=None,
        on_open=None,
        on_error=None,
        on_close=None,
        reconnect=True,
    ):
        """
        Initializes a connection to websocket and starts to receive high frequency news.

        Parameters
        ----------
        
        on_tob_update: function
            - Called every time it receives a top of book update message.
            - Arguments:
                1. Execution report message.
            - Field is not required.
            - Default: print message.

        on_market_status: function
            - Called every time it receives a market status message.
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

        if on_tob_update is None:
            on_tob_update = _default_callback_top_of_book_update
        if on_market_status is None:
            on_market_status = _default_callback_market_status
        if on_open is None:
            on_open = _on_open
        if on_error is None:
            on_error = _on_error
        if on_close is None:
            on_close = _on_close

        def intermediary_on_open(ws):
            on_open()
            self.__nro_reconnect_retries = 0

        def intermediary_on_message(ws, data):
            msg = json.loads(data)
            if msg["feed"] == "market-status":
                on_market_status(msg)
            elif msg["feed"] == "book":
                on_tob_update(msg)
            else:
                print(msg)

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
                self.run(on_tob_update, on_market_status, on_open, on_error, on_close, reconnect)

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
    
    def subscribe(self, tickers: List[str]):
        """
        Subscribe to start receiving market data updates about the provided ticker symbols, such as trades and book updates.

        Parameters
        ----------
        tickers: list[str]
            - List of tickers to subscribe.
            - Field is required.
        """
        if not isinstance(tickers, list):
            raise Exception("'tickers' parameter must be a list of strings")

        self.__send({'action':'subscribe', 'feed': 'book', 'symbols': tickers})

    def unsubscribe(self, tickers: List[str]):
        """
        Unsubscribe to stop receiving market data updates about the provided ticker symbols, such as trades and book updates.

        Parameters
        ----------
        tickers: list[str]
            - List of tickers to unsubscribe.
            - Field is required.
        """
        if not isinstance(tickers, list):
            raise Exception("'tickers' parameter must be a list of strings")

        self.__send({'action':'unsubscribe', 'feed': 'book', 'symbols': tickers})