from typing import Literal

from pydantic import BaseModel

Status = Literal["ok", "error"]


class HealthRead(BaseModel):
    status: Status
    db: Status
    redis: Status
