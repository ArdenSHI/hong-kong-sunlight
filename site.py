# /// script
# requires-python = ">=3.10"
# ///

"""
The same year, with one control and one clear response.

    uv run site.py

Writes two files into site/: index.html and sunlight-2025.json. The page asks
for the JSON and draws from whatever comes back — records, not a finished
picture. Choosing a month keeps that month's rays lit and makes the line under
the control report that month's sunlight; choosing a day lights the single ray
of that day. Nothing else is fetched, and nothing that is not in the reply is
drawn.

The scale is fixed for the whole year before anything is drawn, so choosing a
month or a day changes what is lit, never what a length means.
"""

import csv
import json
from pathlib import Path

FILE = "nasa-power-hong-kong-daily-solar-2025.csv"
MISSING = -999.0

HERE = Path(__file__).parent
DATA = HERE / "data" / FILE
SITE = HERE / "site"

SOURCE = "NASA POWER CERES SYN1deg, 22.28N 114.16E, 2025"
RECORDS = "sunlight-2025.json"

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hong Kong Sunlight 2025</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Permanent+Marker&display=swap">
<style>
  html, body { margin: 0; padding: 0; background: #0B0F14; }
  body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
         display: flex; justify-content: center; }
  #wrap { position: relative; width: min(96vw, 760px); padding: 2.2rem 0 3rem; }
  svg { width: 100%; height: auto; display: block; }

  h1, #title text { font-family: "Permanent Marker", "Marker Felt",
                    "Bradley Hand", "Ink Free", "Segoe Script",
                    "Comic Sans MS", cursive; }
  h1 { margin: 0 0 0.5rem; color: #FFD9A0; font-weight: normal;
       font-size: clamp(23px, 3.6vw, 35px); line-height: 1.15; }
  .promise { margin: 0 0 1.1rem; color: #8A95A3; font-size: 14px; line-height: 1.65; }
  .promise em { color: #C8D0DA; font-style: normal; }

  .controls { display: flex; flex-wrap: wrap; gap: 1.1rem; }
  label { display: flex; align-items: center; gap: 0.5rem; color: #78838F;
          font-size: 13px; }
  select { font: inherit; font-size: 14px; color: #E8EAED; background: #10161E;
           border: 1px solid #26313F; border-radius: 6px; padding: 0.35rem 0.5rem; }
  select:disabled { opacity: 0.45; }
  select:focus-visible { outline: 2px solid #F2C25B; outline-offset: 1px; }

  /* The response. It has height even when empty, so choosing never moves it. */
  #status { min-height: 4.4em; margin: 1rem 0 0; color: #C8D0DA; font-size: 14px;
            line-height: 1.7; }
  #status b { color: #FFF0B8; font-weight: 600; }
  #status .faint { color: #6F7B88; }

  .notes { margin: 1.4rem 0 0; color: #5C6C7C; font-size: 12.5px;
           line-height: 1.75; }
  .notes a { color: #6E93A6; }

  .day { transition: opacity 0.18s ease; }
  svg.focus .day:not(.hot) { opacity: 0.32; }
  svg.picked.focus .day.inmonth:not(.hot) { opacity: 0.34; }
  svg.picked .day:not(.inmonth) { opacity: 0.09; }
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
  #grain-all { pointer-events: none; }
</style>
</head>
<body>
<div id="wrap">
  <header>
    <h1>Hong Kong Sunlight 2025</h1>
    <p class="promise">When I choose a <em>month</em>, the wheel keeps that
      month's rays lit and the line below reports what that month got. When I
      choose a <em>day</em>, one ray stays lit and its three numbers are read
      out. The scale never changes, so choosing never changes what a length
      means.</p>
    <div class="controls">
      <label>Month <select id="month" aria-label="Month"></select></label>
      <label>Day <select id="day" aria-label="Day" disabled></select></label>
    </div>
    <p id="status" role="status" aria-live="polite"></p>
  </header>

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

    <!-- The sun is ink pressed on coarse paper, not a fill. Its rim wanders a
         little, and the paper's tooth keeps part of the ink off the page. -->
    <filter id="ragged" x="-25%" y="-25%" width="150%" height="150%"
            color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="3"
                    seed="13" result="warp"/>
      <feDisplacementMap in="SourceGraphic" in2="warp" scale="9"
                         xChannelSelector="R" yChannelSelector="G"/>
    </filter>
    <filter id="tooth" x="-10%" y="-10%" width="120%" height="120%"
            color-interpolation-filters="sRGB">
      <!-- About two pixels across, because below that the eye averages it into a
           flat veil instead of a texture. -->
      <feTurbulence type="fractalNoise" baseFrequency="0.5" numOctaves="3"
                    seed="9" result="n"/>
      <feColorMatrix in="n" type="matrix"
        values="0 0 0 0 0.043
                0 0 0 0 0.059
                0 0 0 0 0.078
                1.15 0 0 0 -0.475"/>
    </filter>
    <filter id="bleed" x="0%" y="0%" width="100%" height="100%"
            color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="0.021" numOctaves="3"
                    seed="41" result="n"/>
      <feColorMatrix in="n" type="matrix"
        values="0 0 0 0 1.0
                0 0 0 0 0.91
                0 0 0 0 0.72
                1.5 0 0 0 -0.78"/>
    </filter>
    <filter id="fibre" x="0%" y="0%" width="100%" height="100%"
            color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="0.055" numOctaves="3"
                    seed="27" result="n"/>
      <feColorMatrix in="n" type="matrix"
        values="0 0 0 0 0.043
                0 0 0 0 0.059
                0 0 0 0 0.078
                1.05 0 0 0 -0.42"/>
    </filter>
    <radialGradient id="toothfade">
      <stop offset="0%" stop-color="#4A4A4A"/>
      <stop offset="62%" stop-color="#8A8A8A"/>
      <stop offset="100%" stop-color="#FFFFFF"/>
    </radialGradient>
    <mask id="toothmask" maskContentUnits="objectBoundingBox">
      <circle cx="0.5" cy="0.5" r="0.5" fill="url(#toothfade)"/>
    </mask>
  </defs>
  <rect width="900" height="1000" fill="#0B0F14"/>
  <circle id="halo" cx="450" cy="455" r="180" fill="url(#halo)"/>
  <circle id="sun" cx="450" cy="455" r="114" fill="url(#sunskin)" filter="url(#ragged)"/>
  <circle id="sunbleed" cx="450" cy="455" r="114" fill="#FFE9B8"
          filter="url(#bleed)" opacity="0.5"/>
  <circle id="sunfibre" cx="450" cy="455" r="114" fill="#0B0F14"
          filter="url(#fibre)" opacity="0.42"/>
  <circle id="sungrain" cx="450" cy="455" r="114" fill="#0B0F14"
          filter="url(#tooth)" mask="url(#toothmask)"/>
  <g id="rings"></g>
  <g id="rays"></g>
  <g id="months"></g>
  <!-- The whole sheet: the ink the rays are drawn with sits on the same paper
       as the sun does, so it is grained too. Under the words, never over them. -->
  <rect id="grain-all" width="900" height="1000" fill="#0B0F14"
        filter="url(#fibre)" opacity="0.5"/>
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
    <text x="450" y="962">choose a month above, or point at any ray</text>
  </g>
</svg>

  <p class="notes">
    Source: __SOURCE__ · kW-hr/m²/day.
    <a id="request-link">Open the JSON request</a> — what crossed the network is
    daily records, not a picture; every line here is drawn from them in the
    browser.
  </p>
</div>
<div id="tipbox"></div>
<script>
const RECORDS = "__RECORDS__";
const NAMES = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"];

const monthPicker = document.getElementById("month");
const dayPicker = document.getElementById("day");
const status = document.getElementById("status");
const requestLink = document.getElementById("request-link");
requestLink.href = RECORDS;

const CX = 450, CY = 455, R = 380;    // the page
const INNER = 0.30, OUTER = 1.00;     // where a ray starts, where the longest ends
const SVG = "http://www.w3.org/2000/svg";
const RAMP = ["#2E5C77", "#6E93A6", "#C9C2A8", "#F2C25B", "#FFF0B8"];
const RINGS = [2, 4, 6];

const tipbox = document.getElementById("tipbox");
const chart = document.getElementById("chart");
const rays = document.getElementById("rays");

let rows = [];        // the reply: one record per day
let nodes = [];       // one <g> per day, in the same order
let labels = {};      // month number -> its wheel caption
let scale = 1;        // kW-hr/m²/day -> fraction of the radius
let monthNow = 0;     // state: which month is chosen; 0 is the whole year
let dayNow = 0;       // state: which day within it; 0 is the whole month
let chosen = -1;      // the index of the single lit ray, or -1

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
  const a = (-90 + 360 * i / rows.length) * Math.PI / 180;
  return [CX + radius * R * Math.cos(a), CY + radius * R * Math.sin(a)];
}

const el = (name, attrs) => {
  const node = document.createElementNS(SVG, name);
  for (const k in attrs) node.setAttribute(k, attrs[k]);
  return node;
};

const dateOf = (row, how) => new Date(2025, row.month - 1, row.day)
  .toLocaleDateString("en-GB", how);
const shortDay = row => dateOf(row, { day: "numeric", month: "short" });
const longDay = row => dateOf(row, { weekday: "long", day: "numeric",
                                     month: "long", year: "numeric" });
const pct = row => (100 * row.got / row.ceiling).toFixed(1);
const mean = (list, pick) => list.reduce((sum, row) => sum + pick(row), 0)
                           / list.length;
const extreme = (list, better) =>
  list.reduce((best, row) => better(row, best) ? row : best);

// The sun sits in the hole in the middle of the wheel and is not a measurement:
// it is the thing the numbers are about. The zero line is drawn outside it, at
// the radius every ray starts from, so the sun never inflates a single day.
const SUN = 0.26 * R;
for (const id of ["sun", "sunbleed", "sunfibre", "sungrain"])
  document.getElementById(id).setAttribute("r", SUN);
document.getElementById("halo").setAttribute("r", SUN * 1.55);

function draw() {
  // One scale for the year, decided once, before anything is chosen. Selecting
  // a month therefore changes what is lit and never what a length means.
  scale = (OUTER - INNER) / Math.max(...rows.map(row => row.ceiling));

  const labelAngle = (-97) * Math.PI / 180;   // just left of twelve o'clock
  const rings = document.getElementById("rings");
  const label = (r, text, colour) => {
    const t = el("text", {
      x: CX + r * Math.cos(labelAngle) - 6, y: CY + r * Math.sin(labelAngle) - 5,
      fill: colour, "font-size": 13, "text-anchor": "middle" });
    t.textContent = text;
    rings.appendChild(t);
  };

  rings.appendChild(el("circle", { cx: CX, cy: CY, r: INNER * R,  // zero
    fill: "none", stroke: "#FFEFC9", "stroke-width": 2 }));
  label(INNER * R + 15, "0", "#C8D0DA");
  for (const value of RINGS) {         // the ruler, same rings as the print
    const r = INNER + value * scale;
    rings.appendChild(el("circle", { cx: CX, cy: CY, r: r * R,
      fill: "none", stroke: "#1C2632", "stroke-width": 1 }));
    label(r * R, value, "#33404F");
  }

  const months = document.getElementById("months");
  const first = {}, last = {};
  rows.forEach((row, i) => {
    if (first[row.month] === undefined) first[row.month] = i;
    last[row.month] = i;
  });
  for (const month of Object.keys(first)) {
    const [x, y] = point((first[month] + last[month]) / 2, 1.045);
    const t = el("text", { x: x, y: y, fill: "#5C6C7C", "font-size": 20,
      "text-anchor": "middle", "dominant-baseline": "central" });
    t.textContent = NAMES[month - 1].slice(0, 3).toUpperCase();
    months.appendChild(t);
    labels[month] = t;
  }

  rows.forEach((row, i) => {                  // one ray, one day
    const [x0, y0] = point(i, INNER);
    const [x1, y1] = point(i, INNER + row.ceiling * scale);
    const [xr, yr] = point(i, INNER + row.got * scale);

    const g = el("g", { class: "day" });
    const promise = el("line", { class: "promise", x1: x0, y1: y0, x2: x1, y2: y1,
      stroke: "#46596F", "stroke-width": 2 });
    const light = el("line", { class: "got", x1: x0, y1: y0, x2: xr, y2: yr,
      stroke: ramp(row.got / row.ceiling), "stroke-width": 2 });
    const dot = el("circle", { class: "tip", cx: xr, cy: yr, r: 4.5,
      fill: ramp(row.got / row.ceiling), stroke: "#0B0F14", "stroke-width": 1.5 });
    // Six pixels of nothing over every ray, so a line two pixels wide can still
    // be pointed at. It carries the mouse events; the thin lines only carry ink.
    const hit = el("line", { x1: x0, y1: y0, x2: x1, y2: y1,
      stroke: "rgba(0,0,0,0)", "stroke-width": 6, "pointer-events": "stroke" });
    g.appendChild(promise); g.appendChild(light); g.appendChild(dot);
    g.appendChild(hit);
    rays.appendChild(g);
    nodes[i] = g;

    const say = () => {
      tipbox.innerHTML =
        '<div class="when">' + longDay(row) + "</div>" +
        '<div class="row"><span class="swatch" style="background:'
        + ramp(row.got / row.ceiling) + '"></span>reached '
        + row.got.toFixed(2) + " kW-hr/m²/day</div>" +
        '<div class="row dim">ceiling ' + row.ceiling.toFixed(2)
        + " — " + pct(row) + "% of it arrived</div>";
    };
    const move = (e) => {                  // stays inside the window, either side
      const pad = 14, w = tipbox.offsetWidth, h = tipbox.offsetHeight;
      let x = e.clientX + 20, y = e.clientY + 16;
      if (x + w > window.innerWidth - pad) x = e.clientX - w - 20;
      if (y + h > window.innerHeight - pad) y = e.clientY - h - 16;
      tipbox.style.left = Math.max(pad, x) + "px";
      tipbox.style.top = Math.max(pad, y) + "px";
    };
    const show = (e) => {
      g.classList.add("hot"); chart.classList.add("focus"); say();
      tipbox.style.display = "block"; move(e);
    };
    const hide = () => {
      // Leaving the pointer gives the shift back to whichever day is chosen.
      g.classList.remove("hot"); chart.classList.remove("focus");
      if (chosen === i) g.classList.add("hot");
      tipbox.style.display = "none";
    };
    hit.addEventListener("pointerenter", show);
    hit.addEventListener("pointerleave", hide);
    hit.addEventListener("pointermove", move);
    // Clicking a ray moves the control, not only the picture: the state has to
    // be visible somewhere other than the thing you pointed at.
    hit.addEventListener("click", (e) => {
      show(e); e.stopPropagation();
      monthPicker.value = String(row.month);
      dayPicker.disabled = false;
      fillDays(row.month);
      dayPicker.value = String(row.day);
      paint(row.month, row.day);
    });
  });
}

function fillDays(month) {
  dayPicker.replaceChildren();
  dayPicker.add(new Option("Every day in " + NAMES[month - 1], 0));
  for (const row of rows) if (row.month === month)
    dayPicker.add(new Option(shortDay(row), row.day));
}

function paint(month, day) {
  monthNow = month; dayNow = day;
  chart.classList.toggle("picked", month !== 0);
  chosen = -1;
  nodes.forEach((g, i) => {
    const row = rows[i];
    const kept = month === 0 || row.month === month;
    const lit = kept && day !== 0 && row.day === day;
    g.classList.toggle("inmonth", kept);
    g.classList.toggle("hot", lit);
    if (lit) chosen = i;
  });
  for (const month_ of Object.keys(labels))
    labels[month_].setAttribute("fill",
      Number(month_) === month ? "#FFE9A6" : "#5C6C7C");
  status.innerHTML = readout(month, day);
  chart.setAttribute("aria-label", plainText(month, day));
}

function readout(month, day) {
  if (month !== 0 && day !== 0) {
    const row = rows.find(r => r.month === month && r.day === day);
    if (row) return "<b>" + longDay(row) + "</b><br>reached <b>"
      + row.got.toFixed(2) + "</b> of a possible <b>" + row.ceiling.toFixed(2)
      + "</b> kW-hr/m²/day — <b>" + pct(row) + "%</b> of it arrived."
      + '<br><span class="faint">One ray stays lit on the wheel. Pick another '
      + "day, or point at any other ray.</span>";
  }
  const list = month === 0 ? rows : rows.filter(row => row.month === month);
  const got = mean(list, row => row.got);
  const ceiling = mean(list, row => row.ceiling);
  const clearest = extreme(list, (a, b) => a.got / a.ceiling > b.got / b.ceiling);
  const dullest = extreme(list, (a, b) => a.got / a.ceiling < b.got / b.ceiling);
  return "<b>" + (month === 0 ? "2025" : NAMES[month - 1] + " 2025") + "</b> · "
    + list.length + " days · a mean of <b>" + got.toFixed(2) + "</b> kW-hr/m²/day "
    + "arrived out of <b>" + ceiling.toFixed(2) + "</b> a clear sky offered — <b>"
    + (100 * got / ceiling).toFixed(1) + "%</b>.<br>"
    + '<span class="faint">clearest ' + shortDay(clearest) + " (" + pct(clearest)
    + "%), dullest " + shortDay(dullest) + " (" + pct(dullest)
    + "%). Now choose a day to keep one ray lit.</span>";
}

function plainText(month, day) {
  return (readout(month, day).replace(/<[^>]+>/g, " ")).replace(/\\s+/g, " ").trim();
}

monthPicker.add(new Option("The whole year", 0));
NAMES.forEach((name, i) => monthPicker.add(new Option(name, i + 1)));

monthPicker.addEventListener("change", () => {
  const month = Number(monthPicker.value);
  dayPicker.disabled = month === 0;
  if (month !== 0) fillDays(month);
  else dayPicker.replaceChildren();
  paint(month, 0);                    // a new month always starts on no day
});
dayPicker.addEventListener("change", () => {
  paint(monthNow, Number(dayPicker.value));
});

async function load() {
  status.textContent = "Loading one year of sunlight records…";
  try {
    const response = await fetch(RECORDS);
    if (!response.ok) throw new Error("HTTP " + response.status);
    const reply = await response.json();
    if (!Array.isArray(reply.days) || reply.days.length === 0)
      throw new Error("no daily records in the reply");
    rows = reply.days.map(([month, day, got, ceiling]) =>
      ({ month, day, got, ceiling }));
    draw();
    paint(0, 0);                      // state: the whole year, no day chosen
    status.innerHTML = '<span class="faint">' + rows.length
      + " daily records received. Nothing is drawn that is not in them. "
      + "Choose a month.</span><br>" + readout(0, 0);
  } catch (error) {
    status.innerHTML = "The records could not be loaded: " + error.message
        + '. Serve this folder over http (for example <span class="faint">uv run'
        + " python -m http.server</span>, then open <span class='faint'>http://"
        + "127.0.0.1:8000/</span>) or use the published page. A page opened at a "
        + "<span class='faint'>file://</span> address is not allowed to fetch "
        + "even the file beside it.";
  }
}

load();
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


def daily(table):
    """One record per day: month, day, what arrived, what a clear sky offered."""
    days = []
    for year, month, day, allsky, clearsky in table:      # the loop over the numbers
        got, ceiling = float(allsky), float(clearsky)
        if got == MISSING or ceiling == MISSING or ceiling <= 0:
            continue                                      # POWER could not measure it
        days.append([int(month), int(day), round(got, 2), round(ceiling, 2)])
    return days


def main():
    days = daily(rows(DATA))
    SITE.mkdir(exist_ok=True)

    reply = {"source": SOURCE, "unit": "kW-hr/m2/day",
             "note": "Records, not a picture: [month, day, what reached the "
                     "ground, what a cloudless sky would have delivered].",
             "days": days}
    (SITE / RECORDS).write_text(
        json.dumps(reply, separators=(",", ":")), encoding="utf-8")

    page = (PAGE.replace("__RECORDS__", RECORDS).replace("__SOURCE__", SOURCE))
    (SITE / "index.html").write_text(page, encoding="utf-8")
    print(f"{len(days)} days written to "
          f"site/index.html and site/{RECORDS}")


if __name__ == "__main__":
    main()
