#!/usr/bin/env bash
set -euo pipefail

docker rm -f oceanbase-ce 2>/dev/null || true
rm -rf /tmp/oceanbase-volume
bash scripts/setup-oceanbase.sh
