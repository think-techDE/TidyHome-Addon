from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
import uuid


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    room: str
    interval_days: int  # 1=daily, 7=weekly, 30=monthly, 365=yearly
    assigned_to: Optional[str] = None
    points: int = 10
    active: bool = True
    last_done: Optional[str] = None  # ISO date string
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    def next_due(self) -> date:
        if self.last_done:
            base = date.fromisoformat(self.last_done)
        else:
            base = date.fromisoformat(self.created_at[:10])
        from datetime import timedelta
        return base + timedelta(days=self.interval_days)

    def is_overdue(self) -> bool:
        return self.next_due() <= date.today()

    def days_until_due(self) -> int:
        delta = self.next_due() - date.today()
        return delta.days


class TaskCreate(BaseModel):
    name: str
    room: str
    interval_days: int
    assigned_to: Optional[str] = None
    points: int = 10


class TaskDone(BaseModel):
    done_by: Optional[str] = None
    done_at: Optional[str] = None  # ISO date, defaults to today


class Score(BaseModel):
    person: str
    points: int
    tasks_done: int
