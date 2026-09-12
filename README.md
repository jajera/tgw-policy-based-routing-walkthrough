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

`https://tgw-policy-based-routing-walkthrough.johna.kiwi/`
(GitHub Pages custom domain; DNS via [`johna-kiwi-infra`](https://github.com/platformfuzz/johna-kiwi-infra) `sites.yaml`).

| Page | Description |
| ---- | ----------- |
| [Overview](https://tgw-policy-based-routing-walkthrough.johna.kiwi/) | Lab framing and reading order |
| [Architecture](https://tgw-policy-based-routing-walkthrough.johna.kiwi/architecture/) | Hub/spoke topology and path map |
| [Policy Tables](https://tgw-policy-based-routing-walkthrough.johna.kiwi/policy-tables/) | Match criteria and evaluation order |
| [Use Cases](https://tgw-policy-based-routing-walkthrough.johna.kiwi/use-cases/) | Path selection, inspection, isolation |
| [Deploy and prove](https://tgw-policy-based-routing-walkthrough.johna.kiwi/walkthrough/) | Apply, prove, tear down |
| [Troubleshooting](https://tgw-policy-based-routing-walkthrough.johna.kiwi/troubleshooting/) | Failure modes and fixes |
| [Reference](https://tgw-policy-based-routing-walkthrough.johna.kiwi/reference/) | CLI ↔ EC2 API |

## Lab repository

Infrastructure and apply scripts:

- <https://github.com/jajera/tgw-policy-based-routing>

```bash
git clone https://github.com/jajera/tgw-policy-based-routing.git
cd tgw-policy-based-routing
terraform init
terraform apply -auto-approve
```

Then follow [Deploy and prove](https://tgw-policy-based-routing-walkthrough.johna.kiwi/walkthrough/).

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
