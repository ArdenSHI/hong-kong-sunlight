# A year of sunlight over Hong Kong

![2025 over Hong Kong: one ray per day](out/sunlight-2025.png)

## The phenomenon

The sun does not deliver the same thing every day. At 22°N the height of the sun
at noon swings between roughly 45° in December and 90° in June, so a clear June
day offers nearly twice the energy of a clear December one. On top of that comes
the cloud: Hong Kong's sky is generous in winter and stingy in spring, and no
season's ceiling is ever fully delivered. 2025 is a year of both, one number per
day, 365 numbers.

## The data

NASA POWER, CERES SYN1deg, for the point 22.28°N 114.16°E — the file is
`data/nasa-power-hong-kong-daily-solar-2025.csv`, fetched once from the API and
committed unchanged:

<https://power.larc.nasa.gov/api/temporal/daily/point>

365 rows after the header block, one per day of 2025. A row is
`YEAR,MO,DY,ALLSKY_SFC_SW_DWN,CLRSKY_SFC_SW_DWN`, both columns in kW-hr per square
metre per day: what actually reached the ground, and what a cloudless sky would
have delivered to it.

## The picture

Every day of the year is one ray leaving the centre of the page. 1 January is at
the top and the year runs clockwise, so the wheel is a calendar. The pale line is
the clear-sky ceiling of that day; the coloured line over it is what got through;
the colour of that line is the ratio between the two. Winter rays are short
because the ceiling itself is low; summer rays reach far out. A dull day is a
short bright stub inside a long pale promise, which is what much of February to
May looks like: 4 April received 3.44 kW-hr/m² against a ceiling of 5.78.

## What it shows, and what it hides

It shows the two things at once and refuses to separate them — the season sets
the length, the cloud decides the colour. January is the clearest month (85% of
its ceiling); February to May are the dullest, none of them reaching 70%. The
dullest single day was 4 August, when 6% of the available light arrived; the
clearest was 23 March, at 99.8%.

What it hides: one number per day cannot say *when* the sun came out. A day of
clear mornings and rainy afternoons and a uniformly grey day that happen to
deliver the same total are drawn identically. It also hides the space inside the
cell: the value is an average over a 0.5° × 0.625° box, so nothing distinguishes
a sunny island from a cloudy hill. And it is one year — a month here is one
month, not a climate.

## How to run it

```bash
uv run peek.py     # read the file and print it, before drawing anything
uv run plot.py     # writes out/sunlight-2025.png
uv run fetch.py    # only if data/ is missing: asks NASA once
```
