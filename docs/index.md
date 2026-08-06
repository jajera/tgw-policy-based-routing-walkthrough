---
title: Overview
layout: default
nav_order: 1
description: >-
  Walkthrough for the jajera/tgw-policy-based-routing lab — destination-only
  Transit Gateway routing versus Policy-Based Routing with a runnable demo.
---

<div class="pbr-hero">
  <p class="pbr-kicker">jajera · tgw-policy-based-routing-walkthrough</p>
  <h1>TGW Policy-Based Routing</h1>
  <p class="pbr-lede">
    Published walkthrough for the
    <a href="https://github.com/jajera/tgw-policy-based-routing"><code>jajera/tgw-policy-based-routing</code></a>
    lab — a three-account hub-and-spoke demo that proves destination-only Transit Gateway
    routing versus Policy-Based Routing (same Spoke B IP, TCP/443 via Hub, TCP/80 direct).
  </p>
  <div class="pbr-actions">
    <a class="pbr-btn pbr-btn--primary" href="{{ site.baseurl }}/walkthrough/">Deploy and prove</a>
    <a class="pbr-btn pbr-btn--ghost" href="https://github.com/jajera/tgw-policy-based-routing">Lab repository</a>
  </div>
</div>

## Three accounts

<div class="path-grid">
  <a class="path-card" href="{{ site.baseurl }}/architecture/">
    <span class="path-card__label">Network</span>
    <strong>Hub + TGW + NAT</strong>
    <p>Owns the Transit Gateway, Hub VPC, internet egress, and the optional Hub forwarder.</p>
    <span class="path-card__meta">CLI profile <code>network</code></span>
  </a>
  <a class="path-card" href="{{ site.baseurl }}/architecture/">
    <span class="path-card__label">Sandbox</span>
    <strong>Spoke A client</strong>
    <p>Client VPC with the <strong>policy table</strong> on its TGW attachment — where PBR decides the path.</p>
    <span class="path-card__meta">CLI profile <code>sandbox</code></span>
  </a>
  <a class="path-card" href="{{ site.baseurl }}/architecture/">
    <span class="path-card__label">Shared services</span>
    <strong>Spoke B listener</strong>
    <p>HTTP <code>:80</code> / HTTPS <code>:443</code> on one private IP — destination IP alone cannot explain the split.</p>
    <span class="path-card__meta">CLI profile <code>shared-services</code></span>
  </a>
</div>

## What this covers

**The pattern.** Classic transit gateway route tables forward by destination prefix only.
A **policy table** evaluates an ordered rule set (source/destination CIDR, protocol, ports)
and selects a target route table — first match wins; no match is implicit deny. Destination
routing still runs inside the table PBR selects.

**The lab.** Terraform in
[`jajera/tgw-policy-based-routing`](https://github.com/jajera/tgw-policy-based-routing)
provisions the topology. This site is the operator walkthrough and concept docs — clone and
apply the lab, then follow [Deploy and prove]({{ site.baseurl }}/walkthrough/).

{: .finding }
> Lab rule **100** matches destination TCP/443 → Steer via Hub. Rule **200** is a catch-all →
> Direct. Without the catch-all, `:80` and ICMP drop (implicit deny).

## Read in this order

<div class="nav-grid">
  <a class="nav-card" href="{{ site.baseurl }}/architecture/">
    <strong>1. Architecture</strong>
    <span>Hub, spokes, policy vs route tables, path map</span>
  </a>
  <a class="nav-card" href="{{ site.baseurl }}/policy-tables/">
    <strong>2. Policy tables</strong>
    <span>Match criteria, evaluation order, system vs customer entries</span>
  </a>
  <a class="nav-card" href="{{ site.baseurl }}/use-cases/">
    <strong>3. Use cases</strong>
    <span>Path selection (this lab), inspection, isolation</span>
  </a>
  <a class="nav-card" href="{{ site.baseurl }}/walkthrough/">
    <strong>4. Deploy and prove</strong>
    <span>Apply the lab, prove the path split, tear down</span>
  </a>
  <a class="nav-card" href="{{ site.baseurl }}/troubleshooting/">
    <strong>Troubleshooting</strong>
    <span>Failure modes, metrics, and fixes</span>
  </a>
  <a class="nav-card" href="{{ site.baseurl }}/reference/">
    <strong>Reference</strong>
    <span>CLI commands ↔ EC2 API actions</span>
  </a>
</div>

{: .note }
> Last verified against AWS Transit Gateway documentation on **2026-08-06**. Feature
> availability, limits, and behaviour can change — check current AWS docs before relying
> on any claim here.

## Prerequisites in brief

- Terraform >= 1.6 and AWS provider >= 5.0 (in the [lab repo](https://github.com/jajera/tgw-policy-based-routing))
- Profiles `network`, `sandbox`, and `shared-services` (three distinct accounts)
- Session Manager plugin
- Region examples: `ap-southeast-2`

Full detail in the [walkthrough]({{ site.baseurl }}/walkthrough/).

{: .cost }
> The lab is **billable while running**: TGW attachments, NAT, EC2, flow logs. Follow
> teardown in the walkthrough; confirm `terraform state list` is empty.

---

[Next: Architecture →]({{ site.baseurl }}/architecture/){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 }
