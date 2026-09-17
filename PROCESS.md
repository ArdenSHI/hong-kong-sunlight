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
