#!/usr/bin/env bash
# Run inside the Kafka container to create all required topics.
# Usage: docker exec -it <kafka-pod> /bin/bash < kafka/create-topics.sh

BOOTSTRAP=kafka:9092

create_topic() {
  local name=$1
  local partitions=$2
  local replication=$3
  shift 3
  kafka-topics.sh --bootstrap-server "$BOOTSTRAP" \
    --create --if-not-exists \
    --topic "$name" \
    --partitions "$partitions" \
    --replication-factor "$replication" \
    "$@"
  echo "Topic $name: OK"
}

create_topic chat.events         12 3 \
  --config retention.ms=604800000 \
  --config min.insync.replicas=2

create_topic chat.bulk.commands   6 3 \
  --config retention.ms=86400000 \
  --config min.insync.replicas=2

create_topic plot.events         12 3 \
  --config retention.ms=2592000000 \
  --config min.insync.replicas=2

create_topic plot.bulk.commands   6 3 \
  --config retention.ms=86400000 \
  --config min.insync.replicas=2

echo ""
echo "All topics created."
kafka-topics.sh --bootstrap-server "$BOOTSTRAP" --list
