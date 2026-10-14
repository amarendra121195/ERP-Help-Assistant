from langchain_core.tools import tool

from app.core.companies import company_label
from app.rag.retriever import retrieve


def make_document_tools(allowed, trace):

    @tool
    def search_documents(query: str) -> str:
        """Search the ERP documents (D365 guides, SOPs, purchase policies, approval limits,
        helpdesk notes). Use for how-to, process and policy questions."""
        results = retrieve(query, allowed)
        if not results:
            return "No documents found."

        parts = []
        for doc in results:
            trace.add_document(doc.metadata["source"])
            company = company_label(doc.metadata["company"])
            parts.append(f"[Source: {doc.metadata['source']} | Company: {company}]\n{doc.page_content}")
        return "\n\n---\n\n".join(parts)

    return [search_documents]
