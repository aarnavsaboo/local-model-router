from __future__ import annotations

from dataclasses import dataclass, field, replace
from math import inf


@dataclass(frozen=True)
class ModelProfile:
    name: str
    context: int
    memory_gb: float
    tps: float
    quality: dict[str, float] = field(default_factory=dict)
    warm_latency_s: float = .2
    cold_latency_s: float = 3.0
    warm: bool = False
    runtime: str = "local"
    capacity: int = 1
    active: int = 0


@dataclass(frozen=True)
class Task:
    id: str
    kind: str
    prompt_tokens: int
    output_tokens: int
    min_quality: float = 0.0
    max_memory_gb: float = inf
    max_latency_s: float = inf
    preferred_runtime: str | None = None
    priority: int = 0


@dataclass(frozen=True)
class Observation:
    total_seconds: float
    output_tokens: int
    warm: bool
    task_kind: str | None = None
    score: float | None = None


def predicted_seconds(model: ModelProfile, task: Task, queue_seconds: float = 0.0) -> float:
    startup = model.warm_latency_s if model.warm else model.cold_latency_s
    prompt_factor = task.prompt_tokens / max(model.context, 1)
    prompt_cost = startup * min(2.0, prompt_factor)
    decode = task.output_tokens / max(model.tps, 1e-9)
    return queue_seconds + startup + prompt_cost + decode


def feasible(model: ModelProfile, task: Task) -> bool:
    needed = task.prompt_tokens + task.output_tokens
    runtime_ok = task.preferred_runtime is None or task.preferred_runtime == model.runtime
    quality_ok = model.quality.get(task.kind, 0.0) >= task.min_quality
    capacity_ok = model.active < model.capacity
    return (
        needed <= model.context
        and model.memory_gb <= task.max_memory_gb
        and runtime_ok
        and quality_ok
        and capacity_ok
    )


def choose(models: list[ModelProfile], task: Task, queue_delay: dict[str,float] | None = None) -> ModelProfile:
    queue_delay = queue_delay or {}
    candidates = [m for m in models if feasible(m, task)]
    if not candidates:
        raise LookupError("no local model satisfies the workload constraints")
    scored = [
        (
            predicted_seconds(m, task, queue_delay.get(m.name, 0.0)),
            m.memory_gb,
            -m.quality.get(task.kind, 0.0),
            -m.tps,
            m.name,
            m,
        )
        for m in candidates
    ]
    selected = min(scored)[-1]
    if predicted_seconds(selected, task, queue_delay.get(selected.name,0.0)) > task.max_latency_s:
        raise LookupError("no candidate satisfies the latency target")
    return selected


def update_profile(model: ModelProfile, observation: Observation, alpha: float = .25) -> ModelProfile:
    if not 0 < alpha <= 1:
        raise ValueError("alpha must be in (0,1]")
    observed_tps = observation.output_tokens / max(observation.total_seconds, 1e-9)
    tps = alpha * observed_tps + (1-alpha) * model.tps
    quality = dict(model.quality)
    if observation.task_kind is not None and observation.score is not None:
        old = quality.get(observation.task_kind, observation.score)
        quality[observation.task_kind] = alpha * observation.score + (1-alpha) * old
    return replace(model, tps=tps, quality=quality, warm=observation.warm)
