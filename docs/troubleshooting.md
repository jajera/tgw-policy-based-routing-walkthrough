---
layout: default
title: Troubleshooting
nav_order: 6
---

# Troubleshooting
{: .no_toc }

Failure modes for transit gateway policy-based routing — symptoms, diagnostics, and fixes.
{: .fs-5 .fw-300 }

## On this page
{: .no_toc .text-delta }

- TOC
{:toc}

---

## Decision sequence

Use this flowchart to isolate the root cause when traffic does not reach its expected
destination after policy table association.

<div class="diagram">
{% include diagrams/troubleshooting-decision.svg %}
</div>

**Diagram description:** The decision tree starts with "Traffic Dropped?" and walks through
four diagnostic checkpoints in order. First, verify the policy table is associated with the
attachment — if not, associate it. Second, check whether table entries exist using the
GetTransitGatewayPolicyTableEntries API — if the table is empty, add rules. Third, check
the CloudWatch `PacketDropCountNoPolicy` metric — if it is elevated, traffic is hitting
implicit deny, and a catch-all rule is needed. Fourth, check rule ordering — if a broad
rule at a low number shadows a more specific rule at a higher number, reorder entries by
ascending specificity. The sequence ends with "Issue Resolved".
{: .fs-3 .text-grey-dk-000 }

---

## Failure modes

### Traffic dropped by implicit deny

{: .warning }
> Traffic matching no customer-managed entry is silently dropped. There is no reject or
> ICMP unreachable — packets simply disappear.

**Symptom:** Traffic is silently dropped after a policy table is associated with an
attachment. No error is returned to the sender.

**Diagnostic:** Check the CloudWatch metric
[`PacketDropCountNoPolicy`](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}
on the transit gateway. Elevated values confirm that packets are reaching the policy table
but matching no entry.

```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/TransitGateway \
  --metric-name PacketDropCountNoPolicy \
  --dimensions Name=TransitGateway,Value=tgw-0123456789abcdef0 \
  --start-time "$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S)" \
  --end-time "$(date -u +%Y-%m-%dT%H:%M:%S)" \
  --period 300 \
  --statistics Sum
```

**Resolution:** Add a catch-all rule at a high rule number (e.g., 50000) that forwards all
traffic to a default route table. This prevents unmatched traffic from being dropped.

---

### Empty policy table drops all traffic

**Symptom:** All traffic is dropped immediately after associating a policy table that
contains no customer-managed entries.

**Diagnostic:** Query the policy table entries using
[`GetTransitGatewayPolicyTableEntries`](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}
— the result returns only system-managed entries (or is empty of customer-managed entries).

```bash
aws ec2 get-transit-gateway-policy-table-entries \
  --transit-gateway-policy-table-id tgw-ptb-0123456789abcdef0
```

**Resolution:** Add at least one customer-managed entry (such as a catch-all rule) before
or immediately after associating the policy table with an attachment.

{: .tip }
> Create your policy table entries **before** associating the table with a live attachment
> to avoid a traffic blackhole during configuration.

---

### Route table disassociation required

**Symptom:** The API returns an error when attempting to associate a policy table with an
attachment that already has a route table association.

**Diagnostic:** Check the current association status of the attachment:

```bash
aws ec2 get-transit-gateway-attachment-associations \
  --transit-gateway-attachment-id tgw-attach-0123456789abcdef0
```

If the output shows a route table association, it must be removed first.

**Resolution:** Disassociate the existing route table before associating the policy table:

```bash
aws ec2 disassociate-transit-gateway-route-table \
  --transit-gateway-attachment-id tgw-attach-0123456789abcdef0 \
  --transit-gateway-route-table-id tgw-rtb-0123456789abcdef0
```

{: .note }
> An attachment associates with **either** a policy table or a route table — never both.
> See the [AWS documentation](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}
> for details.

---

### Target route table deletion blocked

**Symptom:** Cannot delete a route table that is referenced as the target of a policy table
entry. The API returns a dependency error.

**Diagnostic:** Check which policy table entries reference the route table:

```bash
aws ec2 get-transit-gateway-policy-table-entries \
  --transit-gateway-policy-table-id tgw-ptb-0123456789abcdef0 \
  --filters Name=target-route-table-id,Values=tgw-rtb-0123456789abcdef0
```

**Resolution:** Update or delete the policy table entries that reference the route table
before attempting to delete the route table.

---

### Port range validation error

**Symptom:** The API returns a validation error when submitting a policy table entry that
includes a port range.

**Diagnostic:** Check the protocol specified in the entry. Port ranges are only valid for:

| Protocol | Number |
| --- | :---: |
| TCP | 6 |
| UDP | 17 |

Protocols such as ICMP (1), GRE (47), and Any (\*) do not support port range matching and
resolve port ranges to Any.

**Resolution:** Either remove the port range specification from the entry, or change the
protocol to TCP (6) or UDP (17). See the
[AWS policy table documentation](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}
for the full list of supported match criteria.

---

### Rule shadowing

{: .warning }
> Rule shadowing is silent — no error or warning is raised. Traffic simply matches an
> unexpected entry.

**Symptom:** Traffic matches an unexpected rule. A more specific entry is never reached
despite appearing to be a better match for the traffic.

**Diagnostic:** A broader entry at a **lower** rule number is evaluated first and matches
the traffic before the more specific entry at a higher rule number is considered. Policy
table entries are evaluated in ascending rule number order — the first match wins.

Example of a shadowed configuration:

| Rule # | Source CIDR | Dest CIDR | Target RT | Effect |
| :---: | :---: | :---: | --- | --- |
| 100 | 0.0.0.0/0 | 0.0.0.0/0 | Default RT | Matches all traffic first |
| 200 | 10.1.0.0/16 | 10.100.0.0/16 | Inspection RT | Never reached |

**Resolution:** Reorder rules so that more specific entries have lower rule numbers.
Place the broadest catch-all entry at the highest rule number:

| Rule # | Source CIDR | Dest CIDR | Target RT | Effect |
| :---: | :---: | :---: | --- | --- |
| 100 | 10.1.0.0/16 | 10.100.0.0/16 | Inspection RT | Matches specific traffic |
| 50000 | 0.0.0.0/0 | 0.0.0.0/0 | Default RT | Catch-all for everything else |

---

### Inspecting entries and evaluation order

**Symptom:** Unclear which rules exist in a policy table, their evaluation order, or
whether system-managed entries are present.

**Diagnostic:** Use
[`GetTransitGatewayPolicyTableEntries`](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}
to retrieve all entries — both system-managed and customer-managed — together with their
rule numbers that determine evaluation order:

```bash
aws ec2 get-transit-gateway-policy-table-entries \
  --transit-gateway-policy-table-id tgw-ptb-0123456789abcdef0
```

System-managed entries display a rule number of `*` and are evaluated **before** all
customer-managed entries. Customer-managed entries are evaluated in ascending rule number
order (lowest number first). Traffic matching no entry is dropped by implicit deny.

**Resolution:** Review the complete entry list and adjust customer-managed rule numbers to
achieve the desired evaluation order. Place specific rules at lower numbers and the
catch-all at the highest number.

{: .note }
> For the full API reference, see
> [Transit Gateway policy tables](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-policy-tables.html){:target="_blank"}
> in the AWS documentation.

---

[Next: Reference →]({{ site.baseurl }}/reference/){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 }
