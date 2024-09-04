import requests
import json
import pandas as pd
from typing import Optional
from ..config import BASE_REST_URL
from .authenticator import Authenticator

class TopOfBook:
    """
    This class provides the Top Of Book for all tickers that have at least 1 placed order.

    * Main use case:

    >>> from btgsolutions_otcmarkets import TopOfBook
    >>> tob = TopOfBook(
    >>>     api_key='YOUR_API_KEY',
    >>> )

    >>> tob.get_top_of_book(
    >>>     ticker='ZTEST01',
    >>> )

    >>> tob.get_top_of_book()

    Parameters
    ----------------
    api_key: str
        User identification key.
        Field is required.
    """
    def __init__(
        self,
        api_key: Optional[str]
    ):
        self.api_key = api_key
        self.token = Authenticator(self.api_key).token
        self.headers = {"authorization": f"Bearer {self.token}"}

    def get_top_of_book(
        self,
        ticker: str = None,
        raw_data: bool = False,
    ):
        """
        This method provides the Top Of Book for a given ticker. If no ticker is provided, it returns the Top Of Book for all tickers that have at least 1 placed order.

        Parameters
        ----------------
        ticker: string
            Asset ticker.
            Field is required. Example: 'ZTEST01'.
        
        raw_data: bool
            If false, returns data in a dataframe. If true, returns raw data.
            Field is not required. Default: False.
        """
        if isinstance(ticker, str):
            single_ticker = True
            url = f"{BASE_REST_URL}/api/v1/btg-otc-mkts/mktdata/top-book?symbol={ticker}"
        else:
            single_ticker = False
            url = f"{BASE_REST_URL}/api/v1/btg-otc-mkts/mktdata/top-book/all"
        
        response = requests.request("GET", url,  headers=self.headers)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            if raw_data:
                return response_data
            else:
                if single_ticker:
                    return pd.DataFrame([response_data])
                else:
                    return pd.DataFrame(response_data)

        response = json.loads(response.text)
        raise Exception(f'Error: {response.get("detail", "")}.')
