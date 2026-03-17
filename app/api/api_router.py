from fastapi import APIRouter
# Se elimina 'visitor' de la importación temporalmente
from app.api.endpoints import admin, data_import

api_router = APIRouter()

# Agrupamos las rutas de importación bajo el prefijo /admin/datos
api_router.include_router(data_import.router, prefix="/admin/datos", tags=["Importación"])

# Agrupamos las rutas de administración general bajo /admin
api_router.include_router(admin.router, prefix="/admin", tags=["Administración"])

# (El visitor.py se incluirá aquí cuando iniciemos el desarrollo de esa interfaz)
# api_router.include_router(visitor.router, prefix="/public", tags=["Visitantes"])