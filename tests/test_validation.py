import pytest

from solven.models.financial_observation import SECProvenance, StandardizedObservation
from solven.processing.validation import (
    ValidationError,
    validate_accounting_identity,
    validate_metadata,
)


def create_mock_obs(
    concept_name: str,
    value: float,
    is_instant: bool = False,
    start_date: str | None = "2022-07-01",
) -> StandardizedObservation:
    prov = SECProvenance(
        cik="123",
        concept="Tag",
        namespace="us-gaap",
        form="10-K",
        accession_number="000-123",
        filing_date="2023-01-01",
    )
    return StandardizedObservation(
        concept_name=concept_name,
        value=value,
        unit="USD",
        start_date=None if is_instant else start_date,
        end_date="2023-06-30",
        fiscal_year=2023,
        fiscal_period="FY",
        provenance=prov,
    )


def test_validate_accounting_identity_success() -> None:
    financials = {
        "Total Assets": create_mock_obs("Total Assets", 100.0, is_instant=True),
        "Total Liabilities": create_mock_obs(
            "Total Liabilities", 60.0, is_instant=True
        ),
        "Total Equity": create_mock_obs("Total Equity", 40.0, is_instant=True),
    }
    validate_accounting_identity(financials)  # Should not raise


def test_validate_accounting_identity_failure() -> None:
    financials = {
        "Total Assets": create_mock_obs("Total Assets", 100.0, is_instant=True),
        "Total Liabilities": create_mock_obs(
            "Total Liabilities", 60.0, is_instant=True
        ),
        "Total Equity": create_mock_obs(
            "Total Equity", 50.0, is_instant=True
        ),  # 60 + 50 != 100
    }
    with pytest.raises(ValidationError, match="Accounting identity violated"):
        validate_accounting_identity(financials)


def test_validate_metadata_missing_start_date_for_duration() -> None:
    financials = {
        "Revenue": create_mock_obs("Revenue", 100.0, is_instant=False, start_date=None)
    }
    with pytest.raises(ValidationError, match="is missing a start_date"):
        validate_metadata(financials)


def test_validate_metadata_success() -> None:
    financials = {
        "Revenue": create_mock_obs("Revenue", 100.0, is_instant=False),
        "Total Assets": create_mock_obs("Total Assets", 100.0, is_instant=True),
    }
    validate_metadata(financials)  # Should not raise
