# html-presentation-microsite

A Codex skill for building premium multi-page HTML presentations that feel like a keynote, report microsite, or slide-based showcase rather than a generic landing page.

## What it does

- Generates prompt-ready guidance for presentation-style HTML
- Converts outlines, PRDs, and report content into slide-based web narratives
- Supports both:
  - showcase mode for concise 6-8 page decks
  - report mode for fuller 10-15 page decks
- Automatically chooses deck length based on content volume when the user does not specify page count
- Adds Chinese-friendly presentation rules for:
  - title line control
  - Chinese font stacks
  - card/container overflow handling
  - content-driven card heights
  - real-presentation QA instead of first-render-only polish

## Why this version is different

- It does not assume English-first headline behavior works for Chinese decks
- It treats title wrapping as a design decision, not a browser accident
- It expects revision passes for real presentation use, especially on Chinese slides with long titles
- It prioritizes usable executive-report layouts over visually loud but fragile showcase compositions

## Skill name

Use:

```text
$html-presentation-microsite
```

## Files

- `SKILL.md`: main skill instructions and triggering guidance
- `agents/openai.yaml`: UI metadata
- `references/prompt-template.md`: generator-ready prompt template
- `references/slide-outline-template.md`: content-to-slide outline template

## Install

Copy this folder into your local Codex skills directory as:

```text
$CODEX_HOME/skills/html-presentation-microsite
```

## Example invocation

```text
Use $html-presentation-microsite to turn this PRD into a premium keynote-style HTML presentation. Automatically choose slide count from the content volume and handle Chinese title wrapping explicitly.
```

## License

MIT
