# /// script
# requires-python = ">=3.10"
# ///

"""
The same year, but you can put a finger on it.

    uv run site.py

Reads the file fetch.py saved and writes site/index.html: the 365-ray picture
again, redrawn as SVG, except now every ray answers the mouse. Hovering a ray
dims the rest, thickens that day, and shows the three numbers behind it. The
middle of the wheel is a sun, and its rim is the zero every ray is measured
from. Nothing is fetched and nothing is drawn that is not in the file.
"""

import csv
import json
from pathlib import Path

FILE = "nasa-power-hong-kong-daily-solar-2025.csv"
MISSING = -999.0

HERE = Path(__file__).parent
DATA = HERE / "data" / FILE
SITE = HERE / "site"

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>One year of sunlight over Hong Kong</title>
<style>
  html, body { margin: 0; padding: 0; background: #0B0F14; }
  body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
         display: flex; justify-content: center; }
  #wrap { position: relative; width: min(96vw, 760px); }
  svg { width: 100%; height: auto; display: block; }
  .day { transition: opacity 0.18s ease; }
  svg.focus .day:not(.hot) { opacity: 0.32; }
  .day .promise { transition: stroke 0.15s ease, stroke-width 0.15s ease; }
  .day .got { transition: stroke-width 0.15s ease; }
  .day.hot .promise { stroke: #8FA6BD; stroke-width: 4.5; }
  .day.hot .got { stroke-width: 4.5; }
  .day .tip { opacity: 0; transition: opacity 0.15s ease; }
  .day.hot .tip { opacity: 1; }
  #tipbox {
    position: fixed; display: none; pointer-events: none; z-index: 10;
    background: #10161E; border: 1px solid #26313F; border-radius: 8px;
    padding: 10px 13px; color: #E8EAED; font-size: 13px; line-height: 1.55;
    box-shadow: 0 6px 24px rgba(0,0,0,0.55); white-space: nowrap;
  }
  #tipbox .when { font-size: 14px; font-weight: 600; letter-spacing: 0.02em;
                  margin-bottom: 3px; }
  #tipbox .row { display: flex; align-items: center; gap: 7px; }
  #tipbox .row.dim { color: #8A95A3; }
  #tipbox .swatch { width: 10px; height: 10px; border-radius: 2px;
                    display: inline-block; flex: none; }
</style>
</head>
<body>
<div id="wrap">
<svg id="chart" viewBox="0 0 900 1000" role="img"
     aria-label="Three hundred and sixty-five rays, one per day of 2025, showing how much sunlight reached Hong Kong and how much a clear sky would have delivered">
  <defs>
    <radialGradient id="halo">
      <stop offset="0%" stop-color="rgb(255,170,70)" stop-opacity="0.20"/>
      <stop offset="45%" stop-color="rgb(255,140,50)" stop-opacity="0.09"/>
      <stop offset="100%" stop-color="rgb(255,130,40)" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="sunskin">
      <stop offset="0%" stop-color="#FFE9A6"/>
      <stop offset="30%" stop-color="#F9C24E"/>
      <stop offset="62%" stop-color="#EF8E24"/>
      <stop offset="86%" stop-color="#D45D12"/>
      <stop offset="100%" stop-color="#A63C08"/>
    </radialGradient>
  </defs>
  <rect width="900" height="1000" fill="#0B0F14"/>
  <circle id="halo" cx="450" cy="455" r="180" fill="url(#halo)"/>
  <circle id="sun" cx="450" cy="455" r="114" fill="url(#sunskin)"/>
  <g id="rings"></g>
  <g id="rays"></g>
  <g id="months"></g>
  <g id="title">
    <text x="450" y="447" text-anchor="middle" fill="#4A2C07"
          font-size="21" letter-spacing="2.5">HONG KONG</text>
    <text x="450" y="474" text-anchor="middle" fill="#4A2C07"
          font-size="16" letter-spacing="2">2025</text>
  </g>
  <g id="legend" fill="#78838F" font-size="16" text-anchor="middle">
    <text x="450" y="884">one ray per day, 1 January at the top, clockwise</text>
    <text x="450" y="910">outer length: what a clear sky would have delivered
      — inner length: what reached the ground</text>
    <text x="450" y="936">colour: the ratio between the two, cool when it clouded
      over — rings: kW-hr/m²/day</text>
    <text x="450" y="962">NASA POWER CERES SYN1deg, 22.28°N 114.16°E —
      hover a ray for that day</text>
  </g>
</svg>
</div>
<div id="tipbox"></div>
<script>
const DATA = __DATA__;

const CX = 450, CY = 455, R = 380;    // the page
const INNER = 0.30, OUTER = 1.00;     // where a ray starts, where the longest ends
const SVG = "http://www.w3.org/2000/svg";
const RAMP = ["#2E5C77", "#6E93A6", "#C9C2A8", "#F2C25B", "#FFF0B8"];
const RINGS = [2, 4, 6];

const n = DATA.length;
const maxCeiling = Math.max(...DATA.map(d => d[3]));
const scale = (OUTER - INNER) / maxCeiling;

function ramp(t) {                     // the colour of a day, from ratio alone
  const x = Math.max(0, Math.min(1, t)) * (RAMP.length - 1);
  const i = Math.floor(x), f = x - i;
  if (i >= RAMP.length - 1) return RAMP[RAMP.length - 1];
  const a = RAMP[i], b = RAMP[i + 1];
  const mix = (h, k) => parseInt(a.slice(h, k), 16) * (1 - f)
            + parseInt(b.slice(h, k), 16) * f;
  return "rgb(" + [mix(1, 3), mix(3, 5), mix(5, 7)]
                .map(v => Math.round(v)).join(",") + ")";
}

function point(i, radius) {            // day i at radius, clockwise from noon
  const a = (-90 + 360 * i / n) * Math.PI / 180;
  return [CX + radius * R * Math.cos(a), CY + radius * R * Math.sin(a)];
}

const el = (name, attrs) => {
  const node = document.createElementNS(SVG, name);
  for (const k in attrs) node.setAttribute(k, attrs[k]);
  return node;
};

// The sun sits in the hole in the middle of the wheel and is not a measurement:
// it is the thing the numbers are about. The zero line is drawn outside it, at
// the radius every ray starts from, so the sun never inflates a single day.
const SUN = 0.26 * R;
document.getElementById("sun").setAttribute("r", SUN);
document.getElementById("halo").setAttribute("r", SUN * 1.55);

const rings = document.getElementById("rings");
const labelAngle = (-97) * Math.PI / 180;   // just left of twelve o'clock
const label = (r, text, colour) => {
  const t = el("text", {
    x: CX + r * Math.cos(labelAngle) - 6, y: CY + r * Math.sin(labelAngle) - 5,
    fill: colour, "font-size": 13, "text-anchor": "middle" });
  t.textContent = text;
  rings.appendChild(t);
};

rings.appendChild(el("circle", { cx: CX, cy: CY, r: INNER * R,  // zero, where rays start
  fill: "none", stroke: "#FFEFC9", "stroke-width": 2 }));
label(INNER * R + 15, "0", "#C8D0DA");

for (const value of RINGS) {           // the ruler, same rings as the print
  const r = INNER + value * scale;
  rings.appendChild(el("circle", { cx: CX, cy: CY, r: r * R,
    fill: "none", stroke: "#1C2632", "stroke-width": 1 }));
  label(r * R, value, "#33404F");
}

const MONTHS = ["JAN","FEB","MAR","APR","MAY","JUN",
                "JUL","AUG","SEP","OCT","NOV","DEC"];
const months = document.getElementById("months");
let seen = {};
for (let i = 0; i < n; i++) seen[DATA[i][0]] = i;      // last day of each month
let first = {};
for (let i = n - 1; i >= 0; i--) first[DATA[i][0]] = i; // and its first
for (const m of MONTHS.keys()) {
  const mid = (first[m + 1] + seen[m + 1]) / 2;
  const [x, y] = point(mid, 1.045);
  const t = el("text", { x: x, y: y, fill: "#5C6C7C", "font-size": 20,
    "text-anchor": "middle", "dominant-baseline": "central" });
  t.textContent = MONTHS[m];
  months.appendChild(t);
}

const tipbox = document.getElementById("tipbox");
const chart = document.getElementById("chart");
const rays = document.getElementById("rays");

for (let i = 0; i < n; i++) {          // one ray, one day, in hearing distance
  const [month, day, got, ceiling] = DATA[i];
  const [x0, y0] = point(i, INNER);
  const [x1, y1] = point(i, INNER + ceiling * scale);
  const [xr, yr] = point(i, INNER + got * scale);

  const g = el("g", { class: "day" });
  const promise = el("line", { class: "promise", x1: x0, y1: y0, x2: x1, y2: y1,
    stroke: "#46596F", "stroke-width": 2 });
  const light = el("line", { class: "got", x1: x0, y1: y0, x2: xr, y2: yr,
    stroke: ramp(got / ceiling), "stroke-width": 2 });
  const hit = el("line", { x1: x0, y1: y0, x2: x1, y2: y1,
    stroke: "rgba(0,0,0,0)", "stroke-width": 6, "pointer-events": "stroke" });
  const dot = el("circle", { class: "tip", cx: xr, cy: yr, r: 4.5,
    fill: ramp(got / ceiling), stroke: "#0B0F14", "stroke-width": 1.5 });
  g.appendChild(promise); g.appendChild(light); g.appendChild(dot);
  g.appendChild(hit);
  rays.appendChild(g);

  const date = new Date(2025, month - 1, day);
  const when = date.toLocaleDateString("en-GB",
    { weekday: "short", day: "numeric", month: "short", year: "numeric" })
    .replace(",", "");
  const pct = (100 * got / ceiling).toFixed(1);
  const say = () => {
    tipbox.innerHTML =
      '<div class="when">' + when + "</div>" +
      '<div class="row"><span class="swatch" style="background:'
      + ramp(got / ceiling) + '"></span>reached '
      + got.toFixed(2) + " kW-hr/m²/day</div>" +
      '<div class="row dim">ceiling ' + ceiling.toFixed(2)
      + " — " + pct + "% of it arrived</div>";
  };

  const show = (e) => {
    g.classList.add("hot"); chart.classList.add("focus"); say();
    tipbox.style.display = "block"; move(e);
  };
  const hide = () => {
    g.classList.remove("hot"); chart.classList.remove("focus");
    tipbox.style.display = "none";
  };
  const move = (e) => {                  // stays inside the window, either side
    const pad = 14, w = tipbox.offsetWidth, h = tipbox.offsetHeight;
    let x = e.clientX + 20, y = e.clientY + 16;
    if (x + w > window.innerWidth - pad) x = e.clientX - w - 20;
    if (y + h > window.innerHeight - pad) y = e.clientY - h - 16;
    tipbox.style.left = Math.max(pad, x) + "px";
    tipbox.style.top = Math.max(pad, y) + "px";
  };
  hit.addEventListener("pointerenter", show);
  hit.addEventListener("pointerleave", hide);
  hit.addEventListener("pointermove", move);
  hit.addEventListener("click", (e) => { show(e); e.stopPropagation(); });
}

</script>
</body>
</html>
"""


def rows(path):
    """The data rows. NASA POWER writes a -BEGIN HEADER- block above the table,
    so keep the lines that start with a year."""
    kept = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for line in csv.reader(handle):
            if line and line[0].strip().isdigit():
                kept.append([cell.strip() for cell in line])
    return kept


def main():
    table = rows(DATA)
    days = []
    for year, month, day, allsky, clearsky in table:        # the loop over the numbers
        got, ceiling = float(allsky), float(clearsky)
        if got == MISSING or ceiling == MISSING or ceiling <= 0:
            continue                                        # POWER could not measure that day
        days.append([int(month), int(day), round(got, 2), round(ceiling, 2)])

    SITE.mkdir(exist_ok=True)
    page = PAGE.replace("__DATA__", json.dumps(days, separators=(",", ":")))
    (SITE / "index.html").write_text(page, encoding="utf-8")
    print(f"{len(days)} days written to site/index.html")


if __name__ == "__main__":
    main()
