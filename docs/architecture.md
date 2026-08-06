---
layout: default
title: Architecture
nav_order: 2
---

# Architecture
{: .no_toc }

Three-account hub-and-spoke topology from
[`jajera/tgw-policy-based-routing`](https://github.com/jajera/tgw-policy-based-routing):
Hub VPC + Transit Gateway, Spoke A client with a policy table, Spoke B listener on
`:80` / `:443`.
{: .fs-5 .fw-300 }

## On this page
{: .no_toc .text-delta }

- TOC
{:toc}

---

## Lab topology

Region: **ap-southeast-2**. The Transit Gateway lives in the **network** account and is
shared with **sandbox** and **shared-services** via AWS RAM.

| VPC | Account / profile | CIDR | Role |
| --- | --- | :---: | --- |
| Hub VPC | `network` | `10.0.0.0/24` | Only IGW/NAT; TGW; optional Hub forwarder `:80` |
| Spoke A VPC | `sandbox` | `10.0.1.0/24` | Client instance; **policy table** on TGW attachment |
| Spoke B VPC | `shared-services` | `10.0.2.0/24` | Listener `:80` / `:443`; Direct route table association |

Spokes have **no** Internet Gateway and **no** NAT — internet egress is Hub-only via TGW.

<div class="diagram">
{% include diagrams/example-topology.svg %}
</div>

**Diagram description:** Spoke A (top left) enters a Transit Gateway policy table. Rule 100
(TCP/443) selects Steer → Hub (right). Rule 200 (catch-all) selects Direct → Spoke B
(bottom left). Hub RT associates horizontally with the Hub attachment. Cluster title sits
top-left; edge chips label flows so text does not sit on connectors.
{: .fs-3 .text-grey-dk-000 }

## What the lab proves

| Goal | How |
| --- | --- |
| Same destination IP, different paths | Curl Spoke B on **443** vs **80** |
| 443 steered via Hub | Hub VPC flow logs / TGW ENI show spoke-to-spoke `:443` |
| 80 skips Hub | No spoke-to-spoke `:80` on the Hub TGW path |
| Hub-only internet | Spokes reach `8.8.8.8` / `example.com` only via Hub NAT |
| Bidirectional reachability | Ping/curl among Spoke A, Spoke B, and Hub forwarder |

## Destination-based vs attribute-based forwarding

A classic transit gateway **route table** forwards by destination prefix alone. Without
PBR, Spoke A’s attachment uses one route table — TCP/80 and TCP/443 to the same Spoke B
address take the **same** path.

A **policy table** sits in front of route tables for the associated attachment: rules match
packet attributes, the first match **selects** a target route table, then that table does
normal destination-CIDR lookup.

<div class="diagram">
{% include diagrams/forwarding-compare.svg %}
</div>

**Diagram description:** Top lane — destination-only forwarding: packet → route table →
next hop; `:80` and `:443` to the same IP share one path. Bottom lane — PBR: packet →
policy table (L3/L4) forks to Steer (TCP/443 via Hub) or Direct (`:80` / ICMP), then each
route table looks up the next hop.
{: .fs-3 .text-grey-dk-000 }

| Aspect | Route Table | Policy Table |
| --- | --- | --- |
| Match criteria | Destination IP prefix | Source/dest CIDR, protocol, ports |
| Action | Forward to next-hop attachment | Select a target route table |
| Association | One per attachment | One per attachment (mutually exclusive with route table) |
| This lab | Spoke B → Direct; Hub → Hub RT | Spoke A → policy table |

{: .note }
> An attachment associates with **either** a policy table or a route table — never both.
> Associating a policy table requires first disassociating any existing route table.

## Policy rules (this lab)

| Rule | Match | Target route table |
| :---: | --- | --- |
| 100 | Protocol TCP (`6`), destination port **443** | Steer (via Hub hairpin) |
| 200 | Catch-all `*` | Direct |

{: .warning }
> Without catch-all rule 200, unmatched traffic — including `:80` and ICMP — is
> **dropped** (implicit deny). The catch-all is required for a usable lab.

## Path map (Spoke A → …)

| Traffic | Policy rule | Route table | Path |
| --- | :---: | :---: | --- |
| Spoke B `:443` | 100 | Steer | Spoke A → Hub → Spoke B |
| Spoke B `:80` / ICMP | 200 | Direct | Spoke A → Spoke B |
| Hub forwarder `:80` | 200 | Direct | Spoke A → Hub |
| Internet (non-443) | 200 | Direct | Spoke A → Hub → NAT |
| Internet HTTPS | 100 | Steer | Spoke A → Hub → NAT |

## Static routes (conceptual)

| Route table | Destination | Next hop |
| --- | :---: | --- |
| Direct | `10.0.2.0/24` | Spoke B attachment |
| Direct | `10.0.1.0/24` | Spoke A attachment |
| Direct | `0.0.0.0/0` | Hub attachment |
| Steer | `10.0.2.0/24` | **Hub** attachment (hairpin) |
| Steer | `10.0.1.0/24` | Spoke A attachment |
| Steer | `0.0.0.0/0` | Hub attachment |
| Hub | `10.0.1.0/24` / `10.0.2.0/24` | Spoke attachments |

**NAT return path:** the Hub **public** subnet route table must route spoke CIDRs
(`10.0.1.0/24`, `10.0.2.0/24`) → TGW. Without those routes, outbound SYN can leave via NAT
but replies blackhole — SSM and internet curls time out. The lab adds those routes in
`tgw.tf`.

Live IDs and IPs change every apply — refresh with `terraform output` in the
[lab repository](https://github.com/jajera/tgw-policy-based-routing). See
[Deploy and prove]({{ site.baseurl }}/walkthrough/).

For AWS behaviour detail, see
[Transit gateway policy tables](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}.

[Next: Policy Tables →]({{ site.baseurl }}/policy-tables/){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 }
