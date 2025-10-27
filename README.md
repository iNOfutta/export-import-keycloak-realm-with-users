# Keycloak Realm Migration Tool

A professional tool for exporting and importing Keycloak realms with users between different environments while maintaining data integrity.

## Features

- Export complete realms with users from Keycloak instances
- Selective UUID regeneration to prevent conflicts
- Preserve user and group IDs for database consistency
- Support for bare metal, container, and Kubernetes deployments
- Cross-environment realm migration

## Prerequisites

- Python 3.6+
- Keycloak 15+ (with kc.sh command)
- kubectl (for Kubernetes deployments)
- Appropriate permissions for Keycloak administration

## Quick Start

### 1. Export Realm from Source Environment

```bash
# Inside Keycloak container/pod
/opt/keycloak/bin/kc.sh export \
  --realm MyRealm \
  --file /opt/keycloak/data/export/MyRealm-complete.json \
  --users same_file
```

### 2. Copy Export File (Kubernetes)

```bash
# Extract from source pod
kubectl exec -n production keycloak-pod-name -- \
  cat /opt/keycloak/data/export/MyRealm-complete.json > MyRealm-export.json
```

### 3. Process for Target Environment

```bash
# Regenerate UUIDs to prevent conflicts
python3 regenerate_ids.py MyRealm-export.json MyRealm-Dev
```

### 4. Import to Target Environment

```bash
# Copy to target pod
kubectl exec -n development -i keycloak-target-pod -- \
  tee /opt/keycloak/data/import/MyRealm-processed.json > /dev/null < MyRealm-export-selective.json

# Import realm
kubectl exec -n development keycloak-target-pod -- \
  /opt/keycloak/bin/kc.sh import --file /opt/keycloak/data/import/MyRealm-processed.json
```

## Usage Scenarios

### Scenario 1: Production to Development Migration

```bash
# 1. Export from production
kubectl exec -n prod keycloak-prod-pod -- \
  /opt/keycloak/bin/kc.sh export --realm ProductionRealm \
  --file /opt/keycloak/data/export/prod-realm.json --users same_file

# 2. Extract file
kubectl exec -n prod keycloak-prod-pod -- \
  cat /opt/keycloak/data/export/prod-realm.json > prod-realm.json

# 3. Process for dev environment
python3 regenerate_ids.py prod-realm.json DevRealm

# 4. Deploy to development
kubectl exec -n dev -i keycloak-dev-pod -- \
  tee /opt/keycloak/data/import/dev-realm.json > /dev/null < prod-realm-selective.json

kubectl exec -n dev keycloak-dev-pod -- \
  /opt/keycloak/bin/kc.sh import --file /opt/keycloak/data/import/dev-realm.json
```

### Scenario 2: Staging Environment Setup

```bash
# Export with original realm name preservation
python3 regenerate_ids.py source-realm.json

# Import maintains realm structure but prevents ID conflicts
```

### Scenario 3: Cross-Cluster Migration

```bash
# Source cluster export
kubectl --context=source-cluster exec -n keycloak keycloak-pod -- \
  /opt/keycloak/bin/kc.sh export --realm SourceRealm \
  --file /opt/keycloak/data/export/migration.json --users same_file

# Process and transfer
kubectl --context=source-cluster exec -n keycloak keycloak-pod -- \
  cat /opt/keycloak/data/export/migration.json > realm-migration.json

python3 regenerate_ids.py realm-migration.json TargetRealm

# Target cluster import
kubectl --context=target-cluster exec -n keycloak -i keycloak-pod -- \
  tee /opt/keycloak/data/import/target.json > /dev/null < realm-migration-selective.json

kubectl --context=target-cluster exec -n keycloak keycloak-pod -- \
  /opt/keycloak/bin/kc.sh import --file /opt/keycloak/data/import/target.json
```

## Script Options

```bash
# Basic usage - preserves realm name
python3 regenerate_ids.py <realm-file.json>

# With new realm name
python3 regenerate_ids.py <realm-file.json> <new-realm-name>

# Examples
python3 regenerate_ids.py MyRealm-export.json
python3 regenerate_ids.py MyRealm-export.json "MyRealm-Development"
```

## What Gets Preserved vs Changed

### Preserved (for data integrity):
- User IDs
- Group IDs
- User-group relationships
- User attributes and credentials

### Regenerated (to prevent conflicts):
- Realm ID
- Client IDs
- Role IDs
- Client scope IDs
- Authentication flow IDs
- Protocol mapper IDs
- Component IDs

## Deployment Options

### Bare Metal / VM Deployment

```bash
# Export realm directly on server
/opt/keycloak/bin/kc.sh export \
  --realm MyRealm \
  --file /opt/keycloak/data/export/MyRealm-export.json \
  --users same_file

# Process export file
python3 regenerate_ids.py /opt/keycloak/data/export/MyRealm-export.json MyRealm-Target

# Copy processed file to target server
scp MyRealm-export-selective.json user@target-server:/opt/keycloak/data/import/

# Import on target server
ssh user@target-server "/opt/keycloak/bin/kc.sh import --file /opt/keycloak/data/import/MyRealm-export-selective.json"
```

### Docker/Podman Containers

```bash
# Export from container
docker exec keycloak-container /opt/keycloak/bin/kc.sh export \
  --realm MyRealm --file /opt/keycloak/data/export/realm.json --users same_file

# Copy from container
docker cp keycloak-container:/opt/keycloak/data/export/realm.json ./realm.json

# Process file
python3 regenerate_ids.py realm.json NewRealm

# Copy to target container
docker cp realm-selective.json target-container:/opt/keycloak/data/import/

# Import
docker exec target-container /opt/keycloak/bin/kc.sh import \
  --file /opt/keycloak/data/import/realm-selective.json
```

### Kubernetes Deployment

```bash
# Export from pod
kubectl exec -n production keycloak-pod -- \
  /opt/keycloak/bin/kc.sh export --realm MyRealm \
  --file /opt/keycloak/data/export/realm.json --users same_file

# Copy from pod (when tar is not available)
kubectl exec -n production keycloak-pod -- \
  cat /opt/keycloak/data/export/realm.json > realm-export.json

# Process file
python3 regenerate_ids.py realm-export.json MyRealm-Dev

# Copy to target pod
kubectl exec -n development -i keycloak-target-pod -- \
  tee /opt/keycloak/data/import/realm-processed.json > /dev/null < realm-export-selective.json

# Import
kubectl exec -n development keycloak-target-pod -- \
  /opt/keycloak/bin/kc.sh import --file /opt/keycloak/data/import/realm-processed.json
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure proper permissions for file operations and Keycloak access
2. **File Not Found**: Verify export completed successfully before copying
3. **Import Conflicts**: Use the UUID regeneration script to prevent ID conflicts
4. **Large Files**: For realms with many users, consider using volume mounts or direct file system access
5. **Network Issues**: Ensure connectivity between source and target environments

### Verification

```bash
# Verify export file structure
python3 -m json.tool realm-export.json > /dev/null && echo "Valid JSON"

# Check realm name in processed file
grep '"realm"' realm-export-selective.json
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Security Considerations

- Always review exported data before importing to production
- Ensure proper network security when transferring realm files
- Consider encrypting realm export files during transfer
- Validate user permissions after import
- Test imports in non-production environments first
