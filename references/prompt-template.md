# Prompt Template

可放映的 HTML 优先写 `deck.json`，再用 `scripts/render_deck.py` 生成。步骤见 `references/deck-contract.md`。下面这段提示词只用于「只要提示词、不直接生成文件」的场合。

Use this when the user wants a generator-ready prompt for a premium HTML presentation.

```text
Create a premium multi-page HTML presentation website that feels like a high-end keynote / PPT report, designed for desktop presentation and large-screen display.

Overall requirements:
- Build a full-screen multi-section presentation in HTML, CSS, and JavaScript.
- Each section should behave like a slide, with clear page-to-page transitions and strong visual rhythm.
- Use a 16:9 presentation layout, each slide filling 100vw × 100vh.
- Automatically choose a concise 6-8 slide structure or a fuller 10-15 slide structure based on the amount of source content.
- The overall style should be cinematic, refined, modern, and suitable for business showcase / strategic report / brand presentation.
- The interaction and motion language should feel smooth, elegant, subtle, continuous, and premium.
- Avoid generic landing page structure. This must feel like a presentation deck, not a marketing homepage.

Slide structure:
- Create 6-15 slides with distinct layouts and purposes, depending on content volume.
- If the content is concise and visual-first, use a tighter 6-8 slide showcase structure.
- If the content is dense, chapter-based, or closer to a real report, use a 10-15 slide report structure with chapter openers, thesis pages, proof/detail pages, roadmap or implementation pages, summary, and closing.
- Each slide should have a unique composition while remaining visually consistent as part of one deck.
- Keep strong hierarchy in titles, subtitles, supporting text, and labels.
- Every slide must include at least one strong visual element: image, grid, statistic, panel, timeline, or card system.

Motion and transition:
- Add delicate, continuous, presentation-grade animations for every slide.
- Use refined transitions between slides: fade, scale, parallax, mask reveal, and soft vertical or horizontal motion.
- Prefer long, smooth easing such as cubic-bezier(0.16, 1, 0.3, 1).
- Elements should animate in sequence with subtle stagger and depth.
- Maintain continuity between slides so the whole experience feels like one coherent presentation.
- Support mouse wheel, keyboard arrow, and navigation dot controls for slide switching.

Visual design:
- Use a dark, atmospheric, high-contrast visual system suitable for projection and showcase.
- Backgrounds can combine editorial typography, gradients, image overlays, soft blur, and shadow depth.
- Use large typography, generous spacing, and clean alignment.
- Use curated high-quality imagery where appropriate.
- Background images should be desaturated, darkened, or grayscale by default, with selective color reveal on active states.
- Add gradient overlays so text remains readable at all times.
- The design should feel premium, sharp, and art-directed rather than template-like.
- If the deck is primarily in Chinese:
  - use Chinese-friendly font stacks for headline and body text
  - do not use a single global headline width limit like `max-width: 10ch`
  - explicitly control whether each important title is 1 line, 2 lines, or 3 lines
  - for forced multi-line titles, implement each line as its own block element so the browser does not re-wrap unexpectedly
  - make title width follow the card/container width before reducing font size
  - keep card body text inside cards with `min-width: 0` on grid/flex children and `overflow: hidden` on cards where needed
  - adjust card heights to actual copy length instead of forcing all cards to match if that creates empty lower space

Interactive showcase slide:
- Include one slide featuring the main memorable interaction.
- Example options: horizontal expanding accordion, timeline expansion, layered image reveal, or stat focus transition.
- If using a horizontal accordion:
  - 4 panels side by side
  - full width and about 80vh height
  - collapsed state shows a rotated vertical title and small index number
  - active state grows smoothly to around 4x width using CSS flex transition over 0.8s with cubic-bezier(0.16, 1, 0.3, 1)
  - expanded state reveals title, subtitle, short description, and CTA
  - background images remain grayscale and dark by default, then reveal partial color and higher brightness when active
  - add a dark gradient overlay for readability

Interface details:
- Add discreet slide indicators or pagination.
- Optional: add a custom cursor-dot and cursor-ring if the experience is presentation-first and premium.
- Keep controls minimal and unobtrusive.

Code and implementation:
- Output a complete self-contained HTML file with embedded CSS and JavaScript.
- Ensure smooth performance and responsive scaling for large desktop screens.
- Optimize for presentation/demo use rather than mobile-first browsing.
- Use semantic structure and maintainable code organization.
- Avoid duplicated CSS selectors that redefine the same slide headline later in the file unless intentional.
- Add page-level CSS overrides for slides with unusually long Chinese headlines instead of relying only on global typography rules.

Important creative direction:
- Make it feel like an award-quality interactive report or keynote microsite.
- Do not make it look like a generic SaaS website.
- Do not use bland cards-on-white layouts.
- Prioritize immersive storytelling, motion continuity, and premium editorial composition.
- Prioritize direct usability for real presentations, not just a visually impressive first render.
```
