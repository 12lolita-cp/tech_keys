import asyncio

from database import db


departments = [
    {
        "name": "ICU",
        "code": "ICU",
        "is_active": True
    },
    {
        "name": "Emergency",
        "code": "EMERGENCY",
        "is_active": True
    },
    {
        "name": "Pharmacy",
        "code": "PHARMACY",
        "is_active": True
    },
    {
        "name": "Radiology",
        "code": "RADIOLOGY",
        "is_active": True
    }
]


async def seed_departments():
    for department in departments:
        existing = await db.departments.find_one(
            {"code": department["code"]}
        )

        if not existing:
            await db.departments.insert_one(department)
            print(f"Created: {department['name']}")
        else:
            print(f"Already exists: {department['name']}")

    print("Department seeding completed.")


asyncio.run(seed_departments())