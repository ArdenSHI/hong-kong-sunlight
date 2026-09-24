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
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap

FILE = "nasa-power-hong-kong-daily-solar-2025.csv"
PICTURE = "sunlight-2025.png"
MISSING = -999.0

PLACE = "HONG KONG"
YEAR = "2025"

INNER = 0.30           # where a ray starts, and where the measurement starts from
OUTER = 1.00           # where the rim of the wheel is
FULL_SCALE = 8.0       # kW-hr/m²/day at that rim — the same number the page
                       # uses, and the same in 2025 and in 2026, so a ray's
                       # length means one thing in print and in both years
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

# It is ink on coarse paper, not a fill: the rim wanders, the sheet's tooth keeps
# part of the ink off the page, and where the ink thinned the paper lit up.
SUN_EDGE = 0.075       # how far the rim wanders, as a fraction of the radius
SUN_TOOTH = 0.45       # paper showing through the ink
SUN_MOTTLE = 0.16      # the unevenness of a hand, not of a printer
SUN_BLEED = 0.30       # the pale places where the ink thinned
SUN_PALE = "#FFE9B8"   # the colour of a thinned place
GRAIN_FADE = 0.20      # how much of the grain survives at the very centre

# The title is written rather than typeset, if this machine has a hand to lend.
# Missing, it falls back to the default face and the picture still works.
TITLE_HANDS = ("Marker Felt", "Bradley Hand", "Chalkboard", "Comic Sans MS")

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


def polar(span, grid):
    """How far every point on the page is from the middle, and at what angle.
    Everything round in this picture is built out of these two arrays."""
    axis = np.linspace(-span, span, grid)
    xx, yy = np.meshgrid(axis, axis)
    return np.hypot(xx, yy), np.arctan2(yy, xx)


def field(stops, rr, radius):
    """A round sheet laid over the page, with `stops` — (fraction of `radius`,
    value) — running outward. `rr` is how far every point already is. A value is
    either '#rrggbb' or a plain number, and numbers land in the alpha channel.
    Returns how far out each point is, as a fraction of the radius."""
    t = np.clip(rr / radius, 0, 1)
    sheet = np.zeros((*rr.shape, 4))
    along = [stop[0] for stop in stops]
    if isinstance(stops[0][1], str):
        for channel in range(3):
            sheet[..., channel] = np.interp(
                t, along, [rgb(stop[1])[channel] for stop in stops])
        sheet[..., 3] = 1.0
    else:
        sheet[..., 3] = np.interp(t, along, [stop[1] for stop in stops])
    return t, sheet


def wobble(theta, seed=3, harmonics=6):
    """A slow wander round a circle, so a rim looks drawn and not stamped. Built
    from sines, so it closes on itself, and seeded, so it is the same every run."""
    rng = np.random.default_rng(seed)
    phase = rng.random(harmonics) * 2 * math.pi
    weight = 1.0 / np.arange(1, harmonics + 1)
    out = sum(w * np.sin((k + 1) * theta + p)
              for k, (w, p) in enumerate(zip(weight, phase)))
    return out / weight.sum()


def fibre(grid, cells, octaves, seed):
    """The sheet the ink sits on: random values on a coarse grid, enlarged and
    half as loud at each step, so it is rough at every size at once. 0 to 1,
    around 0.5, and the same on every run."""
    rng = np.random.default_rng(seed)
    out = np.zeros((grid, grid))
    weight, total = 1.0, 0.0
    for _ in range(octaves):
        small = rng.random((cells, cells))
        at = np.linspace(0, cells - 1, grid)
        lo = np.floor(at).astype(int)
        hi = np.minimum(lo + 1, cells - 1)
        frac = at - lo
        soft = frac * frac * (3 - 2 * frac)      # smoothstep, or the grid shows
        band = small[:, lo] * (1 - soft) + small[:, hi] * soft        # along x
        out += weight * (band[lo, :] * (1 - soft)[:, None]
                         + band[hi, :] * soft[:, None])               # then along y
        total += weight
        weight *= 0.5
        cells *= 2
    return out / total


def speck(grid, cells, seed, weight, darkest=True):
    """The roughness of one size of paper, as an amount of colour to lay down.
    Above the average the sheet's tooth keeps the ink off; below it the ink
    thinned and the paper shows through paler. `cells` sets the size."""
    field = fibre(grid, cells, 1, seed)
    z = (field - field.mean()) / field.std()
    if not darkest:
        z = -z
    return weight * np.clip(z / 2.0, 0, 1)


def ink_over(skin, alpha, colour):
    """Lay a colour over the skin where `alpha` says so — the paper showing
    through, or ink thinning out into it."""
    want = np.array(rgb(colour))
    for channel in range(3):
        skin[..., channel] = (skin[..., channel] * (1 - alpha)
                              + want[channel] * alpha)
    return skin


def hands():
    """The first hand this machine has, or None, which is not a failure."""
    have = {face.name for face in font_manager.fontManager.ttflist}
    return next((name for name in TITLE_HANDS if name in have), None)


def sun(ax, grid=1400, span=1.05):
    """The thing the numbers are about, in the hole at the middle of the wheel.
    Not a measurement: it is smaller than the radius the rays start from, so no
    day can be inflated by it. It is ink on paper, so it is not flat either."""
    rr, theta = polar(span, grid)

    # The warmth the sun puts on the page, laid down first so the ink sits on
    # top of its own light.
    gt, glow = field(HALO, rr, SUN_R * 1.55)
    glow[..., 0], glow[..., 1], glow[..., 2] = rgb("#FFAA46")
    glow[..., 3] *= 1 - np.clip((gt - 1 / 1.55) / 0.02, 0, 1)   # room for the ink
    ax.imshow(glow, extent=(-span, span, -span, span), origin="lower",
              interpolation="bilinear", zorder=0.5)

    t, skin = field(SUN_SKIN, rr, SUN_R * (1 + SUN_EDGE * wobble(theta)))

    # A hand is never even. Broad blotches, then the tooth of the sheet, then the
    # places the ink thinned and the paper lit up. The middle stays clearest: it
    # is the part of the sun the eye is supposed to read through.
    # A hand is never even, and paper is rough at every size at once, so each
    # scale is laid down on its own: the blotches a hand leaves, the grain of the
    # sheet, and the pale places where the ink thinned. Also: separate layers,
    # because one fractal field added up and then thresholded would let the
    # coarse part swallow the fine part wherever it happened to be low.
    fade = GRAIN_FADE + (1 - GRAIN_FADE) * np.clip(t, 0, 1)
    # The grain is asked for at about the size of a pixel of the finished
    # picture. Any coarser and the enlargement blurs it into a wash.
    for cells, seed, colour, weight, darkest in (
            (18, 27, PAPER, SUN_MOTTLE, True),      # the unevenness of a hand
            (112, 41, SUN_PALE, SUN_BLEED, False),  # where the ink thinned
            (700, 9, PAPER, SUN_TOOTH, True)):      # the tooth of the sheet
        ink_over(skin, speck(grid, cells, seed, weight, darkest) * fade, colour)

    skin[..., 3] = 1 - np.clip((t - 0.975) / 0.025, 0, 1)     # a soft rim
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
    # One scale, and not this file's own: the page draws the same year, and the
    # page also draws a year that is still arriving, so the rim has to mean one
    # number wherever it appears. FULL_SCALE is that number.
    scale = (OUTER - INNER) / FULL_SCALE
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

    # Written on the sun in whatever hand is available. The sizes are set so the
    # widest hand still fits inside the ink: 0.26 of the radius is 0.52 across.
    hand = hands()
    for text, size, y in ((PLACE, 15, 0.040), (YEAR, 11.5, -0.034)):
        ax.text(0, y, text, color=SUN_INK, ha="center", va="center", zorder=5,
                fontproperties=font_manager.FontProperties(
                    family=hand or "sans-serif", size=size))
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
