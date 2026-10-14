import pytest

from app.services.access import UnknownUserError, blocked_companies, get_allowed_companies


def test_allowed_companies():
    assert get_allowed_companies("U01") == ["C01"]
    assert get_allowed_companies("u02") == ["C02", "C03"]
    assert get_allowed_companies("U03") == ["C01", "C02", "C03"]


def test_unknown_user():
    with pytest.raises(UnknownUserError):
        get_allowed_companies("U99")


def test_blocked_companies():
    assert blocked_companies("Show open POs for Project Riverside", ["C02", "C03"]) == ["C01"]
    assert blocked_companies("Greenleaf payment terms?", ["C01"]) == ["C02"]
    assert blocked_companies("Show open POs for Project Riverside", ["C01"]) == []
