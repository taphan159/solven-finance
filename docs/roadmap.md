# SOLVEN Roadmap

## Version 0.1.0 (Current)
- Foundational repository structure.
- Basic SEC EDGAR data retrieval.
- Core standardization logic for 5 primary metrics (Revenue, Net Income, Assets, Liabilities, Operating Cash Flow).
- Strict typing and financial integrity validation.

## Version 0.2.0 (Proposed Scope)
- **Quarterly Reporting:** Add full support and validation for quarterly (Q1, Q2, Q3) and year-to-date observations.
- **Taxonomy Expansion:** Expand taxonomy mapping to support more comprehensive Income Statement and Balance Sheet breakdown.
- **Pandas Integration:** Introduce Pandas DataFrames at the edge (CLI layer) for tabular historical analysis over multiple periods.
- **Local Caching:** Add a basic local file cache to prevent repeated SEC HTTP requests for the same Company Facts payload.

## Version 0.3.0 and beyond
- Ratio analysis and operating performance metrics.
- Output generation to Excel (`openpyxl`).
- Historical financial analysis.
- DCF valuation modules.
