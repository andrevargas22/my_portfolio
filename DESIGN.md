---
name: André Vargas — Portfolio
description: A monochrome ink-black type specimen — one voice, one typeface, the work as an index.
colors:
  field: "oklch(0.185 0.008 270)"
  field-deep: "oklch(0.14 0.008 270)"
  field-raise: "oklch(0.25 0.01 270)"
  hair: "oklch(0.35 0.01 270)"
  ink: "oklch(0.95 0.005 250)"
  ink-muted: "oklch(0.72 0.01 260)"
typography:
  display:
    fontFamily: "Bricolage Grotesque, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "clamp(2.75rem, 8.5vw, 5.75rem)"
    fontWeight: 800
    lineHeight: 0.98
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "Bricolage Grotesque, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "clamp(1.75rem, 4vw, 2.75rem)"
    fontWeight: 600
    lineHeight: 1.05
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Bricolage Grotesque, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "clamp(1.4rem, 3.4vw, 2.6rem)"
    fontWeight: 600
    lineHeight: 1.05
    letterSpacing: "-0.025em"
  body:
    fontFamily: "Bricolage Grotesque, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: "normal"
  label:
    fontFamily: "Bricolage Grotesque, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: "-0.005em"
  micro:
    fontFamily: "Bricolage Grotesque, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: "0"
rounded:
  sm: "3px"
  md: "6px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "48px"
  xxl: "96px"
components:
  cta:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.field}"
    rounded: "{rounded.sm}"
    padding: "0.7em 1.4em"
  cta-hover:
    backgroundColor: "{colors.ink-muted}"
    textColor: "{colors.field}"
    rounded: "{rounded.sm}"
    padding: "0.7em 1.4em"
  index-item:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    padding: "clamp(1.1rem,3vw,2rem) clamp(1.25rem,5vw,4rem)"
  index-item-hover:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.field}"
    padding: "clamp(1.1rem,3vw,2rem) clamp(1.25rem,5vw,4rem)"
  plainlink:
    textColor: "{colors.ink}"
  nav-link:
    textColor: "{colors.ink-muted}"
---

# Design System: André Vargas — Portfolio

## 1. Overview

**Creative North Star: "The Specimen"**

The site is set the way a type foundry sets a specimen sheet: a person and their work presented as commanding type on a single drenched field, with nothing between the reader and the words. There is one typeface, two tones, and no chrome — no cards, no panels, no dashboards, no decorative graphics. Confidence comes from restraint carried to an extreme. The page doesn't *describe* rigor; its precise setting *is* the rigor, which is the entire strategic point for an audience that "trusts demonstrated work over stated claims."

The field is a near-neutral ink-black — printed ink, not the cool blue-grey of a developer's terminal. That distinction is deliberate and load-bearing: an earlier draft of this system used graphite + a warm signal accent + monospace labels + a data-viz panel, and it read as generic "technical portfolio" the moment you saw it. The whole dev-portfolio vocabulary is now **banned** here (see §6). The work is presented instead as a bold **typographic index** — large, plain, honest lines you hover to *invert* — because André is a methodical cataloguer (he indexes the games he finishes and the countries he visits), and an index is his native form.

This system explicitly rejects, per PRODUCT.md's anti-references: the generic AI/SaaS template (the outgoing `#FFFAF0` cream, gradient buttons, identical feature-card grids, tracked uppercase eyebrows); the flashy dev-bro portfolio (neon-on-black, glitch, scroll hijacking); the corporate/LinkedIn-blue brochure; and cluttered busy-ness. It also rejects the trap one tier deeper — the "technical = dark-terminal-plus-mono" reflex — which is why the execution is a *type specimen*, not a dashboard.

**Key Characteristics:**
- Two tones only: ink-black field, near-white type. No accent color anywhere.
- One typeface (Bricolage Grotesque) at extreme size and weight contrast carries the whole page.
- Interaction is by **inversion**, not by a colored signal.
- The work is a typographic **index**, never cards or tags.
- Emphasis is weight, scale, and tone — never decoration.

## 2. Colors

A two-tone monochrome: a drenched ink-black field and a near-white ink, with two darker field steps and one muted ink for hierarchy. There is **no accent color** — that absence is the design.

### Neutral
- **Ink-Black Field** (`oklch(0.185 0.008 270)`): The drenched ground for the entire site. Near-neutral chroma (0.008) so it reads as printed ink, not cool dev-graphite. Carries ~90% of every screen.
- **Field Deep** (`oklch(0.14 0.008 270)`): The alternating/lower band — the colophon, footers, quiet zones. One step into the black.
- **Field Raise** (`oklch(0.25 0.01 270)`): The only "up" step — dropdown surfaces and subtle hover washes where inversion is too heavy.
- **Hair** (`oklch(0.35 0.01 270)`): 1px rules and dividers. Structural, never decorative.
- **Ink** (`oklch(0.95 0.005 250)`): The type. Near-white paper with a faint cool cast; ≥16:1 on the field.
- **Ink Muted** (`oklch(0.72 0.01 260)`): Secondary type — the set-up lines of the statement, meta lines, asides, colophon prose. ≥7.5:1 on the field.

### Named Rules
**The No Accent Rule.** This system has exactly two tones. There is no brand accent, no "signal" color, no highlight hue. If something needs to stand out, it stands out through **weight, size, or inversion** — never a second color. Introducing an accent breaks the specimen.

**The Inversion Rule.** Interactive emphasis is expressed by flipping field and ink: a hovered index row becomes ink-filled with field-colored type; the CTA is permanently inverted (ink block, field text). This is the only "highlight" mechanic the system owns.

## 3. Typography

**Display / Body Font:** Bricolage Grotesque (with 'Helvetica Neue', Arial fallback)

**Character:** Bricolage Grotesque is a contemporary grotesque with deliberate irregularities — it has personality at display scale (where it carries the statement) and stays clean and legible at reading sizes. One family across the entire system is the point: hierarchy comes from weight (400 → 600 → 800) and size, the way a specimen sheet shows a single face at every scale. **There is no second family — and specifically no monospace.**

### Hierarchy
- **Display** (800, `clamp(2.75rem, 8.5vw, 5.75rem)`, line-height 0.98, −0.035em): The single statement per page. Set in stacked lines; the set-up in Ink Muted, the payoff in full Ink at weight 800 — the "turn" is done with tone and weight, never a color. `text-wrap: balance`.
- **Headline** (600, `clamp(1.75rem, 4vw, 2.75rem)`): Section headings on interior pages.
- **Title / Index** (600, `clamp(1.4rem, 3.4vw, 2.6rem)`, −0.025em): The large names in the work index; card/section titles on interior pages.
- **Body** (400, `1.0625rem`, line-height 1.55): Prose — the colophon, article text. Capped at ~65ch.
- **Label** (500, `0.9375rem`, letter-spacing −0.005em): Quiet meta lines, nav links, asides. **Sentence case, normal tracking.**
- **Micro** (500, `0.75rem`): The smallest step — dense captions like the games-grid metadata and badges. Below this, hierarchy breaks down; don't go smaller.

### Named Rules
**The No Mono Rule.** Monospace is forbidden. It was the costume that made the first draft read as fake-technical. Machine output that genuinely needs a fixed pitch (a code block on the blog) is the *only* exception, and even then it is a functional necessity, never a stylistic label.

**The No Eyebrow Rule.** No tiny uppercase tracked labels above sections. Meta and locating lines are sentence case at normal tracking (e.g. "Machine learning & MLOps engineer, based in Brasília."). An all-caps tracked kicker is the AI scaffold this system refuses.

## 4. Elevation

Flat and edgeless. The system is drenched, so there are **no shadows** — depth is expressed entirely through tonal bands (Field → Field Deep) and 1px Hair rules. A section is distinguished by dropping into a darker field step and by a hairline, never by lifting off the page.

The one exception is the dropdown menu, which must escape the flow: it sits on Field Raise with a Hair border and may use a single soft shadow to read as floating (`0 8px 32px oklch(0.10 0.01 270 / 0.6)`). Nothing else casts a shadow.

### Named Rules
**The Flat Ink Rule.** Ink on paper has no shadow. Surfaces are flat; hierarchy is tonal bands and hairlines. If a section has a drop shadow, delete it.

## 5. Components

### The Statement (signature)
The hero is a single typographic statement, not a headline-plus-subhead block. Set in stacked Display lines with the set-up in Ink Muted and the payoff in full Ink weight 800. It carries the fold alone — no imagery, no panel, no supporting stat tiles. On load, the lines rise into place in sequence (see motion, below).

### The Index (signature)
The work is a vertical list of large plain lines (Title/Index size), each a full-width row separated by Hair rules. The left holds an honest description ("A convolutional network you can draw into"); the right holds a quiet label ("3D visualiser"). On hover/focus the **entire row inverts** — Ink fill, Field type — and the name nudges right. No tags, no icons, no arrows, no numbers-as-scaffold.

### Buttons
- **CTA (inverted):** Ink fill, Field text, 3px radius, `0.7em 1.4em` padding. Stands out by inversion alone. Hover deepens the fill to Ink Muted and lifts `translateY(-2px)`. This is the conversion action ("Get in touch"). One per view.
- **Plain link:** Ink text with a 1px Hair underline that goes full-Ink on hover. The low-commitment path (Résumé, secondary links).

### Navigation
Near-zero chrome: a transparent bar over the field, wordmark in Bricolage 700, links in Label (Ink Muted → Ink on hover). Dropdowns open as Field Raise surfaces with Hair borders. `position: fixed`/popover so they never clip. Keyboard-navigable, visible focus.

### Colophon
A Field Deep band closing the page: real credentials in Body/Ink Muted (Casas Bahia, Banco do Brasil) stated flatly, plus plain profile links. The honest proof, no dashboard.

## 6. Do's and Don'ts

### Do:
- **Do** route every color through the two-tone token layer — one shared `:root` (the fix for the retired six-palette fragmentation).
- **Do** express emphasis through weight, scale, and inversion (The No Accent Rule, The Inversion Rule).
- **Do** keep one typeface (Bricolage Grotesque) at extreme weight/size contrast.
- **Do** set meta and locating lines in sentence case at normal tracking.
- **Do** present the work as a typographic index of honest lines, not cards.
- **Do** keep body ≥7:1 on the field, prose ≤65ch, and give every animation a `prefers-reduced-motion` alternative (PRODUCT.md targets WCAG 2.1 AA).

### Don't:
- **Don't** add an accent color, a "signal" hue, or any third tone. Two tones only.
- **Don't** use monospace as a stylistic label (The No Mono Rule) — it is the exact fake-technical costume this system was rebuilt to remove.
- **Don't** use tiny uppercase tracked eyebrows over sections (The No Eyebrow Rule).
- **Don't** build readout panels, stat tiles, dashboards, or decorative data-viz — the dev-portfolio vocabulary is banned here.
- **Don't** drift toward cool dev-graphite; the black is near-neutral printed ink.
- **Don't** reintroduce the `#FFFAF0` cream, gradient buttons, identical card grids, glassmorphism, gradient text, or `border-left` accent stripes (shared absolute bans + PRODUCT.md anti-references).
- **Don't** add a resting drop shadow (The Flat Ink Rule).
