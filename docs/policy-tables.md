---
layout: default
title: Policy Tables
nav_order: 3
description: >-
  Transit gateway policy table mechanics — match criteria, rule evaluation order,
  system-managed and customer-managed entries, limitations, and best practices.
---

# Policy Tables
{: .no_toc }

Match criteria, evaluation order, system vs customer entries, and limits — as stated in
[Transit gateway policy tables](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}.
{: .fs-5 .fw-300 }

## On this page
{: .no_toc .text-delta }

- TOC
{:toc}

---

## Match Criteria

Each policy table entry matches on five fields
([source](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}):

| Field | Format | Example |
| --- | --- | --- |
| Source IP CIDR | CIDR block or Any | `10.0.0.0/8` |
| Destination IP CIDR | CIDR block or Any | `172.16.0.0/12` |
| Source port range | Port range or Any | `1024-65535` |
| Destination port range | Port range or Any | `443-443` |
| Protocol | Number or Any (`*`) | `6` (TCP) |

Each entry also specifies a **target transit gateway route table** to which matching
traffic is forwarded
([source](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}).

{: .note }
> Any match field that is omitted defaults to **Any**, meaning the entry matches all
> values for that field
> ([source](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}).

---

## Evaluation Order

<div class="diagram">
{% include diagrams/rule-evaluation.svg %}
</div>

**Text description (equivalent to diagram above):** Evaluation proceeds in three phases.
First, system-managed entries (rule number `*`) are evaluated. If no system-managed entry
matches, customer-managed entries are evaluated in ascending rule number order — lowest
rule number first. The first matching entry wins and evaluation stops immediately. If no
entry matches at all, an implicit deny drops the traffic.

The full evaluation sequence
([source](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}):

1. **System-managed entries** — created by AWS, rule number displayed as `*`, read-only.
   Evaluated before all customer-managed entries.
2. **Customer-managed entries** — evaluated in ascending rule number order. First match
   wins; evaluation stops.
3. **Implicit deny** — traffic matching no entry is dropped.

---

## Entry Types

### System-Managed Entries

System-managed entries are created and maintained by AWS. They:

- Display a rule number of `*`
- Are read-only — you cannot modify or delete them
- Are evaluated **before** all customer-managed entries

([source](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"})

### Customer-Managed Entries

Customer-managed entries are entries you create and control. They:

- Use rule numbers in the range **1 to 50,000**
- Are evaluated in ascending rule number order after system-managed entries
- Follow first-match-wins semantics — once a packet matches an entry, evaluation stops

([source](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"})

---

## Protocol and Port Behaviour

Port range matching applies only to protocols that use ports
([source](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}):

| Protocol | Number | Port range behaviour |
| --- | :---: | --- |
| TCP | `6` | Source and destination port ranges are evaluated as specified |
| UDP | `17` | Source and destination port ranges are evaluated as specified |
| ICMPv4 | `1` | Port ranges resolve to Any |
| GRE | `47` | Port ranges resolve to Any |
| Any | `*` | Port ranges resolve to Any |

When you specify ICMPv4, GRE, or Any as the protocol, any port range values are ignored
and treated as Any.

---

## Best Practices

{: .tip }
> Follow these practices to keep policy tables maintainable and predictable
> ([source](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}).

- **Use non-consecutive rule numbers.** Leave gaps (for example, 100, 200, 500) so you
  can insert entries later without renumbering.
- **Order by specificity — most specific first.** Place narrow CIDR matches at lower rule
  numbers so they are evaluated before broader entries.
- **Add an explicit catch-all at a high rule number.** A broad entry (for example,
  `0.0.0.0/0` at rule 49000) forwards unmatched traffic to a known route table rather
  than relying on the implicit deny.

---

## Attachment Exclusivity

{: .warning }
> An attachment associates with **either** a policy table **or** a route table — not both.
> Associating a policy table with an attachment that already has a route table association
> is unsupported; you must disassociate the route table first
> ([source](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}).

---

## Availability and Pricing

{: .note }
> Policy-based routing is available in **every AWS Region** where transit gateway is
> available. There is no additional charge beyond standard transit gateway fees
> ([source](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}).

---

## Limitations

### Cloud WAN Peering Attachments

Transit gateway to AWS Cloud WAN peering attachments do **not** support customer-managed
policy table entries. Traffic on those attachments is controlled exclusively by
system-managed entries
([source](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}).

### BGP Route Advertisement Withholding

A transit gateway **withholds BGP route advertisements** to Site-to-Site VPN and Connect
attachments that are associated with a policy table. Peers on those attachments do not
receive transit gateway route advertisements while the policy table association is active
([source](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}).

### Direct Connect Allowed-Prefixes

Direct Connect advertisements to a customer gateway remain governed by the
**allowed-prefixes list** on the Direct Connect gateway association. Those advertisements
continue while a policy table is associated — the allowed-prefixes filtering is independent
of policy table behaviour
([source](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}).

---

[Next: Use Cases →]({{ site.baseurl }}/use-cases/){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 }
