from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
import re

# Keywords that could be used for prompt injection
_DANGEROUS_PATTERNS = re.compile(
    r"(ignore\s+(all\s+)?(previous\s+)?instructions|"
    r"system\s*prompt|"
    r"you\s+are\s+now|"
    r"forget\s+(everything|all)|"
    r"disregard|"
    r"override)",
    re.IGNORECASE,
)

_MAX_ADDITIONAL_PREFS_LENGTH = 200


class UserPreferences(BaseModel):
    location: str
    budget: Literal["low", "medium", "high", "very high"]
    cuisine: Optional[str] = None
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    additional_preferences: Optional[str] = None

    @field_validator("additional_preferences")
    @classmethod
    def sanitize_additional_preferences(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Strip dangerous prompt-injection patterns
        sanitized = _DANGEROUS_PATTERNS.sub("", v)
        # Collapse extra whitespace left after stripping
        sanitized = re.sub(r"\s{2,}", " ", sanitized).strip()
        # Cap length
        if len(sanitized) > _MAX_ADDITIONAL_PREFS_LENGTH:
            sanitized = sanitized[:_MAX_ADDITIONAL_PREFS_LENGTH].rstrip()
        return sanitized or None

