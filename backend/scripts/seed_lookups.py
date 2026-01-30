"""
Seed script for Department and Location lookup tables
Run this after migrations to populate initial lookup data
"""
import asyncio
import sys
sys.path.insert(0, '.')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from app.core.config import settings
from app.models.lookup import Department, Location


# Initial departments data
DEPARTMENTS = [
    {"name": "IT", "code": "IT", "description": "Information Technology", "display_order": 1},
    {"name": "Marketing", "code": "MKT", "description": "Marketing and Communications", "display_order": 2},
    {"name": "Finance", "code": "FIN", "description": "Finance and Accounting", "display_order": 3},
    {"name": "HR", "code": "HR", "description": "Human Resources", "display_order": 4},
    {"name": "Operations", "code": "OPS", "description": "Business Operations", "display_order": 5},
    {"name": "Engineering", "code": "ENG", "description": "Engineering and Development", "display_order": 6},
    {"name": "Sales", "code": "SLS", "description": "Sales and Business Development", "display_order": 7},
    {"name": "Legal", "code": "LGL", "description": "Legal and Compliance", "display_order": 8},
    {"name": "Customer Support", "code": "CS", "description": "Customer Service and Support", "display_order": 9},
]

# Initial locations data - EXACTLY 17 locations as specified
LOCATIONS = [
    # Metro Manila & Nearby
    {"name": "Makati", "code": "MKT", "description": "Makati City", "region": "Metro Manila", "display_order": 1},
    {"name": "Quezon City", "code": "QC", "description": "Quezon City", "region": "Metro Manila", "display_order": 2},
    {"name": "Paranaque", "code": "PNQ", "description": "Paranaque City", "region": "Metro Manila", "display_order": 3},
    # Luzon Provinces
    {"name": "Pampanga", "code": "PAM", "description": "Pampanga Province", "region": "Central Luzon", "display_order": 4},
    {"name": "Bulacan", "code": "BUL", "description": "Bulacan Province", "region": "Central Luzon", "display_order": 5},
    {"name": "Cavite", "code": "CAV", "description": "Cavite Province", "region": "CALABARZON", "display_order": 6},
    {"name": "Laguna", "code": "LAG", "description": "Laguna Province", "region": "CALABARZON", "display_order": 7},
    {"name": "Batangas", "code": "BAT", "description": "Batangas Province", "region": "CALABARZON", "display_order": 8},
    # Visayas
    {"name": "Cebu", "code": "CEB", "description": "Cebu City", "region": "Central Visayas", "display_order": 9},
    {"name": "Iloilo", "code": "ILO", "description": "Iloilo City", "region": "Western Visayas", "display_order": 10},
    {"name": "Bacolod", "code": "BAC", "description": "Bacolod City", "region": "Western Visayas", "display_order": 11},
    # Mindanao
    {"name": "Davao", "code": "DVO", "description": "Davao City", "region": "Davao Region", "display_order": 12},
    {"name": "Cagayan De Oro", "code": "CDO", "description": "Cagayan De Oro City", "region": "Northern Mindanao", "display_order": 13},
    {"name": "Pagadian", "code": "PAG", "description": "Pagadian City", "region": "Zamboanga Peninsula", "display_order": 14},
    {"name": "Tagum", "code": "TAG", "description": "Tagum City", "region": "Davao Region", "display_order": 15},
    {"name": "Zamboanga", "code": "ZAM", "description": "Zamboanga City", "region": "Zamboanga Peninsula", "display_order": 16},
    {"name": "General Santos", "code": "GNS", "description": "General Santos City", "region": "SOCCSKSARGEN", "display_order": 17},
]


async def seed_departments(session: AsyncSession):
    """Seed departments table"""
    print("Seeding departments...")
    
    for dept_data in DEPARTMENTS:
        # Check if already exists
        result = await session.execute(
            select(Department).where(Department.name == dept_data["name"])
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"  - Department '{dept_data['name']}' already exists, skipping")
        else:
            dept = Department(**dept_data, is_active=True)
            session.add(dept)
            print(f"  + Added department: {dept_data['name']}")
    
    await session.commit()
    print(f"✓ Departments seeding complete")


async def seed_locations(session: AsyncSession):
    """Seed locations table"""
    print("Seeding locations...")
    
    for loc_data in LOCATIONS:
        # Check if already exists
        result = await session.execute(
            select(Location).where(Location.name == loc_data["name"])
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"  - Location '{loc_data['name']}' already exists, skipping")
        else:
            loc = Location(**loc_data, is_active=True)
            session.add(loc)
            print(f"  + Added location: {loc_data['name']}")
    
    await session.commit()
    print(f"✓ Locations seeding complete")


async def main():
    print("=" * 60)
    print("ABAC Lookup Tables Seeder")
    print("=" * 60)
    
    # Create engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        await seed_departments(session)
        print()
        await seed_locations(session)
    
    await engine.dispose()
    
    print()
    print("=" * 60)
    print("✓ All lookup tables seeded successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
