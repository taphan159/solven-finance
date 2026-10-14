# SOLVEN Architecture

## Overview
SOLVEN is built on a clean, modular architecture, adhering to separation of concerns.

### `solven.data`
- Handles all external communication.
- Currently contains `sec_client.py` using `httpx` to fetch raw Company Facts.

### `solven.models`
- Contains the core data structures using plain Python `dataclasses`.
- `financial_observation.py` holds definitions for `RawObservation`, `StandardizedObservation`, and `SECProvenance`.

### `solven.processing`
- Contains financial logic, purely functional.
- `normalization.py`: Maps SEC taxonomy tags to standardized concepts and applies data selection policies.
- `validation.py`: Asserts financial integrity (e.g., Accounting Identity) and metadata completeness.

### Data Flow
1. `cli.py` triggers `SECClient`.
2. Raw JSON facts are fetched and passed to `normalization.py`.
3. `RawObservation`s are extracted and filtered by period.
4. Selection policies (`latest_restated`, `as_reported`) resolve overlaps.
5. Standardized measures are outputted as `StandardizedObservation`s and passed to `validation.py`.
6. Safe, verifiable financial data is displayed to the user or saved as JSON.
