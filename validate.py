#!/usr/bin/env python3
"""
Validation script for Keycloak realm export files.
Checks JSON structure and provides basic statistics.
"""

import json
import sys
import os

def validate_realm_export(file_path):
    """Validate and analyze Keycloak realm export file."""
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}")
        return False
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Basic validation
    if not isinstance(data, dict):
        print("Error: Root element must be an object")
        return False
    
    if 'realm' not in data:
        print("Warning: No 'realm' field found")
    
    # Statistics
    print(f"Realm Export Analysis: {file_path}")
    print("-" * 40)
    print(f"Realm Name: {data.get('realm', 'N/A')}")
    print(f"Realm ID: {data.get('id', 'N/A')}")
    
    users = data.get('users', [])
    print(f"Users: {len(users)}")
    
    clients = data.get('clients', [])
    print(f"Clients: {len(clients)}")
    
    roles = data.get('roles', {})
    realm_roles = roles.get('realm', []) if isinstance(roles, dict) else []
    print(f"Realm Roles: {len(realm_roles)}")
    
    groups = data.get('groups', [])
    print(f"Groups: {len(groups)}")
    
    # File size
    file_size = os.path.getsize(file_path)
    print(f"File Size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
    
    print("-" * 40)
    print("Validation: PASSED")
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 validate.py <realm-export.json>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    success = validate_realm_export(file_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()