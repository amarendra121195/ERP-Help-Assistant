import pytest

from tests.evaluation.metrics import retrieval_scores, run_checks


def test_checks():
    case = {
        "expected_route": "data",
        "must_contain": ["33,34,200"],
        "must_not_contain": ["3,00,000"],
        "expected_sources": ["a.pdf"],
    }
    good = {"answer": "Total is INR 33,34,200.00", "route": "data", "sources": ["a.pdf"]}
    bad = {"answer": "Total is INR 3,00,000", "route": "documents", "sources": []}

    assert all(ok for _, ok, _ in run_checks(case, good))
    failed = {kind for kind, ok, _ in run_checks(case, bad) if not ok}
    assert failed == {"route", "facts", "forbidden", "sources"}


def test_retrieval_scores():
    case = {"expected_sources": ["b.pdf"]}
    assert retrieval_scores(case, {"documents_retrieved": ["a.pdf", "b.pdf"]}) == (True, pytest.approx(0.5))
    assert retrieval_scores(case, {"documents_retrieved": ["a.pdf"]}) == (False, 0.0)
    assert retrieval_scores({}, {"documents_retrieved": ["a.pdf"]}) is None
