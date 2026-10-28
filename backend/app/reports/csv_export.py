import csv
import io
from typing import Any

FORMULA_CHARS = ("=", "+", "-", "@", "\t", "\r")


def sanitize_csv_cell(value: Any) -> str:
    """
    Prevents CSV / Spreadsheet Formula Injection (Formula Injection Vulnerability).
    If a string starts with =, +, -, @, or tab, prepend a single quote to neutralize it.
    """
    if value is None:
        return ""
    str_val = str(value).strip()
    if str_val.startswith(FORMULA_CHARS):
        return f"'{str_val}"
    return str_val


def generate_issues_csv(audit: Any, issues: list[Any]) -> str:
    """
    Generates a secure, structured CSV of all detected SEO issues and fixes.
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    # Headers
    headers = [
        "Rank",
        "Issue Code",
        "Title",
        "Category",
        "Severity",
        "Priority Score",
        "Impact",
        "Confidence",
        "Estimated Effort",
        "Affected Pages Count",
        "Status",
        "Suggested Fix",
        "Why It Matters",
        "Priority Reason",
    ]
    writer.writerow([sanitize_csv_cell(h) for h in headers])

    for idx, issue in enumerate(issues, start=1):
        row = [
            idx,
            issue.issue_code,
            issue.title,
            issue.category,
            issue.severity,
            issue.priority_score,
            round(issue.impact, 2),
            round(issue.confidence, 2),
            round(issue.estimated_effort, 2),
            issue.affected_page_count,
            issue.status,
            issue.suggested_fix,
            issue.why_it_matters or "",
            issue.priority_reason or "",
        ]
        writer.writerow([sanitize_csv_cell(val) for val in row])

    return output.getvalue()
