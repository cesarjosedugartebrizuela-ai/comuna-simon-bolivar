from ninja import NinjaAPI
from apps.cuenta.api import router as cuenta_router
from apps.carga_familiar.api import router as carga_router
from apps.constancias.api import router as constancias_router

api = NinjaAPI(
    title="API de Constancias de Residencia",
    description="API para la gestión de usuarios, carga familiar y constancias.",
    version="1.0.0"
)

api.add_router("/cuenta", cuenta_router, tags=["Cuenta"])
api.add_router("/carga-familiar", carga_router, tags=["Carga Familiar"])
api.add_router("/constancias", constancias_router, tags=["Constancias"])