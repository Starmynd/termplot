#!/usr/bin/env python3
"""termplot - ASCII charts in the terminal: bars, histograms, sparklines.

Importable functions plus a small CLI. Pure standard library.
"""

from __future__ import annotations

import argparse
import sys

SPARK_CHARS = "▁▂▃▄▅▆▇█"


def bar_chart(labels: list[str], values: list[float], width: int = 40,
              char: str = "█") -> list[str]:
    """Horizontal bar chart, one line per label, longest bar == width."""
    if len(labels) != len(values):
        raise ValueError("labels and values must have the same length")
    if not values:
        return []
    vmax = max(values)
    scale = (width / vmax) if vmax > 0 else 0.0
    lines = []
    lw = max(len(str(l)) for l in labels)
    for label, value in zip(labels, values):
        bar = char * max(0, round(value * scale))
        lines.append(f"{str(label):>{lw}} │{bar} {value:g}")
    return lines


def histogram(data: list[float], bins: int = 10, width: int = 40,
              char: str = "█") -> list[str]:
    """Histogram of raw values with equal-width bins."""
    if not data:
        return []
    lo, hi = min(data), max(data)
    if lo == hi:
        lines = [f"[{lo:g}] {'█' * width} {len(data)}"]
        return lines
    bin_w = (hi - lo) / bins
    counts = [0] * bins
    for x in data:
        idx = int((x - lo) / bin_w)
        counts[min(idx, bins - 1)] += 1
    vmax = max(counts)
    scale = (width / vmax) if vmax else 0
    lines = []
    for i, c in enumerate(counts):
        a, b = lo + i * bin_w, lo + (i + 1) * bin_w
        lines.append(f"[{a:8.3g}, {b:8.3g}) {'█' * round(c * scale)} {c}")
    return lines


def sparkline(values: list[float]) -> str:
    """Compact one-line chart using Unicode block characters."""
    if not values:
        return ""
    lo, hi = min(values), max(values)
    if hi == lo:
        return SPARK_CHARS[0] * len(values)
    n = len(SPARK_CHARS)
    return "".join(SPARK_CHARS[min(n - 1, int((v - lo) / (hi - lo) * n))]
                   for v in values)


def line_chart(values: list[float], width: int = 60, height: int = 12,
               char: str = "*") -> list[str]:
    """Simple ASCII line plot; x spread over `width` columns."""
    if not values:
        return []
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    n = len(values)
    grid = [[" "] * width for _ in range(height)]

    def col_for(i: int) -> int:
        return min(width - 1, i * (width - 1) // max(1, n - 1))

    def row_for(v: float) -> int:
        return min(height - 1, int((v - lo) / span * (height - 1)))

    for i, v in enumerate(values):
        grid[height - 1 - row_for(v)][col_for(i)] = char

    lines = [f"{hi:8.3g} ┤" + "".join(row) for row in grid]
    axis = " " * 9 + "└" + "─" * width
    lines.append(axis)
    lines.append(f"{lo:8.3g} ┘")
    return lines


def _selftest() -> int:
    failed = 0

    def check(cond: bool, label: str) -> None:
        nonlocal failed
        print(("PASS " if cond else "FAIL ") + label)
        if not cond:
            failed += 1

    bars = bar_chart(["a", "bb", "ccc"], [1, 5, 3], width=10)
    check(len(bars) == 3, "one line per label")
    check("█" * 10 in bars[1] and " 5" in bars[1], "max bar fills width")
    check(len([c for c in bars[0] if c == "█"]) == 2, "scaled bar for a=1")

    data = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5]
    hist = histogram(data, bins=4, width=20)
    total = 0
    for ln in hist:
        tail = ln.rsplit(" ", 1)[-1]
        if tail.isdigit():
            total += int(tail)
    check(total == len(data), f"histogram counts sum to len(data) (got {total})")

    sp = sparkline([1, 2, 3, 4, 5])
    check(sp == "▁▃▅▇█", f"sparkline known output (got {sp!r})")
    check(sparkline([7, 7, 7]) == "▁▁▁", "flat sparkline")
    check(sparkline([]) == "", "empty sparkline")

    lc = line_chart([1, 3, 2, 5, 4], width=20, height=6)
    stars = sum(ln.count("*") for ln in lc)
    check(stars == 5, f"line_chart plots every point (got {stars})")
    check(lc[-1].strip().startswith("1"), "axis shows min")

    try:
        bar_chart(["a"], [1, 2])
        check(False, "bar_chart length mismatch raises")
    except ValueError:
        check(True, "bar_chart length mismatch raises")

    print(f"selftest: failures={failed}")
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--test" in argv:
        return _selftest()

    ap = argparse.ArgumentParser(prog="termplot",
                                 description="ASCII charts in the terminal.")
    sub = ap.add_subparsers(dest="cmd")

    p_bar = sub.add_parser("bar", help="bar chart from label=value pairs")
    p_bar.add_argument("items", nargs="+", metavar="label=value")
    p_bar.add_argument("--width", type=int, default=40)

    p_hist = sub.add_parser("hist", help="histogram from numbers")
    p_hist.add_argument("nums", nargs="*", type=float)
    p_hist.add_argument("--bins", type=int, default=10)

    p_spark = sub.add_parser("spark", help="sparkline from numbers")
    p_spark.add_argument("nums", nargs="*", type=float)

    p_line = sub.add_parser("line", help="line chart from numbers")
    p_line.add_argument("nums", nargs="*", type=float)
    p_line.add_argument("--width", type=int, default=60)
    p_line.add_argument("--height", type=int, default=12)

    args = ap.parse_args(argv)

    if args.cmd == "bar":
        labels, values = [], []
        for item in args.items:
            if "=" not in item:
                ap.error(f"expected label=value, got {item!r}")
            l, v = item.split("=", 1)
            labels.append(l)
            values.append(float(v))
        print("\n".join(bar_chart(labels, values, args.width)))
    elif args.cmd in ("hist", "spark", "line"):
        nums = list(args.nums)
        if not nums:  # read from stdin
            nums = [float(x) for x in sys.stdin.read().split()]
        if args.cmd == "hist":
            print("\n".join(histogram(nums, bins=args.bins)))
        elif args.cmd == "spark":
            print(sparkline(nums))
        else:
            print("\n".join(line_chart(nums)))
    else:
        ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
