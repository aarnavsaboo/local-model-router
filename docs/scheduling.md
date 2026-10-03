# Scheduling notes

Single-request routing and workload scheduling are different problems.

A fast small model can be the best choice for one request and still become a bottleneck when many jobs arrive together. Queue delay therefore appears alongside predicted execution time.

The simulator intentionally uses a simple virtual-time model. It is useful for comparing routing heuristics and warm-pool configurations before connecting the router to a real local service.
