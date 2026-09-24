# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest"]
# ///

"""One small test, in the spirit of week 4: red before the code is right.

    uv run --with pytest python -m pytest tests/test_site.py

It tests the two things the page cannot check for itself: that the raw file is
read past its header block, and that a day NASA could not measure is dropped
rather than drawn as -999.
"""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "nasa-power-hong-kong-daily-solar-2025.csv"

# site.py cannot be imported by name: the standard library already owns "site",
# and it is imported before this line runs. So load the file itself.
_spec = importlib.util.spec_from_file_location("sunlight_site", ROOT / "site.py")
_site = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_site)

MISSING, daily, rows = _site.MISSING, _site.daily, _site.rows


def test_the_header_block_is_not_read_as_data():
    table = rows(DATA)
    assert len(table) == 365
    assert table[0][0] == "2025"
    assert table[0][1:3] == ["1", "1"]          # 1 January is the first row


def test_a_day_without_a_measurement_is_dropped():
    table = [["2025", "1", "1", "1.83", "3.77"],
             ["2025", "1", "2", str(MISSING), str(MISSING)],
             ["2025", "1", "3", "4.45", "4.46"]]
    days = daily(table)
    assert [day[1] for day in days] == [1, 3]    # 2 January is not drawn


def test_what_arrived_is_never_more_than_the_ceiling():
    for month, day, got, ceiling in daily(rows(DATA)):
        assert 0 <= got <= ceiling, f"{month}/{day} arrived above its ceiling"
