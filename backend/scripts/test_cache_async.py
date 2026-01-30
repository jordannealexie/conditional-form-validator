import asyncio
from app.core.cache import cache
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

async def main():
    await cache.connect()
    print("connected:", cache.is_connected())
    ok = await cache.set("test:key", {"hello":"world"}, ttl=5)
    print("set ok:", ok)
    val = await cache.get("test:key")
    print("got:", val)
    await asyncio.sleep(6)
    val2 = await cache.get("test:key")
    print("after ttl, got:", val2)
    await cache.disconnect()

if __name__ == "__main__":
    asyncio.run(main())