from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path
# 1. El Middleware para el túnel y el celular
from fastapi.middleware.cors import CORSMiddleware

# 2. ¡ESTA ES LA LÍNEA QUE SE BORRÓ! El guardia de seguridad
from app.api.endpoints.admin import verificar_sesion_admin

# Importaciones de tu arquitectura modular
from app.api.api_router import api_router
from app.database import engine, Base


Path("data").mkdir(exist_ok=True)
# 1. Creación de tablas en PostgreSQL
# Esto asegura que al arrancar, las tablas existan antes de cualquier petición
Base.metadata.create_all(bind=engine)

# 2. Inicialización de la Aplicación
app = FastAPI(
    title="Sistema Museo Herpetología",
    version="1.0.0"
)

# 3. Configuración de CORS (Cross-Origin Resource Sharing)
# ESTO ES CRÍTICO PARA EL TÚNEL Y DISPOSITIVOS MÓVILES.
# Permite que el navegador del celular cargue recursos (como imágenes) sin bloquearlos por políticas de seguridad cruzada.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite peticiones desde cualquier origen (tu URL del túnel)
    allow_credentials=True, # Necesario si vas a seguir usando Cookies para la sesión
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todas las cabeceras (incluyendo Authorization si usas JWT)
)

# 4. Configuración de Archivos Estáticos 
# El orden es importante. Las imágenes locales se sirven desde aquí.
app.mount("/data", StaticFiles(directory="data"), name="data")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 5. Configuración de Plantillas Jinja2
templates = Jinja2Templates(directory="templates")

# 6. Inclusión de Rutas de la API (Backend)
# Aquí se conectan los endpoints de administración, importación y visitantes
app.include_router(api_router)

# 7. Rutas de Interfaz (Frontend con Jinja2)

@app.get("/admin/importar")
async def view_importar(
    request: Request,
    admin_token: str = Depends(verificar_sesion_admin) # <-- GUARDIA INYECTADO AQUÍ
):
    """
    Renderiza la interfaz de carga de CSV para el Sprint 1
    """
    return templates.TemplateResponse("importar.html", {"request": request})