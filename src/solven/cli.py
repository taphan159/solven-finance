import argparse
import json
import sys
from dataclasses import asdict
from typing import Any

from solven.data.sec_client import SECAPIError, SECClient
from solven.processing.normalization import extract_standardized_financials
from solven.processing.validation import ValidationError, validate_financials


def format_currency(value: float, unit: str) -> str:
    """Format large numbers for display."""
    if unit == "USD":
        if value >= 1_000_000_000:
            return f"${value / 1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            return f"${value / 1_000_000:.2f}M"
        return f"${value:,.2f}"
    return f"{value} {unit}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SOLVEN — Financial Intelligence Engine",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch_parser = subparsers.add_parser(
        "fetch", help="Fetch financial facts for a CIK"
    )
    fetch_parser.add_argument(
        "cik", type=str, help="10-digit SEC CIK (e.g. 0000789019 for MSFT)"
    )
    fetch_parser.add_argument(
        "--period",
        type=str,
        default="annual",
        choices=["annual"],
        help="Reporting period",
    )
    fetch_parser.add_argument(
        "--fy", type=int, required=True, help="Target fiscal year (e.g. 2023)"
    )
    fetch_parser.add_argument(
        "--policy",
        type=str,
        default="latest_restated",
        choices=["latest_restated", "as_reported"],
        help="Data selection policy",
    )
    fetch_parser.add_argument("--json", type=str, help="Path to save output as JSON")

    args = parser.parse_args()

    if args.command == "fetch":
        client = SECClient()
        try:
            print(f"Fetching SEC facts for CIK {args.cik}...")
            facts = client.fetch_company_facts(args.cik)

            print(
                f"Extracting financials for FY {args.fy} ({args.period}, {args.policy})..."
            )
            financials = extract_standardized_financials(
                facts, fy=args.fy, period=args.period, policy=args.policy
            )

            # Validate
            try:
                validate_financials(financials)
                print("[OK] Validation passed (Metadata & Accounting Identities).\n")
            except ValidationError as ve:
                print(f"[WARNING] Validation Failed: {ve}\n", file=sys.stderr)

            # Display
            output_dict: dict[str, Any] = {}
            print(f"{'Concept':<20} | {'Value':<15} | {'Prov: Tag / Accession'}")
            print("-" * 75)
            for concept, obs in financials.items():
                if obs:
                    val_str = format_currency(obs.value, obs.unit)
                    tag_acc = f"{obs.provenance.concept} / {obs.provenance.accession_number[:10]}..."
                    print(f"{concept:<20} | {val_str:<15} | {tag_acc}")
                    output_dict[concept] = asdict(obs)
                else:
                    print(f"{concept:<20} | {'--':<15} | Not Found / Ambiguous")
                    output_dict[concept] = None

            if args.json:
                with open(args.json, "w") as f:
                    json.dump(output_dict, f, indent=2)
                print(f"\nSaved JSON output to {args.json}")

        except SECAPIError as e:
            print(f"Error fetching data: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
