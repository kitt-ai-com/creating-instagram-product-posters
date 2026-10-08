---
name: creating-instagram-product-posters
description: Use when a user provides a product image or product brief and asks for an Instagram feed, product poster, campaign visual, or says “인스타 피드 시작하자”.
---

# Creating Instagram Product Posters

Turn one product photo and a short brief into one vertical poster. Preserve the product, ground claims in the brief, and use the requested execution mode.

**REQUIRED SUB-SKILL:** Use `imagegen` for generation or editing.

Read [references/role-contracts.md](references/role-contracts.md) before dispatching roles.
The visual agent must also read [references/art-direction.md](references/art-direction.md).

## Minimum input

- product image
- product name and one truthful feature, supplied by the user or clearly readable from the image
- optional target customer or intended mood
- optional exact headline and subtitle
- optional exact `eyebrow`, `feature_text`, and `footer` metadata supplied by the user; `feature_text` is distinct from the factual product `feature`

Ask only when the product identity or any truthful feature is unavailable. Treat missing audience, mood, and art-direction details as explicit assumptions and continue. Never invent ingredients, efficacy, certification, price, discount, or availability.

## Execution modes

### Fast automatic mode

Activate when the user attaches a product image with short product information and says **“인스타 피드 시작하자”**. Equivalent direct phrases such as “인스타그램 피드 시작하자” or “제품 포스터 시작하자” also activate it.

The trigger phrase is advance approval for the brief, copy, visual direction, and image generation in this one poster job. Run the complete workflow without intermediate approval messages. The coordinator may make reversible creative assumptions, record them in the brief, and continue. It must still stop for missing factual product information, unsupported claims, unsafe content, unavailable required tools, or a `needs_decision` review result.

### Guided mode

Use guided mode for all other requests. Pause at both approval gates below.

## Workflow

1. Inspect the product image. Treat it as the edit target, not a style reference.
2. Dispatch the **analysis agent**. It returns a normalized brief with `facts`, `assumptions`, `must_keep`, and `must_avoid`.
3. **Approval gate 1:** in guided mode, show the brief and wait. In fast automatic mode, record the brief and continue.
4. Dispatch the **copy agent** and **visual agent** in parallel from the approved brief.
5. Dispatch the **generation agent** with both results. It returns one production prompt; it does not generate yet.
6. **Approval gate 2:** in guided mode, show the exact copy and one-paragraph visual direction and wait. In fast automatic mode, preserve both as the approved production record and continue.
7. Use the built-in image-generation tool to create a **text-free** product scene. Preserve the product's silhouette, proportions, label, logo, colors, and packaging unless explicitly asked otherwise. Use vertical 4:5 as an internal default, not a platform-limit claim.
8. Resolve `skill_root` to the directory containing this `SKILL.md`, then add the approved copy with `python <skill_root>/scripts/compose_poster.py`. Do not resolve the script relative to the user's workspace. The script accepts only bundled Pretendard or Noto Sans KR files with their license file present.
9. Dispatch the **review agent** on actual pixels. Text mismatch, product distortion, generic art direction, invented claims, unreadable hierarchy, unintended logos, and watermarks are blocking.
10. Route issues to their owner and revise only affected stages. Allow two automatic revision rounds. If blocking issues remain, return `needs_decision`; never relabel them as passed.

In fast automatic mode, intermediate subagent outputs stay internal unless the user asks to inspect them. Send concise progress updates while working, then return the finished poster.

Before composition, verify that Python can `import PIL`. If it cannot, stop and ask the user to install the bundled dependency file with `python3 -m pip install -r <skill_root>/requirements.txt`; do not silently install packages.

## Text rule

Headline and subtitle are immutable after approval or the fast-mode production record. Optional `eyebrow`, `feature_text`, and `footer` text may be composed only when the user supplied or explicitly approved each exact string; otherwise leave them empty. The factual product `feature` never becomes display metadata automatically. Before gate 2, compare every composed string character-for-character with the brief and restore any changed punctuation, spacing, or wording. If an already approved source string itself appears incorrect, return `needs_decision` instead of rewriting it. Never inject hard-coded editorial labels. Never ask the image model to render poster copy. Compose it with the bundled script and licensed font assets.

For a multi-line Korean headline, start with `--title-spacing 10` on the 1080×1350 canvas. The line boxes must remain visually separate; never use tight or negative leading when glyphs appear to touch. If the user requests only line-spacing adjustment, keep the scene and copy unchanged, rerun composition with `--title-spacing`, then rerun pixel review. Inspect both the full-size image and a 270×338 mobile preview.

## Font rule

Only use font files bundled under `assets/fonts/` and accepted by `scripts/compose_poster.py`. Every font must include its license file. Current default: Pretendard Bold and Regular under SIL OFL 1.1. Do not substitute system fonts, inferred lookalikes, or model-rendered typography.

## Final handoff

Return the image inline, workspace path, final copy, production prompt, assumptions that affected the result, and review status. Label synthetic test products clearly.

## Quick reference

| Problem | Route |
|---|---|
| Unsupported product claim | analysis |
| Weak or long wording | copy |
| Poor hierarchy or staging | visual |
| Product drift or artifacts | generation |
| Rendered copy mismatch, clipping, size, or spacing | composition |
| Product-label distortion or scene artifact | generation |

## Common mistakes

- Sending the raw user request straight to image generation.
- Treating the product photo as optional inspiration and redesigning it.
- Letting generation rewrite approved copy.
- Using a polished but generic studio gradient when the brief calls for a campaign poster.
- Naming a font in the prompt instead of composing with the bundled font file.
- Approving from the prompt without inspecting the rendered image.
