# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///

"""
Ask again for the year that is not finished yet.

    uv run update.py
    uv run site.py

fetch.py fetched 2025 once and keeps it, so the assignment can be run with the
network switched off. This is the opposite of that: it goes back to NASA POWER
and rewrites the file for the year that is still growing, because that file gets
a new line every day. Whatever comes back is written byte for byte — including
the -999 that POWER puts where it has not published a day yet. site.py drops
those when it draws, so the wheel simply stops where the published days stop.

It never touches the year that is over. Run site.py afterwards to rebuild the
pages; on GitHub the two run in that order once a day (see
.github/workflows/update-2026.yml).
"""

import datetime as dt
from pathlib import Path

import requests

LATITUDE = 22.28          # the same window fetch.py looks through
LONGITUDE = 114.16
PLACE = "hong-kong"
PARAMETERS = "ALLSKY_SFC_SW_DWN,CLRSKY_SFC_SW_DWN"

HERE = Path(__file__).parent
DATA = HERE / "data"


def url_for(year):
    return ("https://power.larc.nasa.gov/api/temporal/daily/point"
            f"?parameters={PARAMETERS}&community=RE"
            f"&longitude={LONGITUDE}&latitude={LATITUDE}"
            f"&start={year}0101&end={year}1231&format=CSV")


def ask(year):
    """Ask for one year and keep the reply exactly as it arrived."""
    path = DATA / f"nasa-power-{PLACE}-daily-solar-{year}.csv"
    print(f"asking NASA POWER for {year}")
    reply = requests.get(url_for(year), timeout=180,
                         headers={"User-Agent": "SD5913 PolyU student"})
    reply.raise_for_status()
    DATA.mkdir(exist_ok=True)
    path.write_bytes(reply.content)

    published = [line for line in reply.content.decode("utf-8-sig").splitlines()
                 if line.startswith(f"{year},") and "-999" not in line]
    print(f"data/{path.name}: {len(published)} days with both numbers, "
          f"{len(reply.content) // 1024} KB")
    return path


if __name__ == "__main__":
    ask(dt.date.today().year)
