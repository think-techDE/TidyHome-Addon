from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, date
import uuid


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    room: str
    interval_days: int  # 1=daily, 7=weekly, 30=monthly, 365=yearly
    assigned_to: list[str] = []  # Mehrere Personen möglich

    @field_validator("assigned_to", mode="before")
    @classmethod
    def _coerce_assigned_to(cls, v):
        """Rückwärtskompatibilität: alter String-Wert → Liste."""
        if v is None:
            return []
        if isinstance(v, str):
            return [v] if v else []
        return v
    points: int = 10
    icon: str = ""        # expliziter Icon-Key; leer = automatisch aus Name/Raum
    active: bool = True
    important: bool = False
    onetime: bool = False  # einmalige Aufgabe: nach Erledigung archiviert
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


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    room: str
    assigned_to: Optional[str] = None
    description: Optional[str] = None
    icon: str = ""        # expliziter Icon-Key; leer = automatisch aus Raum
    active: bool = True
    completed: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    def progress(self, steps: list["Step"]) -> tuple[int, int]:
        total = len(steps)
        done = sum(1 for s in steps if s.completed)
        return done, total


class Step(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    name: str
    points: int = 5
    completed: bool = False
    completed_by: Optional[str] = None
    completed_at: Optional[str] = None


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
