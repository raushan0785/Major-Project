"""FastAPI application entry point with MongoDB wiring."""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from . import mongo
from .routers import auth as auth_router
from .routers import transcribe
from .routers import srs
from .routers import analysis
from .routers import export
from .routers import grammar

app = FastAPI(title="GenAI SRS Backend (Mongo Auth)")

# Routers
app.include_router(auth_router.router)
app.include_router(transcribe.router)
app.include_router(srs.router)
app.include_router(analysis.router)
app.include_router(export.router)
app.include_router(grammar.router)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, allow all. In production, specify frontend URL.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    # Initialize Mongo connection once when app starts
    await mongo.connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    # Clean up Mongo client
    await mongo.close_mongo_connection()


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    """Very simple health check (no DB ping to avoid hangs)."""
    return {"status": "ok"}
