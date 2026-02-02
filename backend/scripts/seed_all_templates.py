"""Unified, non-destructive template seeding script.

Run this script to seed all form-related templates and their
dependencies (predefined field types, custom field types, lookups,
sample templates, and JSON-schema-based templates) without
dropping tables or deleting existing data.

Usage (from backend/ directory):
    python scripts/seed_all_templates.py
"""

import asyncio
import sys
from pathlib import Path


current_dir = Path(__file__).parent

# Ensure "scripts" and backend root are on sys.path so imports work
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir.parent))

import seed_predefined_field_types
import seed_field_types
import seed_lookups
import seed_sample_templates
from seed_form_templates import seed_form_templates


async def seed_all_templates() -> None:
    """Run all safe, non-destructive template-related seeders."""
    print("\n" + "=" * 70)
    print("🌱 Unified Template Seeding")
    print("=" * 70)

    # 1. Predefined field types (base field definitions)
    await seed_predefined_field_types.seed_predefined_types()

    # 2. Custom enums and field types
    await seed_field_types.main()

    # 3. Lookup tables (departments, locations, etc.)
    await seed_lookups.main()

    # 4. Sample templates using the field types
    await seed_sample_templates.main()

    # 5. JSON-schema-based bank templates
    await seed_form_templates()

    print("\n" + "=" * 70)
    print("✅ Unified template seeding completed successfully")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(seed_all_templates())
