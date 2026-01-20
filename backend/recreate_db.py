from sqlalchemy import create_engine
from app.db.base import Base
from app.core.config import settings

def recreate_db():
    sync_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_url)
    
    print("Dropping all tables with CASCADE...")
    with engine.connect() as conn:
        # For Postgres, dropping the schema and recreating it is a clean way to drop all tables
        conn.execute(sqlalchemy.text("DROP SCHEMA public CASCADE;"))
        conn.execute(sqlalchemy.text("CREATE SCHEMA public;"))
        conn.commit()
    
    print("Creating all tables from current models...")
    Base.metadata.create_all(bind=engine)
    
    print("Database schema recreated successfully.")

import sqlalchemy

if __name__ == "__main__":
    recreate_db()
