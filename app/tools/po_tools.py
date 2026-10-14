from langchain_core.tools import tool

from app.core.companies import COMPANIES, company_code
from app.db.sql_server import run_query
from app.tools.po_filters import GROUPS, PO_TABLE, build_where, describe_status
from app.tools.schemas import GroupArgs, ListArgs, POFilters
from app.utils.formatting import format_inr

ACCESS_DENIED = "ACCESS DENIED: this data belongs to a company the user is not allowed to see. Give no figures."
NO_ROWS = "No purchase order lines match these filters."


def format_row(r):
    project = r["project_name"] or "No project"
    qty = f"{float(r['quantity']):g} {r['unit']}"
    return (f"{r['purchase_order']} | {r['po_date']} | {r['company']} | "
            f"{r['vendor_name']} ({r['vendor_account']}) | {project} | {r['item_description']} | "
            f"{qty} | {format_inr(r['line_amount_inr'])} | {r['purchase_status']}")


def make_po_tools(allowed, trace):

    def query(sql, params):
        trace.add_query(sql, params)
        return run_query(sql, params)

    def empty_result(filters):
        # nothing found for this user - check if it's because the data is in another company
        if filters.get("company") and company_code(filters["company"]) not in allowed:
            return ACCESS_DENIED

        others = [code for code in COMPANIES if code not in allowed]
        if others:
            # ignore the company filter here, the LLM sometimes adds the user's own company
            other_filters = {k: v for k, v in filters.items() if k != "company"}
            where, params = build_where(others, **other_filters)
            count = query(f"SELECT COUNT(*) AS n FROM {PO_TABLE} WHERE {where}", params)[0]["n"]
            if count:
                return ACCESS_DENIED
        return NO_ROWS

    @tool(args_schema=POFilters)
    def get_po_total(**filters) -> str:
        """Exact total value (INR, without GST) and number of PO lines for the filters.
        Use for 'total value', 'how much', 'how many POs' questions."""
        where, params = build_where(allowed, **filters)
        sql = (f"SELECT COUNT(*) AS lines, COUNT(DISTINCT purchase_order) AS pos, "
               f"SUM(line_amount_inr) AS total FROM {PO_TABLE} WHERE {where}")
        row = query(sql, params)[0]
        if row["lines"] == 0:
            return empty_result(filters)

        return (f"Total value: {format_inr(row['total'])} (without GST)\n"
                f"PO lines: {row['lines']} on {row['pos']} purchase orders\n"
                f"Statuses included: {describe_status(filters.get('status'))}")

    @tool(args_schema=ListArgs)
    def list_purchase_orders(limit: int = 25, **filters) -> str:
        """List PO lines for the filters (PO number, date, vendor, project, item, amount, status).
        Use for 'show', 'list', 'which POs' questions."""
        where, params = build_where(allowed, **filters)
        sql = f"SELECT TOP (?) * FROM {PO_TABLE} WHERE {where} ORDER BY po_date"
        rows = query(sql, [min(limit, 100)] + params)
        if not rows:
            return empty_result(filters)

        header = "PO | Date | Company | Vendor | Project | Item | Qty | Amount (without GST) | Status"
        lines = [format_row(r) for r in rows]
        return (f"{len(rows)} lines (statuses: {describe_status(filters.get('status'))})\n"
                + header + "\n" + "\n".join(lines))

    @tool(args_schema=GroupArgs)
    def get_po_totals_grouped(group_by: str, top_n: int = 10, **filters) -> str:
        """Exact PO value totals grouped by vendor, company, project, status, buyer, item or month,
        highest first. Use for 'which vendor has the highest', 'total per company' questions."""
        column, label = GROUPS[group_by]
        where, params = build_where(allowed, **filters)
        sql = (f"SELECT TOP (?) {column} AS group_key, {label} AS label, COUNT(*) AS lines, "
               f"SUM(line_amount_inr) AS total FROM {PO_TABLE} WHERE {where} "
               f"GROUP BY {column} ORDER BY total DESC")
        rows = query(sql, [min(top_n, 50)] + params)
        if not rows:
            return empty_result(filters)

        lines = []
        for i, r in enumerate(rows, 1):
            name = r["group_key"] or f"No {group_by}"
            if r["label"]:
                name += f" - {r['label']}"
            lines.append(f"{i}. {name}: {format_inr(r['total'])} ({r['lines']} lines)")

        status = describe_status(filters.get("status"))
        return f"PO value by {group_by}, highest first (without GST; {status}):\n" + "\n".join(lines)

    return [get_po_total, list_purchase_orders, get_po_totals_grouped]
