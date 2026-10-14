import re

from app.core import config
from app.core.companies import COMPANIES, COMPANY_KEYWORDS
from app.db.sql_server import run_query


class UnknownUserError(Exception):
    pass


def get_allowed_companies(user_id):
    # companies_allowed looks like "C01", "C02, C03" or "All"
    sql = f"SELECT companies_allowed FROM {config.ACCESS_TABLE} WHERE user_id = ?"
    rows = run_query(sql, [user_id.strip().upper()])
    if not rows:
        raise UnknownUserError(f"Unknown user '{user_id}'")

    value = (rows[0]["companies_allowed"] or "").strip().upper()
    if value == "ALL":
        return list(COMPANIES)

    codes = [code.strip() for code in value.split(",")]
    return [code for code in codes if code in COMPANIES]


def companies_in_question(question):
    text = question.lower()
    found = {code.upper() for code in re.findall(r"\bc0[1-9]\b", text)}
    for word, code in COMPANY_KEYWORDS.items():
        if word in text:
            found.add(code)
    return found & set(COMPANIES)


def blocked_companies(question, allowed):
    return sorted(companies_in_question(question) - set(allowed))
