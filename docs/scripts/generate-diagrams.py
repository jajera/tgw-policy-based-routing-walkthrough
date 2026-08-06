#!/usr/bin/env python3
"""Generate theme-aware SVG diagram includes for the docs site.

Matches the privatelink-conduit diagram helper style: cluster titles top-left,
edge labels on diagram-edge-bg chips, no centred title text over connectors.

Produces under docs/_includes/diagrams/:
  - example-topology.svg
  - rule-evaluation.svg
  - inspection-steering.svg
  - pbr-mental-model.svg
  - forwarding-compare.svg
  - troubleshooting-decision.svg

Usage:
  python3 docs/scripts/generate-diagrams.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_includes" / "diagrams"
OUT.mkdir(parents=True, exist_ok=True)


def svg(width: int, height: int, body: str, title: str, desc: str = "") -> str:
    desc_el = f"\n  <desc>{desc}</desc>" if desc else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" role="img" aria-label="{title}">
  <title>{title}</title>{desc_el}
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" class="diagram-arrow-head"/>
    </marker>
  </defs>
{body}
</svg>
'''


def box(x: float, y: float, w: float, h: float, lines: list, kind: str = "node") -> str:
    """kind: node | cluster | accent. Clusters get a top-left title only."""
    cls = {"node": "diagram-node", "cluster": "diagram-cluster", "accent": "diagram-accent"}[kind]
    rx = 12 if kind == "cluster" else 10
    parts = [f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}"/>']
    if kind == "cluster":
        parts.append(
            f'  <text x="{x + 14}" y="{y + 22}" class="diagram-label" '
            f'font-weight="600" font-size="12">{lines[0]}</text>'
        )
        return "\n".join(parts)

    n = len(lines)
    line_h = 15
    block_h = n * line_h
    first_y = y + (h - block_h) / 2 + line_h / 2
    for i, line in enumerate(lines):
        weight = ' font-weight="600"' if i == 0 else ""
        size = 12 if i == 0 else 11
        parts.append(
            f'  <text x="{x + w / 2}" y="{first_y + i * line_h}" text-anchor="middle" '
            f'dominant-baseline="middle" class="diagram-text"{weight} font-size="{size}">{line}</text>'
        )
    return "\n".join(parts)


def arrow(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    label: str | None = None,
    dashed: bool = False,
) -> str:
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    parts = [
        f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="diagram-line"{dash} '
        f'marker-end="url(#arrow)"/>'
    ]
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        tw = max(72, len(label) * 6.8)
        parts.append(
            f'  <rect x="{mx - tw / 2}" y="{my - 11}" width="{tw}" height="20" rx="4" '
            f'class="diagram-edge-bg"/>'
        )
        parts.append(
            f'  <text x="{mx}" y="{my}" text-anchor="middle" dominant-baseline="middle" '
            f'class="diagram-edge-text" font-size="11">{label}</text>'
        )
    return "\n".join(parts)


def path_arrow(points: str, label: str | None = None, label_at: tuple | None = None) -> str:
    """Orthogonal polyline arrow. points = 'x1,y1 x2,y2 ...'."""
    parts = [
        f'  <polyline points="{points}" fill="none" class="diagram-line" '
        f'marker-end="url(#arrow)"/>'
    ]
    if label and label_at:
        mx, my = label_at
        tw = max(72, len(label) * 6.8)
        parts.append(
            f'  <rect x="{mx - tw / 2}" y="{my - 11}" width="{tw}" height="20" rx="4" '
            f'class="diagram-edge-bg"/>'
        )
        parts.append(
            f'  <text x="{mx}" y="{my}" text-anchor="middle" dominant-baseline="middle" '
            f'class="diagram-edge-text" font-size="11">{label}</text>'
        )
    return "\n".join(parts)


# ── 1. Lab topology ──────────────────────────────────────────────────────────
# Clean left → centre → right layout; no title text over connectors.

def generate_example_topology() -> str:
    """Lab topology — orthogonal lanes, cluster title top-left only."""
    parts = []

    # Accounts
    parts.append(box(20, 56, 156, 68, ["Spoke A", "sandbox", "10.0.1.0/24"], "node"))
    parts.append(box(20, 250, 156, 68, ["Spoke B", "shared-svc", "10.0.2.0/24"], "node"))

    # Hub spans the two right-hand lanes so arrows stay horizontal
    parts.append(box(730, 56, 150, 232, ["Hub", "network", "10.0.0.0/24", "IGW + NAT"], "accent"))

    # TGW cluster
    parts.append(box(210, 24, 490, 310, ["Transit Gateway"], "cluster"))

    parts.append(box(234, 64, 140, 64, ["Policy table", "Spoke A only"], "accent"))
    parts.append(box(430, 64, 140, 56, ["Steer RT", "via Hub"], "node"))
    parts.append(box(430, 148, 140, 56, ["Direct RT", "catch-all"], "node"))
    parts.append(box(430, 232, 140, 56, ["Hub RT"], "node"))

    parts.append(
        '  <rect x="234" y="308" width="430" height="16" rx="4" class="diagram-edge-bg"/>'
    )
    parts.append(
        '  <text x="449" y="316" text-anchor="middle" dominant-baseline="middle" '
        'class="diagram-edge-text" font-size="11">'
        "Rule 100 → Steer (TCP/443) · Rule 200 → Direct (*)</text>"
    )

    # Spoke A → Policy
    parts.append(arrow(176, 90, 234, 90))

    # Policy → Steer
    parts.append(arrow(374, 96, 430, 96))

    # Policy → Direct
    parts.append(path_arrow("374,96 400,96 400,176 430,176"))

    # Steer → Hub (horizontal)
    parts.append(arrow(570, 92, 730, 92, "TCP/443"))

    # Hub RT → Hub (horizontal)
    parts.append(arrow(570, 260, 730, 260, "assoc."))

    # Direct → Spoke B (orthogonal, clear of titles)
    parts.append(
        path_arrow(
            "430,176 400,176 400,284 176,284",
            label=":80 / ICMP",
            label_at=(300, 284),
        )
    )

    return svg(
        900,
        350,
        "\n".join(parts),
        "Lab topology: three-account hub-and-spoke with PBR",
        "Spoke A policy table selects Steer (TCP/443 via Hub) or Direct "
        "(:80 / ICMP to Spoke B). Hub owns IGW/NAT.",
    )


# ── 2. Rule evaluation ───────────────────────────────────────────────────────

def step_badge(x: float, y: float, n: int) -> str:
    """Numbered circle so evaluation order is unmistakable."""
    return "\n".join(
        [
            f'  <circle cx="{x}" cy="{y}" r="14" class="diagram-accent"/>',
            f'  <text x="{x}" y="{y}" text-anchor="middle" dominant-baseline="middle" '
            f'class="diagram-text" font-weight="600" font-size="13">{n}</text>',
        ]
    )


def generate_rule_evaluation() -> str:
    """Vertical numbered sequence — order reads top→bottom at a glance."""
    parts = []

    parts.append(
        '  <text x="360" y="26" text-anchor="middle" class="diagram-label" '
        'font-weight="600" font-size="13">Evaluation order (top → bottom)</text>'
    )

    # Step 1
    parts.append(step_badge(36, 70, 1))
    parts.append(box(64, 46, 280, 48, ["System-managed entries", "rule number * · match → stop"], "accent"))

    parts.append(arrow(204, 94, 204, 126, "no match"))

    # Step 2 cluster
    parts.append(step_badge(36, 160, 2))
    parts.append(box(64, 126, 560, 168, ["Customer-managed — ascending rule # (lowest first)"], "cluster"))

    parts.append(box(84, 158, 170, 48, ["2a · Rule 100", "TCP/443 → Steer"], "node"))
    parts.append(arrow(254, 182, 300, 182))
    parts.append(box(300, 158, 150, 48, ["→ Steer RT", "match · stop"], "accent"))

    parts.append(arrow(169, 206, 169, 230, "no match"))

    parts.append(box(84, 230, 170, 48, ["2b · Rule 200", "* → Direct"], "node"))
    parts.append(arrow(254, 254, 300, 254))
    parts.append(box(300, 230, 150, 48, ["→ Direct RT", "match · stop"], "accent"))

    parts.append(arrow(204, 294, 204, 326, "no match"))

    # Step 3
    parts.append(step_badge(36, 366, 3))
    parts.append(box(64, 342, 280, 48, ["Implicit deny", "no match anywhere → drop"], "accent"))

    parts.append(
        '  <text x="360" y="418" text-anchor="middle" class="diagram-label" '
        'font-size="12">First matching entry wins; evaluation stops.</text>'
    )

    return svg(
        720,
        440,
        "\n".join(parts),
        "Policy table rule evaluation order",
        "1 system-managed, 2 customer-managed ascending (lab: 100 then 200), "
        "3 implicit deny if nothing matches.",
    )


# ── 3. Path selection (lab pattern) ──────────────────────────────────────────

def generate_inspection_steering() -> str:
    """Path selection — orthogonal lanes; Steer↔Hub and Direct↔Spoke B share Y."""
    parts = []

    # Shared lane centres (box height 56 → ± y = top + 28; height 64 → top + 32)
    steer_cy = 100
    direct_cy = 188
    policy_cy = (steer_cy + direct_cy) / 2  # 144 — midway between route tables

    # Left: Spoke A centred on policy lane
    parts.append(box(20, policy_cy - 32, 140, 64, ["Spoke A", "10.0.1.0/24"], "node"))

    # Transit Gateway cluster
    parts.append(box(200, 40, 360, 240, ["Transit Gateway"], "cluster"))
    parts.append(box(220, policy_cy - 28, 130, 56, ["Policy table"], "accent"))
    parts.append(box(390, steer_cy - 28, 140, 56, ["Steer RT"], "node"))
    parts.append(box(390, direct_cy - 28, 140, 56, ["Direct RT"], "node"))

    # Right: Hub aligned with Steer; Spoke B aligned with Direct
    parts.append(box(620, steer_cy - 32, 140, 64, ["Hub", "hairpin / NAT"], "accent"))
    parts.append(box(620, direct_cy - 32, 140, 64, ["Spoke B", "10.0.2.0/24"], "node"))

    # Spoke A → Policy (horizontal)
    parts.append(arrow(160, policy_cy, 220, policy_cy))

    # Policy → fork → Steer / Direct (orthogonal T)
    parts.append(path_arrow(f"350,{policy_cy:.0f} 370,{policy_cy:.0f} 370,{steer_cy} 390,{steer_cy}"))
    parts.append(path_arrow(f"370,{policy_cy:.0f} 370,{direct_cy} 390,{direct_cy}"))

    # Steer → Hub and Direct → Spoke B (horizontal, same Y as boxes)
    parts.append(arrow(530, steer_cy, 620, steer_cy, "TCP/443"))
    parts.append(arrow(530, direct_cy, 620, direct_cy, ":80 / ICMP"))

    # Hub hairpin down into Spoke B (right edge aligned)
    parts.append(
        path_arrow(f"760,{steer_cy} 780,{steer_cy} 780,{direct_cy} 760,{direct_cy}")
    )

    parts.append(
        '  <rect x="220" y="248" width="320" height="22" rx="4" class="diagram-edge-bg"/>'
    )
    parts.append(
        '  <text x="380" y="259" text-anchor="middle" dominant-baseline="middle" '
        'class="diagram-edge-text" font-size="11">'
        "Same Spoke B IP — path diverges by destination port</text>"
    )

    return svg(
        800,
        300,
        "\n".join(parts),
        "Path selection: TCP/443 via Hub vs Direct",
        "Spoke A policy table steers destination TCP/443 via Hub and sends "
        "TCP/80 and ICMP Direct to Spoke B.",
    )


# ── 4. PBR mental model (policy selects route table) ─────────────────────────

def generate_pbr_mental_model() -> str:
    """Packet → policy table → route table → next hop (orthogonal, not ASCII)."""
    parts = []
    row_cy = 150

    # Entry chip above Policy table (same column)
    parts.append(box(24, 28, 190, 48, ["Packet in on attachment"], "accent"))
    parts.append(arrow(119, 76, 119, 118))

    # Horizontal decision chain — gaps ≥ 100 so edge chips clear the boxes
    parts.append(box(24, row_cy - 32, 190, 64, ["Policy table", "(L3/L4 match)"], "node"))
    parts.append(arrow(214, row_cy, 314, row_cy, "selects"))
    parts.append(box(314, row_cy - 32, 190, 64, ["Route table", "(destination IP)"], "node"))
    parts.append(arrow(504, row_cy, 620, row_cy, "CIDR lookup"))
    parts.append(box(620, row_cy - 32, 190, 64, ["Attachment /", "next hop"], "accent"))

    return svg(
        840,
        230,
        "\n".join(parts),
        "PBR mental model: policy table then route table",
        "Packet arrives on a policy-associated attachment; the policy table "
        "selects a route table; that table does destination-CIDR lookup to a next hop.",
    )


# ── 5. Destination-based vs attribute-based (side-by-side) ───────────────────

def generate_forwarding_compare() -> str:
    """Two stacked lanes: classic route-table path vs PBR path."""
    parts = []

    # ── Lane A: destination-only ────────────────────────────────────────────
    parts.append(box(20, 16, 760, 118, ["Destination-based (route table)"], "cluster"))
    parts.append(box(40, 48, 150, 56, ["Packet in", "on attachment"], "accent"))
    parts.append(arrow(190, 76, 250, 76))
    parts.append(box(250, 48, 180, 56, ["Route table", "dest IP only"], "node"))
    parts.append(arrow(430, 76, 520, 76, "CIDR lookup"))
    parts.append(box(520, 48, 180, 56, ["Attachment /", "next hop"], "accent"))
    parts.append(
        '  <rect x="40" y="112" width="300" height="18" rx="4" class="diagram-edge-bg"/>'
    )
    parts.append(
        '  <text x="190" y="121" text-anchor="middle" dominant-baseline="middle" '
        'class="diagram-edge-text" font-size="11">'
        ":80 and :443 to same IP → same path</text>"
    )

    # ── Lane B: attribute-based PBR ─────────────────────────────────────────
    parts.append(box(20, 154, 760, 196, ["Attribute-based (policy table)"], "cluster"))
    parts.append(box(40, 190, 150, 56, ["Packet in", "on attachment"], "accent"))
    parts.append(arrow(190, 218, 250, 218))
    parts.append(box(250, 190, 150, 56, ["Policy table", "L3/L4 match"], "node"))

    # Fork to two route tables (same destination IP, different ports)
    parts.append(path_arrow("400,218 430,218 430,196 460,196"))
    parts.append(path_arrow("430,218 430,250 460,250"))
    parts.append(box(460, 168, 140, 48, ["Steer RT", "TCP/443"], "accent"))
    parts.append(box(460, 230, 140, 48, ["Direct RT", ":80 / ICMP"], "node"))

    parts.append(arrow(600, 192, 650, 192))
    parts.append(arrow(600, 254, 650, 254))
    parts.append(box(650, 168, 110, 48, ["Spoke B", "via Hub"], "accent"))
    parts.append(box(650, 230, 110, 48, ["Spoke B", "direct"], "node"))

    parts.append(
        '  <rect x="40" y="308" width="420" height="18" rx="4" class="diagram-edge-bg"/>'
    )
    parts.append(
        '  <text x="250" y="317" text-anchor="middle" dominant-baseline="middle" '
        'class="diagram-edge-text" font-size="11">'
        "First match selects a route table; then dest-CIDR lookup</text>"
    )

    return svg(
        800,
        370,
        "\n".join(parts),
        "Destination-based vs attribute-based forwarding",
        "Classic route tables forward by destination IP only so equal destinations "
        "share a path. A policy table matches L3/L4 attributes first, selects a "
        "route table, then destination lookup runs — so :443 and :80 can diverge.",
    )


# ── 6. Troubleshooting decision ──────────────────────────────────────────────

def generate_troubleshooting_decision() -> str:
    parts = []
    y = 20
    parts.append(box(280, y, 200, 44, ["Traffic dropped?"], "accent"))
    y = 84
    parts.append(arrow(380, 64, 380, y))
    parts.append(box(260, y, 240, 48, ["Policy table associated?"], "node"))

    parts.append(path_arrow("260,108 120,108", label="no", label_at=(190, 108)))
    parts.append(box(20, 86, 100, 44, ["Associate"], "accent"))

    y = 160
    parts.append(arrow(380, 132, 380, y))
    parts.append(box(260, y, 240, 48, ["Entries present?"], "node"))
    parts.append(path_arrow("260,184 120,184", label="empty", label_at=(190, 184)))
    parts.append(box(20, 162, 100, 44, ["Add rules"], "accent"))

    y = 236
    parts.append(arrow(380, 208, 380, y))
    parts.append(box(240, y, 280, 48, ["PacketDropCountNoPolicy?"], "node"))
    parts.append(path_arrow("240,260 120,260", label="elevated", label_at=(180, 260)))
    parts.append(box(20, 238, 100, 44, ["Catch-all", "or rules"], "accent"))

    y = 312
    parts.append(arrow(380, 284, 380, y))
    parts.append(box(260, y, 240, 48, ["Rule order / shadowing"], "node"))
    parts.append(arrow(380, 360, 380, 384))
    parts.append(box(280, 384, 200, 40, ["Reorder by specificity"], "accent"))

    return svg(
        760,
        440,
        "\n".join(parts),
        "Troubleshooting decision sequence",
        "Check association, entries, PacketDropCountNoPolicy, then rule order.",
    )


def main() -> None:
    diagrams = {
        "example-topology.svg": generate_example_topology(),
        "rule-evaluation.svg": generate_rule_evaluation(),
        "inspection-steering.svg": generate_inspection_steering(),
        "pbr-mental-model.svg": generate_pbr_mental_model(),
        "forwarding-compare.svg": generate_forwarding_compare(),
        "troubleshooting-decision.svg": generate_troubleshooting_decision(),
    }
    for name, content in diagrams.items():
        path = OUT / name
        path.write_text(content, encoding="utf-8")
        print(f"  wrote {path}")
    print(f"\nGenerated {len(diagrams)} diagrams in {OUT}")


if __name__ == "__main__":
    main()
