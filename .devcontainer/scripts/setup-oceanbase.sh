#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="oceanbase-ce"
SCRATCH_DIR="/tmp/oceanbase-volume"

echo "==> Preparing OceanBase scratch space"
mkdir -p "${SCRATCH_DIR}"

echo "==> Removing previous OceanBase container"
docker rm -f "${CONTAINER_NAME}" 2>/dev/null || true

echo "==> Starting OceanBase CE in SLIM mode"
docker run \
  --name "${CONTAINER_NAME}" \
  --ulimit nofile=65535:65535 \
  -p 2881:2881 \
  -e MODE=SLIM \
  -v "${SCRATCH_DIR}:/mnt/oceanbase" \
  -d \
  oceanbase/oceanbase-ce

echo "==> Waiting for OceanBase"

for i in $(seq 1 60); do
  if docker exec "${CONTAINER_NAME}" \
      obclient \
      -h127.0.0.1 \
      -P2881 \
      -uroot@sys \
      -Doceanbase \
      -A \
      -e "SELECT 1;" >/dev/null 2>&1; then

    echo "==> OceanBase is ready"
    docker exec "${CONTAINER_NAME}" \
      obclient \
      -h127.0.0.1 \
      -P2881 \
      -uroot@sys \
      -Doceanbase \
      -A \
      -e "SELECT VERSION();"

    echo "==> Scratch storage"
    docker exec "${CONTAINER_NAME}" df -h /mnt/oceanbase

    exit 0
  fi

  sleep 2
done

echo "OceanBase failed to become ready"
docker logs "${CONTAINER_NAME}"
exit 1
