from datetime import datetime
from typing import Any

from solven.models.financial_observation import (
    RawObservation,
    SECProvenance,
    StandardizedObservation,
)

TAXONOMY_MAP = {
    "Revenue": [
        "Revenues",
        "SalesRevenueNet",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
    ],
    "Net Income": [
        "NetIncomeLoss",
        "ProfitLoss",
    ],
    "Total Assets": [
        "Assets",
    ],
    "Total Liabilities": [
        "Liabilities",
    ],
    "Operating Cash Flow": [
        "NetCashProvidedByUsedInOperatingActivities",
    ],
    "Total Equity": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ],
}


class ExtractionError(Exception):
    """Raised when there is an issue extracting data."""

    pass


def extract_raw_observations(
    company_facts: dict[str, Any], concept: str, expected_tags: list[str]
) -> list[RawObservation]:
    """Extracts raw observations from SEC JSON payload for given US-GAAP tags."""
    observations = []
    cik = str(company_facts.get("cik", ""))
    us_gaap = company_facts.get("facts", {}).get("us-gaap", {})

    for tag in expected_tags:
        if tag in us_gaap:
            units_data = us_gaap[tag].get("units", {})
            for unit_key, facts in units_data.items():
                for fact in facts:
                    # Filter out purely projected/estimated facts if any exist
                    if "val" not in fact:
                        continue

                    prov = SECProvenance(
                        cik=cik,
                        concept=tag,
                        namespace="us-gaap",
                        form=fact.get("form", ""),
                        accession_number=fact.get("accn", ""),
                        filing_date=fact.get("filed", ""),
                    )

                    obs = RawObservation(
                        value=float(fact["val"]),
                        unit=unit_key,
                        start_date=fact.get("start"),  # Missing for instants
                        end_date=fact.get("end", ""),
                        fy=fact.get("fy", 0),
                        fp=fact.get("fp", ""),
                        frame=fact.get("frame"),
                        provenance=prov,
                    )
                    observations.append(obs)
    return observations


def _is_compatible_period(
    obs: RawObservation, target_fy: int, period: str, is_instant: bool
) -> bool:
    """Checks if a raw observation matches the target fiscal year and period type (annual vs quarterly)."""
    # Exclude invalid missing metadata if we rely on it
    if not obs.fy or not obs.end_date:
        return False

    if obs.fy != target_fy:
        return False

    # Handling annual vs quarterly logic
    # The SEC 'fp' field might indicate the filing it was presented in (e.g., Q1, FY)
    # However, 'frame' like CY2023 vs CY2023Q1 is more reliable if it exists
    if period == "annual":
        if is_instant:
            # For annual instants, look for 'FY' form or frame matches CY202X
            if obs.frame and len(obs.frame) == 6:  # e.g. CY2023
                return True
            # Fallback for instants without frames, checking FY and 'FY' fp
            if obs.fp == "FY":
                return True

            # Additional heuristic: checking if it is from a 10-K
            return obs.provenance.form == "10-K"
        else:
            # Duration concepts
            if not obs.start_date:
                return False
            # Check duration in days
            start = datetime.strptime(obs.start_date, "%Y-%m-%d")
            end = datetime.strptime(obs.end_date, "%Y-%m-%d")
            days = (end - start).days

            if 350 <= days <= 380:  # roughly a year
                return True

            # Check frame
            return bool(obs.frame is not None and len(obs.frame) == 6)

    # For now, we mainly support annual in 0.1.0 as requested, but keep quarterly structure open
    return False


def standardize_concept(
    concept_name: str,
    raw_observations: list[RawObservation],
    fy: int,
    period: str = "annual",
    policy: str = "latest_restated",
    is_instant: bool = False,
) -> StandardizedObservation | None:
    """
    Standardize a concept based on selection policy.

    Policies:
    - 'latest_restated': Pick the observation with the most recent filing_date.
    - 'as_reported': Pick the observation whose filing_date is earliest (or closely matches the end_date).
    """
    if not raw_observations:
        return None

    compatible_obs = [
        obs
        for obs in raw_observations
        if _is_compatible_period(obs, fy, period, is_instant)
    ]

    if not compatible_obs:
        return None

    # Sort by filing date
    compatible_obs.sort(
        key=lambda x: datetime.strptime(x.provenance.filing_date, "%Y-%m-%d")
    )

    if policy == "latest_restated":
        selected_raw = compatible_obs[-1]
    elif policy == "as_reported":
        selected_raw = compatible_obs[0]
    else:
        raise ValueError(f"Unknown policy: {policy}")

    return StandardizedObservation(
        concept_name=concept_name,
        value=selected_raw.value,
        unit=selected_raw.unit,
        start_date=selected_raw.start_date,
        end_date=selected_raw.end_date,
        fiscal_year=selected_raw.fy,
        fiscal_period=selected_raw.fp,
        provenance=selected_raw.provenance,
    )


def extract_standardized_financials(
    company_facts: dict[str, Any],
    fy: int,
    period: str = "annual",
    policy: str = "latest_restated",
) -> dict[str, StandardizedObservation | None]:
    """Extract all core standardized financials for a specific fiscal year and period."""
    results: dict[str, StandardizedObservation | None] = {}

    for concept, tags in TAXONOMY_MAP.items():
        raw_obs = extract_raw_observations(company_facts, concept, tags)
        is_instant = concept in ["Total Assets", "Total Liabilities", "Total Equity"]
        std_obs = standardize_concept(concept, raw_obs, fy, period, policy, is_instant)
        results[concept] = std_obs

    return results
