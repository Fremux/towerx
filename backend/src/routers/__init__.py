from fastapi import APIRouter
from routers.view import router as view_router


router = APIRouter(prefix="/api/v1")
router.include_router(view_router, tags=["View"])
