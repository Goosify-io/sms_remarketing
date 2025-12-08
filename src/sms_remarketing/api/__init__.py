from fastapi import APIRouter
from .clients import router as clients_router
from .leads import router as leads_router
from .templates import router as templates_router
from .messages import router as messages_router
from .triggers import router as triggers_router
from .credits import router as credits_router
from .webhooks import router as webhooks_router

api_router = APIRouter()

api_router.include_router(clients_router, prefix="/clients", tags=["clients"])
api_router.include_router(leads_router, prefix="/leads", tags=["leads"])
api_router.include_router(templates_router, prefix="/templates", tags=["templates"])
api_router.include_router(messages_router, prefix="/messages", tags=["messages"])
api_router.include_router(triggers_router, prefix="/triggers", tags=["triggers"])
api_router.include_router(credits_router, prefix="/credits", tags=["credits"])
api_router.include_router(webhooks_router, prefix="/webhooks", tags=["webhooks"])

__all__ = ["api_router"]
