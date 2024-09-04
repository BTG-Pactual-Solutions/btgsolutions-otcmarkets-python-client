import requests
import json
from typing import Optional
from ..config import BASE_REST_URL
from .authenticator import Authenticator

class Risk:
    """
    This class provides risk status information for a given trader or investor ID.

    * Main use case:

    >>> from btgsolutions_otcmarkets import Risk
    >>> risk = Risk(
    >>>     api_key='YOUR_API_KEY',
    >>> )

    >>> risk.risk_status_trader(
    >>>     investor='YOUR_INVESTOR_ID',
    >>> )

    >>> risk.risk_status_investor(
    >>>     investor='YOUR_INVESTOR_ID',
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

    def risk_status_trader(
        self,
        investor_id: str,
    ):
        """
        This method provides trader current risk status for a given Investor ID.

        Parameters
        ----------------
        investor_id: string
            Investor ID. You can locate this information at upper right corner in the OTC platform UI.
            Field is required. Example: 'MyInvestorID'.
        """
        if not isinstance(investor_id, str):
            raise Exception(f'Must provide a valid investor')

        url = f"{BASE_REST_URL}/api/v1/btg-otc-mkts/risk-status/trader?investor={investor_id}"

        response = requests.request("GET", url,  headers=self.headers)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            return response_data

        response = json.loads(response.text)
        raise Exception(f'Error: {response.get("message", "")}.')

    def risk_status_investor(
        self,
        investor_id: str,
    ):
        """
        This method provides investor current risk status for a given Investor ID.

        Parameters
        ----------------
        investor_id: string
            Investor ID. You can locate this information at upper right corner in the OTC platform UI.
            Field is required. Example: 'MyInvestorID'.
        """
        if not isinstance(investor_id, str):
            raise Exception(f'Must provide a valid investor')

        url = f"{BASE_REST_URL}/api/v1/btg-otc-mkts/risk-status/investor?investor={investor_id}"

        response = requests.request("GET", url, headers=self.headers)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            return response_data

        response = json.loads(response.text)
        raise Exception(f'Error: {response.get("message", "")}.')
