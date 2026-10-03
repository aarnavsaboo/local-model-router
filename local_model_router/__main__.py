from argparse import ArgumentParser
import json

from .io import load_pool, load_task, load_tasks
from .pool import ModelPool
from .report import summarize
from .scheduler import route
from .simulation import replay


def main():
    parser = ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("route")
    r.add_argument("pool")
    r.add_argument("task")

    s = sub.add_parser("simulate")
    s.add_argument("pool")
    s.add_argument("workload")
    s.add_argument("--arrival-gap", type=float, default=0.0)

    args = parser.parse_args()
    models, memory_limit = load_pool(args.pool)
    pool = ModelPool(models, memory_limit)

    if args.cmd == "route":
        print(json.dumps(route(pool, load_task(args.task)).__dict__, indent=2))
    else:
        rows = replay(pool, load_tasks(args.workload), args.arrival_gap)
        print(json.dumps({"summary":summarize(rows),"records":rows}, indent=2))


if __name__ == "__main__":
    main()
