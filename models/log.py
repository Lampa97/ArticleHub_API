from pydantic import BaseModel, Field
from datetime import datetime, timezone

class Log(BaseModel):
    type: str = Field(..., description="Log type ('user', 'article')")
    message: str = Field(..., description="Log message text")
    created_at: datetime = Field(default=datetime.now(timezone.utc).isoformat(), description="Log creation time")