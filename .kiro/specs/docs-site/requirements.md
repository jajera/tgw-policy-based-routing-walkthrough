# Requirements Document

## Introduction

This feature delivers a GitHub Pages walkthrough site for the
`jajera/tgw-policy-based-routing-walkthrough` repository. The site is the published operator
guide and concept docs for the runnable lab
[`jajera/tgw-policy-based-routing`](https://github.com/jajera/tgw-policy-based-routing): a
three-account hub-and-spoke demo that proves destination-only Transit Gateway routing versus
Policy-Based Routing (same Spoke B IP; TCP/443 via Hub; TCP/80 Direct).

This repository contains documentation sources and CI configuration only. It provisions no AWS
infrastructure and ships no Infrastructure-as-Code — Terraform lives in the lab repository.
The site shell (Jekyll + just-the-docs, custom light/dark colour schemes, Docker-based local
preview with Bundler fallback, static SVG diagram pipeline) and the CI workflow set are
adapted from the reference repository `jajera/privatelink-conduit` and rebranded for the
Transit Gateway PBR topic.

The intended audience is platform and network engineers who already understand Amazon VPC and
classic transit gateway route tables, and who will apply the lab with Terraform.

All statements about AWS behaviour in this document were verified against the AWS Transit
Gateway documentation for policy-based routing (`tgw-policy-tables*` pages in the Amazon VPC
Transit Gateways guide) on 2026-08-06.

### Confirmed Decisions

1. **Demo depth**: `walkthrough.md` is the operator runbook for the lab repository (apply,
   prove, destroy); concept pages cover policy-table mechanics.
2. **Primary topology story**: the lab’s path-selection pattern (TCP/443 via Hub vs Direct)
   is primary; inspection steering and segmentation are secondary conceptual use cases.
3. **Region**: examples use `ap-southeast-2`.
4. **Colour schemes**: custom just-the-docs schemes are named `pbr` (light) and `pbr-dark`.
5. **Local preview**: Docker Compose is preferred; host Ruby + Bundler is an allowed fallback
   when Docker is unavailable (parity with the Reference_Repository).
6. **Spec artifacts**: formal requirements under `.kiro/specs/` remain in the Repository; there
   is no separate root-level `kiro-spec-brief.md`.
7. **Dependabot scope**: update checks cover GitHub Actions and Bundler only (no Terraform
   ecosystem entries).

## Glossary

- **Repository**: The Git repository `jajera/tgw-policy-based-routing-walkthrough`, including all
  tracked files at every path.
- **Docs_Site**: The Jekyll site whose sources live under the `docs/` directory of the Repository
  and whose built output is published to GitHub Pages.
- **Root_README**: The file `README.md` at the root of the Repository.
- **Jekyll_Build**: The Jekyll build process that transforms `docs/` sources into the static
  Docs_Site output, configured by `docs/_config.yml`.
- **Preview_Script**: The shell script at `scripts/docs-serve.sh` that starts a local Docs_Site
  preview, preferring Docker Compose and falling back to host Bundler when Docker is unavailable.
- **Pages_Deploy_Workflow**: The GitHub Actions workflow at `.github/workflows/docs.yml` that
  calls the `actionsforge` `jekyll-pages-deploy@main` reusable workflow.
- **Markdown_Lint_Workflow**: The GitHub Actions workflow at `.github/workflows/markdown-lint.yml`
  that calls the `actionsforge` `markdown-lint@main` reusable workflow.
- **Commit_Conform_Workflow**: The GitHub Actions workflow at
  `.github/workflows/commitmsg-conform.yml` that calls the `actionsforge`
  `commitmsg-conform@main` reusable workflow.
- **Diagram_Generator**: The script at `docs/scripts/generate-diagrams.py` that emits the static
  SVG diagram files under `docs/_includes/diagrams/`.
- **Page_Set**: The seven published Markdown pages of the Docs_Site: `index.md`,
  `architecture.md`, `policy-tables.md`, `use-cases.md`, `walkthrough.md`, `troubleshooting.md`,
  and `reference.md`, all located directly under `docs/`.
- **Overview_Page**: The page `docs/index.md`.
- **Architecture_Page**: The page `docs/architecture.md`.
- **Policy_Tables_Page**: The page `docs/policy-tables.md`.
- **Use_Cases_Page**: The page `docs/use-cases.md`.
- **Walkthrough_Page**: The page `docs/walkthrough.md`.
- **Troubleshooting_Page**: The page `docs/troubleshooting.md`.
- **Reference_Page**: The page `docs/reference.md`.
- **Authoring_Brief**: The file `docs/walkthrough-brief.md`, an internal authoring note that is
  tracked in the Repository but excluded from Jekyll_Build output.
- **PBR**: Policy-Based Routing for AWS Transit Gateway — rule-based forwarding across a transit
  gateway using packet attributes rather than destination IP address alone.
- **Policy_Table**: A transit gateway policy table — an ordered set of rules, each of which
  specifies match criteria and a target transit gateway route table.
- **Policy_Table_Entry**: A single rule within a Policy_Table, identified by a rule number and
  classified as either customer-managed or system-managed.
- **Route_Table**: A classic transit gateway route table, which forwards traffic by destination
  IP address lookup.
- **Attachment**: A transit gateway attachment. Customer-managed PBR is compatible with VPC,
  Direct Connect, Site-to-Site VPN, Client VPN, VPN Concentrator, Network Functions, Connect,
  and peering Attachments, except transit gateway-to-Cloud WAN peering Attachments (see
  Requirement 9).
- **Reference_Repository**: The repository `jajera/privatelink-conduit`, the source of the
  Docs_Site shell, theme, CI, and authoring patterns.
- **Contributor**: A person making changes to files in the Repository.
- **Reader**: A platform or network engineer consuming the published Docs_Site.

## Requirements

### Requirement 1: Documentation-Only Repository Shape

**User Story:** As a Reader, I want the repository to contain documentation and CI only, so that I
understand this is a learning resource and never expect to provision billable AWS resources from
it.

#### Acceptance Criteria

1. THE Repository SHALL restrict its tracked content to documentation sources under `docs/`,
   contributor tooling under `scripts/`, CI configuration under `.github/`, spec artifacts under
   `.kiro/`, and root-level `README.md`, `LICENSE`, `.gitignore`, and Markdown lint configuration
   files.
2. WHEN a Contributor inspects the Repository file tree, THE Repository SHALL present a count of
   zero for files that declare AWS infrastructure resources, where such files are identified by
   the extensions `.tf`, `.tf.json`, and `.tfvars`, by CloudFormation template files
   (`template.yaml`, `template.yml`, `*.cfn.yaml`, `*.cfn.yml`, `*.cfn.json`), and by AWS CDK
   project manifests (`cdk.json`, `cdk.context.json`).
3. THE Repository SHALL include a root `.gitignore` entry set that excludes the Jekyll build
   artifact paths `docs/_site/`, `docs/.jekyll-cache/`, `docs/.jekyll-metadata`, and
   `docs/vendor/` from version control, independently of what other content the Repository holds.
4. THE Repository SHALL include `docs/.gitignore` excluding local Jekyll and Bundler artifact
   paths (`_site/`, `.jekyll-cache/`, `.jekyll-metadata`, `.sass-cache/`, `vendor/`) so that
   preview runs inside `docs/` cannot accidentally stage build output.

### Requirement 2: Root README as Site Pointer

**User Story:** As a Reader arriving from GitHub search, I want the root README to orient me in
under a minute and send me to the published site, so that I read long-form content in its intended
presentation.

#### Acceptance Criteria

1. THE Root_README SHALL state in its first paragraph that this Repository publishes the
   walkthrough site for the lab repository `jajera/tgw-policy-based-routing`, and that Terraform
   lives in that lab repository (this Repository provisions no AWS resources).
2. THE Root_README SHALL summarize what the lab proves (destination-only versus PBR path split) in
   5 sentences or fewer.
3. THE Root_README SHALL include a link to `https://jajera.github.io/tgw-policy-based-routing-walkthrough/`.
4. THE Root_README SHALL include a link to `https://github.com/jajera/tgw-policy-based-routing`.
5. THE Root_README SHALL list each page of the Page_Set with a one-line description and a link to
   the corresponding published URL.
6. THE Root_README SHALL contain the local preview command that invokes the Preview_Script.
7. THE Root_README SHALL limit its total length to 200 lines.
8. THE Root_README SHALL NOT claim that this Repository itself contains Terraform or deploys the
   lab; deploy instructions SHALL point at the lab repository.

### Requirement 3: Site Shell and Theme Parity with the Reference Repository

**User Story:** As a Reader, I want the site to present the same navigation, typography, and
light/dark behaviour as the Reference_Repository site, so that the reading experience is familiar
and legible in either colour mode.

#### Acceptance Criteria

1. THE Jekyll_Build SHALL use the `just-the-docs` theme as its remote theme or gem-based theme,
   sourced through `docs/Gemfile` and declared in `docs/_config.yml`.
2. THE Docs_Site SHALL define two custom just-the-docs colour schemes under
   `docs/_sass/color_schemes/` named `pbr` (light) and `pbr-dark`, whose palettes are adapted from
   the Reference_Repository schemes and rebranded for the Transit Gateway PBR topic.
3. THE Docs_Site SHALL expose each custom colour scheme through a corresponding stylesheet entry
   point under `docs/assets/css/` (`just-the-docs-pbr.scss` and `just-the-docs-pbr-dark.scss`).
4. WHEN a Reader activates the colour scheme toggle in the site header, THE Docs_Site SHALL switch
   between the light and dark colour schemes and persist the selection in `localStorage` so that
   the choice survives page navigations and browser sessions on the same origin.
5. THE Docs_Site SHALL render an Overview hero matching the Reference_Repository pattern:
   kicker, brand-level title, one lede, and two CTA buttons (primary and ghost), using the
   custom styles defined in `docs/_sass/custom/custom.scss` (ported from the Reference
   Repository with a `pbr-` class prefix).
6. THE Docs_Site SHALL provide callout styles for `finding`, `note`, `tip`, `warning`,
   `blocked`, and `cost` admonitions (parity with the Reference_Repository), and THE Page_Set
   SHALL use those callout styles for emphasis rather than raw HTML.
7. THE Docs_Site SHALL set `url` to `https://jajera.github.io` and `baseurl` to
   `/tgw-policy-based-routing-walkthrough` in `docs/_config.yml`.
8. THE Docs_Site SHALL set the `docs/_config.yml` title to `TGW Policy-Based Routing` and the
   description to a single sentence naming AWS Transit Gateway policy tables.
9. THE Docs_Site SHALL supply favicon, Apple touch icon, and Open Graph image assets under
   `docs/assets/images/`.
10. THE Jekyll_Build SHALL assign every page of the Page_Set an explicit `nav_order` value so that
    left-hand navigation order matches the reading order defined in Requirement 6.
11. THE Docs_Site SHALL enable site search and `jekyll-seo-tag` through `docs/_config.yml`, matching
    the Reference_Repository plugin set needed for navigation and sharing metadata.

### Requirement 4: Local Preview

**User Story:** As a Contributor, I want a one-command local preview, so that I can verify layout,
links, and diagrams before opening a pull request.

#### Acceptance Criteria

1. WHEN a Contributor runs the Preview_Script and Docker is available, THE Preview_Script SHALL
   start a Docker Compose service defined in `docs/docker-compose.yml` that serves the Docs_Site
   over HTTP on the local machine.
2. WHEN the Preview_Script serves the Docs_Site, THE Docs_Site SHALL be reachable at a local URL
   whose path prefix equals the configured `baseurl`.
3. WHILE the Preview_Script is running via Docker Compose or host Bundler with watch enabled, THE
   Jekyll_Build SHALL regenerate affected pages after a Contributor saves a change to any file
   under `docs/`.
4. IF Docker is unavailable and Ruby with Bundler is available on the Contributor machine, THEN
   THE Preview_Script SHALL start the Docs_Site using host Bundler (`bundle exec jekyll serve`)
   from `docs/` and emit the local preview URL.
5. IF neither Docker nor Ruby with Bundler is available, THEN THE Preview_Script SHALL emit a
   message naming both Docker and Ruby+Bundler as acceptable prerequisites and exit with a
   non-zero status code.
6. THE Repository SHALL pin the Jekyll and just-the-docs dependency versions in `docs/Gemfile` and
   commit the resolved `docs/Gemfile.lock`.

### Requirement 5: GitHub Pages Deployment

**User Story:** As a maintainer, I want documentation changes on the default branch to publish
automatically, so that the site never drifts from the repository.

#### Acceptance Criteria

1. WHEN a commit is pushed to the `main` branch and changes files under `docs/` or
   `.github/workflows/docs.yml`, THE Pages_Deploy_Workflow SHALL call the `actionsforge`
   `jekyll-pages-deploy@main` reusable workflow with the source directory set to `docs`.
2. THE Pages_Deploy_Workflow SHALL declare the `pages: write`, `id-token: write`, and
   `contents: read` permissions required by the GitHub Pages deployment.
3. WHEN a pull request targeting `main` changes any file under `docs/` or
   `.github/workflows/docs.yml`, THE Pages_Deploy_Workflow SHALL build the Docs_Site without
   publishing to GitHub Pages.
4. IF the Jekyll_Build fails, THEN THE Pages_Deploy_Workflow SHALL conclude with a failed status
   and retain the previously published Docs_Site.
5. IF the Pages_Deploy_Workflow completes a triggered run without executing the Jekyll_Build, THEN
   THE Pages_Deploy_Workflow SHALL conclude with a failed status.
6. WHEN the Jekyll_Build runs, THE Jekyll_Build SHALL exclude the Authoring_Brief,
   `docker-compose.yml`, `Gemfile`, `Gemfile.lock`, `vendor/`, `README.md`, `scripts/`, and
   `diagrams/` from the published output through the `exclude` list in `docs/_config.yml`.

### Requirement 6: Published Page Set and Reading Order

**User Story:** As a Reader new to PBR, I want a defined reading order from concepts through
configuration to troubleshooting, so that I can build understanding without jumping between pages.

#### Acceptance Criteria

1. THE Docs_Site SHALL publish exactly the seven pages of the Page_Set.
2. THE Overview_Page SHALL follow the Reference_Repository Overview composition: hero (kicker,
   brand title, lede, two CTAs), a three-card use-case grid (inspection steering, path selection,
   routing-domain isolation), a short "what this covers" section, a reading-order card grid for
   Architecture_Page, Policy_Tables_Page, Use_Cases_Page, Walkthrough_Page, Troubleshooting_Page,
   and Reference_Page, plus currency and non-goals sections.
3. THE Architecture_Page SHALL describe the example topology in terms of its VPCs, transit gateway,
   Attachments, Route_Tables, and Policy_Tables, and SHALL compare destination-based Route_Table
   forwarding against attribute-based Policy_Table forwarding.
4. THE Policy_Tables_Page SHALL document Policy_Table mechanics, covering match criteria, rule
   evaluation order, and the distinction between customer-managed and system-managed
   Policy_Table_Entry records.
5. THE Use_Cases_Page SHALL present inspection steering as the first use case, followed by path
   selection across Direct Connect and Site-to-Site VPN, followed by routing-domain isolation, and
   SHALL state for each use case the condition under which a Policy_Table is preferable to a
   Route_Table.
6. THE Troubleshooting_Page SHALL document each failure mode listed in Requirement 9 with its
   symptom, diagnostic step, and resolution.
7. THE Reference_Page SHALL map each PBR operation to its AWS CLI command and its corresponding
   EC2 API action, and SHALL link to the AWS documentation page for each operation.
8. THE Page_Set SHALL include at the end of each page a "Next" link that points to the following
   page in the reading order, and the Reference_Page SHALL instead link back to the Overview_Page.
9. THE Page_Set SHALL express every AWS behavioural claim with a link to the AWS documentation page
   that states the behaviour.
10. THE Page_Set SHALL include on the Overview_Page a statement that AWS feature availability,
    limits, and behaviour can change, together with the date on which the content was last verified
    against AWS documentation.

### Requirement 7: Diagrams

**User Story:** As a Reader, I want diagrams that stay legible in both colour schemes and stay in
sync with the prose, so that I can follow packet flow without decoding a screenshot.

#### Acceptance Criteria

1. THE Docs_Site SHALL store every diagram as a static SVG file under
   `docs/_includes/diagrams/`.
2. WHEN a page displays a diagram, THE Page_Set SHALL embed the SVG through a Jekyll `include`
   statement rather than an `img` element.
3. THE Docs_Site SHALL render each diagram using CSS custom properties for stroke, fill, and text
   colour so that the diagram adopts the colours of the active colour scheme.
4. THE Docs_Site SHALL provide diagrams for the example topology, Policy_Table rule evaluation
   order, the inspection steering traffic path, and the troubleshooting decision sequence.
5. WHEN a Contributor runs the Diagram_Generator, THE Diagram_Generator SHALL write every SVG file
   named in acceptance criterion 4 into `docs/_includes/diagrams/`.
6. WHEN the Diagram_Generator runs twice against an unchanged source definition, THE
   Diagram_Generator SHALL produce byte-identical SVG output on both runs.
7. THE Repository SHALL provide `docs/diagrams/README.md` describing the command that regenerates
   the diagrams and the prerequisites that command requires.
8. THE Page_Set SHALL provide a text description adjacent to each diagram that conveys the same
   information as the diagram for Readers using assistive technology.

### Requirement 8: Technical Accuracy — Policy Table Mechanics

**User Story:** As a network engineer, I want the mechanics described exactly as AWS documents
them, so that I can design against the site content with confidence.

#### Acceptance Criteria

1. THE Policy_Tables_Page SHALL state that a Policy_Table_Entry matches on source IP CIDR,
   destination IP CIDR, source port range, destination port range, and protocol.
2. THE Policy_Tables_Page SHALL state that an omitted match field defaults to Any.
3. THE Policy_Tables_Page SHALL state that each Policy_Table_Entry specifies a target transit
   gateway Route_Table to which matching traffic is forwarded.
4. THE Policy_Tables_Page SHALL state that customer-managed Policy_Table_Entry records are
   evaluated in ascending rule number order and that the first matching entry is applied and
   evaluation stops.
5. THE Policy_Tables_Page SHALL state that traffic matching no Policy_Table_Entry is dropped by
   implicit deny.
6. THE Policy_Tables_Page SHALL state that an Attachment associates with either a Policy_Table or
   a Route_Table, and that associating both with one Attachment is unsupported.
7. THE Policy_Tables_Page SHALL state that system-managed Policy_Table_Entry records are created
   by AWS, display a rule number of `*`, are read-only, and are evaluated before all
   customer-managed entries.
8. THE Policy_Tables_Page SHALL state that customer-managed rule numbers occupy the range 1 to
   50,000.
9. THE Policy_Tables_Page SHALL state that port range matching applies to protocol TCP (`6`) and
   protocol UDP (`17`), and that protocols ICMPv4 (`1`), GRE (`47`), and Any (`*`) resolve port
   ranges to Any.
10. THE Policy_Tables_Page SHALL recommend non-consecutive rule numbers, most-specific-rule-first
    ordering, and an explicit catch-all entry at a high rule number.
11. THE Policy_Tables_Page SHALL state that PBR is available in every AWS Region where transit
    gateway is available at no charge beyond standard transit gateway fees.
12. THE Policy_Tables_Page SHALL state that evaluation order is system-managed entries first, then
    customer-managed entries in ascending rule number order, then implicit deny.

### Requirement 9: Technical Accuracy — Limitations and Failure Modes

**User Story:** As a network engineer evaluating PBR for a production design, I want the documented
limitations stated up front, so that I avoid an outage caused by a surprise interaction.

#### Acceptance Criteria

1. THE Policy_Tables_Page SHALL state that transit gateway to AWS Cloud WAN peering Attachments do
   not support customer-managed Policy_Table_Entry records, and that traffic on those Attachments
   is controlled exclusively by system-managed entries.
2. THE Policy_Tables_Page SHALL state that a transit gateway withholds BGP route advertisements to
   Site-to-Site VPN and Connect Attachments that are associated with a Policy_Table.
3. THE Policy_Tables_Page SHALL state that Direct Connect advertisements to a customer gateway
   remain governed by the allowed-prefixes list on the Direct Connect gateway association and
   continue while a Policy_Table is associated.
4. WHERE the Use_Cases_Page presents path selection across Site-to-Site VPN, THE Use_Cases_Page
   SHALL restate the BGP advertisement limitation from acceptance criterion 2 alongside that use
   case.
5. THE Troubleshooting_Page SHALL document the `PacketDropCountNoPolicy` CloudWatch metric as the
   signal for traffic dropped by implicit deny.
6. THE Troubleshooting_Page SHALL document that an Attachment associated with an empty
   Policy_Table drops all ingressing packets.
7. THE Troubleshooting_Page SHALL document that associating a Policy_Table with an Attachment that
   already has a Route_Table association fails until the Route_Table is disassociated.
8. THE Troubleshooting_Page SHALL document that a Route_Table referenced as the target of a
   Policy_Table_Entry cannot be deleted until that entry is updated or deleted.
9. THE Troubleshooting_Page SHALL document that submitting a port range with a protocol other than
   TCP or UDP through the API returns a validation error.
10. THE Troubleshooting_Page SHALL document `GetTransitGatewayPolicyTableEntries` as the operation
    that reveals system-managed and customer-managed entries together with their evaluation order.
11. THE Troubleshooting_Page SHALL document unexpected rule matching caused by a broader
    customer-managed entry at a lower rule number shadowing a more specific entry at a higher
    rule number, and SHALL name reordering by ascending specificity as the resolution.

### Requirement 10: Walkthrough Content

**User Story:** As a network engineer, I want an operator runbook for the
`jajera/tgw-policy-based-routing` lab, so that I can apply it, prove destination-only versus PBR
path divergence, and tear it down safely.

#### Acceptance Criteria

1. THE Walkthrough_Page SHALL identify
   `https://github.com/jajera/tgw-policy-based-routing` as the lab repository to clone and apply.
2. THE Walkthrough_Page SHALL present apply, prove, and destroy guidance for the three-account
   hub-and-spoke lab (profiles `network`, `sandbox`, `shared-services`).
3. THE Walkthrough_Page SHALL explain the mental model: policy table selects a target route table;
   destination routing still runs inside that table; lab rules 100 (TCP/443 → Steer via Hub) and
   200 (catch-all → Direct).
4. THE Walkthrough_Page SHALL use `ap-southeast-2` as the AWS Region in examples.
5. THE Walkthrough_Page SHALL direct Readers to `terraform output` / `prove_commands` for live
   resource IDs rather than treating ephemeral IDs as permanent.
6. THE Walkthrough_Page SHALL NOT claim that Terraform lives in this Repository; all IaC commands
   SHALL target the lab repository working tree.
7. THE Walkthrough_Page SHALL include a prove checklist covering Spoke A → Spoke B `:443` vs `:80`,
   Hub hairpin evidence via flow logs, and Hub-only internet egress.
8. THE Walkthrough_Page SHALL provide destroy guidance and residual-cost warnings for leftover
   attachments, NAT, and EC2.
9. THE Walkthrough_Page SHALL state that the lab incurs billable AWS charges while running, using a
   `cost` callout.

### Requirement 11: Repository Hygiene Workflows

**User Story:** As a maintainer, I want lint and commit-message checks on every pull request, so
that documentation quality and commit history stay consistent without manual review.

#### Acceptance Criteria

1. WHEN a pull request is opened or updated, THE Markdown_Lint_Workflow SHALL call the
   `actionsforge` `markdown-lint@main` reusable workflow.
2. IF a Markdown file violates the configured lint rules, THEN THE Markdown_Lint_Workflow SHALL
   conclude with a failed status and report the file path and rule identifier for each violation.
3. WHEN a pull request is opened or updated, THE Commit_Conform_Workflow SHALL call the
   `actionsforge` `commitmsg-conform@main` reusable workflow.
4. IF a commit message in the pull request violates the configured convention, THEN THE
   Commit_Conform_Workflow SHALL conclude with a failed status and report the non-conforming
   commit.
5. THE Repository SHALL provide a Markdown lint configuration file at the Repository root that
   records every rule exemption the Page_Set relies upon.
6. THE Repository SHALL provide `.github/dependabot.yml` configuring weekly update checks for the
   GitHub Actions ecosystem at `/` and the Bundler ecosystem at `/docs`, and SHALL omit Terraform
   ecosystem entries.
7. THE Repository maintainer documentation in the Root_README or Authoring_Brief SHALL state that
   the Markdown_Lint_Workflow and Commit_Conform_Workflow status checks must be required on
   `main` so that a failed check blocks merge.

### Requirement 12: Authoring Notes and Scope Boundaries

**User Story:** As a Contributor, I want authoring notes kept out of the published site and the
project scope stated explicitly, so that internal drafts stay internal and contributions stay in
scope.

**Note:** Acceptance criterion 4 in this requirement is stated negatively because it records a
deliberate scope exclusion rather than system behaviour.

#### Acceptance Criteria

1. THE Repository SHALL track the Authoring_Brief at `docs/walkthrough-brief.md`.
2. WHEN the Jekyll_Build runs, THE Jekyll_Build SHALL omit the Authoring_Brief from the published
   output.
3. THE Overview_Page SHALL state prerequisites for running the lab (Terraform, three AWS profiles,
   Session Manager) and SHALL link to the lab repository.
4. THE Docs_Site SHALL describe this Repository as the published walkthrough for the lab
   repository and SHALL NOT claim that Terraform trees live in this Repository.
5. WHERE explaining a behaviour requires AWS documentation content, THE Docs_Site SHALL reproduce
   only the portion needed for that explanation and SHALL link to the AWS source page.
6. THE Repository SHALL retain formal spec artifacts under `.kiro/specs/`; removal after the first
   release SHALL remain a maintainer decision rather than an automated step.
