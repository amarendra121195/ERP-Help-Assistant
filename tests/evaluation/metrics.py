import statistics

CATEGORIES = ["documents", "data", "access", "not_available"]
CHECK_TYPES = ["route", "facts", "forbidden", "sources"]


def run_checks(case, result):
    # returns a list of (check_type, passed, message)
    answer = result["answer"].lower()
    checks = []

    if case.get("expected_route"):
        ok = result["route"] == case["expected_route"]
        checks.append(("route", ok, f"route was '{result['route']}', expected '{case['expected_route']}'"))

    for text in case.get("must_contain", []):
        checks.append(("facts", text.lower() in answer, f"missing '{text}'"))

    any_of = case.get("must_contain_any", [])
    if any_of:
        ok = any(text.lower() in answer for text in any_of)
        checks.append(("facts", ok, f"contains none of {any_of}"))

    for text in case.get("must_not_contain", []):
        checks.append(("forbidden", text.lower() not in answer, f"should not contain '{text}'"))

    for source in case.get("expected_sources", []):
        checks.append(("sources", source in result["sources"], f"source '{source}' not cited"))

    if case.get("expect_no_sources"):
        checks.append(("sources", not result["sources"], f"expected no sources, got {result['sources']}"))

    return checks


def retrieval_scores(case, result):
    # (hit, reciprocal_rank) for questions that expect a source document, else None
    # hit = all expected documents were retrieved
    # reciprocal_rank = 1 / position of the first expected document in the retrieved list
    expected = case.get("expected_sources")
    if not expected:
        return None

    retrieved = result.get("documents_retrieved", [])
    hit = all(doc in retrieved for doc in expected)
    reciprocal_rank = 0.0
    for position, doc in enumerate(retrieved, 1):
        if doc in expected:
            reciprocal_rank = 1 / position
            break
    return hit, reciprocal_rank


def summarize(rows):
    summary = {"total": len(rows), "passed": sum(row["passed"] for row in rows)}

    summary["by_category"] = {}
    for category in CATEGORIES:
        group = [row for row in rows if row["case"]["category"] == category]
        summary["by_category"][category] = (sum(row["passed"] for row in group), len(group))

    summary["by_check"] = {}
    for check_type in CHECK_TYPES:
        results = [ok for row in rows for kind, ok, _ in row["checks"] if kind == check_type]
        summary["by_check"][check_type] = (sum(results), len(results))

    retrieval = [row["retrieval"] for row in rows if row["retrieval"]]
    summary["retrieval_hits"] = (sum(hit for hit, _ in retrieval), len(retrieval))
    summary["mrr"] = statistics.mean(rr for _, rr in retrieval) if retrieval else None

    judged = [row["faithful"] for row in rows if row["faithful"] is not None]
    summary["faithful"] = (sum(judged), len(judged))

    seconds = [row["seconds"] for row in rows]
    summary["latency"] = (statistics.mean(seconds), statistics.median(seconds), max(seconds))

    summary["input_tokens"] = sum(row["result"]["usage"]["input_tokens"] for row in rows)
    summary["output_tokens"] = sum(row["result"]["usage"]["output_tokens"] for row in rows)
    summary["cost"] = sum(row["result"]["usage"]["cost_usd"] for row in rows)
    summary["judge_cost"] = sum(row["judge_cost"] for row in rows)
    return summary
