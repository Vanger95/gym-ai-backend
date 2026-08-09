from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.trainer import Trainer
from app.repositories.trainer_repository import TrainerRepository
from app.schemas.auth import (
    TokenResponse,
    TrainerLoginRequest,
    TrainerRegisterRequest,
    TrainerResponse,
)


class AuthService:
    def __init__(
        self,
        repository: TrainerRepository,
    ) -> None:
        self.repository = repository

    async def register(
        self,
        request: TrainerRegisterRequest,
    ) -> TrainerResponse:
        email = request.email.lower().strip()

        existing = await self.repository.get_by_email(
            email
        )

        if existing is not None:
            raise ValueError(
                "A trainer with this email already exists."
            )

        trainer = Trainer(
            email=email,
            hashed_password=hash_password(
                request.password
            ),
            display_name=request.display_name.strip(),
        )

        created = await self.repository.create(
            trainer
        )

        return TrainerResponse(
            id=created.id,
            email=created.email,
            display_name=created.display_name,
            is_active=created.is_active,
        )

    async def login(
        self,
        request: TrainerLoginRequest,
    ) -> TokenResponse:
        email = request.email.lower().strip()

        trainer = await self.repository.get_by_email(
            email
        )

        if trainer is None:
            raise ValueError(
                "Invalid email or password."
            )

        if not verify_password(
            request.password,
            trainer.hashed_password,
        ):
            raise ValueError(
                "Invalid email or password."
            )

        if not trainer.is_active:
            raise ValueError(
                "Trainer account is inactive."
            )

        token = create_access_token(
            trainer.id
        )

        return TokenResponse(
            access_token=token,
        )