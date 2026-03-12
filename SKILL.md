---
name: "html-presentation-microsite"
description: "Use when the user wants a premium multi-page HTML presentation, keynote-style microsite, or slide-based report page with full-screen sections, refined motion, editorial layout, image-led storytelling, desktop showcase behavior, and standout interactions such as expanding accordions."
---

# HTML Presentation Microsite

Builds high-end HTML presentations that feel like a keynote, boardroom report, or brand showcase rather than a generic landing page.

## When to use
- Multi-page HTML 汇报页、提案页、发布会页面、战略展示页
- “像 PPT / keynote / pitch deck 一样”的网页
- 需要全屏 slide、章节切换、滚轮/键盘导航、分页指示
- 需要高级动效、细腻转场、暗色氛围、图片叙事
- 需要一页高记忆点交互，例如横向 expanding panel accordion

## Deliverable modes
- Prompt only: 先输出高质量生成提示词
- Prototype: 直接产出单文件 HTML/CSS/JS demo
- Content conversion: 把 PRD、提纲、汇报结构改写成网页化 slide deck

## Presentation modes
- Showcase mode: 6-8 页，适合概念展示、品牌氛围、创意提案、主视觉驱动的短 deck
- Report mode: 10-15 页，适合正式汇报、策略方案、产品发布、融资叙事、章节推进更完整的 deck
- If the user does not specify the page count, choose the mode automatically based on content volume

## Automatic mode selection
- Use showcase mode when the source material is light:
  - one core idea with limited supporting detail
  - fewer than 4 clear chapters
  - minimal data, proof, or implementation detail
  - the request is primarily about visual impact, concept expression, or a hero interaction
- Use report mode when the source material is substantial:
  - 4 or more chapters, workstreams, or argument layers
  - meaningful data, proof points, roadmap, comparison, or implementation detail
  - the request reads like a real proposal, report, PRD, strategy deck, or business narrative
  - compressing to 6-8 slides would force overloaded pages
- When uncertain, default to report mode if the content already contains structure that benefits from chaptering

## Workflow
1. Clarify the presentation role: brand showcase, strategy report, product proposal, launch story, or executive summary.
2. Assess content volume and choose the deck length:
   - 6-8 slides for showcase mode
   - 10-15 slides for report mode
3. Convert the request into a slide narrative with chapters, not just stacked sections.
4. Give each slide a distinct job:
   - shorter decks can use cover, agenda, thesis, data, story, showcase, summary, closing
   - longer decks should distribute content across chapter openers, proof pages, detail pages, roadmap pages, summary, and closing
5. Define one coherent visual system:
   - one dominant background mood
   - one accent color family
   - one typography pairing
   - one repeated motif such as glass cards, framed imagery, numbered chapters, or side markers
6. Define one coherent motion system:
   - primary easing should feel long and controlled
   - use staggered entrances, depth shifts, fades, masks, and parallax sparingly
   - transitions must feel continuous across pages, not isolated per block
7. Include at least one memorable hero interaction if the brief allows it:
   - horizontal accordion
   - image reveal comparison
   - timeline expansion
   - stat focus transition
8. Build for desktop presentation first:
   - 100vw x 100vh slides
   - wheel, keyboard, and dot navigation
   - readable overlay gradients on imagery
   - strong type hierarchy and restrained copy density
9. QA before declaring complete:
   - no generic SaaS layout patterns
   - no flat white background with stacked cards unless explicitly requested
   - no abrupt motion, weak contrast, or repeated slide compositions
   - for longer decks, no filler slides or chapter drift

## Slide recipe
- Cover: one thesis line, one supporting paragraph, one visual anchor
- Agenda: 3-5 chapters with strong numbering or section framing
- Thesis: one key point presented with editorial emphasis
- Data: large stats, short labels, simple chart or comparison blocks
- Story: image-led layout with 2-4 supporting arguments
- Showcase: strongest interactive or visual moment
- Summary: compress the argument into 3-4 takeaways
- Closing: final message and CTA or sign-off

## Long deck recipe
- For 10-15 page decks, organize the presentation into 3-5 chapters
- Use chapter opener slides to reset rhythm and keep the viewer oriented
- Spread dense material across several proof or detail slides instead of compressing it into one
- Keep 1-2 standout visual or interaction moments for the whole deck; do not make every slide compete at the same volume
- Use summary slides at both chapter level and final deck level when the material is complex

## Design rules
- Treat every page like a slide, not a webpage section
- Keep titles large and short; body copy should read like narration, not documentation
- Every slide needs at least one dominant visual object
- Prefer dark or atmospheric backgrounds for premium presentation work unless the content strongly suggests otherwise
- Desaturate or darken imagery by default, then release color selectively on active states
- Use gradients to protect readability instead of placing text directly on raw images
- Avoid equal-weight layouts; one element should dominate
- Preserve breathing room; premium work looks intentional because it is not overfilled

## Chinese typography rules
- When the deck is primarily in Chinese, do not reuse English-first title behavior blindly
- Use Chinese-friendly font stacks:
  - serif display: `"Songti SC", "Noto Serif SC", "Source Han Serif SC", serif`
  - sans body: `"PingFang SC", "Hiragino Sans GB", "Noto Sans SC", sans-serif`
- Do not rely on generic `max-width: 10ch` style headline constraints for Chinese titles; they often make titles collapse into narrow vertical-looking blocks
- Prefer slide-specific title widths instead of one global title width rule
- Use manual line breaks for long Chinese titles on presentation-critical slides
- If the user requests `1 line`, `2 lines`, or `3 lines`, implement it explicitly with separate block lines, not just `<br>` and hope the browser preserves the rhythm
- Body copy can use softer wrapping rules, but titles should be deliberately line-managed
- Avoid aggressive global rules like `word-break: keep-all` if they distort normal Chinese layout across the deck

## Card and container rules
- Card content must stay inside cards. Always constrain cards with:
  - `overflow: hidden`
  - grid/flex children using `min-width: 0`
  - page-level checks for text bleed on large titles and long body copy
- When a slide uses cards with short copy, reduce card height to fit content. Do not leave large empty bottoms just to maintain a rigid grid
- For report decks, prefer content-driven card heights on text-heavy pages over forcing equal-height cards everywhere
- If only one card on a page has heavy content, let that card breathe and compress adjacent cards rather than stretching all cards equally
- For title cards, remove inherited narrow width constraints from the heading if the body text already fits the container correctly

## Title layout rules
- Distinguish between:
  - one-line titles
  - controlled two-line titles
  - controlled three-line titles
- For controlled line layouts, use per-line block elements so each line occupies the card width intentionally
- Never let browser auto-wrap decide the final layout for executive-report titles in Chinese
- If a title must fill more of a hero card, first widen the title container to the card width; only then tune font size and line height
- When a title still looks too narrow, inspect inherited width constraints before shrinking typography further
- Check for duplicated CSS selectors that override headline sizes later in the file

## Report-mode layout rules
- In 10-15 page report decks, do not keep showcase-mode compositions unchanged
- Report slides need calmer, more readable layouts with stricter chapter rhythm
- Use visual intensity selectively: a few strong hero slides, then quieter proof/detail slides
- Do not force every slide into the same “hero left + cards right” structure
- For text-heavy strategy slides, use broader reading columns and reduce decorative empty space
- For capability/proof pages, split dense ideas across multiple calmer cards instead of oversized empty glass panels

## QA rules for real usability
- Before declaring the deck complete, verify every slide for:
  - title lines match requested line count
  - titles do not overflow or collapse into narrow columns
  - body copy does not bleed outside cards
  - cards with little text are not visibly too tall
  - no duplicated style rules are fighting each other
  - OpenClaw / product names are not awkwardly split across lines
- For Chinese decks specifically:
  - scan all long titles at desktop width
  - inspect hero cards where title and body share the same container
  - inspect chapter-closing slides where oversized serif titles can easily overflow
- If screenshots from the user reveal one broken slide, do not assume it is isolated. Re-check the same layout pattern on other slides before finishing

## Motion rules
- Default to `cubic-bezier(0.16, 1, 0.3, 1)` unless the brief needs a different feel
- Use 0.7s-1.2s for major transitions and 0.3s-0.5s for hover/detail transitions
- Sequence entrances with small delay offsets so the eye knows where to look
- Keep hover effects subtle: scale, brightness, reveal, blur reduction, or card lift
- Never stack too many effect types on one object

## Interaction rules
- Navigation should work with wheel, trackpad, arrow keys, and explicit page dots
- Custom cursor is optional; use it only for showcase-style experiences
- If using a hero accordion, default collapsed panels to vertical title + small number, then reveal full content only on hover/active
- If using background images, pair them with a dark bottom gradient and muted default filter

## Prompting
- If the user wants generation help, use `references/prompt-template.md`
- If the user needs layout planning, use `references/slide-outline-template.md`
- Keep prompts explicit about:
  - presentation format
  - slide count
  - whether page count should be auto-selected from content volume
  - motion tone
  - visual mood
  - showcase interaction
  - implementation scope

## Output expectations
- Prefer a self-contained HTML demo unless the repo already has a frontend stack
- If building directly, keep CSS and JS readable and structured by slide system, motion system, and showcase components
- If only writing prompts, output a ready-to-paste prompt, not notes about how to write one
- If the deck is Chinese and intended for actual presentation, assume at least one revision pass will be needed for line breaks and card fit unless the user explicitly says rough prototype is fine

## Do not
- Do not produce a generic landing page when the brief asks for a presentation
- Do not repeat the same layout on every slide
- Do not overload slides with long paragraphs or dense bullet lists
- Do not use flashy motion that weakens the premium tone
- Do not rely on interaction alone; each slide must still read well in a static state
- Do not trust globally inherited headline width constraints on Chinese slides
- Do not leave fixed-height cards with obviously empty lower halves when the page is text-light
