import time
from typing import Any

import httpx

from solven.config import config


class SECAPIError(Exception):
    """Exception raised for SEC API related errors."""

    pass


class SECClient:
    """Client for retrieving financial data from the SEC EDGAR API."""

    BASE_URL = "https://data.sec.gov/api/xbrl/companyfacts"
    RATE_LIMIT_DELAY = 0.11  # ~9 requests per second to stay under 10/sec SEC limit

    def __init__(self) -> None:
        self._last_request_time = 0.0

    def _wait_for_rate_limit(self) -> None:
        """Enforce SEC fair-access guidelines."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - elapsed)

    def fetch_company_facts(self, cik: str) -> dict[str, Any]:
        """
        Fetch company facts for a given CIK.

        Args:
            cik: The 10-digit Central Index Key (e.g., '0000789019' for MSFT)

        Returns:
            The JSON response from the SEC API.
        """
        # Ensure CIK is padded to 10 digits as required by the SEC API
        padded_cik = str(cik).zfill(10)
        url = f"{self.BASE_URL}/CIK{padded_cik}.json"

        headers = {
            "User-Agent": config.sec_user_agent,
            "Accept-Encoding": "gzip, deflate",
        }

        self._wait_for_rate_limit()

        try:
            with httpx.Client(timeout=config.sec_api_timeout) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                self._last_request_time = time.time()
                data = response.json()
                if not isinstance(data, dict):
                    raise SECAPIError("Invalid JSON response format")
                return data
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                raise SECAPIError(
                    "SEC API Access Forbidden (403). Check your User-Agent format."
                ) from e
            elif e.response.status_code == 404:
                raise SECAPIError(f"CIK {cik} not found (404).") from e
            elif e.response.status_code == 429:
                raise SECAPIError("Rate limit exceeded (429).") from e
            raise SECAPIError(f"HTTP Error {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise SECAPIError(f"Network error while connecting to SEC API: {e}") from e
        except Exception as e:
            raise SECAPIError(f"Unexpected error: {e}") from e
