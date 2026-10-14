from typing import Mapping
from solven.models.financial_observation import StandardizedObservation


class ValidationError(Exception):
    pass


def validate_accounting_identity(
    financials: Mapping[str, StandardizedObservation | None],
) -> None:
    """
    Validates that Total Assets = Total Liabilities + Total Equity.
    Raises ValidationError if the identity is violated and all three metrics are present.
    """
    assets = financials.get("Total Assets")
    liabilities = financials.get("Total Liabilities")
    equity = financials.get("Total Equity")

    if assets and liabilities and equity:
        # Check if they are in the same unit
        if not (assets.unit == liabilities.unit == equity.unit):
            raise ValidationError("Unit mismatch in accounting identity check.")

        # Allow a small float tolerance
        diff = abs(assets.value - (liabilities.value + equity.value))
        if diff > 1.0:  # Allow 1 unit difference for rounding
            raise ValidationError(
                f"Accounting identity violated: Assets ({assets.value}) != "
                f"Liabilities ({liabilities.value}) + Equity ({equity.value})"
            )


def validate_metadata(financials: Mapping[str, StandardizedObservation | None]) -> None:
    """
    Ensure that any standardized value retains its provenance and has valid dates.
    """
    for concept, obs in financials.items():
        if obs is None:
            continue

        if not obs.end_date:
            raise ValidationError(f"Missing end_date for {concept}")

        if not obs.provenance.accession_number:
            raise ValidationError(f"Missing SEC accession number for {concept}")

        if not obs.is_instant and not obs.start_date:
            raise ValidationError(f"Duration concept {concept} is missing a start_date")


def validate_financials(
    financials: Mapping[str, StandardizedObservation | None],
) -> None:
    """Runs all validation checks on extracted financials."""
    validate_metadata(financials)
    validate_accounting_identity(financials)
