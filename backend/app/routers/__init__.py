from .upload import router as upload_router
from .scan import router as scan_router
from .reports import router as reports_router
from .dashboard import router as dashboard_router

__all__ = ["upload_router", "scan_router", "reports_router", "dashboard_router"]
