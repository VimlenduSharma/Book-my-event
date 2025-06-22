"""
CategoryEnum
============

Centralised list of allowed event categories.  Storing categories as a
**string Enum** keeps the database simple (TEXT column) while preventing
typos in code and enabling validation in Pydantic / FastAPI.

Feel free to extend the list — just remember to bump any
front-end dropdowns.
"""

from __future__ import annotations

from enum import Enum


class CategoryEnum(str, Enum):
    DESIGN = "Design"
    BUSINESS = "Business"
    FITNESS = "Fitness"
    MUSIC = "Music"
    TECH = "Tech"
    ART = "Art"
    OTHER = "Other"

    @classmethod
    def list(cls) -> list[str]:
        """Return raw string values for e.g. dropdown options."""
        return [c.value for c in cls]
