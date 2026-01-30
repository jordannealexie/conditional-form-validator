import asyncio
import time
import os
import sys

# Ensure project root is on sys.path when run as a script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.cache import cache, CacheKeys
from app.db.session import AsyncSessionLocal
from app.models.forms import FormTemplate
from sqlalchemy import select
from sqlalchemy.orm import joinedload


async def to_dict(template: FormTemplate) -> dict:
    bank = None
    if getattr(template, "bank", None):
        b = template.bank
        bank = {
            "id": b.id,
            "name": b.name,
            "code": b.code,
            "logo_url": b.logo_url,
            "primary_color": b.primary_color,
            "description": b.description,
            "active": b.active,
            "created_at": b.created_at.isoformat() if b.created_at else None,
            "updated_at": b.updated_at.isoformat() if b.updated_at else None,
        }
    d = {
        "id": template.id,
        "bank_id": template.bank_id,
        "name": template.name,
        "version": template.version,
        "form_type": template.form_type,
        "schema_json": template.schema_json,
        "fields": template.fields,
        "ui_schema": template.ui_schema,
        "description": template.description,
        "active": template.active,
        "created_at": template.created_at.isoformat() if template.created_at else None,
        "updated_at": template.updated_at.isoformat() if template.updated_at else None,
        "created_by": template.created_by,
        "bank": bank,
    }
    return d


async def main(template_id: int = 1):
    await cache.connect()
    print("cache connected:", cache.is_connected())

    # Optionally clear template keys to force DB fetch
    deleted = await cache.delete_pattern("template:*")
    print("deleted template keys:", deleted)

    async with AsyncSessionLocal() as db:
        # 1) Fetch fresh from DB (simulate first request)
        start = time.time()
        result = await db.execute(
            select(FormTemplate).options(joinedload(FormTemplate.bank)).where(FormTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()
        db_time_ms = (time.time() - start) * 1000
        print(f"DB fetch time: {db_time_ms:.2f} ms")
        if not template:
            print("No template found with id", template_id)
            await cache.disconnect()
            return

        # 2) Cache it (simulate repository caching)
        cache_key = CacheKeys.template(template_id)
        payload = await to_dict(template)
        ok = await cache.set(cache_key, payload, ttl=3600)
        print("cached:", ok, "key:", cache_key)

        # 3) Read from cache (simulate subsequent request)
        start = time.time()
        cached = await cache.get(cache_key)
        cache_time_ms = (time.time() - start) * 1000
        print(f"Cache fetch time: {cache_time_ms:.2f} ms")
        print("cached value found:", bool(cached))

    await cache.disconnect()


if __name__ == "__main__":
    # change template_id if needed
    asyncio.run(main(template_id=1))
