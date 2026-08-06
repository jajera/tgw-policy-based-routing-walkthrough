---
layout: default
title: Use Cases
nav_order: 4
description: >-
  Scenarios where transit gateway policy tables beat route tables — path selection
  (this lab), inspection steering, and routing-domain isolation.
---

# Use Cases
{: .no_toc }

Where a transit gateway **policy table** beats a destination-based **route table** —
starting with the path-selection pattern the
[lab](https://github.com/jajera/tgw-policy-based-routing) proves.
{: .fs-5 .fw-300 }

## On this page
{: .no_toc .text-delta }

- TOC
{:toc}

---

## Use Case 1: Path selection (this lab)

**Scenario** — Send traffic to the **same destination IP** over different paths based on
protocol or port. In
[`jajera/tgw-policy-based-routing`](https://github.com/jajera/tgw-policy-based-routing),
Spoke A → Spoke B **TCP/443** hairpins via the Hub VPC; **TCP/80** (and ICMP) go Direct.

**When a policy table is preferable** — A classic route table picks one next hop per
destination prefix. It cannot send `:443` one way and `:80` another to the same address.
A policy table matches L3/L4 attributes first, then destination routing runs inside the
selected table.

<div class="diagram">
{% include diagrams/inspection-steering.svg %}
</div>

**Diagram description:** Traffic from Spoke A enters the Transit Gateway on a policy-table
association. Destination TCP/443 matches rule 100 and takes the Steer route table (via
Hub). Other traffic matches the catch-all and takes the Direct route table to Spoke B or
Hub NAT.
{: .text-small }

See [Architecture]({{ site.baseurl }}/architecture/) for the path map and
[Deploy and prove]({{ site.baseurl }}/walkthrough/) for apply and verification.

{: .warning }
> Associating a policy table with a Site-to-Site VPN or Connect attachment **stops**
> Transit Gateway BGP advertisements to that attachment. Plan static routing or an
> alternate advertisement path. See
> [AWS Transit Gateway policy tables](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}.

## Use Case 2: Inspection steering

**Scenario** — Steer sensitive-subnet (or sensitive-port) traffic through an inspection or
security appliance VPC before it reaches its destination; leave other traffic on the
direct path.

**When a policy table is preferable** — You need attribute-based selection of an inspection
route table without duplicating attachments or splitting every prefix. Match on source
CIDR, destination CIDR, protocol, and ports; first match wins.

The lab’s Hub hairpin is the same *mechanism* (select a route table that next-hops via an
intermediate VPC). Swap Hub for an appliance VPC and the pattern becomes classic inspection
steering.

## Use Case 3: Routing-domain isolation

**Scenario** — Isolate traffic domains by directing different source CIDRs to separate
route tables with non-overlapping route sets on a single transit gateway.

**When a policy table is preferable** — Tenants or business units share one TGW but need
independent forwarding domains. Match on source CIDR and send each domain to its own route
table without a TGW per domain.

---

[Next: Deploy and prove →]({{ site.baseurl }}/walkthrough/){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 }
