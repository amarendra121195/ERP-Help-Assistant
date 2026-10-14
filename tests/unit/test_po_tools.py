from app.tools.po_tools import make_po_tools
from app.tools.trace import ToolTrace


def get_tools(companies):
    return {t.name: t for t in make_po_tools(companies, ToolTrace())}


def test_open_po_total_riverside():
    out = get_tools(["C01"])["get_po_total"].invoke({"project": "Project Riverside", "status": "open"})
    assert "INR 33,34,200.00" in out
    assert "6 on 6" in out


def test_top_vendor_grouped_by_account():
    out = get_tools(["C01", "C02", "C03"])["get_po_totals_grouped"].invoke({"group_by": "vendor", "top_n": 1})
    assert "V-00145" in out
    assert "INR 42,34,000.00" in out


def test_canceled_lines_excluded_by_default():
    tools = get_tools(["C01", "C02", "C03"])
    assert "INR 1,05,69,530.00" in tools["get_po_total"].invoke({})
    assert "INR 5,26,800.00" in tools["get_po_total"].invoke({"status": "canceled"})


def test_sql_is_traced():
    trace = ToolTrace()
    tools = {t.name: t for t in make_po_tools(["C01"], trace)}
    tools["get_po_total"].invoke({"status": "open"})
    assert trace.queries[0]["params"][0] == "C01"


def test_other_company_denied():
    tools = get_tools(["C02", "C03"])
    assert tools["list_purchase_orders"].invoke({"project": "Riverside", "status": "open"}).startswith("ACCESS DENIED")
    assert tools["get_po_total"].invoke({"company": "C01"}).startswith("ACCESS DENIED")


def test_denied_when_llm_adds_own_company():
    # Plant 2 Upgrade is a C02 project
    out = get_tools(["C01"])["get_po_total"].invoke({"project": "Plant 2 Upgrade", "company": "C01"})
    assert out.startswith("ACCESS DENIED")


def test_totals_only_for_allowed_companies():
    out = get_tools(["C02", "C03"])["get_po_totals_grouped"].invoke({"group_by": "company"})
    assert "C02" in out and "C03" in out
    assert "C01" not in out


def test_unknown_project():
    out = get_tools(["C02", "C03"])["get_po_total"].invoke({"project": "Moon Base"})
    assert out == "No purchase order lines match these filters."
