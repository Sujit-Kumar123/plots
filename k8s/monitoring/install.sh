#!/usr/bin/env bash
# Install the full Plots monitoring stack:
#   - kube-prometheus-stack (Prometheus + Grafana + Alertmanager + node-exporter)
#   - ServiceMonitors for all 6 app services
#   - Kafka / PostgreSQL / Redis exporters
#
# Prerequisites: helm 3+, kubectl configured to the target cluster
# Usage: bash k8s/monitoring/install.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Adding prometheus-community Helm repo"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

echo "==> Installing kube-prometheus-stack"
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --values "${SCRIPT_DIR}/helm-values.yaml" \
  --wait \
  --timeout 10m

echo "==> Ensuring plots-system namespace exists"
kubectl apply -f "${SCRIPT_DIR}/../namespace.yaml"

echo "==> Applying exporters (kafka / postgres / redis)"
kubectl apply -f "${SCRIPT_DIR}/exporters.yaml"

echo "==> Applying ServiceMonitors"
kubectl apply -f "${SCRIPT_DIR}/servicemonitors.yaml"

echo ""
echo "Done. Access UIs via port-forward:"
echo "  Grafana:    kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring"
echo "  Prometheus: kubectl port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090 -n monitoring"
echo "  Alertmgr:   kubectl port-forward svc/monitoring-kube-prometheus-alertmanager 9093:9093 -n monitoring"
