import asyncio

from database import db
from utils.password import hash_password


async def create_staff_user():
    department = await db.departments.find_one(
        {"code": "ICU"}
    )

    if not department:
        print("ICU department not found.")
        return

    existing_user = await db.users.find_one(
        {"email": "staff@hospital.com"}
    )

    if existing_user:
        print("Staff user already exists.")
        return

    user = {
        "name": "ICU Staff",
        "email": "staff@hospital.com",
        "password_hash": hash_password("Staff@123"),
        "role": "DEPARTMENT_STAFF",
        "department_id": department["_id"],
        "is_active": True
    }

    await db.users.insert_one(user)

    print("Department Staff user created successfully.")


asyncio.run(create_staff_user())