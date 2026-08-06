# Implementation Plan: Documentation Site for TGW Policy-Based Routing

## Overview

This plan delivers a GitHub Pages walkthrough site (Jekyll + just-the-docs) for the
`jajera/tgw-policy-based-routing` lab. Terraform stays in the lab repository; this repo ships
docs and CI only.
custom `pbr` / `pbr-dark` colour schemes, static SVG diagrams, Docker Compose local preview
with Bundler fallback, and CI via `actionsforge/actions` reusable workflows. Tasks are
sequenced so scaffolding and configuration come first, then theme/styling, then diagrams and
content pages, then preview/CI and root README. Each checkpoint validates a buildable slice
before more work lands.

## Tasks

- [x] 1. Repository scaffolding and Jekyll configuration
  - [x] 1.1 Create root `.gitignore` and `docs/.gitignore`
    - Root `.gitignore` excludes `docs/_site/`, `docs/.jekyll-cache/`, `docs/.jekyll-metadata`, `docs/vendor/`
    - `docs/.gitignore` excludes `_site/`, `.jekyll-cache/`, `.jekyll-metadata`, `.sass-cache/`, `vendor/`
    - Confirm the tree contains zero IaC fingerprints (`.tf`, `.tf.json`, `.tfvars`, CloudFormation templates, `cdk.json` / `cdk.context.json`)
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 1.2 Create `docs/Gemfile` and commit `docs/Gemfile.lock`
    - Include `jekyll ~> 4.3`, `just-the-docs 0.12.0`, `jekyll-sass-converter ~> 3.1`, `jekyll-seo-tag ~> 2.8`, `jekyll-include-cache ~> 0.2`, `webrick ~> 1.9`
    - Run `bundle lock` (or `bundle install`) in `docs/` and commit the resolved `Gemfile.lock`
    - _Requirements: 3.1, 4.6_

  - [x] 1.3 Create `docs/_config.yml`
    - Set title `TGW Policy-Based Routing`, description naming policy tables, `theme: just-the-docs`, `url` / `baseurl`, `permalink: pretty`, `heading_anchors`, `back_to_top`, `aux_links` (GitHub), `color_scheme: pbr`, `favicon_ico`, defaults `image` for OG, `twitter.card`, sass `quiet_deps` / `silence_deprecations`, search, `callouts_level: loud`
    - Callouts: `finding` (green), `note` (blue), `tip` (purple), `warning` (yellow), `blocked` (red), `cost` (red) — parity with Reference_Repository
    - Footer stating docs-only scope and that AWS behaviour can change
    - Plugins: `jekyll-seo-tag`, `jekyll-include-cache`
    - Exclude: `Gemfile`, `Gemfile.lock`, `vendor/`, `README.md`, `walkthrough-brief.md`, `docker-compose.yml`, `scripts/`, `diagrams/`
    - _Requirements: 3.1, 3.6, 3.7, 3.8, 3.10, 3.11, 5.6, 12.2_

- [x] 2. Custom colour schemes and stylesheets
  - [x] 2.1 Create `docs/_sass/color_schemes/pbr.scss` (light scheme)
    - Define palette variables adapted from Reference_Repository; set font families (Sora, Source Sans 3, IBM Plex Mono)
    - _Requirements: 3.2_

  - [x] 2.2 Create `docs/_sass/color_schemes/pbr-dark.scss` (dark scheme)
    - Define dark palette variables; do NOT `@import` theme `dark.scss`; import accessible-pygments github-dark; set `$color-scheme: dark`
    - _Requirements: 3.2_

  - [x] 2.3 Create stylesheet entry points under `docs/assets/css/`
    - `just-the-docs-pbr.scss` with front matter and liquid include for `pbr` scheme
    - `just-the-docs-pbr-dark.scss` with front matter and liquid include for `pbr-dark` scheme
    - _Requirements: 3.3_

  - [x] 2.4 Create `docs/_sass/custom/custom.scss`
    - Port Reference_Repository `custom.scss` with `conduit` → `pbr` rename (do not ship a minimal hero-only sheet)
    - Include tokens, page chrome, `.pbr-hero` / `.pbr-btn*`, `.path-grid` / `.path-card*`, `.nav-grid` / `.nav-card`, diagram classes, `.pbr-theme-toggle*`, `.pbr-nav-foot`
    - _Requirements: 3.5, 7.3_

- [x] 3. Theme toggle and include overrides
  - [x] 3.1 Create `docs/_includes/head_custom.html`
    - Google Fonts link tags (Sora, Source Sans 3, IBM Plex Mono)
    - Favicon link tags referencing `docs/assets/images/` files
    - Early theme stylesheet swap script reading `localStorage` key `tgw-pbr-docs-theme` (values `pbr` / `pbr-dark`); use `prefers-color-scheme` as fallback
    - _Requirements: 3.4, 3.9_

  - [x] 3.2 Create `docs/_includes/components/aux_nav.html`
    - Moon/sun toggle button calling `jtd.setTheme()` and persisting to `localStorage`
    - GitHub aux link matching `_config.yml` aux_links
    - Toggle button with accessible `aria-label` / `title` that updates with the active mode
    - _Requirements: 3.4_

  - [x] 3.3 Create `docs/_includes/header_custom.html` and `docs/_includes/nav_footer_custom.html`
    - `header_custom.html`: empty override for parity
    - `nav_footer_custom.html`: short brand line "TGW PBR docs"
    - _Requirements: 3.4_

- [x] 4. Asset files
  - [x] 4.1 Create placeholder image assets under `docs/assets/images/`
    - `favicon.ico`, `favicon-16.png`, `favicon-32.png`, `apple-touch-icon.png`, `icon-512.png`, `og-image.png`
    - _Requirements: 3.9_

- [x] 5. Checkpoint — Verify site shell builds
  - From `docs/`: `bundle exec jekyll build` succeeds with the configured `baseurl`
  - Confirm custom schemes compile and `_config.yml` exclude list omits authoring/tooling paths
  - Ask the user if questions arise

- [x] 6. SVG diagram system
  - [x] 6.1 Create `docs/scripts/generate-diagrams.py`
    - Python 3.8+ script using standard library only
    - Implements helper functions (`box()`, `arrow()`, SVG doc builder) with fixed coordinates
    - Generates four SVG files: `example-topology.svg`, `rule-evaluation.svg`, `inspection-steering.svg`, `troubleshooting-decision.svg`
    - Creates output directory `docs/_includes/diagrams/` if absent
    - Deterministic output: no timestamps, no UUIDs, stable attribute order
    - Each SVG has `<title>`, `<desc>`, `role="img"`, `aria-label`; elements use CSS classes (`diagram-node`, `diagram-text`, etc.)
    - Run the script once and commit the generated SVGs
    - _Requirements: 7.1, 7.3, 7.4, 7.5, 7.6_

  - [x] 6.2 Create `docs/diagrams/README.md`
    - Document the regeneration command (`python3 docs/scripts/generate-diagrams.py`)
    - State prerequisites (Python 3.8+, no third-party packages)
    - List the four output SVG files and their usage locations
    - _Requirements: 7.7_

  - [x] 6.3 Checkpoint — Diagram idempotency
    - Run the generator twice; `diff` the SVG outputs and expect no differences
    - _Requirements: 7.6_

- [x] 7. Documentation pages (Page Set)
  - [x] 7.1 Create `docs/index.md` (Overview)
    - Front matter: `layout: default`, `title: Overview`, `nav_order: 1`
    - Match Reference_Repository Overview shell: `.pbr-hero` (kicker, brand h1, lede, two CTAs), `.path-grid` three-use cards, "What this covers" + `finding` callout, `.nav-grid` reading-order cards, currency `note`, non-goals, `cost` callout
    - Must NOT describe the repo as a deployable multi-account lab
    - _Requirements: 3.5, 6.1, 6.2, 6.10, 12.3, 12.4_

  - [x] 7.2 Create `docs/architecture.md`
    - Front matter: `layout: default`, `title: Architecture`, `nav_order: 2`
    - Example topology description (VPCs, TGW, Attachments, Route_Tables, Policy_Tables)
    - Comparison: destination-based Route_Table forwarding vs attribute-based Policy_Table forwarding
    - Include `example-topology.svg` via `{% include %}` (not `<img>`) with adjacent text description
    - "Next" link to Policy Tables
    - _Requirements: 6.3, 7.2, 7.4, 7.8_

  - [x] 7.3 Create `docs/policy-tables.md`
    - Front matter: `layout: default`, `title: Policy Tables`, `nav_order: 3`
    - Match criteria, evaluation order (system-managed → customer-managed ascending → implicit deny)
    - Customer-managed vs system-managed entries, rule number range (1–50,000), omitted fields default to Any
    - Protocol/port behaviour, non-consecutive / most-specific-first / catch-all recommendations
    - Limitations: Cloud WAN peering (system-managed only), BGP withholding for VPN/Connect, DX allowed-prefixes continue
    - Attachment exclusivity (Policy_Table XOR Route_Table); PBR availability and pricing note
    - Include `rule-evaluation.svg` with adjacent text description
    - Every AWS behavioural claim linked to AWS documentation
    - "Next" link to Use Cases
    - _Requirements: 6.4, 6.9, 7.2, 7.4, 7.8, 8.1–8.12, 9.1, 9.2, 9.3_

  - [x] 7.4 Create `docs/use-cases.md`
    - Front matter: `layout: default`, `title: Use Cases`, `nav_order: 4`
    - Inspection steering (primary), path selection (DX/VPN), routing-domain isolation
    - For each: condition when Policy_Table is preferable to Route_Table
    - Restate BGP advertisement limitation alongside VPN path selection use case
    - Include `inspection-steering.svg` with adjacent text description
    - "Next" link to Walkthrough
    - _Requirements: 6.5, 6.9, 7.2, 7.4, 7.8, 9.4_

  - [x] 7.5 Create `docs/walkthrough.md`
    - Front matter: `layout: default`, `title: Walkthrough`, `nav_order: 5`
    - Prerequisites: existing TGW, target Route_Tables, disassociate-before-associate, IAM actions, region `ap-southeast-2`, `cost` callout for TGW charges
    - Numbered steps: create Policy_Table, create entries (sensitive → inspection RT, catch-all → default RT, non-consecutive rule numbers), associate, inspect entries, verify
    - Verification step after each state-changing CLI command
    - Teardown section removing created resources and restoring prior Route_Table association if documented
    - EXAMPLE suffixes, RFC 1918 CIDRs, no Terraform/CDK/CFN instructions
    - Console alternatives as navigation paths (no screenshots)
    - "Next" link to Troubleshooting
    - _Requirements: 6.9, 7.2, 10.1–10.10_

  - [x] 7.6 Create `docs/troubleshooting.md`
    - Front matter: `layout: default`, `title: Troubleshooting`, `nav_order: 6`
    - Document each failure mode from Requirement 9: `PacketDropCountNoPolicy`, empty policy table drops, Route_Table disassociation required, target RT deletion blocked, port range validation error, rule shadowing, `GetTransitGatewayPolicyTableEntries`
    - Each with symptom, diagnostic step, resolution
    - Include `troubleshooting-decision.svg` with adjacent text description
    - "Next" link to Reference
    - _Requirements: 6.6, 6.9, 7.2, 7.4, 7.8, 9.5–9.11_

  - [x] 7.7 Create `docs/reference.md`
    - Front matter: `layout: default`, `title: Reference`, `nav_order: 7`
    - Table mapping PBR operations to AWS CLI commands and EC2 API actions
    - Links to AWS documentation for each operation
    - Prefer callouts over raw HTML; "Next" link back to Overview
    - _Requirements: 6.7, 6.8, 6.9, 7.2_

- [x] 8. Checkpoint — Verify pages build and render
  - `bundle exec jekyll build` succeeds; every Page_Set page has `nav_order` and a Next link
  - Diagrams appear via include (not `<img>`); spot-check light/dark colours in local preview if available
  - Ask the user if questions arise

- [x] 9. Local preview infrastructure
  - [x] 9.1 Create `docs/docker-compose.yml`
    - Service name `docs`, image `ruby:3.3-bookworm`, ports `4000` and `35729`, bind-mount `.` → `/srv/jekyll`, named volume `docs_bundle` for gems
    - Command: `bundle install` then `bundle exec jekyll serve --host 0.0.0.0 --livereload --force_polling --watch`
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 9.2 Create `scripts/docs-serve.sh`
    - Prefer Docker Compose (`docker compose -f docs/docker-compose.yml up`); else host Bundler (`cd docs && bundle exec jekyll serve --livereload --watch`); else print both prerequisites and exit 1
    - Print preview URL `http://127.0.0.1:4000/tgw-policy-based-routing-walkthrough/`
    - Make executable (`chmod +x`)
    - _Requirements: 4.1, 4.2, 4.4, 4.5_

- [x] 10. CI workflows and repository hygiene
  - [x] 10.1 Create `.github/workflows/docs.yml`
    - Triggers: push to `main` (paths `docs/**`, `.github/workflows/docs.yml`), pull_request (same paths), `workflow_dispatch`
    - Permissions: `contents: read`, `pages: write`, `id-token: write`
    - Concurrency group `pages-${{ github.ref }}` with `cancel-in-progress: false`
    - Call `actionsforge/actions/.github/workflows/jekyll-pages-deploy.yml@main` with `source: docs`, `destination: docs/_site`, `ruby-version: "3.4"`
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 10.2 Create `.github/workflows/markdown-lint.yml`
    - Trigger: pull_request
    - Permissions: statuses write, checks write, contents read, pull-requests read
    - Call `actionsforge/actions/.github/workflows/markdown-lint.yml@main`
    - _Requirements: 11.1, 11.2_

  - [x] 10.3 Create `.github/workflows/commitmsg-conform.yml`
    - Trigger: pull_request
    - Permissions: statuses write, checks write, contents read, pull-requests read
    - Call `actionsforge/actions/.github/workflows/commitmsg-conform.yml@main`
    - _Requirements: 11.3, 11.4_

  - [x] 10.4 Create `.github/dependabot.yml`
    - GitHub Actions ecosystem at `/` (weekly) and Bundler at `/docs` (weekly)
    - Commit message prefix `chore` with scope; no Terraform ecosystem entries
    - _Requirements: 11.6_

  - [x] 10.5 Create `.markdownlint.yml` at repository root
    - Record rule exemptions needed by Page_Set (e.g. MD013 for long CLI commands/URLs; avoid MD033 by preferring callouts)
    - _Requirements: 11.5_

- [x] 11. Authoring brief and root README
  - [x] 11.1 Create `docs/walkthrough-brief.md`
    - Internal authoring notes: rule numbers, EXAMPLE IDs, teardown order, required status-check setup for maintainers
    - Verify it is listed in `_config.yml` exclude
    - _Requirements: 12.1, 12.2, 11.7_

  - [x] 11.2 Rewrite root `README.md`
    - First paragraph: walkthrough for lab repo; no Terraform in this repo
    - Link to lab `https://github.com/jajera/tgw-policy-based-routing`
    - ≤ 5-sentence PBR summary
    - Link to `https://jajera.github.io/tgw-policy-based-routing-walkthrough/`
    - Table of Page_Set pages with descriptions and published URLs
    - Local preview command (`./scripts/docs-serve.sh`)
    - Note that Markdown lint and commit-conform checks must be required status checks on `main`
    - ≤ 200 lines; must NOT describe repo as deployable lab/sandbox/Terraform project
    - _Requirements: 2.1–2.7, 11.7_

- [x] 12. Final checkpoint — Verify complete delivery
  - Jekyll build succeeds; preview script prints the baseurl URL
  - Repo shape check: zero IaC fingerprint files
  - Diagram generator idempotency re-check
  - Confirm `.kiro/specs/` retained; Authoring_Brief excluded from published output
  - Ask the user if questions arise
  - _Requirements: 1.2, 7.6, 12.2, 12.6_

## Notes

- No property-based tests: declarative config, static content, and deterministic scripts only.
- Each task references requirements for traceability.
- Checkpoints gate shell → pages → full delivery.
- Run the diagram generator (task 6.1) before page tasks that include SVGs (section 7).
- Commit `docs/Gemfile.lock` with the Gemfile (task 1.2).
- Prefer just-the-docs callouts (`finding`, `note`, `tip`, `warning`, `blocked`, `cost`) over raw HTML in Page_Set content.
- Overview and `custom.scss` must stay visually aligned with [privatelink-conduit](https://jajera.github.io/privatelink-conduit/) (rename-only port).
- Reproduce only the AWS doc excerpts needed for explanation; always link the source (Requirement 12.5).
- `.kiro/hooks/` markdown formatters are contributor tooling for specs; they are not Page_Set deliverables.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "4.1"] },
    { "id": 1, "tasks": ["1.3", "2.1", "2.2"] },
    { "id": 2, "tasks": ["2.3", "2.4"] },
    { "id": 3, "tasks": ["3.1", "3.2", "3.3"] },
    { "id": 4, "tasks": ["5"] },
    { "id": 5, "tasks": ["6.1", "6.2"] },
    { "id": 6, "tasks": ["6.3"] },
    { "id": 7, "tasks": ["7.1", "7.2", "7.3", "7.4", "7.5", "7.6", "7.7"] },
    { "id": 8, "tasks": ["8"] },
    { "id": 9, "tasks": ["9.1", "9.2", "10.1", "10.2", "10.3", "10.4", "10.5"] },
    { "id": 10, "tasks": ["11.1", "11.2"] },
    { "id": 11, "tasks": ["12"] }
  ]
}
```
