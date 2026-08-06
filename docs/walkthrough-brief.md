# Authoring brief (excluded from Jekyll build)

Internal notes for maintainers of this walkthrough site.

## Relationship

- **Lab (Terraform):** https://github.com/jajera/tgw-policy-based-routing
- **This repo:** published Pages walkthrough + concept docs only

Keep topology, profiles (`network` / `sandbox` / `shared-services`), CIDRs
(`10.0.0.0/24`, `10.0.1.0/24`, `10.0.2.0/24`), and prove semantics aligned with the lab
README and `docs/walkthrough.md` there. Prefer `terraform output` over committing
ephemeral IDs.

## Site shell

Parity with `jajera/privatelink-conduit`: hero, path/nav grids, callouts, theme toggle,
`pbr` / `pbr-dark` schemes.
