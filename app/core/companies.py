COMPANIES = {
    "C01": "Riverside Infra Ltd",
    "C02": "Greenleaf Pharma Ltd",
    "C03": "Coastal Retail Ltd",
}

# documents in the "Common - All Companies" folder
COMMON = "ALL"

COMPANY_KEYWORDS = {
    "riverside": "C01",
    "greenleaf": "C02",
    "coastal": "C03",
}


def company_label(code):
    if code == COMMON:
        return "All companies"
    return f"{code} {COMPANIES[code]}"


def company_code(text):
    text = text.strip()
    if text.upper() in COMPANIES:
        return text.upper()
    for word, code in COMPANY_KEYWORDS.items():
        if word in text.lower():
            return code
    raise ValueError(f"Unknown company '{text}'. Use C01, C02 or C03.")
