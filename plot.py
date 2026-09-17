# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib", "numpy"]
# ///

"""
One year of sunlight over Hong Kong, drawn as one ray per day.

    uv run plot.py

Two numbers arrive for every day of 2025, both in kW-hr per square metre per day:
what reached the ground, and what would have reached it under a clear sky. Each
day becomes a ray leaving the centre of the page.

    the pale outer length   what the sky promised that day: the season talking
    the coloured inner part what actually got through: how clear the day was
    the colour itself       the ratio between the two, cool when it clouded over

Summer rays reach further out because the ceiling itself is higher; a dull day is
a short bright stub inside a long pale promise. Nothing here is decorative: every
line is one line of the file.
"""

import csv
import datetime as dt
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

FILE = "nasa-power-hong-kong-daily-solar-2025.csv"
PICTURE = "sunlight-2025.png"
MISSING = -999.0

PLACE = "HONG KONG"
YEAR = "2025"

INNER = 0.30           # where a ray starts
OUTER = 1.00           # where the longest ray ends
START = 0.5 * math.pi  # 1 January sits at twelve o'clock and the year runs clockwise

PROMISE = "#46596F"    # the clear-sky ceiling, barely lit
INK = "#E8EAED"        # captions
PAPER = "#0B0F14"      # the page

# A few rings of the same radius for every day, so the eye has a ruler.
RULER = "#1C2632"
RINGS = (2, 4, 6)      # kW-hr per square metre per day

# What came through, from a shuttered sky to a bare one. One colour ramp, and it
# carries the only thing the picture refuses to draw any other way.
CLEARNESS = LinearSegmentedColormap.from_list("clearness", [
    "#2E5C77", "#6E93A6", "#C9C2A8", "#F2C25B", "#FFF0B8",
])

HERE = Path(__file__).parent
DATA = HERE / "data" / FILE
OUT = HERE / "out"


def rows(path):
    """The data rows. NASA POWER writes a -BEGIN HEADER- block above the table,
    so keep the lines that start with a year."""
    kept = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for line in csv.reader(handle):
            if line and line[0].strip().isdigit():
                kept.append([cell.strip() for cell in line])
    return kept


def number(text):
    """Power's numbers arrive as text; -999 is its way of saying 'no reading'."""
    value = float(text)
    return None if value == MISSING else value


def xy(angle, radius):
    """A place on the page from an angle and how far out along it."""
    return (radius * math.cos(angle), radius * math.sin(angle))


def ray(ax, angle, got, ceiling, scale):
    """One day: a pale promise from centre to ceiling, and the light that got
    through drawn over it, coloured by how much that was."""
    x0, y0 = xy(angle, INNER)
    x1, y1 = xy(angle, INNER + ceiling * scale)
    ax.plot([x0, x1], [y0, y1], color=PROMISE, linewidth=2.0, solid_capstyle="butt", zorder=2)

    xr, yr = xy(angle, INNER + got * scale)
    ax.plot([x0, xr], [y0, yr], color=CLEARNESS(got / ceiling),
            linewidth=2.0, solid_capstyle="butt", zorder=3)


def sun(ax, radius=0.46, brightness=0.07):
    """A soft disc where the rays come from. Not data — the paper the data sits on."""
    axis = np.linspace(-1.05, 1.05, 400)
    xx, yy = np.meshgrid(axis, axis)
    falloff = np.exp(-(np.hypot(xx, yy) / radius) ** 2)
    disc = np.zeros((*falloff.shape, 4))
    disc[..., 0], disc[..., 1], disc[..., 2] = 1.0, 0.93, 0.76
    disc[..., 3] = falloff * brightness
    ax.imshow(disc, extent=(-1.05, 1.05, -1.05, 1.05), origin="lower",
              interpolation="bilinear", zorder=1)


def ruler(ax, scale):
    """Rings at the round numbers, so a length on the page has a size."""
    turn = [2 * math.pi * t / 360 for t in range(361)]
    for value in RINGS:
        r = INNER + value * scale
        ax.plot([r * math.cos(t) for t in turn], [r * math.sin(t) for t in turn],
                color=RULER, linewidth=0.5, zorder=1.5)
        x, y = xy(math.radians(97), r)
        ax.text(x, y, f"{value}", color="#2E3B4A", fontsize=7.5, ha="center",
                va="bottom", zorder=4)


def main():
    table = rows(DATA)
    days, got, ceiling = [], [], []
    for year, month, day, allsky, clearsky in table:        # the loop over the numbers
        a, c = number(allsky), number(clearsky)
        if a is None or c is None or c <= 0:
            continue                                        # POWER could not measure that day
        days.append(dt.date(int(year), int(month), int(day)))
        got.append(a)
        ceiling.append(c)

    n = len(days)
    scale = (OUTER - INNER) / max(ceiling)
    print(f"{n} days, {days[0]} to {days[-1]}")
    print(f"ceiling {min(ceiling):.2f} to {max(ceiling):.2f}, "
          f"got {min(got):.2f} to {max(got):.2f} kW-hr/m2/day")

    fig, ax = plt.subplots(figsize=(9, 10.2), facecolor=PAPER)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.99, bottom=0.15)
    ax.set_facecolor(PAPER)
    ax.set_aspect("equal")
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    ax.axis("off")

    sun(ax)
    ruler(ax, scale)

    for i in range(n):                                      # one ray, one day
        ray(ax, START - 2 * math.pi * i / n, got[i], ceiling[i], scale)

    # Where the months are, so the shape has a calendar under it.
    for month in range(1, 13):
        first = min(i for i, d in enumerate(days) if d.month == month)
        last = max(i for i, d in enumerate(days) if d.month == month)
        angle = START - 2 * math.pi * (first + last) / 2 / n
        x, y = xy(angle, 1.015)
        ax.text(x, y, days[first].strftime("%b").upper(), color="#5C6C7C",
                fontsize=10, ha="center", va="center")

    ax.text(0, 0, f"{PLACE}\n{YEAR}", color=INK, fontsize=14,
            ha="center", va="center", linespacing=1.6)
    fig.text(0.5, 0.055,
             "one ray per day, 1 January at the top, clockwise\n"
             "outer length: what a clear sky would have delivered      "
             "inner length: what reached the ground\n"
             "colour: the ratio between the two, cool when it clouded over      "
             "rings: kW-hr/m²/day\n"
             "NASA POWER CERES SYN1deg, 22.28°N 114.16°E",
             color="#78838F", fontsize=9, ha="center", va="bottom", linespacing=1.9)

    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / PICTURE, dpi=200, facecolor=PAPER)
    print(f"saved out/{PICTURE}")
    plt.show()


if __name__ == "__main__":
    main()
