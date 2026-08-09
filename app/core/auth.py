from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.database.session import get_db_session
from app.models.trainer import Trainer
from app.repositories.trainer_repository import TrainerRepository


# oauth2_scheme = OAuth2PasswordBearer(
#     tokenUrl="/auth/login"
# )
bearer_scheme = HTTPBearer()

# async def get_current_trainer(
#     token: str = Depends(bearer_scheme),
#     session: AsyncSession = Depends(get_db_session),
# ) -> Trainer:
#     try:
#         trainer_id = decode_access_token(
#             token
#         )
#     except Exception as error:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired access token.",
#             headers={"WWW-Authenticate": "Bearer"},
#         ) from error

#     repository = TrainerRepository(session)

#     trainer = await repository.get_by_id(
#         trainer_id
#     )

#     if trainer is None or not trainer.is_active:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or inactive trainer account.",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     return trainer


async def get_current_trainer(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> Trainer:
    token = credentials.credentials

    try:
        trainer_id = decode_access_token(token)

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    repository = TrainerRepository(session)

    trainer = await repository.get_by_id(
        trainer_id
    )

    if trainer is None or not trainer.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive trainer account.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return trainer