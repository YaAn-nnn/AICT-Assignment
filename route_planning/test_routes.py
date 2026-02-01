import time
import csv
from graph import graph_today, graph_future
from search_algorithms import SearchAlgorithms


def init_totals():
    return {
        "DFS": {"cost": 0.0, "nodes": 0, "time": 0.0, "count": 0},
        "BFS": {"cost": 0.0, "nodes": 0, "time": 0.0, "count": 0},
        "GBFS": {"cost": 0.0, "nodes": 0, "time": 0.0, "count": 0},
        "A*": {"cost": 0.0, "nodes": 0, "time": 0.0, "count": 0},
    }


def record(totals, algo_name, path, cost, expanded, elapsed):
    # If algorithm fails to find a path, skip it so averages aren’t broken
    if path is None:
        return
    totals[algo_name]["cost"] += float(cost)
    totals[algo_name]["nodes"] += int(expanded)
    totals[algo_name]["time"] += float(elapsed)
    totals[algo_name]["count"] += 1


def totals_to_averages(totals):
    avgs = {}
    for algo, v in totals.items():
        c = v["count"]
        if c == 0:
            avgs[algo] = {"avg_cost": None, "avg_nodes": None, "avg_time": None, "count": 0}
        else:
            avgs[algo] = {
                "avg_cost": v["cost"] / c,
                "avg_nodes": v["nodes"] / c,
                "avg_time": v["time"] / c,

            }
    return avgs

def print_summary(avgs, title="COMBINED AVERAGE RESULTS SUMMARY (ALL TESTS)"):
    def fmt(x, decimals):
        if x is None:
            return "N/A"
        return str(round(x, decimals))

    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)
    print(f"{'Algorithm':<10} | {'Avg Cost (min)':>14} {'Avg Nodes':>12} {'Avg Time (ms)':>14}")
    print("-" * 72)

    for algo in ["DFS", "BFS", "GBFS", "A*"]:
        row = avgs.get(algo, {"avg_cost": None, "avg_nodes": None, "avg_time": None})
        avg_time_ms = row["avg_time"] * 1000 if row["avg_time"] is not None else None

        print(f"{algo:<10} | "
              f"{fmt(row['avg_cost'], 2):>14} "
              f"{fmt(row['avg_nodes'], 2):>12} "
              f"{fmt(avg_time_ms, 3):>14}")

    print("=" * 72)

def run_one(algos, algo_name, start, goal, time_of_day):
    t0 = time.perf_counter()

    if algo_name == "DFS":
        path, cost, expanded = algos.dfs(start, goal, max_depth=None, time_of_day=time_of_day)
    elif algo_name == "BFS":
        path, cost, expanded = algos.bfs(start, goal, time_of_day=time_of_day)
    elif algo_name == "GBFS":
        path, cost, expanded = algos.gbfs(start, goal, time_of_day=time_of_day)
    elif algo_name == "A*":
        path, cost, expanded = algos.a_star(start, goal, time_of_day=time_of_day)
    else:
        raise ValueError("Unknown algorithm: " + algo_name)

    t1 = time.perf_counter()

    if path is None:
        return None  # caller decides how to handle

    elapsed_ms = (t1 - t0) * 1000
    return {
        "path": path,
        "cost": float(cost),
        "nodes": int(expanded),
        "time_ms": float(elapsed_ms)
    }

def write_csv(avgs, filename="combined_algorithm_averages.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Algorithm",
            "AvgCostMinutes",
            "AvgNodesExpanded",
            "AvgTimeMilliseconds"
        ])

        for algo in ["DFS", "BFS", "GBFS", "A*"]:
            row = avgs.get(algo, {"avg_cost": None, "avg_nodes": None, "avg_time": None})
            avg_time_ms = row["avg_time"] * 1000 if row["avg_time"] is not None else None

            writer.writerow([
                algo,
                round(row["avg_cost"], 6) if row["avg_cost"] is not None else "",
                round(row["avg_nodes"], 6) if row["avg_nodes"] is not None else "",
                round(avg_time_ms, 6) if avg_time_ms is not None else ""
            ])

    print(f"CSV saved: {filename}")

def write_today_vs_future_same_pairs_csv(graph_today, graph_future, od_pairs_same, filename="today_vs_future_same_pairs.csv", time_of_day="off_peak"):
    algos_today = SearchAlgorithms(graph_today)
    algos_future = SearchAlgorithms(graph_future)

    algorithms = ["DFS", "BFS", "GBFS", "A*"]

    rows = []
    for (start, goal) in od_pairs_same:
        for algo in algorithms:
            r_today = run_one(algos_today, algo, start, goal, time_of_day)
            r_future = run_one(algos_future, algo, start, goal, time_of_day)

            # If either fails, still write row but leave blanks
            if r_today is None or r_future is None:
                rows.append([
                    algo, start, goal,
                    "" if r_today is None else round(r_today["cost"], 6),
                    "" if r_today is None else r_today["nodes"],
                    "" if r_today is None else round(r_today["time_ms"], 6),
                    "" if r_future is None else round(r_future["cost"], 6),
                    "" if r_future is None else r_future["nodes"],
                    "" if r_future is None else round(r_future["time_ms"], 6),
                    "", "", ""
                ])
                continue

            delta_cost = r_future["cost"] - r_today["cost"]
            delta_nodes = r_future["nodes"] - r_today["nodes"]
            delta_time = r_future["time_ms"] - r_today["time_ms"]

            rows.append([
                algo, start, goal,
                round(r_today["cost"], 6), r_today["nodes"], round(r_today["time_ms"], 6),
                round(r_future["cost"], 6), r_future["nodes"], round(r_future["time_ms"], 6),
                round(delta_cost, 6), delta_nodes, round(delta_time, 6)
            ])

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Algorithm", "Start", "Goal",
            "TodayCostMin", "TodayNodes", "TodayTimeMs",
            "FutureCostMin", "FutureNodes", "FutureTimeMs",
            "DeltaCostMin_FutureMinusToday", "DeltaNodes_FutureMinusToday", "DeltaTimeMs_FutureMinusToday"
        ])
        writer.writerows(rows)

    print(f"CSV saved: {filename}")

def run_tests_and_accumulate(graph, od_pairs, totals, time_of_day="off_peak", verbose=True):
    algos = SearchAlgorithms(graph)

    for start, goal in od_pairs:
        if verbose:
            print(f"\nOD Pair: {start} -> {goal}")

        # DFS
        t0 = time.perf_counter()
        path, cost, expanded = algos.dfs(start, goal, max_depth=None, time_of_day=time_of_day)
        t1 = time.perf_counter()
        if verbose:
            print(f"DFS Path: {path}")
            elapsed_ms = (t1 - t0) * 1000
            print(f"Cost: {round(cost, 2)} Nodes: {expanded} Time: {round(elapsed_ms, 3)} ms")

        record(totals, "DFS", path, cost, expanded, t1 - t0)

        # BFS
        t0 = time.perf_counter()
        path, cost, expanded = algos.bfs(start, goal, time_of_day=time_of_day)
        t1 = time.perf_counter()
        if verbose:
            print(f"BFS Path: {path}")
            elapsed_ms = (t1 - t0) * 1000
            print(f"Cost: {round(cost, 2)} Nodes: {expanded} Time: {round(elapsed_ms, 3)} ms")
        record(totals, "BFS", path, cost, expanded, t1 - t0)

        # GBFS
        t0 = time.perf_counter()
        path, cost, expanded = algos.gbfs(start, goal, time_of_day=time_of_day)
        t1 = time.perf_counter()
        if verbose:
            print(f"GBFS Path: {path}")
            elapsed_ms = (t1 - t0) * 1000
            print(f"Cost: {round(cost, 2)} Nodes: {expanded} Time: {round(elapsed_ms, 3)} ms")
        record(totals, "GBFS", path, cost, expanded, t1 - t0)

        # A*
        t0 = time.perf_counter()
        path, cost, expanded = algos.a_star(start, goal, time_of_day=time_of_day)
        t1 = time.perf_counter()
        if verbose:
            print(f"A* Path: {path}")
            elapsed_ms = (t1 - t0) * 1000
            print(f"Cost: {round(cost, 2)} Nodes: {expanded} Time: {round(elapsed_ms, 3)} ms")
        record(totals, "A*", path, cost, expanded, t1 - t0)


if __name__ == "__main__":

    od_today = [
        ("Changi Airport", "City Hall"),
        ("Changi Airport", "Orchard"),
        ("Changi Airport", "Gardens by the Bay"),
        ("Paya Lebar", "Changi Airport"),
        ("Tampines", "Changi Airport"),
    ]

    od_future = [
        ("Changi Airport", "City Hall"),
        ("Changi Airport", "Orchard"),
        ("Changi Airport", "Gardens by the Bay"),
        ("Paya Lebar", "T5"),
        ("Harbourfront", "T5"),
        ("Bishan", "T5"),
        ("Tampines", "T5"),
    ]

    od_same = [ #For comparison between today and future
        ("Changi Airport", "City Hall"),
        ("Changi Airport", "Orchard"),
        ("Changi Airport", "Gardens by the Bay"),
    ]

    totals = init_totals()

    print("=" * 30)
    print("Running tests for: TODAY MODE")
    print("=" * 30)
    run_tests_and_accumulate(graph_today, od_today, totals, time_of_day="off_peak", verbose=True)

    print("\n" + "=" * 30)
    print("Running tests for: FUTURE MODE")
    print("=" * 30)
    run_tests_and_accumulate(graph_future, od_future, totals, time_of_day="off_peak", verbose=True)

    avgs = totals_to_averages(totals)
    print_summary(avgs, title="COMBINED AVERAGE RESULTS SUMMARY (ALL OD PAIRS TOGETHER)")
    write_csv(avgs, filename="combined_algorithm_averages.csv")
    write_today_vs_future_same_pairs_csv(
        graph_today,
        graph_future,
        od_same,
        filename="today_vs_future_same_pairs.csv",
        time_of_day="off_peak"
    )