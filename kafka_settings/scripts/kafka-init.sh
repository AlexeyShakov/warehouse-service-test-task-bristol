#!/bin/bash

LOG_DIR="/var/lib/kafka/data"

if [ ! -f "$LOG_DIR/meta.properties" ]; then
  echo "Formatting storage directory for KRaft mode..."

  if [ -z "$KAFKA_CLUSTER_ID" ]; then
    echo "❌ Error: KAFKA_CLUSTER_ID is not set!"
    exit 1
  fi

  echo "Using CLUSTER_ID from .env: $KAFKA_CLUSTER_ID"

  kafka-storage format \
    --cluster-id "$KAFKA_CLUSTER_ID" \
    --config /etc/kafka/kraft.properties \
    --ignore-formatted
else
  echo "Kafka storage already formatted. Skipping format."
fi
