from decimal import Decimal


def format_inr(amount):
    """3334200 -> 'INR 33,34,200.00'"""
    whole, paise = f"{Decimal(amount or 0):.2f}".split(".")
    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        parts = []
        while head:
            parts.insert(0, head[-2:])
            head = head[:-2]
        whole = ",".join(parts) + "," + tail
    return f"INR {whole}.{paise}"
