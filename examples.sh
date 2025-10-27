#!/bin/bash

# Keycloak Realm Migration Examples
# Replace pod names and namespaces with your actual values

set -e

echo "=== Keycloak Realm Migration Examples ==="

# Example 1: Export from Production Kubernetes Pod
echo "1. Exporting realm from production..."
kubectl exec -n production keycloak-prod-pod -- \
  /opt/keycloak/bin/kc.sh export \
  --realm MyRealm \
  --file /opt/keycloak/data/export/MyRealm-complete.json \
  --users same_file

# Example 2: Copy export file from pod (when tar is not available)
echo "2. Copying export file from pod..."
kubectl exec -n production keycloak-prod-pod -- \
  cat /opt/keycloak/data/export/MyRealm-complete.json > MyRealm-export.json

# Example 3: Process export for target environment
echo "3. Processing export file..."
python3 regenerate_ids.py MyRealm-export.json MyRealm-Dev

# Example 4: Copy processed file to target pod
echo "4. Copying to target environment..."
kubectl exec -n development -i keycloak-dev-pod -- \
  tee /opt/keycloak/data/import/MyRealm-processed.json > /dev/null < MyRealm-export-selective.json

# Example 5: Import to target environment
echo "5. Importing to target environment..."
kubectl exec -n development keycloak-dev-pod -- \
  /opt/keycloak/bin/kc.sh import \
  --file /opt/keycloak/data/import/MyRealm-processed.json

echo "Migration complete!"

# Alternative: Docker/Podman usage
echo ""
echo "=== Docker/Podman Alternative ==="

# Export from Docker container
echo "Exporting from Docker container..."
docker exec keycloak-source /opt/keycloak/bin/kc.sh export \
  --realm MyRealm \
  --file /opt/keycloak/data/export/realm.json \
  --users same_file

# Copy from container
docker cp keycloak-source:/opt/keycloak/data/export/realm.json ./realm-export.json

# Process
python3 regenerate_ids.py realm-export.json MyRealm-Target

# Copy to target
docker cp realm-export-selective.json keycloak-target:/opt/keycloak/data/import/

# Import
docker exec keycloak-target /opt/keycloak/bin/kc.sh import \
  --file /opt/keycloak/data/import/realm-export-selective.json