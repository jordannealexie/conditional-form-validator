#!/usr/bin/env python3
"""
Script to fix PostgreSQL sequence values that are out of sync with actual data.
This can happen after bulk inserts, database restores, or other operations.

Usage:
    python scripts/fix_sequences.py
"""

import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings


# Tables with auto-increment primary keys to check
TABLES_TO_CHECK = [
    'users',
    'roles',
    'banks',
    'form_templates',
    'form_submissions',
    'file_uploads',
    'audit_logs',
    'departments',
    'locations',
    'user_attributes',
    'resource_attributes',
    'abac_policies',
    'field_type_definitions',
    'enum_definitions',
    'form_field_mappings',
]


def fix_sequences():
    """Check and fix all table sequences."""
    # Use sync connection for this maintenance task
    db_url = settings.DATABASE_URL.replace('+asyncpg', '')
    engine = create_engine(db_url)
    
    fixed_count = 0
    
    with engine.connect() as conn:
        for table in TABLES_TO_CHECK:
            try:
                # Get max ID in table
                max_result = conn.execute(text(f'SELECT MAX(id) FROM {table}'))
                max_id = max_result.scalar() or 0
                
                # Get current sequence value
                seq_name = f'{table}_id_seq'
                seq_result = conn.execute(text(f"SELECT last_value FROM {seq_name}"))
                seq_val = seq_result.scalar()
                
                if seq_val < max_id:
                    new_val = max_id + 1
                    print(f'⚠️  {table}: max_id={max_id}, seq={seq_val} - FIXING...')
                    conn.execute(text(f"SELECT setval('{seq_name}', {new_val}, false)"))
                    print(f'   ✅ Sequence set to {new_val}')
                    fixed_count += 1
                else:
                    print(f'✓ {table}: max_id={max_id}, seq={seq_val} - OK')
                    
            except Exception as e:
                # Table might not exist or have different structure
                print(f'- {table}: skipped ({type(e).__name__})')
        
        conn.commit()
    
    print(f'\nDone. Fixed {fixed_count} sequence(s).')
    return fixed_count


if __name__ == '__main__':
    fix_sequences()
