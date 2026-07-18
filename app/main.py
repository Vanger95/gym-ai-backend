from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


from app.api.clients import router as clients_router
from app.core.config import get_settings
from app.database.session import get_db_session
from app.api.documents import router as documents_router


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(clients_router)
app.include_router(documents_router)

@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/database-check")
async def database_check(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    await session.execute(text("SELECT 1"))

    return {
        "status": "connected",
        "database": "sqlite",
    }