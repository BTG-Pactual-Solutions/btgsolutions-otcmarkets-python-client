import requests
import json
import pandas as pd
from typing import Optional
from ..config import BASE_REST_URL
from .authenticator import Authenticator

class Pricing:
    """
    This class provides asset pricing.

    * Main use case:

    >>> from btgsolutions_otcmarkets import Pricing
    >>> pricing = Pricing(
    >>>     api_key='YOUR_API_KEY',
    >>> )

    >>> pricing.get_ticker_price(
    >>>     ticker='ZTEST01',
    >>>     rate=6.41,
    >>> )

    >>> pricing.get_ticker_rate(
    >>>     ticker='ZTEST01',
    >>>     price=952.32,
    >>> )

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

    def get_ticker_price(
        self,
        ticker: str,
        rate: float,
        date: str=None,
    ):
        """
        This method calculates ticker unit price for a given rate.

        Parameters
        ----------------
        ticker: string
            Asset ticker.
            Field is required. Example: 'ZTEST01'.
        rate: float
            Desired rate. Expressed in percentage (6.41% would be represented as 6.41).
            Field is required. Example: 6.41.
        date: string
            Desired date, in "YYYY-MM-DD" format.
            Field is not required. Default: today, represented in "YYYY-MM-DD" format.
        """

        url = f"{BASE_REST_URL}/api/v1/btg-otc-mkts/pricing/pu?ticker={ticker}&rate={rate}"
        if isinstance(date, str):
            url += f'&date={date}'

        response = requests.request("GET", url,  headers=self.headers)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            return response_data

        response = json.loads(response.text)
        raise Exception(f'Error: {response.get("ApiClientError", "")}.\nSuggested action: {response.get("SuggestedAction", "")}.')

    def get_ticker_rate(
        self,
        ticker: str,
        price: float,
        date: str=None,
    ):
        """
        This method calculates asset rate for a given unit price.

        Parameters
        ----------------
        ticker: string
            Asset ticker.
            Field is required. Example: 'ZTEST01'.
        price: float
            Desired unit price. Expressed in absolute value (R$923,70 would be represented as 923.7).
            Field is required. Example: 923.7.
        date: string
            Desired date, in "YYYY-MM-DD" format.
            Field is not required. Default: today, represented in "YYYY-MM-DD" format.
        """

        url = f"{BASE_REST_URL}/api/v1/btg-otc-mkts/pricing/rate?ticker={ticker}&pu={price}"
        if isinstance(date, str):
            url += f'&date={date}'

        response = requests.request("GET", url,  headers=self.headers)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            return response_data

        response = json.loads(response.text)
        raise Exception(f'Error: {response.get("ApiClientError", "")}.\nSuggested action: {response.get("SuggestedAction", "")}.')
