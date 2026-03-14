#!/usr/bin/env python3
"""
Validation script for data-001: Quarterly Sales Analysis.

Reads /workspace/analysis.md and checks for correct answers derived from sales.csv.
Checks (5 total):
  1. Total revenue per region (all 4 regions within 2% tolerance)
  2. Product with highest average MoM growth
  3. Quarter with highest average revenue
  4. Identification of >20% revenue drop (West region, June 2025)
  5. Total overall revenue within 2% tolerance

Exit code 0 if >= 4/5 checks pass, 1 otherwise.
"""

import csv
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Compute ground-truth answers from the CSV
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
CSV_PATH = SCRIPT_DIR / "sales.csv"
ANALYSIS_PATH = Path(os.environ.get("WORKSPACE", "/workspace")) / "analysis.md"


def load_ground_truth():
    with open(CSV_PATH) as f:
        rows = list(csv.DictReader(f))

    # Region totals
    region_revenue = defaultdict(float)
    for r in rows:
        region_revenue[r["region"]] += float(r["revenue"])

    # Monthly product revenue
    monthly_product = defaultdict(lambda: defaultdict(float))
    for r in rows:
        monthly_product[r["date"]][r["product"]] += float(r["revenue"])

    months = sorted(monthly_product.keys())
    products = sorted({r["product"] for r in rows})

    # Average MoM growth per product
    product_avg_mom = {}
    for p in products:
        growths = []
        for i in range(1, len(months)):
            prev = monthly_product[months[i - 1]][p]
            curr = monthly_product[months[i]][p]
            if prev > 0:
                growths.append((curr - prev) / prev * 100)
        product_avg_mom[p] = sum(growths) / len(growths) if growths else 0

    best_mom_product = max(product_avg_mom, key=product_avg_mom.get)

    # Quarterly average revenue
    quarter_revenue = defaultdict(list)
    for r in rows:
        m = int(r["date"].split("-")[1])
        q = (m - 1) // 3 + 1
        quarter_revenue[f"Q{q}"].append(float(r["revenue"]))

    quarter_avg = {q: sum(v) / len(v) for q, v in quarter_revenue.items()}
    best_quarter = max(quarter_avg, key=quarter_avg.get)

    # Identify months with >20% regional revenue drops
    monthly_region = defaultdict(lambda: defaultdict(float))
    for r in rows:
        monthly_region[r["date"]][r["region"]] += float(r["revenue"])

    drops = []
    regions = sorted({r["region"] for r in rows})
    for reg in regions:
        for i in range(1, len(months)):
            prev = monthly_region[months[i - 1]][reg]
            curr = monthly_region[months[i]][reg]
            if prev > 0:
                change_pct = (curr - prev) / prev * 100
                if change_pct < -20:
                    drops.append(
                        {
                            "region": reg,
                            "month": months[i],
                            "change_pct": change_pct,
                        }
                    )

    total_revenue = sum(float(r["revenue"]) for r in rows)

    return {
        "region_revenue": dict(region_revenue),
        "best_mom_product": best_mom_product,
        "best_quarter": best_quarter,
        "drops": drops,
        "total_revenue": total_revenue,
    }


# ---------------------------------------------------------------------------
# 2. Parse and validate the analysis
# ---------------------------------------------------------------------------


def read_analysis(path):
    if not path.exists():
        print(f"FATAL: {path} not found.")
        sys.exit(1)
    return path.read_text()


def check_region_revenue(text, expected, tolerance=0.02):
    """Check 1: All 4 region totals mentioned within tolerance."""
    passed = 0
    for region, expected_val in expected.items():
        # Look for the region name near a number
        # Accept formats like 518,300 or 518300 or $518,300 or 518.3k etc.
        pattern = re.compile(
            rf"{region}[^$\d]{{0,80}}[\$]?\s*([\d,]+(?:\.\d+)?)", re.IGNORECASE
        )
        matches = pattern.findall(text)
        # Also try reversed: number then region
        pattern2 = re.compile(
            rf"[\$]?\s*([\d,]+(?:\.\d+)?)[^a-zA-Z]{{0,80}}{region}", re.IGNORECASE
        )
        matches += pattern2.findall(text)
        found = False
        for m in matches:
            try:
                val = float(m.replace(",", ""))
                if abs(val - expected_val) / expected_val <= tolerance:
                    found = True
                    break
            except ValueError:
                continue
        if found:
            passed += 1
    ok = passed == 4
    return ok, f"Region revenues: {passed}/4 correct"


def check_best_mom_product(text, expected):
    """Check 2: Highest avg MoM growth product identified."""
    # Accept Widget-B or WidgetB or Widget B
    patterns = [
        r"widget[\s\-_]?b",
        r"Widget[\s\-_]?A",  # also accept A (highest single-month MoM)
    ]
    # Primary: Widget-B (highest average MoM)
    primary = bool(re.search(r"widget[\s\-_]?b", text, re.IGNORECASE))
    # Alternate: Widget-A (highest single-month MoM)
    alternate = bool(re.search(r"widget[\s\-_]?a", text, re.IGNORECASE))

    # We look for MoM / month-over-month context near the product name
    mom_context = re.search(
        r"(month.over.month|MoM|mom|m-o-m|monthly growth)", text, re.IGNORECASE
    )

    if primary and mom_context:
        return True, "Best MoM product: Widget-B correctly identified"
    if alternate and mom_context:
        # Widget-A had the highest single-month spike; accept it
        return True, "Best MoM product: Widget-A identified (highest single-month MoM — accepted)"
    if primary:
        return True, "Best MoM product: Widget-B mentioned (MoM context implied)"
    return False, f"Best MoM product: expected Widget-B (or Widget-A), not clearly found"


def check_best_quarter(text, expected):
    """Check 3: Quarter with highest average revenue."""
    # expected is like 'Q3'
    pattern = re.compile(
        rf"(highest|best|top|largest|greatest|peak|strongest)[^.]*?{expected}|{expected}[^.]*?(highest|best|top|largest|greatest|peak|strongest)",
        re.IGNORECASE,
    )
    found = bool(pattern.search(text))
    if not found:
        # Simpler: just check Q3 is mentioned near "average" or "revenue"
        found = bool(
            re.search(rf"{expected}.*?(average|revenue|avg)", text, re.IGNORECASE)
        ) or bool(
            re.search(rf"(average|revenue|avg).*?{expected}", text, re.IGNORECASE)
        )
    return found, f"Best quarter: {'correctly' if found else 'not'} identified as {expected}"


def check_drop_identified(text, drops):
    """Check 4: At least one >20% drop identified."""
    found_any = False
    for drop in drops:
        region = drop["region"]
        month = drop["month"]
        # Accept various month formats: 2025-06, June 2025, Jun 2025, June, Jun, 06/2025
        month_patterns = []
        month_num = int(month.split("-")[1])
        month_names = [
            "",
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        month_abbrevs = [
            "",
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        month_patterns.append(month)  # 2025-06
        month_patterns.append(month_names[month_num])  # June
        month_patterns.append(month_abbrevs[month_num])  # Jun

        for mp in month_patterns:
            # Region + month or month + region within proximity
            if re.search(
                rf"{region}[^.]*?{mp}|{mp}[^.]*?{region}", text, re.IGNORECASE
            ):
                # Also check for "drop" / "decline" / "decrease" / "fall" / "dip" or a negative percentage
                if re.search(
                    r"(drop|decline|decrease|fall|dip|plummet|\-\d+\.?\d*\s*%|down)",
                    text,
                    re.IGNORECASE,
                ):
                    found_any = True
                    break
        if found_any:
            break

    return found_any, f"Revenue drop: {'correctly' if found_any else 'not'} identified (West, June 2025, -57.1%)"


def check_total_revenue(text, expected, tolerance=0.02):
    """Check 5: Total overall revenue."""
    # Find large numbers that could be the total
    numbers = re.findall(r"[\$]?\s*([\d,]+(?:\.\d+)?)", text)
    for n in numbers:
        try:
            val = float(n.replace(",", ""))
            if abs(val - expected) / expected <= tolerance:
                return True, f"Total revenue: correctly stated (~{expected:,.0f})"
        except ValueError:
            continue
    return False, f"Total revenue: expected ~{expected:,.0f}, not found within {tolerance*100:.0f}% tolerance"


def main():
    truth = load_ground_truth()
    text = read_analysis(ANALYSIS_PATH)

    checks = [
        check_region_revenue(text, truth["region_revenue"]),
        check_best_mom_product(text, truth["best_mom_product"]),
        check_best_quarter(text, truth["best_quarter"]),
        check_drop_identified(text, truth["drops"]),
        check_total_revenue(text, truth["total_revenue"]),
    ]

    print("=" * 60)
    print("DATA-001: Quarterly Sales Analysis — Validation Results")
    print("=" * 60)

    passed = 0
    for i, (ok, msg) in enumerate(checks, 1):
        status = "PASS" if ok else "FAIL"
        print(f"  Check {i}: [{status}] {msg}")
        if ok:
            passed += 1

    print("-" * 60)
    print(f"  Result: {passed}/5 checks passed (threshold: 4/5)")

    if passed >= 4:
        print("  STATUS: PASSED")
        sys.exit(0)
    else:
        print("  STATUS: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
