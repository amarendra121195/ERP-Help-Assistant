# Arguments for the PO tools. The descriptions are sent to the LLM.
from typing import Literal

from pydantic import BaseModel, Field


class POFilters(BaseModel):
    project: str | None = Field(
        None, description="Project name or ID, e.g. 'Riverside Towers', 'Riverside' or 'RIL-PRJ-0007'.")
    vendor: str | None = Field(
        None, description="Vendor name or account, e.g. 'Gujarat Steel' or 'V-00145'.")
    status: str | None = Field(
        None, description="'open', 'received', 'invoiced', 'canceled' or 'any'. "
                          "Leave empty for all lines except canceled ones.")
    company: str | None = Field(
        None, description="Company code or name, e.g. 'C01'. Leave empty for all companies the user can see.")
    from_date: str | None = Field(None, description="PO date from, YYYY-MM-DD.")
    to_date: str | None = Field(None, description="PO date to, YYYY-MM-DD.")


class ListArgs(POFilters):
    limit: int = Field(25, description="Max lines to return.")


class GroupArgs(POFilters):
    group_by: Literal["vendor", "company", "project", "status", "buyer", "item", "month"] = Field(
        description="What to total by.")
    top_n: int = Field(10, description="How many groups to return, highest value first.")
