from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from app.database import db
from app.schemas.auth import LoginRequest
from app.utils.password import verify_password
from app.utils.jwt import create_access_token
from app.utils.auth import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login")
async def login(data: LoginRequest):

    user = await db.users.find_one(
        {"email": data.email}
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        data.password,
        user["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
    {
        "sub": str(user["_id"]),
        "role": user["role"],
        "department_id": str(user["department_id"])
    }
)

    return {
    "message": "Login successful",
    "access_token": token,
    "token_type": "bearer"
}
@router.get("/me")
async def get_me(
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("sub")

    user = await db.users.find_one(
        {"_id": ObjectId(user_id)}
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "user_id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "department_id": str(user["department_id"])
    }