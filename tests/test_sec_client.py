import httpx
import pytest
import respx

from solven.data.sec_client import SECAPIError, SECClient


@respx.mock
def test_fetch_company_facts_success() -> None:
    client = SECClient()
    mock_response = {"cik": 789019, "facts": {}}
    respx.get("https://data.sec.gov/api/xbrl/companyfacts/CIK0000789019.json").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    data = client.fetch_company_facts("0000789019")
    assert data == mock_response


@respx.mock
def test_fetch_company_facts_403_forbidden() -> None:
    client = SECClient()
    respx.get("https://data.sec.gov/api/xbrl/companyfacts/CIK0000789019.json").mock(
        return_value=httpx.Response(403)
    )

    with pytest.raises(SECAPIError, match="SEC API Access Forbidden"):
        client.fetch_company_facts("0000789019")


@respx.mock
def test_fetch_company_facts_404_not_found() -> None:
    client = SECClient()
    respx.get("https://data.sec.gov/api/xbrl/companyfacts/CIK0000789019.json").mock(
        return_value=httpx.Response(404)
    )

    with pytest.raises(SECAPIError, match="not found \\(404\\)"):
        client.fetch_company_facts("0000789019")


@respx.mock
def test_fetch_company_facts_network_error() -> None:
    client = SECClient()
    respx.get("https://data.sec.gov/api/xbrl/companyfacts/CIK0000789019.json").mock(
        side_effect=httpx.ConnectError("Network is unreachable")
    )

    with pytest.raises(SECAPIError, match="Network error"):
        client.fetch_company_facts("0000789019")
