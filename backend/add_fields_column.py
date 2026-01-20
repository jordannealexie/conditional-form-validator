import asyncio
import sys
from pathlib import Path
from sqlalchemy import text

# Add project root to path
backend_path = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_path))

from app.db.session import AsyncSessionLocal

async def add_column():
    async with AsyncSessionLocal() as session:
        print("Adding 'fields' column to 'form_templates' table...")
        try:
            await session.execute(text('ALTER TABLE form_templates ADD COLUMN IF NOT EXISTS fields JSON;'))
            await session.commit()
            print("Successfully added 'fields' column.")
        except Exception as e:
            print(f"Error adding column: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(add_column())
