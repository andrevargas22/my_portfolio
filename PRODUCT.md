# Product

## Register

brand

## Platform

web

## Users

The primary audience is recruiters and hiring managers evaluating André Vargas for machine learning and MLOps roles. They arrive with limited time, often mid-shortlist, and need to quickly gauge seniority, judge whether the experience is real, and decide whether he is worth a conversation. They skim before they read, and they trust demonstrated work over stated claims.

A secondary audience of engineering peers and curious visitors will appreciate the technical demos (the Three.js CNN visualization, the Mapbox travel map, the finished-games archive), but the site is optimized for the recruiter first.

## Product Purpose

This is André Vargas's personal portfolio — the canonical place that represents who he is as a machine learning engineer. It exists to convert a cold recruiter visit into contact. Success is a recruiter leaving convinced that André is a senior, production-focused ML/MLOps engineer and taking the step to reach out. Every page reinforces credibility; the demos are not decoration, they are evidence.

## Positioning

*(synthesized — confirm or adjust)* A production-focused ML/MLOps engineer who doesn't just claim technical depth but demonstrates it: the site's own interactive demos, built from scratch, are the proof of the exact build-and-ship capability the role requires.

## Conversion & proof

- Primary CTA: Get in touch (reach out about opportunities, via LinkedIn / email).
- Secondary CTA: View LinkedIn — the low-commitment fallback for a recruiter still deciding, letting them validate the profile and network before messaging.
- The line a visitor remembers after 10 seconds: *(synthesized — confirm or adjust)* "A Brazilian ML engineer who ships real production systems — and built everything you're looking at himself."
- Belief ladder *(synthesized — confirm or adjust)*, the order a recruiter must believe before reaching out:
  1. This person is a serious, senior engineer, not a hobbyist.
  2. His experience is real and production-grade (credit risk models, CI/CD pipelines, cloud migrations at scale).
  3. He can actually build and ship — the demos on this very site prove it.
  4. He is worth a conversation right now.
- Proof on hand: a detailed career timeline (Universidade de Brasília → hardware engineering → Data Scientist → ML Engineer Specialist at Grupo Casas Bahia, including Banco do Brasil credit-risk work), a downloadable résumé, Medium publications, and three working technical demos. No testimonials or client logos supplied yet — add them under `.impeccable/assets/proof/` if available, as they would strengthen the credibility case for recruiters.

## Brand Personality

Technical and precise above all: engineered, sharp, and quietly confident. The voice is that of a senior engineer who lets the work speak — direct, unembellished, no hype. Personality shows through the substance (the demos, the games archive, the honest self-taught story) rather than through decoration. The feel to evoke is expert confidence: a recruiter should sense competence and rigor, not marketing.

## Anti-references

This must not look like:
- A generic AI/SaaS template — cream backgrounds, gradient buttons, identical feature-card grids, tiny uppercase tracked eyebrows over every section. (The current `#FFFAF0` body background is exactly this tell and should go.)
- A flashy dev-bro portfolio — neon-on-black, glitch effects, scroll hijacking, "full-stack ninja" theatrics. Precise, not loud.
- Corporate or stiff — stock photography, LinkedIn-blue, soulless enterprise-brochure tone with no personality.
- Cluttered or busy — competing elements with no breathing room. Clarity and hierarchy over density.

## Design Principles

- **Show, don't tell.** The demos are the argument. Lead with evidence of building and shipping, not adjectives about it.
- **Precision as personality.** Every alignment, weight, and spacing decision signals engineering rigor. Sloppiness reads as a red flag to the audience this serves.
- **One coherent system.** A single shared token layer (color, type, spacing) across every page — the current per-page palette fragmentation is the antithesis of "precise" and must be unified.
- **Respect the skim.** Recruiters scan first. Hierarchy, scannability, and an obvious path to "get in touch" outrank cleverness.
- **Substance over spectacle.** Motion and effects earn their place only when they clarify or reveal real work; never decoration for its own sake.

## Accessibility & Inclusion

Target WCAG 2.1 AA: body text at ≥4.5:1 contrast (large text ≥3:1), full keyboard navigability, visible focus states, meaningful alt text on images and demo canvases, and a `prefers-reduced-motion` alternative for every animation (including the hero video and any demo motion).
