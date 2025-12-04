#!/usr/bin/env python3
"""
Marketplace Seed Script - Standalone

Kullanım:
    python scripts/seed_marketplace.py
"""
import asyncio
import sys
from pathlib import Path

# Project root'u path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.marketplace.seed import seed_marketplace
from app.core.db import async_session_factory


async def main():
    """Seed script main function."""
    print("🌱 Marketplace seed script başlatılıyor...")
    
    async with async_session_factory() as session:
        try:
            items = await seed_marketplace(session, clear_existing=False)
            print(f"✅ Marketplace seeded: {len(items)} items oluşturuldu")
            print("\n📦 Oluşturulan item'ler:")
            for item in items:
                print(f"  - {item.title} ({item.item_type}) - {item.price_ncr} NCR")
        except Exception as e:
            print(f"❌ Seed failed: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

