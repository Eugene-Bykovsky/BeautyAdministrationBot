from .handlers_start import router as start_router
from .handlers_master import router as master_router
from .handlers_salons import router as salon_router
from .handlers_phone import router as phone_router


__all__ = ["start_router", "master_router", "salon_router", "phone_router"]
