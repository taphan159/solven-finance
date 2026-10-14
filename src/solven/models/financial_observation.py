from dataclasses import dataclass


@dataclass(frozen=True)
class SECProvenance:
    """Tracks the origin of a financial observation within SEC filings."""

    cik: str
    concept: str  # e.g., 'NetIncomeLoss'
    namespace: str  # e.g., 'us-gaap'
    form: str  # e.g., '10-K', '10-Q'
    accession_number: str
    filing_date: str


@dataclass(frozen=True)
class RawObservation:
    """A single raw financial fact from the SEC Company Facts API."""

    value: float
    unit: str  # e.g., 'USD'
    start_date: str | None  # None for instant concepts
    end_date: str
    fy: int  # Fiscal year
    fp: str  # Fiscal period (e.g., 'FY', 'Q1')
    frame: str | None  # e.g., 'CY2023', 'CY2023Q1'
    provenance: SECProvenance


@dataclass(frozen=True)
class StandardizedObservation:
    """A financial observation mapped to a SOLVEN standardized concept."""

    concept_name: str  # e.g., 'Revenue', 'Net Income'
    value: float
    unit: str
    start_date: str | None
    end_date: str
    fiscal_year: int
    fiscal_period: str
    provenance: SECProvenance

    @property
    def is_instant(self) -> bool:
        """True if the concept is measured at a point in time (e.g., balance sheet)."""
        return self.concept_name in [
            "Total Assets",
            "Total Liabilities",
            "Total Equity",
        ]
