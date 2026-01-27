#!/usr/bin/env python3
"""
Migration script to update existing form templates with old phone validation patterns.
This script finds templates with the old phone pattern and updates them to use the new Philippines format.
"""
import sys
import os
import asyncio
import json
import re
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.config import settings
from app.models.forms import FormTemplate

async def update_phone_patterns():
    """Update phone validation patterns in existing templates."""
    
    # Create async engine and session  
    database_url = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"
    engine = create_async_engine(database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    old_pattern = r'^\+?[1-9]\d{1,14}$'
    new_pattern = r'^(09|\+639)\d{9}$'
    
    async with async_session() as session:
        try:
            # Find all templates
            result = await session.execute(text("SELECT id, name, schema_json FROM form_templates"))
            templates = result.fetchall()
            
            updated_count = 0
            
            for template in templates:
                template_id = template[0]
                template_name = template[1]
                schema_json = template[2]
                
                if schema_json and isinstance(schema_json, dict):
                    schema_str = json.dumps(schema_json)
                    
                    # Check if this template has the old phone pattern
                    if old_pattern.replace('\\', '\\\\') in schema_str:
                        print(f"Updating template '{template_name}' (ID: {template_id})")
                        
                        # Replace the old pattern with the new one
                        updated_schema_str = schema_str.replace(
                            old_pattern.replace('\\', '\\\\'), 
                            new_pattern.replace('\\', '\\\\')
                        )
                        updated_schema = json.loads(updated_schema_str)
                        
                        # Update the database
                        await session.execute(
                            text("UPDATE form_templates SET schema_json = :schema WHERE id = :id"),
                            {"schema": json.dumps(updated_schema), "id": template_id}
                        )
                        updated_count += 1
            
            await session.commit()
            
            print(f"\\n✅ Migration completed!")
            print(f"📊 Templates updated: {updated_count}")
            print(f"📋 Templates checked: {len(templates)}")
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            await session.rollback()
            raise
        
        finally:
            await engine.dispose()

if __name__ == "__main__":
    print("🔄 Starting phone pattern migration...")
    print("=" * 50)
    asyncio.run(update_phone_patterns())