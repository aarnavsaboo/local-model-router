from __future__ import annotations

from dataclasses import asdict
import heapq

from .pool import ModelPool
from .router import Task
from .scheduler import route


def replay(pool: ModelPool, tasks: list[Task], arrival_gap_s: float = 0.0) -> list[dict]:
    now = 0.0
    finishes: list[tuple[float,str]] = []
    available_at = {name:0.0 for name in pool.models}
    records = []

    for task in tasks:
        while finishes and finishes[0][0] <= now:
            finished_at, model_name = heapq.heappop(finishes)
            pool.release(model_name)

        queue = {name:max(0.0, t-now) for name,t in available_at.items()}
        try:
            decision = route(pool, task, queue)
            model = pool.models[decision.model]
            if model.active >= model.capacity:
                # virtual queueing: free the earliest slot for this model
                start = available_at[model.name]
            else:
                start = now
            finish = start + decision.predicted_seconds
            pool.acquire(model.name)
            available_at[model.name] = finish
            heapq.heappush(finishes, (finish, model.name))
            records.append({
                **asdict(decision),
                "arrival_s": now,
                "start_s": start,
                "finish_s": finish,
                "queued_s": start-now,
                "ok": True,
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
