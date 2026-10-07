"""Count comparisons and swaps for every algorithm. Run inside this folder: python3 count_ops.py"""
import os
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
import sort_visualizer as sv

N, RUNS = 100, 20


def make(pattern, rng):
    data = [rng.randint(20, 100) for _ in range(N)]
    if pattern == "reversed":
        return sorted(data, reverse=True)
    if pattern == "sorted":
        return sorted(data)
    if pattern == "few unique":
        return [rng.choice((20, 40, 60, 80, 100)) for _ in range(N)]
    return data


def count(algorithm, arr):
    compares = swaps = 0
    for event in algorithm(arr):
        compares += event.action == "compare"
        swaps += event.action == "swap"
    return compares, swaps


patterns = ("random", "reversed", "sorted", "few unique")
print(f"n={N}, mean of {RUNS} arrays per input (compares / swaps)")
print(f"{'algorithm':20s}" + "".join(f"{p:>18s}" for p in patterns))
for name, algorithm in sv.ALGORITHMS:
    cells = []
    for p in patterns:
        rng = random.Random(42)
        c = s = 0
        for _ in range(RUNS):
            ci, si = count(algorithm, make(p, rng))
            c, s = c + ci, s + si
        cells.append(f"{c / RUNS:,.0f} / {s / RUNS:,.0f}")
    print(f"{name:20s}" + "".join(f"{x:>18s}" for x in cells))
