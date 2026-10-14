import re

from app.core import config
from app.core.companies import company_code

PO_TABLE = config.PO_TABLE

STATUSES = {
    "open": "Open order",
    "open order": "Open order",
    "received": "Received",
    "invoiced": "Invoiced",
    "canceled": "Canceled",
    "cancelled": "Canceled",
}

# group_by -> (column to group on, label column)
GROUPS = {
    "vendor": ("vendor_account", "MIN(vendor_name)"),  # same vendor is spelled in different ways
    "company": ("company", "NULL"),
    "project": ("project_id", "MIN(project_name)"),
    "status": ("purchase_status", "NULL"),
    "buyer": ("buyer", "NULL"),
    "item": ("item_number", "MIN(item_description)"),
    "month": ("CONVERT(char(7), po_date, 120)", "NULL"),
}


def build_where(companies, project=None, vendor=None, status=None,
                company=None, from_date=None, to_date=None):
    # the company filter is always there - it's the user's access
    where = [f"company IN ({', '.join('?' * len(companies))})"]
    params = list(companies)

    if company:
        where.append("company = ?")
        params.append(company_code(company))

    if project:
        name = re.sub(r"^\s*project\s+", "", project, flags=re.I).strip()
        where.append("(project_id = ? OR project_name LIKE ?)")
        params += [name, f"%{name}%"]

    if vendor:
        # search by vendor account, because the names are not consistent
        where.append(f"vendor_account IN (SELECT vendor_account FROM {PO_TABLE} "
                     f"WHERE vendor_account = ? OR REPLACE(vendor_name, '.', '') LIKE ?)")
        params += [vendor.strip(), f"%{vendor.replace('.', '').strip()}%"]

    status = (status or "").strip().lower()
    if status in ("", "active"):
        where.append("purchase_status <> 'Canceled'")
    elif status in STATUSES:
        where.append("purchase_status = ?")
        params.append(STATUSES[status])
    elif status not in ("any", "all"):
        raise ValueError(f"Unknown status '{status}'. Use open, received, invoiced, canceled or any.")

    if from_date:
        where.append("po_date >= ?")
        params.append(from_date)
    if to_date:
        where.append("po_date <= ?")
        params.append(to_date)

    return " AND ".join(where), params


def describe_status(status):
    status = (status or "").strip().lower()
    if status in ("", "active"):
        return "all statuses except Canceled"
    if status in ("any", "all"):
        return "all statuses including Canceled"
    return STATUSES[status]
