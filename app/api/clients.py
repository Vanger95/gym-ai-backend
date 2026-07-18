from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.schemas.client import ClientCreate, ClientResponse
from app.services.client_service import ClientService

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
) -> ClientResponse:
    service = ClientService(session)
    return await service.create_client(payload)