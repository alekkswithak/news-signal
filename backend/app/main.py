from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.dependencies import get_mongo_client, close_mongo_client
from app.routers import articles


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database connection
    await get_mongo_client()
    # Create unique index on url to prevent duplicates
    client = await get_mongo_client()
    collection = client[settings.mongodb_db_name]["analyzed_articles"]
    await collection.create_index("url", unique=True)
    yield
    # Close database connection
    await close_mongo_client()


app = FastAPI(title="News Signal API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
