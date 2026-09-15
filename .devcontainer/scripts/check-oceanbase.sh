#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="${CONTAINER_NAME:-oceanbase-ce}"

echo "==> Checking OceanBase DevEx Lab"

# 1. Container exists
if ! docker inspect "${CONTAINER_NAME}" >/dev/null 2>&1; then
  echo "❌ Container '${CONTAINER_NAME}' does not exist"
  echo "   Run: ./scripts/setup-oceanbase.sh"
  exit 1
fi

# 2. Container is running
if [ "$(docker inspect -f '{{.State.Running}}' "${CONTAINER_NAME}")" != "true" ]; then
  echo "❌ Container '${CONTAINER_NAME}' is not running"
  echo "   Run: docker start ${CONTAINER_NAME}"
  exit 1
fi

echo "✓ Container is running"

# 3. OceanBase process
if ! docker exec "${CONTAINER_NAME}" \
  pgrep observer >/dev/null 2>&1; then
  echo "❌ observer process is not running"
  echo
  echo "Recent logs:"
  docker logs --tail 30 "${CONTAINER_NAME}"
  exit 1
fi

echo "✓ observer is running"

# 4. SQL connectivity
if ! docker exec "${CONTAINER_NAME}" \
  obclient \
    -h127.0.0.1 \
    -P2881 \
    -uroot@sys \
    -Doceanbase \
    -A \
    -e "SELECT 1;" >/dev/null 2>&1; then
  echo "❌ Cannot connect to OceanBase on port 2881"
  echo
  echo "Recent logs:"
  docker logs --tail 30 "${CONTAINER_NAME}"
  exit 1
fi

echo "✓ SQL connection succeeded"

# 5. Version
VERSION=$(
  docker exec "${CONTAINER_NAME}" \
    obclient \
      -h127.0.0.1 \
      -P2881 \
      -uroot@sys \
      -Doceanbase \
      -A \
      -N \
      -e "SELECT VERSION();" 2>/dev/null
)

echo "✓ Version: ${VERSION}"

# 6. Scratch storage (optional)
if docker exec "${CONTAINER_NAME}" \
  test -d /mnt/oceanbase >/dev/null 2>&1; then

  echo
  echo "Scratch storage:"
  docker exec "${CONTAINER_NAME}" \
    df -h /mnt/oceanbase | tail -n 1
fi

echo
echo "========================================"
echo " OceanBase DevEx Lab is READY ✌️"
echo " Container : ${CONTAINER_NAME}"
echo " SQL       : localhost:2881"
echo " Version   : ${VERSION}"
echo "========================================"
