# Goose Technical Keynote: design system

The house style for this deck. One light theme, one typeface, one structural
accent. Everything here is implemented in `styles/index.css` and demonstrated
in `slides.md`.

The deck is pinned to light with `colorSchema: light` in the headmatter. That
also removes the theme toggle and makes Shiki use its light code theme, so code
blocks match the slide background instead of punching a dark hole in it.

## Principle

Element defaults carry the design. Writing plain markdown produces a correct
slide, so `slides.md` stays readable and the helper classes below are only
needed for the few things markdown cannot express.

## Where it came from

Distilled from a bake-off of four keynote directions (Apple Minimal Dark,
Google Material Expressive, Monochrome Engineering, Editorial Technical) plus
four hybrids, each built and rendered before choosing. The result is
Monochrome Engineering as the base, Apple's one-idea-per-slide discipline for
the statement layout, and Material's semantic colour idea confined to terminal
output. Full research notes are outside the repo, in the session scratchpad
under `keynote-design-research.md` and `presentation-tools-research.md`.

## Type

Geist for everything, Geist Mono for code and numeric labels. Both are on
Google Fonts and load via the `fonts` key in the deck headmatter, so there are
no local font files to manage.

| Token | Size | Weight | Tracking | Used for |
| --- | --- | --- | --- | --- |
| `--t-hero` | 96px | 600 | -3px | `.statement` slides only |
| `--t-title` | 60px | 600 | -2px | `h1`, cover and closing |
| `--t-section` | 52px | 600 | -1.5px | `.section` dividers |
| `--t-head` | 40px | 600 | -1px | `h2`, stat labels, quotes |
| `--t-lead` | 22px | 400 | -0.4px | `h3`, `.lead` |
| `--t-body` | 19px | 400 | 0 | body copy, lists |
| `--t-code` | 15px | 400 | 0 | `pre`, `.term` |
| `--t-caption` | 14px | 400 | 0 | `.caption`, badges, table |
| `--t-eyebrow` | 13px | 500 | 0.1em | `.eyebrow`, uppercase |

Body is 19px rather than the more common 16px, and body text is `#444444`
rather than a lighter grey, both so the deck stays readable on a projector and
in a screen recording. Negative tracking applies at display sizes only and
returns to zero at body size.

## Colour

| Token | Value | Role |
| --- | --- | --- |
| `--bg` | `#ffffff` | Slide background |
| `--surface` | `#f7f7f6` | Cards, terminal, code blocks |
| `--surface-hi` | `#eeeeeb` | Inline code |
| `--border` | `rgba(0,0,0,.10)` | Hairlines, used instead of shadows |
| `--text` | `#101010` | Headings, emphasis |
| `--text-soft` | `#444444` | Body copy |
| `--text-faint` | `#767676` | Captions, de-emphasis |
| `--accent` | `#0a58ca` | The only structural accent |
| `--ok` | `#10713c` | Terminal success |
| `--run` | `#9a5b00` | Terminal in-progress |
| `--fail` | `#c0271b` | Terminal failure |

Every colour here clears 4.5:1 against the background. That is why the accent
is a deep blue rather than the bright agent-blue common in dark themes: on
white, that lighter blue lands near 2.4:1 and disappears under projector
washout.

The accent carries all structure: eyebrows, bullets, list numbers, the quote
rule, the active comparison column. The status trio appears only inside
`.term` blocks, where colour means something. Do not use it for decoration.

## Layouts

`slides.md` is 35 slides built from `goose-agent-workshop.pptx`, carrying the
pptx speaker notes as Slidev presenter notes. Slide copy follows the writing
rules in the global `CLAUDE.md`: no em dashes, no emojis, active voice, short
words, and no achievement language. Code blocks, terminal blocks, commands,
config keys and error strings are exempt and stay exactly as written.

| Slide | Layout | How |
| --- | --- | --- |
| Cover | Centred title | `layout: center`, `class: cover` |
| Agenda | Numbered list | plain `1.` ordered list |
| Statement | One claim, loud | `layout: center`, `class: statement` |
| Section | Divider | `class: section` plus `.section-num` |
| Prose | Heading and bullets | plain markdown |
| Stat and terminal | Split | `grid grid-cols-2` plus `.stat` and `.term` |
| Comparison | Before and after | two columns, `.compare-label` and `.is-after` |
| Code | Highlighted build | fenced block with `{1-3\|5-8\|all}` |
| Cards | Three up | `grid grid-cols-3` plus `.card` |
| Quote | Pull quote | plain `>` blockquote |
| Table | Comparison grid | plain markdown table |
| Closing | Mirrors the cover | `layout: center`, `class: cover` |

Add `class: vcenter` to any content slide to centre it vertically while keeping
text left-aligned. Most content slides want it; `layout: center` also centres
horizontally, which is only right for statement and cover slides.

## Helper classes added for the workshop deck

| Class | Use |
| --- | --- |
| `.flow` + `.flow-node` + `.flow-arrow` | Left-to-right step diagram. `.is-active` accents the node under discussion, `.is-human` marks a step the person performs |
| `.loop-back` | Return line drawn under a `.flow` or `.loop-steps`, labelled "repeat until done" |
| `.loop-steps` + `.loop-step` | Six numbered stages abreast, for the interactive loop |
| `.metrics` + `.metric-value` + `.metric-label` | Row of headline numbers |
| `.warn` + `.warn-label` | Amber-ruled callout for a gotcha the audience will otherwise hit |
| `.card` | Standard panel. `.is-key` accents the one card carrying the slide's argument |
| `.card-sm` | Compact panel, for grids of six or more |
| `.row-item` | Same content as a `.card-sm` at roughly half the height. Use when a column has four or more items |
| `.colhead` | Mono, ruled column heading |
| `.matrix` | Wraps a markdown table so column two reads as the argued-for option |
| `.agenda-item` + `.agenda-num` | Ruled agenda row with a mono number |
| `.acp` + `.acp-box` + `.acp-link` | Client, wire, agent protocol diagram |
| `.linkrow` | Footer row of labelled destinations |
| `.ref` | Source line pinned to the foot of a slide. The global 72px bottom padding exists to clear it |

## Fitting content

The canvas is 980x552. Any slide carrying more than about six panels needs
`class: vcenter dense`, which steps down padding, headings, card padding, code,
terminal and table sizes together rather than shrinking one part and leaving the
rest. Four slides in this deck overflowed before `dense` was tuned: the vendor
matrix, the twelve-card context-engineering grid, the MCP surface slide, and the
recipes slide. The MCP one only fitted once its eight `.card-sm` panels became
`.row-item` rows. The recipes slide needed its column split widened from
`0.9fr 1.1fr` to `1.15fr 0.85fr`, because a narrow column wraps every list item
onto two lines and doubles the height.

Check fit in `/overview/` rather than by eye in the editor. Overflow shows up as
content sliding under the `.ref` hairline.

## Deck chrome

`global-bottom.vue` at the project root draws two things on every slide except
the first and the last, so the deck opens and closes on a clean frame.

| Element | Class | Detail |
| --- | --- | --- |
| Progress rail | `.deck-rail` + `.deck-rail-fill` | 2px along the bottom edge, `--border` track, `--accent` fill, width animated at `--dur` |
| Slide number | `.deck-no` | Zero-padded, mono, on the same baseline as `.ref` |

`.ref` carries `padding-right: 54px` to keep long reference lines from running
under the number. Change one and check the other.

## The meetup QR

`components/MeetupQr.vue` holds the QR for `https://www.meetup.com/aiyatra/` as
an inline SVG path, so it needs no image file and stays sharp at any size. It
was produced with segno at error level Q, version 3, 29x29 modules, then decoded
back with OpenCV to confirm it resolves to that exact URL.

Two things will break it. The `viewBox` is `-4 -4 37 37` because a QR needs a
four-module quiet zone; cropping to the modules themselves makes it harder to
scan. And the fill is near-black on white rather than the accent, because
coloured QR codes lose contrast under projector washout.

To point it somewhere else, regenerate rather than hand-edit the path:

```
uv run --with segno python -c "import segno; segno.make('URL', error='q').save('qr.svg', scale=1)"
```

The slide appears twice, second and last. Early so the room can scan while it
settles, and again at the end.

## Restraint, and what was deliberately not added

Four pieces of polish, chosen to work inside the existing rules rather than
around them.

1. **Background depth.** Slides are a single accent bloom at 3.5% over white,
   not flat white. The cover and closing use 7.5%. This is the only gradient in
   the deck.
2. **Eyebrow rule.** An 18px accent bar before the eyebrow text, drawn with
   `::before`. It reuses the accent that already carries every structural cue.
3. **Balanced headings.** `text-wrap: balance` on `h1` and `h2` evens out
   wrapped display lines rather than leaving one orphan word.
4. **Deck chrome**, above.

Two things were considered and rejected. Card shadows, because this system uses
hairlines instead of shadows and mixing the two reads as indecision. Section
divider slides, because fourteen of them would add fourteen slides to a deck
whose eyebrows already carry the section number.

The `.statement` layout is built and currently unused. It is the one place the
deck is allowed to go loud, so it is available if a single claim ever deserves
a whole slide.

## Motion

Deck transition is `slide-left`. Custom durations are capped at 200ms with
`cubic-bezier(0.4, 0, 0.2, 1)`; short motion reads as fast and survives screen
capture better than cinematic timing. A `prefers-reduced-motion` block
collapses everything to near zero.

Use `<v-clicks>` for progressive bullet reveals and the fenced-code line
ranges for code builds. Reserve the `.statement` layout for the single biggest
claim in the talk. Using it more than once spends its impact.

## Gotchas worth remembering

These all cost time during the build and will recur.

1. **A blank line inside an HTML block breaks Vue compilation.** The markdown
   parser injects a `<p>` and tag nesting fails with "Element is missing end
   tag." That is why `.term` uses one `<div>` per line and `&nbsp;` for the
   spacer line rather than a `pre` with real blank lines.
2. **`theme-default` styles beat bare classes on specificity.** Its
   `.slidev-layout h1` outranks a plain `.k-hero`, silently flattening the
   type scale. Element rules here are scoped under `.slidev-layout` for this
   reason.
3. **Do not write `margin: 0 0 16px` on elements.** It outranks `mt-*` utility
   classes used in the deck. Top margins are zeroed in a single
   `:where(...)` rule, which has zero specificity, so utilities still win.
4. **`ch` units resolve against the element's own font-size.** A `max-width`
   in `ch` on a body-size wrapper containing display-size text collapses the
   text into a column. Use px when the wrapper and its content differ in size.
5. **Export needs `playwright-chromium`**, already in `devDependencies`. PPTX
   export embeds each slide as an image, so the result opens anywhere but is
   not editable in PowerPoint.

## Commands

```
npm run dev           # dev server with hot reload on :3030
npm run build         # static site to dist/
npm run export        # PDF
npm run export:pptx   # PPTX, image-based slides
```

Presenter view is at `/presenter/`, the grid overview at `/overview/`, and a
browser-based exporter at `/export/`.
