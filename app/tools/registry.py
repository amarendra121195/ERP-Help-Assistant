from app.tools.document_tools import make_document_tools
from app.tools.po_tools import make_po_tools
from app.tools.trace import ToolTrace

DOCUMENT_TOOLS = {"search_documents"}
DATA_TOOLS = {"get_po_total", "list_purchase_orders", "get_po_totals_grouped"}


def build_tools(allowed):
    # tools are created per request, so the user's companies are fixed inside them
    trace = ToolTrace()
    tools = make_document_tools(allowed, trace) + make_po_tools(allowed, trace)
    return tools, trace
