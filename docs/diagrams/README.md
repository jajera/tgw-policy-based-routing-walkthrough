# Diagram Generation

Theme-aware **inline SVG** (same approach as
[privatelink-conduit](https://privatelink-conduit.johna.kiwi/)). Prefer SVG over
Draw.io here so diagrams inherit `pbr` / `pbr-dark` CSS variables, stay in git as text, and
need no binary editor.

## Brand assets (favicon / OG)

```bash
/usr/bin/python3 docs/scripts/generate-brand-assets.py
```

Writes `docs/assets/images/{favicon.ico,favicon-16.png,favicon-32.png,apple-touch-icon.png,icon-512.png,og-image.png}`
using the PBR theme colours (`#0f766e` accent, mint surfaces). Requires system Pillow
(`/usr/bin/python3` + `python3-pil`).

Open Graph art: edit/replace `docs/assets/images/og-source.png`, then re-run the script —
`og-image.png` is derived from that master (1200×630). Without `og-source.png`, a
procedural conduit-style fallback is generated.

## Regeneration (diagrams)

```bash
python3 docs/scripts/generate-diagrams.py
```

## Prerequisites

- Python 3.8+ (standard library only)

## Output

| File | Page |
| --- | --- |
| `docs/_includes/diagrams/example-topology.svg` | Architecture |
| `docs/_includes/diagrams/forwarding-compare.svg` | Architecture (route vs policy) |
| `docs/_includes/diagrams/rule-evaluation.svg` | Policy Tables |
| `docs/_includes/diagrams/inspection-steering.svg` | Use Cases (path selection) |
| `docs/_includes/diagrams/pbr-mental-model.svg` | Walkthrough (mental model) |
| `docs/_includes/diagrams/troubleshooting-decision.svg` | Troubleshooting |

Edit definitions in `docs/scripts/generate-diagrams.py`, regenerate, then commit both the
script and the SVG outputs. Output is deterministic.
