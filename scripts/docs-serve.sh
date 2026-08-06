#!/usr/bin/env bash
set -euo pipefail

URL="http://127.0.0.1:4000/tgw-policy-based-routing-walkthrough/"

if command -v docker &>/dev/null; then
  echo "Open ${URL}"
  exec docker compose -f docs/docker-compose.yml up "$@"
elif command -v bundle &>/dev/null; then
  cd docs
  bundle check || bundle install
  echo "Open ${URL}"
  exec bundle exec jekyll serve --livereload --watch
else
  echo "Error: neither Docker nor Ruby Bundler found on PATH." >&2
  echo "Install one of the following:" >&2
  echo "  • Docker (includes Docker Compose)  — https://docs.docker.com/get-docker/" >&2
  echo "  • Ruby + Bundler                    — https://bundler.io/" >&2
  exit 1
fi
