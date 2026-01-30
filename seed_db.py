import asyncio
from src.core.database import seed_cultural_personas, seed_safety_rules

async def main():
    print("Seeding cultural personas...")
    await seed_cultural_personas()
    print("Seeding safety rules...")
    await seed_safety_rules()
    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(main())
