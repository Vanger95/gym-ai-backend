from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.schemas.client import ClientCreate, ClientResponse
from app.services.client_service import ClientService

from app.core.auth import get_current_trainer
from app.models.trainer import Trainer

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
)


@router.post(
    "",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_client(
    payload: ClientCreate,
    session: AsyncSession = Depends(get_db_session),
    trainer: Trainer = Depends(get_current_trainer),
) -> ClientResponse:
    service = ClientService(session)

    return await service.create_client(
        payload,
        trainer_id=trainer.id,
    )


@router.get(
    "",
    response_model=list[ClientResponse],
)

async def list_clients(
    session: AsyncSession = Depends(get_db_session),
    trainer: Trainer = Depends(get_current_trainer),
) -> list[ClientResponse]:
    service = ClientService(session)

    return await service.list_clients(
        trainer_id=trainer.id,
    )




@router.get(
    "/{client_id}",
    response_model=ClientResponse,
)

async def get_client(
    client_id: str,
    session: AsyncSession = Depends(get_db_session),
    trainer: Trainer = Depends(get_current_trainer),
) -> ClientResponse:
    service = ClientService(session)

    client = await service.get_client(
        client_id=client_id,
        trainer_id=trainer.id,
    )

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Client not found.",
        )

    return client



@router.patch(
    "/{client_id}",
    response_model=ClientResponse,
)
async def update_client(
    client_id: str,
    payload: ClientCreate,
    session: AsyncSession = Depends(get_db_session),
    trainer: Trainer = Depends(get_current_trainer),
) -> ClientResponse:
    service = ClientService(session)

    updated = await service.update_client(
        client_id=client_id,
        trainer_id=trainer.id,
        payload=payload,
    )

    if updated is None:
        raise HTTPException(status_code=404, detail="Client not found.")

    return updated


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_client(
    client_id: str,
    session: AsyncSession = Depends(get_db_session),
    trainer: Trainer = Depends(get_current_trainer),
) -> None:
    service = ClientService(session)

    deleted = await service.delete_client(
        client_id=client_id,
        trainer_id=trainer.id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Client not found.")

    return None


