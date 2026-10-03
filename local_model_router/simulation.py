from __future__ import annotations

from dataclasses import asdict, replace

from .pool import ModelPool
from .router import Task, choose, predicted_seconds


def replay(pool: ModelPool, tasks: list[Task], arrival_gap_s: float = 0.0) -> list[dict]:
    now = 0.0
    # One next-available timestamp per configured model capacity slot.
    slots = {
        name: [0.0 for _ in range(max(1, model.capacity))]
        for name, model in pool.models.items()
    }
    records = []

    for task in tasks:
        queue_delay = {
            name: max(0.0, min(times) - now)
            for name, times in slots.items()
        }
        # Queue simulation considers a busy model eligible because the queue
        # delay is explicitly included in the predicted completion time.
        candidates = [replace(model, active=0) for model in pool.snapshot()]
        try:
            model = choose(candidates, task, queue_delay)
            model_slots = slots[model.name]
            slot_index = min(range(len(model_slots)), key=lambda i:model_slots[i])
            start = max(now, model_slots[slot_index])
            queued = start - now
            execution = predicted_seconds(model, task, 0.0)
            finish = start + execution
            model_slots[slot_index] = finish
            records.append({
                "task_id":task.id,
                "model":model.name,
                "arrival_s":now,
                "start_s":start,
                "finish_s":finish,
                "queued_s":queued,
                "predicted_seconds":execution,
                "warm":model.warm,
                "ok":True,
            })
        except Exception as exc:
            records.append({
                "task_id":task.id,
                "arrival_s":now,
                "ok":False,
                "error_type":type(exc).__name__,
                "error":str(exc),
            })
        now += arrival_gap_s

    return records
