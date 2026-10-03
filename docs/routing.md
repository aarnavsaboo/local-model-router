# Routing experiments

The router uses constraints first and ranking second. A model that cannot fit the prompt, exceeds the memory budget or misses the configured task floor is removed before latency is considered.

The current score is deliberately simple: predicted startup plus decode time. Experiments can replace it with a Pareto frontier or a learned selector, but the baseline should remain available. A learned router is not automatically better if its own inference cost is comparable to the models being selected.

Useful experiments include keeping two small models warm, measuring cold-start penalties, and changing the task floor until the selected model changes.
