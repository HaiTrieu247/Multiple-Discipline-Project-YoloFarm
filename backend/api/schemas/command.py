from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class Command(BaseModel):
    command: str = Field(..., description="Command name")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Command parameters")
