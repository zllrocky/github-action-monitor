from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.deliveries.models import WebhookDelivery


async def insert_delivery(session: AsyncSession,
                          github_delivery_id: str,
                          payload: dict[str, Any]
                          ) -> bool:
    query = (
        insert(WebhookDelivery)
        .values(github_delivery_id=github_delivery_id, payload=payload)
        .on_conflict_do_nothing(index_elements=["github_delivery_id"])
    ).returning(WebhookDelivery.id)

    result = await session.execute(query)
    return result.scalar_one_or_none() is not None
