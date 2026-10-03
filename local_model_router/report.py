from collections import Counter
from statistics import median


def summarize(records: list[dict]) -> dict:
    ok = [x for x in records if x.get("ok")]
    distribution = Counter(x["model"] for x in ok)
    predicted = [x["predicted_seconds"] for x in ok]
    queued = [x["queued_s"] for x in ok if "queued_s" in x]
    return {
        "tasks":len(records),
        "routed":len(ok),
        "failed":len(records)-len(ok),
        "model_distribution":dict(sorted(distribution.items())),
        "median_predicted_seconds":None if not predicted else median(predicted),
        "median_queue_seconds":None if not queued else median(queued),
        "max_queue_seconds":None if not queued else max(queued),
    }
