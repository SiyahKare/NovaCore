"""
NovaCore - Main Application Entry Point
The Kernel of Nova Ecosystem
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import close_db, init_db
from app.core.logging import get_logger, setup_logging

# Import routers
from app.identity.routes import router as identity_router
from app.wallet.routes import router as wallet_router
from app.xp_loyalty.routes import router as loyalty_router
from app.nova_credit.routes import router as credit_router  # NovaCredit = Kalp
from app.agency.routes import router as agency_router
from app.events.routes import router as events_router
from app.admin.routes import router as admin_router
from app.treasury.routes import router as treasury_router  # Treasury = Devletin Kan Dolaşımı
from app.consent.router import router as consent_router
from app.nova_score.router import router as nova_score_router
from app.justice.router import router as justice_router
from app.flirtmarket.routes import router as flirtmarket_router
from app.telemetry.router import router as telemetry_router
from app.telegram_gateway.router import router as telegram_router
from app.admin.event_routes import router as admin_event_router

# Setup logging
setup_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("novacore_starting", environment=settings.ENV)

    # Initialize database (dev only - use Alembic in prod)
    if settings.is_dev:
        try:
            await init_db()
            logger.info("database_initialized")
        except Exception as e:
            logger.warning("database_init_failed", error=str(e))
            logger.warning("Backend will start but database operations may fail. Start PostgreSQL with: docker-compose up -d postgres")

    yield

    # Shutdown
    logger.info("novacore_shutting_down")
    try:
        await close_db()
    except Exception:
        pass  # Ignore shutdown errors


# Create FastAPI app
app = FastAPI(
    title="NovaCore",
    description="""
    **NovaCore** - The Kernel of Nova Ecosystem
    
    ## Responsibilities
    
    - **Identity/SSO**: Telegram ID ↔ internal user_id, JWT token generation
    - **Wallet/NCR Ledger**: NCR balance, spend, earn, rake, fee, treasury
    - **Treasury**: Devletin ekonomik dolaşım sistemi - revenue routing, pool management
    - **NovaCredit**: Davranış skoru (0-1000), tier, risk, reputation
    - **XP/Loyalty**: XP events, level, tier (Bronze/Silver/Gold/Diamond)
    - **Agency**: Agency, Performer, operator models, revenue sharing
    - **Events**: FlirtMarket, OnlyVips, PokerVerse, Aurora event ingest
    - **Admin**: Treasury summary, top users, health & stats
    
    ## Event Flow
    
    ```
    App → POST /events/* → treasury.route_revenue() → wallet + xp + nova_credit
    ```
    
    FlirtMarket, OnlyVips, PokerVerse, Aurora → POST events to NovaCore
    Treasury → Revenue routing, tax calculation, pool distribution, token burn
    """,
    version="0.1.0",
    docs_url="/docs" if settings.is_dev else None,
    redoc_url="/redoc" if settings.is_dev else None,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(identity_router)
app.include_router(wallet_router)
app.include_router(treasury_router)  # Treasury - Devletin Kan Dolaşımı
app.include_router(loyalty_router)
app.include_router(credit_router)  # NovaCredit - Davranış Skoru
app.include_router(agency_router)
app.include_router(events_router)
app.include_router(admin_router)
app.include_router(consent_router)  # Consent - Onay ve Veri Etiği Yönetimi
app.include_router(nova_score_router)  # NovaScore - Kullanıcı Reputasyon Skoru
app.include_router(justice_router)  # Justice - Adalet Modülü ve CP Motoru
app.include_router(flirtmarket_router)  # FlirtMarket - Example endpoints with enforcement
app.include_router(telemetry_router)  # Telemetry - Growth & Education Event Tracking
app.include_router(telegram_router)  # Telegram Gateway - Bot ↔ NovaCore Bridge
app.include_router(admin_event_router)  # Admin Event Management


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "name": "NovaCore",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs" if settings.is_dev else "disabled",
    }


@app.get("/health", tags=["health"])
async def health():
    """Quick health check."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_dev,
    )

