from fastapi import APIRouter
# CORRECCIÓN: Ahora sí importamos 'visitor' junto a admin y data_import
from app.api.endpoints import admin, data_import, visitor

api_router = APIRouter()

# Agrupamos las rutas de importación bajo el prefijo /admin/datos
api_router.include_router(data_import.router, prefix="/admin/datos", tags=["Importación"])

# Agrupamos las rutas de administración general bajo /admin
api_router.include_router(admin.router, prefix="/admin", tags=["Administración"])

# Conectamos las rutas públicas de los visitantes (sin prefijo para que / sea la raíz)
api_router.include_router(visitor.router, tags=["Visitantes"])