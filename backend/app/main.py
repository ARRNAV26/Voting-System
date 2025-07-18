from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import init_db
from app.config import settings
from app.api import auth, suggestions, votes, websocket

app = FastAPI(
    title="Voting System API",
    description="Real-time voting system for internal suggestions",
    version="1.0.0"
)

@app.on_event("startup")
async def on_startup():
    await init_db()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(suggestions.router, prefix="/api")
app.include_router(votes.router, prefix="/api")
app.include_router(websocket.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Voting System API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 