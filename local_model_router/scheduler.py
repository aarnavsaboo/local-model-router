from __future__ import annotations

from dataclasses import dataclass

from .pool import ModelPool
from .router import Task, choose, predicted_seconds


@dataclass(frozen=True)
class Decision:
    task_id: str
    model: str
    predicted_seconds: float
    queue_seconds: float
    warm: bool
    active_before: int


def route(pool: ModelPool, task: Task, queue_delay: dict[str,float] | None = None) -> Decision:
    delays = queue_delay or {}
    model = choose(pool.snapshot(), task, delays)
    return Decision(
        task_id=task.id,
        model=model.name,
        predicted_seconds=predicted_seconds(model, task, delays.get(model.name,0.0)),
        queue_seconds=delays.get(model.name,0.0),
        warm=model.warm,
        active_before=model.active,
    )
