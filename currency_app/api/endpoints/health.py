from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated

from currency_app.broker.admin import KafkaAdmin
from currency_app.core.dependency import get_broker_admin


health_router = APIRouter(
    prefix='/health',
    tags=['health']
)

@health_router.get('/check')
async def topic_presence_check(
        admin_client: Annotated[KafkaAdmin, Depends(get_broker_admin)]
):
    all_topics = await admin_client.get_topics()
    if 'currency_info' in all_topics:
        return {'status': 'healthy'}
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={'status': 'unhealthy'}
    )
