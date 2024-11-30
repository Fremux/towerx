from fastapi import APIRouter
from routers.process import router as process_router
from routers.view import router as view_router


router = APIRouter(prefix="/api/v1")
router.include_router(process_router, tags=["Process"])
router.include_router(view_router, tags=["View"])
