from pathlib import Path
import json

from .router import ModelProfile, Task


def load_pool(path: str) -> tuple[list[ModelProfile], float | None]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    models = [ModelProfile(**row) for row in data["models"]]
    return models, data.get("memory_limit_gb")


def load_task(path: str) -> Task:
    return Task(**json.loads(Path(path).read_text(encoding="utf-8")))


def load_tasks(path: str) -> list[Task]:
    return [
        Task(**json.loads(line))
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
