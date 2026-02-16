import pytest
from collections import defaultdict

# Dictionary to store results globally for the session
session_results = []


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        params = item.callspec.params

        report.test_metadata = {
            "party": params["party"],
            "statement": params["statement"],
            "expected": params["expected_verdict"],
            "status": "PASSED" if report.passed else "FAILED"
        }

        session_results.append(report)


def pytest_sessionfinish(session, exitstatus):
    """
    Called after all tests are done. Generates the statistics and Markdown file.
    """
    stats = defaultdict(lambda: {"correct": 0, "wrong": 0})
    details = []

    for report in session_results:
        meta = report.test_metadata
        party = meta["party"]

        if meta["status"] == "PASSED":
            stats[party]["correct"] += 1
        else:
            stats[party]["wrong"] += 1
            details.append({
                "party": party,
                "statement": meta["statement"],
                "expected": meta["expected"],
                "error": str(report.longrepr.reprcrash.message if report.longrepr else "Unknown Error")
            })

    # Generate Markdown File
    with open("test_report.md", "w", encoding="utf-8") as f:
        f.write("# Political Classification Test Report\n\n")

        f.write("## 1. Statistics by Party\n\n")
        f.write("| Party | Correct | Wrong | Accuracy |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for party, s in stats.items():
            total = s["correct"] + s["wrong"]
            acc = (s["correct"] / total) * 100 if total > 0 else 0
            f.write(f"| {party} | {s['correct']} | {s['wrong']} | {acc:.1f}% |\n")

        f.write("\n## 2. Failure Log (Reason & Confidence)\n\n")
        f.write("| Party | Statement | Expected | Actual / Rationale |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for d in details:
            # Clean up the error message to fit in table cell
            clean_error = d['error'].replace('\n', ' ')
            f.write(f"| {d['party']} | {d['statement']} | {d['expected']} | {clean_error} |\n")

    print("\n[REPORT] Markdown summary generated: test_report.md")