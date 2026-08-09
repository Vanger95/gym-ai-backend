from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_trainer
from app.database.session import get_db_session
from app.models.trainer import Trainer
from app.repositories.trainer_repository import TrainerRepository
from app.schemas.auth import (
    TokenResponse,
    TrainerLoginRequest,
    TrainerRegisterRequest,
    TrainerResponse,
)
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/register",
    response_model=TrainerResponse,
    status_code=201,
)
async def register(
    request: TrainerRegisterRequest,
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> TrainerResponse:
    repository = TrainerRepository(session)
    service = AuthService(repository)

    try:
        return await service.register(request)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    request: TrainerLoginRequest,
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> TokenResponse:
    repository = TrainerRepository(session)
    service = AuthService(repository)

    try:
        return await service.login(request)

    except ValueError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
        ) from error


@router.get(
    "/me",
    response_model=TrainerResponse,
)
async def me(
    trainer: Trainer = Depends(
        get_current_trainer
    ),
) -> TrainerResponse:
    return TrainerResponse(
        id=trainer.id,
        email=trainer.email,
        display_name=trainer.display_name,
        is_active=trainer.is_active,
    )