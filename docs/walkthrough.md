---
layout: default
title: Deploy and prove
nav_order: 5
permalink: /walkthrough/
---

# Deploy and prove
{: .no_toc }

Operator runbook for
[`jajera/tgw-policy-based-routing`](https://github.com/jajera/tgw-policy-based-routing):
apply the three-account lab, prove destination-only versus PBR path split, then tear down.
{: .fs-5 .fw-300 }

## On this page
{: .no_toc .text-delta }

- TOC
{:toc}

---

{: .cost }
> Billable while running: Transit Gateway attachments, NAT Gateway, EC2, Hub flow logs.
> Review [TGW pricing](https://aws.amazon.com/transit-gateway/pricing/) and follow teardown
> below. Confirm `terraform state list` is empty when finished.

## Prerequisites

- Clone the lab:
  [`jajera/tgw-policy-based-routing`](https://github.com/jajera/tgw-policy-based-routing)
- Terraform **>= 1.6**, AWS provider **>= 5.0**
- AWS CLI with Session Manager plugin
- Three CLI profiles → distinct accounts:
  - `network` — Hub VPC + Transit Gateway (internet egress)
  - `sandbox` — Spoke A client VPC
  - `shared-services` — Spoke B HTTP/HTTPS target VPC
- Region: **ap-southeast-2** (lab default)

If your profiles use different names, set `network_profile`, `sandbox_profile`, and
`shared_services_profile` in `terraform.tfvars` (see `terraform.tfvars.example` in the lab).

## Mental model

PBR does **not** replace Transit Gateway route tables. It sits **in front** of them for
attachments associated with a **policy table**:

1. Packet arrives on a TGW attachment associated with a policy table.
2. Policy rules match packet attributes in ascending rule-number order.
3. The first matching rule selects a **target route table**.
4. That route table does normal **destination-CIDR** lookup.

<div class="diagram">
{% include diagrams/pbr-mental-model.svg %}
</div>

**Diagram description:** A packet arrives on a policy-associated attachment, matches in the
policy table (L3/L4), which **selects** a route table; that table does a destination-CIDR
lookup to an attachment / next hop.
{: .fs-3 .text-grey-dk-000 }

| Question | Destination-only | Policy-Based Routing |
| --- | --- | --- |
| What decides the path? | Destination CIDR | Attributes → which route table, then destination CIDR |
| Same IP, ports 443 vs 80 | Same path | Can diverge (this lab: 443 via Hub, 80 Direct) |
| Unmatched policy traffic | N/A | Dropped (implicit deny) |

{: .finding }
> Live confirmation in the lab: removing catch-all rule 200 (leaving only TCP/443 → Steer)
> makes `:80` and ICMP fail. Restoring rule 200 restores them. Catch-all is not optional.

## Apply

```bash
git clone https://github.com/jajera/tgw-policy-based-routing.git
cd tgw-policy-based-routing
terraform init
terraform apply -auto-approve
```

The default apply includes attachment settle waits (`time_sleep`) to reduce first-apply
races. If your environment is still flaky:

```bash
bash scripts/apply-staged.sh
```

That runs TGW share + attachments + settle timers, full apply convergence, then a plan
check expecting no changes.

Refresh live IDs/IPs after apply:

```bash
terraform output
terraform output -raw prove_commands
```

{: .tip }
> Instance IDs and private IPs change every apply. Prefer `terraform output -raw prove_commands`
> over copying stale IDs from older docs. Stable CIDRs are Hub `10.0.0.0/24`, Spoke A
> `10.0.1.0/24`, Spoke B `10.0.2.0/24`.

Wait until Spoke A SSM is **Online** before proving. If it stays offline for many minutes,
reboot Spoke A once and re-check.

## Prove checklist

Both Spoke B curls use the **same private IP** so destination IP alone cannot explain the
path split. Internet checks prove spokes reach the public network **only through Hub NAT**.

| # | Check | Path under PBR | Expect |
| :---: | --- | --- | --- |
| 1 | SSM to Spoke A | Hub NAT (SSM APIs use TCP/443 → steered) | `PingStatus=Online` / session opens |
| 2 | Internet HTTPS from Spoke A | Rule 100 → Steer → Hub → NAT | HTTP 200 |
| 3 | Internet HTTP from Spoke A | Catch-all → Direct → Hub → NAT | HTTP 200 |
| 4 | Ping Spoke B / Hub / `8.8.8.8` from Spoke A | Catch-all (ICMP) → Direct → … | Replies |
| 5 | Curl Hub `:80` from Spoke A | Catch-all → Direct → Hub | `tgw-pbr-hub-ok` |
| 6 | Spoke A → Spoke B `:443` | Rule 100 → Steer → Hub hairpin | `tgw-pbr-spoke-b-ok` |
| 7 | Spoke A → Spoke B `:80` | Catch-all → Direct | `tgw-pbr-spoke-b-ok` |
| 8 | Spoke B → A / Hub / internet | Spoke B on Direct | Ping A/Hub; Hub ok; internet 200 |
| 9 | Hub → A / B ping + curl B | Hub RT | Ping A/B; B `:80`/`:443` ok |
| 10 | Hub flow logs (~10 min later) | — | Spoke-to-spoke **443** on Hub TGW path; **80** absent there |

### Example prove commands

Substitute IDs from `terraform output`. Profiles: `sandbox` / `shared-services` / `network`.

```bash
# Spoke A — SSM + curls (replace INSTANCE_A and SPOKE_B_IP / HUB_IP)
aws ssm start-session --target INSTANCE_A \
  --region ap-southeast-2 --profile sandbox

# Inside Spoke A:
curl --max-time 8 -sS -o /dev/null -w "internet_443:%{http_code}\n" https://example.com/
curl --max-time 8 -sS -o /dev/null -w "internet_80:%{http_code}\n" http://example.com/
ping -c 3 -W 2 SPOKE_B_IP
ping -c 3 -W 2 HUB_IP
ping -c 3 -W 2 8.8.8.8
curl --max-time 5 http://HUB_IP:80/
curl --max-time 5 -k https://SPOKE_B_IP:443/
curl --max-time 5 http://SPOKE_B_IP:80/
```

### Observability (Hub VPC flow logs)

```bash
aws logs filter-log-events \
  --log-group-name /tgw-pbr-demo/hub-flow-logs \
  --filter-pattern "SPOKE_B_IP_OR_TGW_ENI" \
  --region ap-southeast-2 \
  --profile network
```

Expect ~**10 minutes** delay before concluding a port did not appear. Spoke-to-spoke
**dstport=443** should appear on the Hub TGW ENI path; spoke-to-spoke **dstport=80** should
be **absent** there (Direct skips Hub). NAT/SSM `:443` on the NAT ENI is normal Hub egress —
do not confuse it with the PBR steer signal.

## Destroy

```bash
terraform destroy -auto-approve
terraform state list   # expect empty
```

{: .warning }
> If destroy stalls, check leftover TGW attachments, NAT/EIP, and EC2 in all three accounts
> — those continue to bill. Spot-check the flow-log group:

```bash
aws logs describe-log-groups --profile network --region ap-southeast-2 \
  --log-group-name-prefix /tgw-pbr-demo \
  --query 'logGroups[].logGroupName' --output text
```

## Limits (AWS)

| Quota | Default | Adjustable |
| --- | :---: | :---: |
| Policy tables per Transit Gateway | 20 | No |
| Customer-managed policy table entries per Transit Gateway | 200 | Yes |

## Scope

This page covers the Policy_Table forwarding decision and the three-account hub-and-spoke
lab. It is not a Landing Zone, Control Tower, or general Transit Gateway catalog. Concept
pages for match criteria and other use cases:
[Policy tables]({{ site.baseurl }}/policy-tables/),
[Use cases]({{ site.baseurl }}/use-cases/).

[Next: Troubleshooting →]({{ site.baseurl }}/troubleshooting/){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 }
