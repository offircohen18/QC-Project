import os
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from shared.database import init_db
from api_server.routes import router as tasks_router

load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI):
    # This code runs on startup
    print("API Server is starting up...")
    init_db()
    print("Database initialized successfully.")
    yield
    # This code runs on shutdown
    print("API Server is shutting down...")


app = FastAPI(
    title="Quantum Task API",
    description="API for managing and executing quantum circuits asynchronously",
    lifespan=lifespan
)

app.include_router(tasks_router)


@app.get("/health")
def health_check():
    """Simple health check endpoint to verify server status."""
    return {"status": "ok", "service": "quantum-api"}


if __name__ == "__main__":
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", 8000))
    debug_mode = os.getenv("DEBUG", "True").lower() == "true"

    print(f"Running API on http://{host}:{port}")
    uvicorn.run("api_server.main:app", host=host, port=port, reload=debug_mode)