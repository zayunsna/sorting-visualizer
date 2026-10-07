"""Check that every algorithm really sorts. Run: python3 test_sorts.py"""
import os
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"  # no window needed
import sort_visualizer as sv


def inputs(n, rng):
    data = [rng.randint(20, 100) for _ in range(n)]
    return {
        "random": data,
        "reversed": sorted(data, reverse=True),
        "sorted": sorted(data),
        "few unique": [rng.choice((20, 40, 60, 80, 100)) for _ in range(n)],
    }


def main():
    rng = random.Random(0)
    checked = 0
    for n in (0, 1, 2, 7, 42, 120):
        for pattern, data in inputs(n, rng).items():
            for name, algorithm in sv.ALGORITHMS:
                arr = list(data)
                for _ in algorithm(arr):  # run the generator to the end
                    pass
                assert arr == sorted(data), f"{name} failed on {pattern}, n={n}"
                checked += 1
    print(f"ok: {checked} runs, all sorted")


if __name__ == "__main__":
    main()
