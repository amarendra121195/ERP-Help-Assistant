from dataclasses import dataclass, field


@dataclass
class ToolTrace:
    """Keeps track of the documents and SQL used in one request (for the log)."""
    documents: list = field(default_factory=list)
    queries: list = field(default_factory=list)

    def add_document(self, source):
        if source not in self.documents:
            self.documents.append(source)

    def add_query(self, sql, params):
        self.queries.append({"sql": " ".join(sql.split()), "params": [str(p) for p in params]})
