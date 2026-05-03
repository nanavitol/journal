from fastapi import FastAPI
from app.api.v1 import auth, admin, worker, users

app = FastAPI(title="Вахтенный журнал ВОСВОД", version="0.1.0")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(worker.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Вахтенный журнал ВОСВОД API"}