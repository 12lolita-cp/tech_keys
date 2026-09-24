from fastapi import FastAPI

from app.routes.auth import router as auth_router

from app.routes.requests import router as requests_router

app = FastAPI(
    title="Hospital Support Request System"
)


app.include_router(auth_router)
app.include_router(requests_router)

@app.get("/")
async def root():
    return {
        "message": "Hospital Support Request System API"
    }