# Image Prompt Catalogue for Delta Lake & Apache Iceberg Knowledge Hub

This document defines **what images to generate**, **where they will be used**, **where they should be stored in the repo**, and **detailed prompts** suitable for modern generative image models.

All images are designed to match the **bright, vibrant UI** defined in `assets/css/main.css`:
- Primary colors: vibrant indigo, pink, amber (`#4F46E5`, `#EC4899`, `#F59E0B`)
- Light backgrounds, soft gradients
- Friendly, modern, slightly playful style
- No heavy realism; prefer stylized / illustration / isometric

## 1. Site‑wide Open Graph / Social Preview

**Purpose**: Shown when the site is shared (Twitter, LinkedIn, Slack).  
**Placement**:
- Referenced in [`_layouts/default.html`](_layouts/default.html) as `assets/images/og-image.png`.
- Should represent the entire knowledge hub.

**File path**:
- `assets/images/og-image.png` (1200x630 recommended)

**Prompt** (copy‑paste ready):

> A bright, modern, isometric illustration of a **data lakehouse knowledge hub**.  
> Visual elements: a central lake of data as glowing indigo water, two stylized crystalline structures labeled “Delta Lake” and “Apache Iceberg”, connected by flowing data streams (light beams) and small spark icons, surrounded by floating cards or panels representing documentation, code, charts, and dashboards.  
> Style: clean vector or semi‑flat illustration, vibrant colors (indigo, pink, amber, teal), soft gradients, subtle glow, no text labels embedded in the image (so the same image works internationally), high contrast, plenty of white space around the central composition.  
> Composition: landscape 16:9, centered focal point, suitable for social media preview (1200×630).  
> Background: light, subtle gradient from warm white to light blue, with abstract geometric shapes or faint grid to suggest technology and structure.  
> Mood: friendly, expert, fun, welcoming, high‑tech but not intimidating.

---

## 2. Home Page Hero Illustration

**Page**: [`index.md`](../index.md)  
**Section**: `<section class="hero">` at the top of the home page.  
**Goal**: Visual anchor that reinforces the “Knowledge Hub for Delta Lake & Apache Iceberg” message.

**File path**:
- `assets/images/hero-knowledge-hub.png` (ideally wide, 1600x900 or SVG)

**Prompt**:

> A clean, high‑level illustration showing a **data engineer’s control center** for a data lakehouse.  
> Foreground: a stylized dashboard with multiple panels – one showing a table icon (for Delta Lake), another an iceberg icon (for Apache Iceberg), others showing graphs, timelines, checklists, and code blocks.  
> Middle ground: pipelines or flows of data represented by glowing lines connecting storage icons (data lake) to the dashboard.  
> Background: a futuristic cityscape made of server racks and data blocks, softly blurred so it doesn’t distract.  
> Style: flat or semi‑flat illustration, bright and fun, in a palette of indigo, pink, amber, teal, with soft rounded shapes and subtle gradients. No actual text in the image.  
> Visual tone: playful yet professional, approachable, emphasizing learning and experimentation rather than corporate rigidity.  
> Aspect ratio: wide (16:9), with enough whitespace on left/right so the hero title and buttons can overlay or sit next to it responsively.

---

## 3. Architecture Overview Diagram

**Docs**:
- [`docs/architecture/system-overview.md`](../docs/architecture/system-overview.md)  
- Mentioned under “Architecture” and in `index.md` features (“Explore Architecture”).

**Usage**:
- As the main conceptual diagram for the “System Overview” page.
- Potentially reused in talks or slides.

**File path**:
- `assets/images/architecture/system-overview-diagram.png`

**Prompt**:

> An isometric architecture diagram of an **automated knowledge hub for data lakehouse technologies**.  
> Components to show:
> - Left: various sources — docs icon, RSS feed icon, GitHub icon — feeding into an “Ingestion & Curation” layer.  
> - Middle: a “Knowledge Engine” area with modules labeled conceptually (no literal text in the image): stale content detector, leaderboard, awesome‑list aggregator, CI/CD, validation. Represent them as distinct boxes with iconography (clock, trophy, list, gear, checkmark).  
> - Right: output channels — documentation site, code recipes, dashboards, community. Represent as screens or cards.  
> Connections: arrows or glowing pathways showing the flow from inputs → processing → outputs.  
> Style: clean lines, minimalistic but clear, bright palette (indigo, cyan, magenta, amber), soft gradients, subtle drop shadows for depth.  
> Avoid tiny illegible text; rely on icons and spatial arrangement so the diagram is understandable at 1200×800.  
> Overall: modern tech illustration, not a low‑level infra diagram (no cloud vendor logos).

---

## 4. Delta vs Iceberg Comparison Illustration

**Docs**:
- [`docs/comparisons/feature-matrix.md`](../docs/comparisons/feature-matrix.md)  
- Linked from home page “Comprehensive Comparisons” card.

**Goal**: Convey the idea of two powerful, complementary technologies.

**File path**:
- `assets/images/comparisons/delta-vs-iceberg-overview.png`

**Prompt**:

> A side‑by‑side comparison illustration of **Delta Lake** and **Apache Iceberg** as two friendly, iconic structures built on the same data lake.  
> Left: a crystalline blue‑green “Delta” structure, like a transparent pyramid made of data tiles, with subtle triangle motifs.  
> Right: a multi‑layer iceberg emerging from a calm “lake of data,” visualizing the “Iceberg” metaphor, with data grid patterns embedded in the ice layers.  
> Both sit on the same shared lake surface (representing a data lake), with underlying files drawn as small rectangles.  
> Between them: soft arrows or bridges implying interoperability and shared lakehouse architecture.  
> Style: minimalist but vivid, flat/semi‑flat, with vibrant indigo and cyan blues accented by amber highlights. No logos or text.  
> Mood: neutral and informative — not “versus” as in a fight, but as complementary options in the same ecosystem.

---

## 5. Code Recipes / Labs Illustration

**Docs**:
- [`code-recipes/index.md`](../code-recipes/index.md)  
- Home page “Battle‑Tested Recipes” card linking to `code-recipes/`.

**Goal**: Represent hands‑on experimentation and validated pipelines.

**File path**:
- `assets/images/recipes/code-recipes-lab.png`

**Prompt**:

> A playful yet professional illustration of a **data engineering lab bench** for code recipes.  
> Visual elements:
> - A laptop showing code or terminal output.  
> - Beakers and flasks with glowing data particles to symbolize experiments.  
> - Small pipelines or mini conveyor belts moving data “blocks” between stages labeled visually as “raw”, “validated”, “optimized” (no text).  
> - Checkmarks or green indicators representing tests/validation.  
> Style: bright colors (indigo, pink, amber), slightly cartoony but still tech‑oriented, clean lines, rounded corners.  
> Background: subtle gradient and geometric shapes evoking a lab/tech environment.  
> Composition: medium detail so it remains readable when scaled down as a card thumbnail.

---

## 6. Best Practices / Production Readiness Illustration

**Docs**:
- [`docs/best-practices/index.md`](../docs/best-practices/index.md)  
- [`docs/best-practices/production-readiness.md`](../docs/best-practices/production-readiness.md)

**Goal**: Visual metaphor for robust, production‑ready systems.

**File path**:
- `assets/images/best-practices/production-readiness.png`

**Prompt**:

> An illustration of a **well‑engineered data pipeline control room** representing production readiness.  
> Central: a large status dashboard with multiple green checkmarks, gauges, and alerts indicators all “healthy”.  
> Around it:  
> - A shield icon subtly embedded behind or around the dashboard (security & reliability).  
> - Gears and automation arms tuning or monitoring pipelines.  
> - Logs or metrics panels showing clean trend lines.  
> Style: flat/semi‑flat, bright with emphasis on greens for “healthy” but anchored in the site’s core palette (indigo, pink, amber).  
> Mood: calm, confident, stable — this is the “it’s ready for prod” illustration, not experimental.  
> No text labels; rely on iconography and color coding.

---

## 7. Tutorials / Getting Started Illustration

**Docs**:
- [`docs/tutorials/index.md`](../docs/tutorials/index.md)  
- [`docs/tutorials/getting-started.md`](../docs/tutorials/getting-started.md)

**Goal**: Encourage new users and make the learning path feel guided and safe.

**File path**:
- `assets/images/tutorials/getting-started-path.png`

**Prompt**:

> A friendly illustration of a **guided learning path** for data lakehouse technologies.  
> Visual metaphor: a winding path or staircase of tiles, each tile containing a small icon (book, code, database, chart, rocket).  
> At the start: a person or abstract character standing at “Beginner” with a laptop.  
> Along the path: signposts or milestones, visual but not text‑labeled.  
> At the top or end: a stylized rocket or trophy representing “production‑ready skills”.  
> Style: bright, optimistic colors; soft gradients; rounded shapes; character is abstract enough to be inclusive (no detailed facial features).  
> Mood: encouraging, low‑friction, learning‑friendly.

---

## 8. Gamification / Leaderboard Illustration

**Docs & scripts**:
- [`docs/BLUEPRINT.md`](../docs/BLUEPRINT.md) (Gamification Engine section)  
- Leaderboard surfaced in [`README.md`](../README.md) via `scripts/generate_leaderboard.py`.

**Goal**: Visual representation of community contribution and fun.

**File path**:
- `assets/images/community/leaderboard-gamification.png`

**Prompt**:

> A dynamic illustration of a **developer leaderboard** with a fun gamified feel.  
> Visuals:
> - A large scoreboard panel with rows, avatars, and trophies (no readable text).  
> - Contributors represented as abstract characters or icons with varying trophy levels (gold, silver, bronze).  
> - Badges floating around: stars, diamonds, shields, sparkles, representing achievements.  
> - A “contribute” button visual element suggesting ongoing participation.  
> Style: bright and upbeat, bold color contrasts, soft shadows, playful but not childish.  
> Mood: celebratory and inclusive; emphasizes recognition and collaboration rather than hardcore competition.

---

## 9. AI‑Powered Features Illustration

**Docs**:
- [`docs/BLUEPRINT.md`](../docs/BLUEPRINT.md), “AI‑Powered Features” section.  
- Mentioned on homepage in the “AI‑Powered Curation” feature card.

**File path**:
- `assets/images/ai/ai-curation-engine.png`

**Prompt**:

> A modern illustration of an **AI assistant curating and organizing data lakehouse resources**.  
> Central: an abstract AI “orb” or holographic head made of wireframe lines and dots, hovering above a desk.  
> Around it: small cards representing articles, docs, code snippets, and diagrams being sorted into neat stacks or columns.  
> Visual hints: tiny spark icons and flow lines indicating the AI is analyzing and tagging content.  
> Style: futuristic but friendly, using blues and purples for the AI with warm accent colors (amber, pink) for the curated cards.  
> Background: subtle network or constellation pattern to suggest intelligence and connections.  
> Mood: smart, magical, but trustworthy and not opaque.

---

## 10. Time‑Series Forecasting Weather Example Illustration

**Code recipe**:
- [`code-recipes/examples/time-series-forecasting/README.md`](../code-recipes/examples/time-series-forecasting/README.md)  
- Also suitable as a thumbnail in a listing of advanced recipes.

**File path**:
- `assets/images/recipes/time-series-forecasting-weather.png`

**Prompt**:

> An illustration of **time‑series forecasting for weather data** in a data engineering context.  
> Foreground: a chart with a wavy line representing temperature over time, with a dotted extension into the future indicating forecast.  
> Icons along the line: sun, cloud, rain, snow to show changing conditions.  
> Around the chart:  
> - A calendar icon.  
> - A clock.  
> - A small server or database icon representing storage.  
> Style: flat/semi‑flat, bright and clean, with clear lines and high contrast.  
> Color palette: sky blues, indigo, white, with accent orange/yellow for sun and pink for highlights.  
> Mood: precise yet approachable, blending data science with intuitive visuals.

---

## 11. Where to Place the Generated Files

Once images are generated, place them under:

```text
assets/
  images/
    og-image.png
    hero-knowledge-hub.png
    architecture/
      system-overview-diagram.png
    comparisons/
      delta-vs-iceberg-overview.png
    recipes/
      code-recipes-lab.png
      time-series-forecasting-weather.png
    best-practices/
      production-readiness.png
    tutorials/
      getting-started-path.png
    community/
      leaderboard-gamification.png
    ai/
      ai-curation-engine.png
```

Then update references in:

- [`_layouts/default.html`](_layouts/default.html)
  - Ensure `<meta property="og:image">` and `<meta property="twitter:image">` point to `/assets/images/og-image.png`.
- [`index.md`](../index.md)
  - Add `<img>` or `<figure>` elements in the hero section and near key feature cards.
- Relevant docs (`docs/architecture/system-overview.md`, `docs/comparisons/feature-matrix.md`, etc.) to embed their respective diagrams using standard Markdown:

```md
![System overview of the automated Delta Lake & Apache Iceberg knowledge hub](/assets/images/architecture/system-overview-diagram.png)
```

---

## 12. Quality Checklist for Each Generated Image

Before committing any generated image:

- [ ] Matches the **bright, vibrant** palette (indigo, pink, amber, teal).
- [ ] No embedded text that could conflict with localization or UI copy.
- [ ] Readable and meaningful at **card size** (~320×200) and at large sizes.
- [ ] No vendor logos or IP‑sensitive visuals.
- [ ] Consistent illustration style across all images (line weight, shading, perspective).
- [ ] Good contrast and legibility in **both light and dark themes**.
- [ ] File size optimized (typically `< 300 KB` for web images) without visible artifacts.

Once this catalogue is in place, image generation becomes a repeatable process: pick the prompt, run in your preferred model (Midjourney, DALL·E, SDXL, etc.), select the best candidate, optimize, and save at the documented path.