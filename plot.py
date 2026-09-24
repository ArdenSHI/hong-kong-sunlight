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

In the middle sits a sun, and round it a pale ring at the radius every ray starts
from. That ring is the zero: without it a length on the page can only be compared
with another length, and with it the length can be read. It is drawn outside the
sun, which is why the sun is smaller than the hole it sits in — a sun that
reached the rays would be able to inflate a day.
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

INNER = 0.30           # where a ray starts, and where the measurement starts from
OUTER = 1.00           # where the longest ray ends
START = 0.5 * math.pi  # 1 January sits at twelve o'clock and the year runs clockwise

PROMISE = "#46596F"    # the clear-sky ceiling, barely lit
INK = "#E8EAED"        # captions
PAPER = "#0B0F14"      # the page

# A few rings of the same radius for every day, so the eye has a ruler.
RULER = "#1C2632"
RINGS = (2, 4, 6)      # kW-hr per square metre per day
ZERO = "#FFEFC9"       # the ring at zero, the one ring that is not a comparison

# The sun: what the numbers are about, not one of the numbers. Amber at the
# centre down to burnt orange at the rim, the same stops the page uses.
SUN_R = 0.26           # deliberately less than INNER, so it never touches a ray
SUN_INK = "#4A2C07"    # dark, because it sits on the lit face of the sun
SUN_SKIN = ((0.00, "#FFE9A6"), (0.30, "#F9C24E"), (0.62, "#EF8E24"),
            (0.86, "#D45D12"), (1.00, "#A63C08"))
HALO = ((0.00, 0.20), (0.45, 0.09), (1.00, 0.00))   # radius, then opacity

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


def rgb(hexcolour):
    """'#F9C24E' to three floats, so a stop can be interpolated."""
    return [int(hexcolour[i:i + 2], 16) / 255 for i in (1, 3, 5)]


def field(stops, radius, span=1.05, grid=760):
    """A round sheet laid over the page, with `stops` — (fraction of the radius,
    value) — running outward. A value is either '#rrggbb' or a plain number, and
    numbers land in the alpha channel. Returns how far out every point is, as a
    fraction of the radius, so the caller can trim an edge."""
    axis = np.linspace(-span, span, grid)
    xx, yy = np.meshgrid(axis, axis)
    t = np.clip(np.hypot(xx, yy) / radius, 0, 1)
    sheet = np.zeros((grid, grid, 4))
    along = [stop[0] for stop in stops]
    if isinstance(stops[0][1], str):
        for channel in range(3):
            sheet[..., channel] = np.interp(
                t, along, [rgb(stop[1])[channel] for stop in stops])
        sheet[..., 3] = 1.0
    else:
        sheet[..., 3] = np.interp(t, along, [stop[1] for stop in stops])
    return t, sheet


def sun(ax):
    """The thing the numbers are about, in the hole at the middle of the wheel.
    Not a measurement: it is smaller than the radius the rays start from, so no
    day can be inflated by it."""
    span = 1.05
    t, glow = field(HALO, SUN_R * 1.55, span)   # the warmth it puts on the page
    glow[..., 0], glow[..., 1], glow[..., 2] = rgb("#FFAA46")
    glow[..., 3] *= 1 - np.clip((t - 1 / 1.55) / 0.02, 0, 1)  # leave room for the disc
    ax.imshow(glow, extent=(-span, span, -span, span), origin="lower",
              interpolation="bilinear", zorder=0.5)

    t, skin = field(SUN_SKIN, SUN_R, span)      # the disc itself
    skin[..., 3] = 1 - np.clip((t - 0.98) / 0.02, 0, 1)      # a soft rim
    ax.imshow(skin, extent=(-span, span, -span, span), origin="lower",
              interpolation="bilinear", zorder=1)


def ruler(ax, scale):
    """Rings at the round numbers, so a length on the page has a size. The ring
    at zero is drawn with them and lit differently, because it is the one that
    says what a length means rather than how it compares."""
    turn = [2 * math.pi * t / 720 for t in range(721)]

    ax.plot([INNER * math.cos(t) for t in turn], [INNER * math.sin(t) for t in turn],
            color=ZERO, linewidth=1.4, zorder=4)
    x, y = xy(math.radians(97), INNER + 0.038)
    ax.text(x - 0.014, y, "0", color="#C8D0DA", fontsize=8.5, ha="center",
            va="bottom", zorder=5)

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

    ax.text(0, 0.040, PLACE, color=SUN_INK, fontsize=16,
            ha="center", va="center", zorder=5)
    ax.text(0, -0.034, YEAR, color=SUN_INK, fontsize=12,
            ha="center", va="center", zorder=5)
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
