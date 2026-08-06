# TGW Policy-Based Routing Walkthrough

Published walkthrough and concept docs for the runnable lab
[`jajera/tgw-policy-based-routing`](https://github.com/jajera/tgw-policy-based-routing).

This repository hosts the GitHub Pages site only (Jekyll + just-the-docs). Terraform and
the three-account demo live in the lab repository — clone and apply that repo to
provision AWS resources.

## What the lab proves

AWS Transit Gateway Policy-Based Routing (PBR) sits in front of classic route tables.
On the Spoke A attachment, rule **100** steers destination TCP/443 via the Hub VPC while
rule **200** (catch-all) sends TCP/80 and other traffic Direct — **same Spoke B IP**,
different paths. Destination-based routing still runs inside the route table PBR selects.

## Published site

<https://jajera.github.io/tgw-policy-based-routing-walkthrough/>

| Page | Description |
| ---- | ----------- |
| [Overview](https://jajera.github.io/tgw-policy-based-routing-walkthrough/) | Lab framing and reading order |
| [Architecture](https://jajera.github.io/tgw-policy-based-routing-walkthrough/architecture/) | Hub/spoke topology and path map |
| [Policy Tables](https://jajera.github.io/tgw-policy-based-routing-walkthrough/policy-tables/) | Match criteria and evaluation order |
| [Use Cases](https://jajera.github.io/tgw-policy-based-routing-walkthrough/use-cases/) | Path selection, inspection, isolation |
| [Deploy and prove](https://jajera.github.io/tgw-policy-based-routing-walkthrough/walkthrough/) | Apply, prove, tear down |
| [Troubleshooting](https://jajera.github.io/tgw-policy-based-routing-walkthrough/troubleshooting/) | Failure modes and fixes |
| [Reference](https://jajera.github.io/tgw-policy-based-routing-walkthrough/reference/) | CLI ↔ EC2 API |

## Lab repository

Infrastructure and apply scripts:

- <https://github.com/jajera/tgw-policy-based-routing>

```bash
git clone https://github.com/jajera/tgw-policy-based-routing.git
cd tgw-policy-based-routing
terraform init
terraform apply -auto-approve
```

Then follow [Deploy and prove](https://jajera.github.io/tgw-policy-based-routing-walkthrough/walkthrough/).

## Local preview

```bash
./scripts/docs-serve.sh
```

Prefers Docker Compose; falls back to host Ruby + Bundler when Docker is unavailable.

## Branch protection

Required status checks on `main`:

- **markdown-lint** — Markdown against `.markdownlint.yml`
- **commitmsg-conform** — commit-message conventions

## License

See [LICENSE](LICENSE).
