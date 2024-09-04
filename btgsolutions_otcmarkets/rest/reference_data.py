import requests
import json
import pandas as pd
from typing import Optional
from ..config import BASE_REST_URL
from .authenticator import Authenticator

class ReferenceData:
    """
    This class provides the Top Of Book for all tickers that have at least 1 placed order.

    * Main use case:

    >>> from btgsolutions_otcmarkets import ReferenceData
    >>> ref = ReferenceData(
    >>>     api_key='YOUR_API_KEY',
    >>> )

    >>> ref.get_ticker_data()

    >>> ref.get_ticker_data(
    >>>     tickers=['ZTEST01','ZTEST02'],
    >>> )

    >>> ref.get_ticker_data_paginated(
    >>>     page=1,
    >>>     size=50,
    >>> )

    >>> ref.get_available_tickers()

    >>> ref.get_market_status()

    >>> ref.get_holidays()

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

    def get_ticker_data(
        self,
        tickers: list=[],
        raw_data: bool=False,
    ):
        """
        This method provides ticker data for all available tickers. One can filter by an array of tickers if want.

        Parameters
        ----------------
        tickers: list
            Array of strings, each string representing a single ticker. Example: ['ZTEST01','ZTEST02'].
            Field is not required. Default: Empty list.
        raw_data: bool
            If false, returns data in a dataframe. If true, returns raw data.
            Field is not required. Default: False.
        """

        url = f"{BASE_REST_URL}/api/v1/btg-otc-mkts/mktdata/instrument/all?pagination=False"
        for ticker in tickers:
            if not isinstance(ticker, str):
                raise Exception("'tickers' must be an array of strings")
            url += f'&symbols={ticker}'

        response = requests.request("GET", url,  headers=self.headers)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            return response_data if raw_data else pd.DataFrame(response_data)

        response = json.loads(response.text)
        raise Exception(f'Error: {response.get("detail", "")}.')
    
    def get_ticker_data_paginated(
        self,
        page: int,
        size: int,
    ):
        """
        This method provides paginated ticker data for all available tickers. One must specify the desired page number and page size.

        Parameters
        ----------------
        page: int
            Page number.
            Field is required.
        size: int
            Page size (number of records in a page).
            Field is required.
        """
        if not isinstance(page, int) or not isinstance(size, int):
            raise Exception('Must provide a valid page and a valid size')

        url = f"{BASE_REST_URL}/api/v1/btg-otc-mkts/mktdata/instrument/all?pagination=True&page={page}&size={size}"

        response = requests.request("GET", url,  headers=self.headers)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            return response_data

        response = json.loads(response.text)
        raise Exception(f'Error: {response.get("detail", "")}.')

    def get_available_tickers(
        self,
    ):
        """
        This method provides a list of all tickers available for trading.
        """

        url = f"{BASE_REST_URL}/api/v1/btg-otc-mkts/mktdata/instrument/availables"

        response = requests.request("GET", url,  headers=self.headers)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            return response_data

        response = json.loads(response.text)
        raise Exception(f'Error: {response.get("detail", "")}.')

    def get_market_status(
        self,
    ):
        """
        This method provides opening and closing time for DMA and Algo orders. It also returns OTC Markets server current time.
        """

        url = f"{BASE_REST_URL}/api/v1/btg-otc-mkts/market-status/opening-time"

        response = requests.request("GET", url,  headers=self.headers)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            return response_data

        response = json.loads(response.text)
        raise Exception(f'Error: {response.get("detail", "")}.')

    def get_holidays(
        self,
        raw_data: bool=False,
    ):
        """
        This method provides Top Of Book for all tickers that have at least 1 placed order.

        Parameters
        ----------------
        raw_data: bool
            If false, returns data in a dataframe. If true, returns raw data.
            Field is not required. Default: False.
        """

        url = f"{BASE_REST_URL}/api/v1/btg-otc-mkts/calendar/holidays"

        response = requests.request("GET", url,  headers=self.headers)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            return response_data if raw_data else pd.DataFrame(response_data)

        response = json.loads(response.text)
        raise Exception(f'Error: {response.get("detail", "")}.')
