import json
import typing
from pathlib import Path

import pytest

from solven.processing.normalization import (
    extract_raw_observations,
    extract_standardized_financials,
    standardize_concept,
)


@pytest.fixture
def msft_facts() -> dict[str, typing.Any]:
    fixture_path = Path(__file__).parent / "fixtures" / "msft_company_facts.json"
    with open(fixture_path) as f:
        return typing.cast(dict[str, typing.Any], json.load(f))


def test_extract_raw_observations(msft_facts: dict[str, typing.Any]) -> None:
    raw = extract_raw_observations(msft_facts, "Revenue", ["Revenues"])
    assert len(raw) == 2
    assert raw[0].value == 211915000000.0


def test_standardize_concept_latest_restated(msft_facts: dict[str, typing.Any]) -> None:
    raw = extract_raw_observations(msft_facts, "Revenue", ["Revenues"])
    std = standardize_concept(
        "Revenue", raw, fy=2023, period="annual", policy="latest_restated"
    )
    assert std is not None
    assert std.value == 211915000000.0
    # Should pick the one filed in 2024
    assert std.provenance.filing_date == "2024-07-27"


def test_standardize_concept_as_reported(msft_facts: dict[str, typing.Any]) -> None:
    raw = extract_raw_observations(msft_facts, "Revenue", ["Revenues"])
    std = standardize_concept(
        "Revenue", raw, fy=2023, period="annual", policy="as_reported"
    )
    assert std is not None
    assert std.value == 211915000000.0
    # Should pick the one filed in 2023
    assert std.provenance.filing_date == "2023-07-27"


def test_extract_standardized_financials_annual(
    msft_facts: dict[str, typing.Any],
) -> None:
    financials = extract_standardized_financials(
        msft_facts, fy=2023, period="annual", policy="latest_restated"
    )

    assert financials["Revenue"] is not None
    assert financials["Total Assets"] is not None
    assert financials["Total Liabilities"] is not None
    assert financials["Total Equity"] is not None

    assert financials["Revenue"].value == 211915000000.0
    assert financials["Total Assets"].value == 411976000000.0
    assert financials["Total Liabilities"].value == 205753000000.0
    assert financials["Total Equity"].value == 206223000000.0
    # Net Income is absent in fixture, should be None
    assert financials.get("Net Income") is None
