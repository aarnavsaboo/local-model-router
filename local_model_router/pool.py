from dataclasses import replace

from .router import ModelProfile


class ModelPool:
    def __init__(self, models: list[ModelProfile], memory_limit_gb: float | None = None):
        self.models = {m.name:m for m in models}
        self.memory_limit_gb = memory_limit_gb

    def snapshot(self) -> list[ModelProfile]:
        return list(self.models.values())

    def active_memory_gb(self) -> float:
        return sum(m.memory_gb for m in self.models.values() if m.warm or m.active)

    def can_warm(self, name: str) -> bool:
        model = self.models[name]
        if self.memory_limit_gb is None or model.warm:
            return True
        return self.active_memory_gb() + model.memory_gb <= self.memory_limit_gb

    def set_warm(self, name: str, warm: bool):
        if warm and not self.can_warm(name):
            raise MemoryError("warming model would exceed pool memory limit")
        self.models[name] = replace(self.models[name], warm=warm)

    def acquire(self, name: str):
        model = self.models[name]
        if model.active >= model.capacity:
            raise RuntimeError("model is at configured capacity")
        self.models[name] = replace(model, active=model.active + 1)

    def release(self, name: str):
        model = self.models[name]
        self.models[name] = replace(model, active=max(0, model.active - 1))

    def replace(self, model: ModelProfile):
        self.models[model.name] = model
