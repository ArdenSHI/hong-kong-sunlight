# PROCESS

How this repo got made, and where a model was involved.

## What I used it for

I used WorkBuddy (an AI assistant) for the whole first pass: choosing a source,
writing `fetch.py`, `peek.py` and `plot.py`, and drafting this file and the
README. I chose the phenomenon and the drawing idea — a year of rays, one per
day, the ceiling in pale ink and what got through in colour — and the model
wrote the code that draws it. Every number in the README was then checked against
the CSV by hand, and the one I checked wrong is the first item below.

## One thing I kept

The double encoding. My idea was two separate plots: a line of clear-sky values
and a line of what arrived, one above the other. The model suggested putting them
on the same ray instead — length for the ceiling, colour for the ratio — so that
every day is one line and the gap between promise and delivery is a length you can
see rather than a distance between two panels. It is better than my version for
the reason the brief keeps repeating: the transformation fits the data. Two
numbers per day is not two charts, it is one line with two dimensions.

## One thing I rejected

The first version put a soft glow at the centre — a sun for the rays to come out
of. Rendered, it was a hard-edged grey disc that dominated the page and made the
data look like decoration printed on top of it. Same for the first month labels,
which drew leader lines from the inner ring outward and collided with the ends of
the rays. Both were decoration wearing the clothes of clarity. The glow is still
there but at 0.07 opacity, which is a shadow rather than an object, and the months
now sit outside the wheel where nothing can reach them.

I also declined the obvious next step of adding pandas. The file is 365 rows of
five columns; `csv.reader` and one loop is faster to read and does not need a
dependency the marker would then have to install.

## What I had to correct

The model wrote that 3 April received 0.60 kW-hr/m² against a ceiling of 6.62.
Reading the row, 3 April had 6.30 and 6.41 — nearly a perfect day. The 0.60 was
4 April's *ratio*, not its energy, borrowed from a different line of the same
summary. The sentence read plausibly and was wrong. Every figure in the README
now comes from a printed row, and `peek.py` is committed so that the printing
happens in the repo rather than in a chat window.

The other correction was about the scale rather than a number. The model's first
version typed the ring radii in by hand, which would have gone on being right
until the file changed and then quietly lied. Every length now comes from
`scale = (OUTER - INNER) / max(ceiling)`, so pointing `fetch.py` at another
latitude, longitude or year rescales the whole drawing to the new numbers. The
rings stay at 2, 4 and 6 kW-hr/m²/day and stay honest, because they are drawn with
the same ruler as the rays.

One warning worth recognising: run the script on a machine with no display and
`plt.show()` reports that the canvas is non-interactive. The PNG is already
written by then, so the line is noise, not failure.

## The second version, the one with a mouse

A still picture of 365 days cannot be asked a question, so I asked for a second
version: the same wheel as a page, where pointing at a ray lights that day, dims
the other 364, and reads out its three numbers. The model wrote `site.py`, which reads the same CSV
and writes `site/index.html` — the page is generated, like the PNG, and committed
so the published URL is exactly what the script produces. The PNG, `plot.py` and
the raw file are all still here; nothing was replaced.

The correction was small and worth writing down. The first hover readout said
"7% of it arrived" for 4 August while the README said 6%, and both numbers came
from the same division: the page rounded 6.5% up to the next whole percent, the
sentence had quietly rounded it down. Two files, two answers, one fact. The page
and the README now both carry one decimal, 6.5%, which is what the row says. The
lesson is not "check your numbers" (the numbers were right both times) but that a
second version of the same work is a second chance for the same fact to say two
different things — and the copy is the one that gets believed.

Three decisions after that. The hover outline does not enlarge the ray outward
past its ceiling: a ray that grows on hover would change the measurement, and a
measurement that moves when you look at it is not a measurement. The drifting
title went away — asked for, tried, and cut. It was a nice effect that cost
something real: the centre of the wheel stopped being a fixed point, so the eye
had two places to land instead of one, and the caption is supposed to be the
still centre of a moving year.

The sun came back, and that is the interesting one. My first attempt at it in the
print version was a hard-edged grey disc and I threw it away; this time the
middle of the wheel is a real sun, amber to burnt orange. Filled to the rim of
the hole it was the largest object on the page — 365 days of measurement reduced
to rays coming off a beach ball — so it is deliberately smaller than the hole,
and the zero ring stays outside it as its own visible line. That line matters
more than the sun: zero is where the rays start, and without it a length on the
page is only a length relative to another length. Both are now drawn from
`INNER`, so if the scale ever changes the sun, the ring and the first pixel of
every ray move together.

The print then got the same centre back, which is the part worth keeping. A
drawing that exists twice in two materials is a drawing that can disagree with
itself, and the disagreement is invisible until someone puts the two side by
side. `plot.py` now builds its sun from the same five colour stops and puts its
zero ring at the same fraction of the radius as `site.py` does, so the PNG in
this README and the page at the URL are one drawing in two materials rather than
two similar drawings. The numbers were never at risk; the look was, and the look
is what the reader believes first.

The last thing asked for was a material. The sun was too solid — a filled disc,
which is what a computer draws when you say "circle" — so it became ink on coarse
paper: the rim wanders, the grain of the sheet takes the ink unevenly, and the
name on it is written rather than set. The lesson that cost me the most time is
about size, not strength. My first grain was built by adding several sizes of
noise together and then cutting it off at a threshold, and the coarse part
swallowed the fine part wherever it happened to run low, so the texture came out
as a watercolour wash. Laid down one size at a time it reads as paper. The second
lesson is the same one in different clothes: a grain asked for at a smaller scale
than a pixel of the finished picture is not a fine grain, it is an average, and
it arrives as a flat darkening of the whole disc — which is exactly why the first
web version went muddy brown instead of grainy. Ask for the texture at about the
size it will be seen at. On the page that meant raising the noise frequency until
its wavelength was about two pixels; in the print it meant asking for the grain on
a grid as fine as the output, or the enlargement blurs it back into a wash.

Two smaller decisions. The lettering is whichever hand the machine has: the page
takes a marker webfont and falls back through the handwriting a system is likely
to own, and `plot.py` takes the first of four script faces it can find and falls
back to the default rather than failing, so the script still runs on a machine
with no handwriting at all. And the texture is drawn under the words, never over
them: grain over lettering is how a picture starts to look like a photocopy of
itself.

## The third version, the one with a control

Week 4 asks for one idea from its interface lesson, and asks for the promise to be
written down before the code: *when I ___, the interface ___.* The promise I wrote
is on the page itself, because a promise nobody can read is not a constraint:

> When I choose a month, the wheel keeps that month's rays lit and the line below
> the control reports what that month got.

The shape is the one the week's examples use — input, state, response — and the
data behaves like the browser demo rather than the Streamlit demo: the page asks
for one file of records and draws them itself. Nothing is handed a finished
picture. Reading a day by pointing at it is still there, and clicking a ray now
writes that day into both selectors, which was the point of the exercise and not a
feature: state that lives only in a tooltip is not state, and a control that says
one thing while the picture shows another is a bug with good manners.

I kept one thing from `browser/app.js` on purpose. It fixes a 0–3 m scale before
drawing and says why: *so changing the day does not change the meaning of height.*
The wheel had the same rule already — one scale for the year, computed from the
largest ceiling before anything is chosen — and making it explicit in the page
matters more than it did in a static picture, because a selector invites the reader
to compare one month against another, and a picture that rescales per selection
makes that comparison a lie.

I did not take the other half of the lesson. The week's demos run a Python process
behind the page — Streamlit, or FastAPI in a Worker — and I did not want the work
to depend on one being awake: the brief asks for a repository that runs with the
wifi off, and a URL that is only a picture while something else is running is a
worse artefact than a URL that is always a picture. So the request is real and has
no server: `site.py` writes `sunlight-2025.json` from the same committed CSV, the
page fetches it once, and everything after that is drawn in the browser. The
trade-off is honest and worth stating: a reader with no network sees the page load
and then a sentence explaining why it has nothing to draw, where the Streamlit
version would have worked offline on my laptop and nowhere else.

Two things I had to correct, and both were invisible until I looked properly.

The page was blank for a while and looked like it was still loading. The cause was
my own string-handling: the page is built in Python, and one escaped quote inside
the JavaScript got unescaped on the way out, so the whole `<script>` failed to
parse and the browser silently drew nothing at all — no rays, no error, an empty
status line, which is exactly what a page that is still fetching looks like. I
found it by extracting the script block and asking `node --check` about it. A
script inside a string is not checked by anything that reads the outer file.

The second one is a sentence that had been in the README since the first pass:
that February to May were the dullest months. Writing the readout meant computing
each month's mean rather than eyeballing the wheel, and August is the dullest month
of the year (63.9%), not any of the four I had named. The claim had the right idea
and the wrong months — a shape the eye sees in the picture and the data then
disagrees with. The README now carries the computed months and figures, so the page
and the writing cannot drift apart again without someone noticing.

There is one small test, on reading the file rather than drawing it: that the NASA
header block is not mistaken for data, that a day POWER could not measure is
dropped instead of drawn as -999, and that no day reports arriving with more light
than a clear sky offered. It fails if those guards are removed, which is the only
thing that makes a test worth committing. Writing it turned up a small trap: a file
called `site.py` cannot be imported by name in a test, because the standard library
owns `site` and imports it before the test runs, so the test loads the file by path
with `importlib` instead.
