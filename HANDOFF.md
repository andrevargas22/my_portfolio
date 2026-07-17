# Frontend Redesign — Handoff

A complete visual redesign of your portfolio, on the branch `refactor/website`.
**Your backend is untouched** — this is HTML/CSS/JS only. Flask routes, `website.py`,
`scripts/`, and your data (`games.json`) were not changed. Nothing about how the site
runs or deploys changes; only how it *looks*.

You don't need to know frontend to use this. When in doubt, see **[Getting help](#getting-help)**.

---

## 1. What changed

| Page | Before | After |
|------|--------|-------|
| Landing | cream background, video, social icons | monochrome "type specimen", value statement + work index |
| About | fragile jQuery horizontal timeline | horizontal **scroll** timeline, pure CSS (no JS) |
| Publications | list with in-page expand | typographic index → links to Medium |
| Finished Games | ~40 tag colours, 4 JS libraries | grayscale covers (colour on hover), vanilla filter + lightbox |
| Visited Countries | Bootstrap header | framed dark map, ink popups |
| MNIST | rainbow diagram | monochrome diagram, framed demo |

**New files**
- `static/css/tokens.css` — the single source of truth for colours, font, spacing (see §3).
- `DESIGN.md` — the design-system rulebook.
- `PRODUCT.md` — who the site is for and the brand voice.
- `AI_BRIEFING.md` — paste this into any AI to get help (see §5).

**Removed** (all replaced with less code): global jQuery, `about.js`, `blog.js`,
Isotope, Magnific Popup, imagesLoaded, and the orphan `templates/base/header.html`.

---

## 2. Run it locally (to see the live demos)

The redesign was verified for structure and colour contrast, but the **three live demos**
(map, 3D MNIST, Medium feed) need the app actually running with your secrets.

```bash
# 1. Python env (3.10+)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Secrets — copy the template and fill it in
cp .env.example .env.local
#   For the redesign you only strictly need:
#     MAPBOX_ACCESS_TOKEN  -> the Visited Countries map
#     MNIST_ENDPOINT       -> the MNIST 3D demo
#   (The other vars are for the YouTube/WebSub automation, unrelated to these pages.)

# 3. Run (uses .env.local, opens on http://localhost:5000)
make debug
```

**Check each page:** Landing · About (drag the timeline sideways) · Publications
(pulls your Medium feed) · Games (filter + click a cover) · Map (needs the Mapbox token) ·
MNIST (draw a digit — needs `MNIST_ENDPOINT`).

---

## 3. The design system in 30 seconds

- **Two colours only:** near-black background, near-white text. **No accent colour.**
  Emphasis comes from font weight, size, and **inversion** (hovering flips the colours).
- **One font:** Bricolage Grotesque, at every size.
- **One file controls the whole look:** `static/css/tokens.css`. It defines CSS variables
  like `--field` (background), `--ink` (text), `--font`, spacing, and radius. Change a value
  there and the **entire site** updates.
- Each page also has its own `static/css/<page>.css` for *layout*, but its colours and font
  come from the tokens.
- The full rules live in **`DESIGN.md`**. The two you must not break:
  never bring back the old cream background (`#FFFAF0`), and never give game tags
  their own colours again.

---

## 4. Making small changes safely

| I want to… | Edit this | Notes |
|------------|-----------|-------|
| Change wording on a page | `templates/pages/<page>.html` | The visible text is right there in the HTML. |
| Add a finished game | `static/json/games.json` + a cover in `static/images/games/` | Copy the shape of an existing entry. |
| Change a colour / spacing / the font everywhere | `static/css/tokens.css` | One value → whole site. |
| Adjust one page's layout | `static/css/<page>.css` | Keep using the `var(--...)` tokens for colour. |

Not sure? That's what §5 is for.

---

## 5. Getting help

You don't need to learn frontend. Open **`AI_BRIEFING.md`**, copy its entire contents into
ChatGPT, Claude, Gemini, or whatever AI you like, then ask your question at the bottom.
It hands the AI full context about this project — the stack, the design rules, where every
file lives — so it can walk you through changes step by step and warn you before anything
breaks the design system.

---

## 6. Merge & deploy

1. Review the pull request for `refactor/website`.
2. **Merge it into `main`.**
3. That's it — `.github/workflows/ci_deploy.yml` runs on every push to `main` and
   automatically deploys to **Google Cloud Run** (`gcloud run deploy`). The site at
   **andrevargas.com.br** updates on its own.

> Your Makefile's usual flow is `dev → main`. If you'd rather route this through `dev`
> first, retarget the PR to `dev`; the end result (a push to `main`) is what deploys.

---

## 7. About the `.claude/` and `.impeccable/` folders

Those are the design tooling used to *build* this redesign. They are **not needed** to run,
change, or deploy the site, and they're git-ignored so they won't clutter your tree. You can
ignore them completely. Everything you actually need is in `DESIGN.md`, `PRODUCT.md`,
`tokens.css`, and `AI_BRIEFING.md`.
