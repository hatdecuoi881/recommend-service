from fastapi import FastAPI
from routers import qdrant_router
app = FastAPI()

# Include the Qdrant API routes
app.include_router(qdrant_router.router, prefix="/qdrant", tags=["Qdrant"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Qdrant API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
