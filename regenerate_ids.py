#!/usr/bin/env python3
"""
Keycloak Realm Migration Tool

Selectively regenerates UUIDs in Keycloak realm exports to prevent conflicts
while preserving user and group IDs for database consistency.
"""

import json
import uuid
import sys
import os
from typing import Dict, Set

class RealmMigrationTool:
    """Handles selective UUID regeneration for Keycloak realm migration."""
    
    def __init__(self):
        self.id_mapping: Dict[str, str] = {}
        self.preserve_ids: Set[str] = {'userId', 'groupId'}
        self.change_ids: Set[str] = {
            'realmId', 'clientId', 'roleId', 'clientScopeId',
            'authenticationFlowId', 'authenticatorConfigId', 
            'protocolMapperId', 'componentId', 'credentialId'
        }

    def _generate_new_id(self, old_id: str) -> str:
        """Generate and cache new UUID."""
        if old_id not in self.id_mapping:
            self.id_mapping[old_id] = str(uuid.uuid4())
        return self.id_mapping[old_id]

    def _is_uuid(self, value: str) -> bool:
        """Validate UUID format."""
        if not isinstance(value, str) or len(value) != 36:
            return False
        try:
            uuid.UUID(value)
            return True
        except ValueError:
            return False

    def _should_change_id(self, key: str, context: str = "") -> bool:
        """Determine if ID should be regenerated based on context."""
        if key in self.preserve_ids or (key == 'id' and context in ['users', 'groups']):
            return False
        return key in self.change_ids or (key == 'id' and context not in ['users', 'groups'])

    def _process_object(self, obj, context: str = ""):
        """Recursively process and selectively regenerate UUIDs."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if self._is_uuid(value) and self._should_change_id(key, context):
                    obj[key] = self._generate_new_id(value)
                else:
                    self._process_object(value, key)
        elif isinstance(obj, list):
            for item in obj:
                self._process_object(item, context)

    def process_realm_export(self, realm_file: str, new_realm_name: str = None) -> str:
        """Process realm export file with selective UUID regeneration."""
        print(f"Processing realm export: {realm_file}")

        with open(realm_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if new_realm_name and 'realm' in data:
            print(f"Updating realm name: {data['realm']} -> {new_realm_name}")
            data['realm'] = new_realm_name

        if 'id' in data and self._is_uuid(data['id']):
            data['id'] = self._generate_new_id(data['id'])

        if 'users' in data:
            print(f"Processing {len(data['users'])} users (preserving user IDs)")
            for user in data['users']:
                for key, value in user.items():
                    if key != 'id':
                        self._process_object(value, 'users')

        for key, value in data.items():
            if key != 'users':
                self._process_object(value, key)

        output_file = realm_file.replace('.json', '-selective.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        print(f"Generated: {output_file}")
        return output_file

def main():
    """Main entry point for the realm migration tool."""
    if len(sys.argv) < 2:
        print("Usage: python3 regenerate_ids.py <realm-file.json> [new-realm-name]")
        print("\nExamples:")
        print("  python3 regenerate_ids.py MyRealm-export.json")
        print("  python3 regenerate_ids.py MyRealm-export.json 'MyRealm-Dev'")
        sys.exit(1)

    realm_file = sys.argv[1]
    new_realm_name = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(realm_file):
        print(f"Error: File '{realm_file}' not found")
        sys.exit(1)

    tool = RealmMigrationTool()
    
    print("Keycloak Realm Migration Tool")
    print("Preserving: User IDs, Group IDs")
    print("Regenerating: Structural IDs to prevent conflicts")
    print("-" * 50)

    try:
        output_file = tool.process_realm_export(realm_file, new_realm_name)
        print("-" * 50)
        print(f"Migration complete! UUIDs regenerated: {len(tool.id_mapping)}")
        print(f"Output file: {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
