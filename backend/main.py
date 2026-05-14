from fastapi import FastAPI
from backend.api.routes import household
import uvicorn

app = FastAPI(title="Instamart Intelligence API")

app.include_router(household.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Instamart Intelligence API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
