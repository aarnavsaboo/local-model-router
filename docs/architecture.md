# Architecture

`local-model-router` separates policy, mutable runtime observations and workload simulation so routing decisions remain explainable.

## Components

```text
job
 |
 v
constraint filter
 |  context / memory / task floor
 v
candidate models
 |
 v
latency + queue estimator
 |
 v
routing policy
 |
 v
selected model
 |
 +--> execution observation
          |
          v
      profile update
```

The model profile is descriptive state: context capacity, memory estimate, measured throughput, startup behavior, task scores and concurrency capacity. The job record contains request-specific requirements. Routing combines the two but does not hide either.

## Decision invariants

A candidate is rejected before ranking when it cannot satisfy a hard constraint such as context capacity or memory budget. Soft preferences such as latency target and warm state affect ordering after feasibility is established.

Queue delay is modeled separately from decode time. This matters under bursts: a nominally faster model may become a worse choice when its configured capacity is already occupied.

## Observations

Runtime measurements update profiles using exponential moving averages rather than replacing historical values with the most recent sample. Observations are intentionally explicit so routing behavior can be reproduced from the same profile snapshot.

## Simulation

The simulator uses a virtual clock and the same routing inputs as the online decision path. It is designed for policy experiments, not as a production queue implementation.

Simulation output should retain:

- selected model
- arrival/start/finish times
- predicted and observed latency fields
- queue depth/capacity state
- job constraints
- profile revision used for the decision

## Extension points

New routing policies should consume the same candidate representation and return an ordered decision with reason fields. Runtime adapters should remain outside the policy layer so local servers can be changed without rewriting scheduling logic.
