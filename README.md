# local-model-router

A small routing experiment for choosing between several language models running on the same local machine.

Instead of hard-coding one model for every request, the router keeps simple model profiles and recent observations for throughput, warm/cold latency, context capacity and task scores. A request can then be matched to the smallest local model that satisfies its constraints.

The point is not to invent a universal routing score. It is to make the trade-off explicit and measurable.

## Inputs to a route

- task family
- estimated prompt and output tokens
- minimum task score
- memory budget
- context-window requirement
- recent tokens/second and latency observations
- whether a model is already warm

```python
from local_model_router import ModelProfile, Task, choose

models = [
    ModelProfile("small", context=8192, memory_gb=3.0, tps=55, quality={"summary": .78}),
    ModelProfile("medium", context=32768, memory_gb=8.0, tps=25, quality={"summary": .88}),
]

print(choose(models, Task("summary", prompt_tokens=5000, output_tokens=300)))
```

Maintained by **Aarnav Saboo**.
