import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from procurement_ai_api.core.database import db_manager
from procurement_ai_api.core.config import settings
from procurement_ai_api.api.routes.chat import router as chat_router
from procurement_ai_api.core.logging_config import setup_logging


# Configure logging once
setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        logger.info("Connecting to MongoDB...")
        await db_manager.connect()
        logger.info("MongoDB connected successfully")

    except Exception:
        logger.exception("Failed to connect to MongoDB")
        raise

    try:
        yield

    finally:
        # Shutdown
        logger.info("Closing MongoDB connection...")
        await db_manager.close()
        logger.info("MongoDB connection closed")


app = FastAPI(lifespan=lifespan)




app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)