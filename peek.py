# /// script
# requires-python = ">=3.10"
# ///

"""
Print before you plot. Ten seconds now, ten minutes saved later.

    uv run peek.py

The step the brief asks for before any picture exists: read the file, print the
first row, print one value, print its type. A plot that comes out empty is almost
always a plot whose numbers were still strings.
"""

import csv
import datetime as dt
from pathlib import Path

FILE = "nasa-power-hong-kong-daily-solar-2025.csv"
MISSING = -999.0        # NASA POWER's number for "we could not compute this one"

HERE = Path(__file__).parent
DATA = HERE / "data" / FILE


def rows(path):
    """The data rows, as lists. POWER puts a -BEGIN HEADER- block above the
    table, so start at the line that begins with a year."""
    kept = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for line in csv.reader(handle):
            if line and line[0].strip().isdigit():
                kept.append([cell.strip() for cell in line])
    return kept


def number(text):
    """Text into a number, or None if POWER could not measure that day."""
    value = float(text)
    return None if value == MISSING else value


def main():
    table = rows(DATA)
    print(f"{DATA.name}: {len(table)} rows")
    print(f"first row: {table[0]}")
    print(f"one value: {table[0][3]!r}  its type before we touch it: {type(table[0][3])}")
    print(f"the same value as a number: {number(table[0][3])!r}  -> {type(number(table[0][3]))}")

    days, got, clear = [], [], []
    for year, month, day, allsky, clearsky in table:          # the loop over the numbers
        a, c = number(allsky), number(clearsky)
        if a is None or c is None:
            print(f"skipped {year}-{month}-{day}: POWER had no value")
            continue
        days.append(dt.date(int(year), int(month), int(day)))
        got.append(a)
        clear.append(c)

    print(f"{len(days)} days, {days[0]} to {days[-1]}")
    print(f"reached the ground: min {min(got):.2f}, max {max(got):.2f} kW-hr/m2/day")
    print(f"clear-sky ceiling:  min {min(clear):.2f}, max {max(clear):.2f}")
    ratios = [g / c for g, c in zip(got, clear)]
    print(f"clearness (got / ceiling): min {min(ratios):.2f}, max {max(ratios):.2f}, "
          f"mean {sum(ratios) / len(ratios):.2f}")


if __name__ == "__main__":
    main()
