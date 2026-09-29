# termplot

ASCII charts in the terminal: bar charts, histograms, sparklines and line
plots. Single file, pure standard library - importable functions plus a
small CLI. Useful for quick data checks over SSH, in cron reports, or
anywhere a plotting library is overkill.

## CLI

```console
$ termplot bar "php=312" "python=984" "go=421" --width 30
   php │█████████ 312
python │████████████████████████████ 984
    go │████████████ 421

$ termplot spark 2 4 3 7 6 8 5
▁▃▂▇▆█▅

$ termplot hist 1 2 2 3 3 3 4 4 --bins 3

$ termplot line 1 3 2 5 4 --width 24 --height 6
```

`hist`, `spark` and `line` read numbers from stdin when no arguments are
given:

```console
$ awk '{print $2}' access.log | termplot spark
```

## Python API

```python
from termplot import bar_chart, histogram, sparkline, line_chart

bar_chart(["php", "python"], [312, 984], width=30)   # -> list[str]
histogram([1, 2, 2, 3], bins=4)                      # -> list[str]
sparkline([2, 4, 3, 7, 6, 8, 5])                     # -> "▂▄▃█▅▆▄"
line_chart([1, 3, 2, 5, 4], width=24, height=6)      # -> list[str]
```

- `bar_chart` scales the longest bar to `width`; values are printed
  beside each bar.
- `histogram` uses equal-width bins over the data range; the count is
  printed at the end of every row.
- `sparkline` maps values onto `▁▂▃▄▅▆▇█` (min -> ▁, max -> █); flat
  input renders as a row of `▁`.
- `line_chart` spreads points evenly across `width` columns with the y
  axis labelled by min/max.

All functions are side-effect free and return lines (or a string) ready
to print. `bar_chart` raises `ValueError` when labels and values differ
in length.

## Testing

```console
$ python3 termplot.py --test
selftest: failures=0
```

Covers bar scaling, histogram count conservation, exact sparkline output,
flat/empty sparklines, line-plot point coverage, axis labels and error
handling.

## License

MIT
