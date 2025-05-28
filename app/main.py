from fastapi import FastAPI

from app.users.router import router as users_router
from app.posts.router import router as posts_router


app = FastAPI(title="Blog API Service")

app.include_router(users_router)
app.include_router(posts_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Blog API Service!"}
