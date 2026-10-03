# local-model-router

A local model-pool router and workload scheduler for experiments with several language models on one machine.

The project started as a simple "pick the fastest model that satisfies a task floor" function. It now models a small local inference pool: model capabilities, memory footprints, warm/cold state, observed throughput, queued work and configurable workload constraints.

The router is intended for systems experiments. It does not assume there is one best model for every task.

## Routing inputs

A job can specify:

- task family
- prompt tokens
- expected output tokens
- minimum measured task score
- maximum memory budget
- required model context window
- latency target
- preferred runtime
- batch/interactive class
- priority

A model profile can include:

- context capacity
- estimated resident memory
- observed decode throughput
- warm and cold startup latency
- task-specific scores
- current warm state
- runtime/backend
- number of active jobs
- configured concurrency capacity

## Routing flow

```text
incoming job
    |
    v
capacity/context filter
    |
    v
task-quality floor
    |
    v
memory feasibility
    |
    v
predicted latency
    |
    +--> warm-state adjustment
    +--> queue delay estimate
    +--> decode estimate
    |
    v
candidate ordering
    |
    v
selected local model
    |
    v
observation -> EWMA profile update
```

## Example

```bash
python -m local_model_router route \
  configs/pool.example.json \
  examples/job.json

python -m local_model_router simulate \
  configs/pool.example.json \
  examples/workload.jsonl
```

## Why simulate?

A routing rule can look good one request at a time and behave badly under a burst. If every small request selects the same fast model, queue delay can dominate while a second model sits idle.

The simulator advances a simple virtual clock, tracks active work per model and records selection decisions. It is deliberately small enough to inspect.

## Observations

After a real run, an observation can update:

- tokens/second
- warm/cold startup estimates
- task score
- recent latency
- warm state

Updates use exponential moving averages so one anomalous run does not replace the entire profile.

## Repository layout

- `router.py` — model/task records and selection
- `pool.py` — mutable model-pool state
- `scheduler.py` — queue-aware routing
- `simulation.py` — virtual workload replay
- `observations.py` — profile updates
- `io.py` — JSON model/job formats
- `report.py` — routing distribution and latency summaries
- `configs/` — example local model pools
- `examples/` — workload fixtures
- `tests/` — routing and simulation tests

Maintained by **Aarnav Saboo**.
