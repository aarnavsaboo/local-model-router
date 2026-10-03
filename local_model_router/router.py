from dataclasses import dataclass, field, replace
from math import inf


@dataclass(frozen=True)
class ModelProfile:
    name: str
    context: int
    memory_gb: float
    tps: float
    quality: dict[str, float] = field(default_factory=dict)
    warm_latency_s: float = 0.2
    cold_latency_s: float = 3.0
    warm: bool = False


@dataclass(frozen=True)
class Task:
    kind: str
    prompt_tokens: int
    output_tokens: int
    min_quality: float = 0.0
    max_memory_gb: float = inf


@dataclass(frozen=True)
class Observation:
    total_seconds: float
    output_tokens: int
    warm: bool


def predicted_seconds(model: ModelProfile, task: Task) -> float:
    startup = model.warm_latency_s if model.warm else model.cold_latency_s
    return startup + task.output_tokens / max(model.tps, 1e-9)


def feasible(model: ModelProfile, task: Task) -> bool:
    required_context = task.prompt_tokens + task.output_tokens
    return (
        required_context <= model.context
        and model.memory_gb <= task.max_memory_gb
        and model.quality.get(task.kind, 0.0) >= task.min_quality
    )


def choose(models: list[ModelProfile], task: Task) -> ModelProfile:
    candidates = [m for m in models if feasible(m, task)]
    if not candidates:
        raise LookupError("no local model satisfies the task constraints")
    return min(
        candidates,
        key=lambda m: (
            predicted_seconds(m, task),
            m.memory_gb,
            -m.quality.get(task.kind, 0.0),
            m.name,
        ),
    )


def update_profile(model: ModelProfile, observation: Observation, alpha: float = 0.25) -> ModelProfile:
    if not 0 < alpha <= 1:
        raise ValueError("alpha must be in (0, 1]")
    observed_tps = observation.output_tokens / max(observation.total_seconds, 1e-9)
    next_tps = alpha * observed_tps + (1 - alpha) * model.tps
    return replace(model, tps=next_tps, warm=observation.warm)
