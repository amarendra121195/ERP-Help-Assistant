import pytest

from app.utils.cost import cost_usd
from app.utils.formatting import format_inr


def test_format_inr():
    assert format_inr(3334200) == "INR 33,34,200.00"
    assert format_inr(916500) == "INR 9,16,500.00"
    assert format_inr(25000) == "INR 25,000.00"
    assert format_inr(None) == "INR 0.00"


def test_cost():
    assert cost_usd("gpt-5.6-luna", 1_000_000, 1_000_000) == pytest.approx(1.40)
    assert cost_usd("unknown-model", 1000, 1000) == 0
