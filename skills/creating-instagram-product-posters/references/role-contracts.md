# Role contracts

Use one fresh subagent per logical role. The coordinator owns approvals and the final file. In fast automatic mode, the user's trigger phrase grants the coordinator advance approval for this one poster job; in guided mode, approvals come from the user at the two gates. Roles return structured text and do not silently change upstream decisions.

## Shared brief

```yaml
job_id: ""
revision: 1
product_image: ""
product_name: ""
feature: ""
audience: ""
goal: "product awareness"
mood: ""
facts: []
assumptions: []
must_keep: []
must_avoid: []
headline: ""
subtitle: ""
eyebrow: ""
feature_text: ""
footer: ""
```

## Analysis agent

**Input:** user request and inspected product-image observations.

**Return:** the shared brief. Mark every non-user-supplied decision as an assumption. Do not write polished copy or a design concept. Do not infer efficacy, ingredients, price, certification, or offer terms.

## Copy agent

**Input:** approved shared brief, or the coordinator-recorded brief in fast automatic mode.

**Return:**

```yaml
headline: ""
subtitle: ""
rationale: ""
```

If the user supplied exact strings, preserve them verbatim. Otherwise write one headline and one subtitle only. Keep each short enough to read on a phone and do not introduce new factual claims.

The copy agent leaves `eyebrow`, `feature_text`, and `footer` empty unless the user supplied or explicitly approved each exact string. `feature_text` is display metadata and must never be populated automatically from the factual product `feature`. The coordinator must not inject stock editorial labels.

## Visual agent

**Input:** approved brief, or the coordinator-recorded brief in fast automatic mode, plus product-image observations and `references/art-direction.md`.

**Return:**

```yaml
composition: ""
product_staging: ""
background: ""
lighting: ""
palette: ""
headline_zone: ""
subtitle_zone: ""
negative_constraints: []
```

Design a single poster, not a carousel. The product must remain the focal point. Reserve clear text zones and protect the product, label, logo, and important details from crops or overlays.

## Generation agent

**Input:** approved brief, copy, and visual specification.

**Return:** one prompt using this shape:

```text
Use case: ads-marketing
Asset type: vertical 4:5 Instagram product poster
Primary request: <poster goal>
Input images: Image 1: edit target and product identity source
Subject: <product and staging>
Style/medium: <photography or illustration direction>
Composition/framing: <layout and protected text zones>
Lighting/mood: <direction>
Color palette: <direction>
Text: none; reserve the approved typography zone for later composition
Constraints: preserve product silhouette, proportions, label, logo, colors, and packaging details; no invented claims
Avoid: generated poster text, unrelated logos, watermark, distorted packaging, empty generic studio-template styling
```

Do not generate until approval gate 2 passes in guided mode or the coordinator records the exact copy and visual direction in fast automatic mode. Do not rewrite copy. The coordinator resolves the directory containing `SKILL.md` and adds copy with `python <skill-root>/scripts/compose_poster.py`; never resolve the script relative to the user's workspace.

## Review agent

**Input:** actual rendered image, approved brief, exact copy, and visual specification.

**Return:**

```yaml
status: pass | revise | needs_decision
issues:
  - owner: analysis | copy | visual | generation | composition | user
    severity: blocking | minor
    evidence: ""
    requested_change: ""
```

Inspect actual pixels, including a mobile-size view. Blocking checks:

- the product still matches the supplied image;
- headline and subtitle match character-for-character;
- any optional `eyebrow`, `feature_text`, and `footer` text matches the explicitly supplied or approved strings;
- the composed font comes from the bundled allowlist with its license file present;
- no unsupported claim, extra text, watermark, or unrelated logo appears;
- product and copy remain legible and uncropped;
- artifacts, malformed packaging, poor contrast, and generic catalog-like staging are absent.

Pass only when all blocking checks succeed. Review never edits the image itself.

## Revision routing

| Finding | Owner | Re-run |
|---|---|---|
| Unsupported statement | analysis | analysis onward |
| Copy overflow before approval or fast-mode recording | copy | copy onward |
| Suspected typo or wording problem in an approved source string | user | return `needs_decision` |
| Weak composition or text collision | visual | visual onward |
| Rendered copy mismatch, clipping, font, size, or line spacing | composition | composition and review only |
| Product-label distortion, scene artifact, or product drift | generation | generation and review |
