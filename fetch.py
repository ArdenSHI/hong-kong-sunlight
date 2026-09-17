# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///

"""
Fetch the numbers once, save the raw reply to data/, and never fetch again.

    uv run fetch.py

NASA POWER publishes what the sky did every day, anywhere on Earth, as CSV. Two
columns are asked for, both in kW-hr per square metre per day:

    ALLSKY_SFC_SW_DWN   what actually reached the ground, clouds and all
    CLRSKY_SFC_SW_DWN   what would have reached it if there had been no clouds

The gap between the two is the cloud's doing, and it is what the picture is made
of. The coordinates are Hong Kong; change LATITUDE and LONGITUDE to move the
window to anywhere else on the planet.
"""

from pathlib import Path

import requests

LATITUDE = 22.28          # CHANGE ME: anywhere on Earth
LONGITUDE = 114.16
PLACE = "hong-kong"       # CHANGE ME: shows up in the file name
START, END = "20250101", "20251231"
PARAMETERS = "ALLSKY_SFC_SW_DWN,CLRSKY_SFC_SW_DWN"

URL = ("https://power.larc.nasa.gov/api/temporal/daily/point"
       f"?parameters={PARAMETERS}&community=RE"
       f"&longitude={LONGITUDE}&latitude={LATITUDE}"
       f"&start={START}&end={END}&format=CSV")

FILE = f"nasa-power-{PLACE}-daily-solar-{START[:4]}.csv"

HERE = Path(__file__).parent
DATA = HERE / "data"


def fetch(url, path):
    """Ask for the file once. If it is already in data/, do nothing."""
    if path.exists():
        print(f"data/{path.name} is already here ({path.stat().st_size // 1024} KB). "
              "Delete it to fetch again.")
        return path
    DATA.mkdir(exist_ok=True)
    print(f"asking {url}")
    reply = requests.get(url, timeout=120, headers={"User-Agent": "SD5913 PolyU student"})
    reply.raise_for_status()
    path.write_bytes(reply.content)      # the raw reply, byte for byte: what arrived is what gets committed
    print(f"saved data/{path.name} ({path.stat().st_size // 1024} KB). Now: git add data")
    return path


if __name__ == "__main__":
    fetch(URL, DATA / FILE)
