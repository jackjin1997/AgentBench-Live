#!/usr/bin/env python3
"""Validation script for tool-002: Build data pipeline from GitHub API.

Checks the agent's output against expected requirements:
  1. /workspace/pipeline.py exists and is importable Python
  2. /workspace/output.json exists and contains a JSON list of repos
  3. Each repo has required fields with correct types
  4. Repos are sorted by stars descending
  5. At least 25 repos present (task asks for 30, allow margin)
  6. /workspace/summary.md exists and references top 5
  7. Computed fields (stars_to_forks_ratio, issue_density) are correct

Exits 0 if >= 6/7 checks pass, 1 otherwise.
"""

import importlib.util
import json
import math
import os
import sys

PIPELINE_PATH = "/workspace/pipeline.py"
OUTPUT_PATH = "/workspace/output.json"
SUMMARY_PATH = "/workspace/summary.md"

REQUIRED_FIELDS = [
    "full_name",
    "stars",
    "forks",
    "open_issues",
    "description",
    "license",
    "stars_to_forks_ratio",
    "issue_density",
]

results = []


def check(name: str, passed: bool, detail: str = ""):
    status = "PASS" if passed else "FAIL"
    msg = f"[{status}] {name}"
    if detail:
        msg += f" -- {detail}"
    print(msg)
    results.append(passed)
    return passed


# ---------------------------------------------------------------------------
# Check 1: pipeline.py exists and is valid Python (importable)
# ---------------------------------------------------------------------------
def check_pipeline_importable():
    if not os.path.isfile(PIPELINE_PATH):
        return check("pipeline.py exists and importable", False, "file not found")
    try:
        spec = importlib.util.spec_from_file_location("pipeline", PIPELINE_PATH)
        if spec is None or spec.loader is None:
            return check("pipeline.py exists and importable", False, "cannot create module spec")
        mod = importlib.util.module_from_spec(spec)
        # Compile only -- don't execute (avoids network calls / side effects)
        with open(PIPELINE_PATH, "r") as f:
            source = f.read()
        compile(source, PIPELINE_PATH, "exec")
        return check("pipeline.py exists and importable", True)
    except SyntaxError as e:
        return check("pipeline.py exists and importable", False, f"SyntaxError: {e}")
    except Exception as e:
        return check("pipeline.py exists and importable", False, str(e))


check_pipeline_importable()

# ---------------------------------------------------------------------------
# Check 2: output.json exists and contains a JSON list of repos
# ---------------------------------------------------------------------------
repos = None

if not os.path.isfile(OUTPUT_PATH):
    check("output.json exists with repo list", False, "file not found")
else:
    try:
        with open(OUTPUT_PATH, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            check("output.json exists with repo list", False, f"expected list, got {type(data).__name__}")
        elif len(data) == 0:
            check("output.json exists with repo list", False, "list is empty")
        else:
            repos = data
            check("output.json exists with repo list", True, f"{len(repos)} repos")
    except json.JSONDecodeError as e:
        check("output.json exists with repo list", False, f"invalid JSON: {e}")

# ---------------------------------------------------------------------------
# Check 3: Each repo has required fields
# ---------------------------------------------------------------------------
if repos is None:
    check("repos have required fields", False, "no repos loaded")
else:
    missing_map = {}
    for i, repo in enumerate(repos):
        missing = [f for f in REQUIRED_FIELDS if f not in repo]
        if missing:
            missing_map[i] = missing

    if missing_map:
        # Show first few problems
        examples = []
        for idx, fields in list(missing_map.items())[:3]:
            name = repos[idx].get("full_name", f"repo[{idx}]")
            examples.append(f"{name} missing {fields}")
        check(
            "repos have required fields",
            False,
            f"{len(missing_map)}/{len(repos)} repos incomplete; e.g. {'; '.join(examples)}",
        )
    else:
        check("repos have required fields", True, f"all {len(repos)} repos have {len(REQUIRED_FIELDS)} fields")

# ---------------------------------------------------------------------------
# Check 4: Repos sorted by stars descending
# ---------------------------------------------------------------------------
if repos is None:
    check("repos sorted by stars descending", False, "no repos loaded")
else:
    try:
        star_values = [r["stars"] for r in repos]
        is_sorted = all(star_values[i] >= star_values[i + 1] for i in range(len(star_values) - 1))
        if is_sorted:
            check("repos sorted by stars descending", True, f"range {star_values[0]}..{star_values[-1]}")
        else:
            # Find first violation
            for i in range(len(star_values) - 1):
                if star_values[i] < star_values[i + 1]:
                    check(
                        "repos sorted by stars descending",
                        False,
                        f"violation at index {i}: {star_values[i]} < {star_values[i+1]}",
                    )
                    break
    except (KeyError, TypeError) as e:
        check("repos sorted by stars descending", False, f"cannot read stars: {e}")

# ---------------------------------------------------------------------------
# Check 5: At least 25 repos
# ---------------------------------------------------------------------------
if repos is None:
    check("at least 25 repos", False, "no repos loaded")
else:
    count = len(repos)
    check("at least 25 repos", count >= 25, f"found {count} repos")

# ---------------------------------------------------------------------------
# Check 6: summary.md exists and mentions top 5
# ---------------------------------------------------------------------------
if not os.path.isfile(SUMMARY_PATH):
    check("summary.md exists with top-5 content", False, "file not found")
else:
    with open(SUMMARY_PATH, "r") as f:
        summary_text = f.read()
    if len(summary_text.strip()) < 50:
        check("summary.md exists with top-5 content", False, "file too short (< 50 chars)")
    else:
        text_lower = summary_text.lower()
        has_top5 = "top 5" in text_lower or "top five" in text_lower or "top-5" in text_lower
        if not has_top5:
            # Fallback: check if it at least lists multiple repo names
            if repos and sum(1 for r in repos[:5] if r.get("full_name", "") in summary_text) >= 3:
                has_top5 = True
        check("summary.md exists with top-5 content", has_top5, f"{len(summary_text)} chars")

# ---------------------------------------------------------------------------
# Check 7: Computed fields are correct for a sample
# ---------------------------------------------------------------------------
if repos is None:
    check("computed fields correct (sample)", False, "no repos loaded")
else:
    sample_size = min(5, len(repos))
    errors = []
    for repo in repos[:sample_size]:
        name = repo.get("full_name", "?")
        stars = repo.get("stars")
        forks = repo.get("forks")
        open_issues = repo.get("open_issues")
        ratio = repo.get("stars_to_forks_ratio")
        density = repo.get("issue_density")

        # Validate stars_to_forks_ratio
        if stars is not None and forks is not None and ratio is not None:
            if forks == 0:
                # Accept any non-negative value or inf when forks is 0
                if not (ratio >= 0 or ratio == float("inf")):
                    errors.append(f"{name}: bad ratio {ratio} (forks=0)")
            else:
                expected_ratio = stars / forks
                if not math.isclose(ratio, expected_ratio, rel_tol=0.05):
                    errors.append(f"{name}: ratio {ratio} != expected {expected_ratio:.4f}")

        # Validate issue_density = open_issues / (stars + forks) or similar
        if stars is not None and open_issues is not None and density is not None:
            # Try common formulas: issues/stars, issues/(stars+forks), issues/forks
            candidates = []
            if stars > 0:
                candidates.append(open_issues / stars)
            if forks is not None and (stars + forks) > 0:
                candidates.append(open_issues / (stars + forks))
            if forks is not None and forks > 0:
                candidates.append(open_issues / forks)

            matched = any(math.isclose(density, c, rel_tol=0.05) for c in candidates if c is not None)
            if not matched and density == 0 and open_issues == 0:
                matched = True  # trivially correct
            if not matched:
                errors.append(f"{name}: issue_density {density} doesn't match common formulas")

    if errors:
        check("computed fields correct (sample)", False, "; ".join(errors[:3]))
    else:
        check("computed fields correct (sample)", True, f"verified {sample_size} repos")

# ---------------------------------------------------------------------------
# Final verdict
# ---------------------------------------------------------------------------
passed = sum(results)
total = len(results)
print(f"\n{'='*50}")
print(f"Result: {passed}/{total} checks passed")

if passed >= 6:
    print("VERDICT: PASS")
    sys.exit(0)
else:
    print("VERDICT: FAIL")
    sys.exit(1)
