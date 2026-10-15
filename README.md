# SOLVEN — Financial Intelligence Engine

> **Clarity in complexity.**

SOLVEN is a new open-source Python financial intelligence and modeling engine. It transforms SEC financial disclosures into standardized, auditable financial data.

## Brand Identity
SOLVEN adheres to the "01 — Warm Espresso" palette:
- Canvas: `#F6F3ED`
- Primary: `#302820`
- Secondary: `#A79B8D`
- Accent: `#B57B57`

*The visual direction is warm, minimalist, editorial, understated, and premium.*

## Version 0.1.0 Features

- **SEC API Client:** Fetches raw Company Facts via EDGAR.
- **Financial Observation Model:** Retains full SEC provenance (accession number, form, filing date).
- **Standardization:** Extracts core metrics (Revenue, Net Income, Assets, Liabilities, Operating Cash Flow).
- **Data Selection Policies:** Supports `latest_restated` and `as_reported`.
- **Integrity Validation:** Performs metadata and accounting identity checks.
- **CLI Interface:** Basic command-line access.

## Setup and Installation

Requirements: Python 3.12+

```bash
git clone https://github.com/solven-finance/solven.git
cd solven
pip install -e .[dev]
```

## Usage

Set your user agent environment variable (required by the SEC):
```bash
export SOLVEN_SEC_USER_AGENT="YourProjectName YourEmail@domain.com"
```

Fetch Microsoft (MSFT) annual financials for Fiscal Year 2023:
```bash
solven fetch 0000789019 --fy 2023 --period annual --policy latest_restated --json msft_2023.json
```

## Running Tests

```bash
pytest
```

## License

MIT License
