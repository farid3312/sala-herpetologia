from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Importaciones de tu arquitectura modular
from app.api.api_router import api_router
from app.database import engine, Base

# 1. Creación de tablas en PostgreSQL
# Esto asegura que al arrancar, las tablas existan antes de cualquier petición
Base.metadata.create_all(bind=engine)

# 2. Inicialización de la Aplicación
app = FastAPI(
    title="Sistema Museo Herpetología",
    version="1.0.0"
)

# 3. Configuración de Archivos Estáticos y Plantillas
# Debe ir después de inicializar 'app'
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 4. Inclusión de Rutas de la API (Backend)
# Aquí se conectan los endpoints de administración, importación y visitantes
app.include_router(api_router)

# 5. Rutas de Interfaz (Frontend con Jinja2)
# Estas rutas sirven los HTML para que puedas realizar las pruebas
@app.get("/")
def read_root():
    return {"mensaje": "API Operativa. Ve a /admin/importar para la interfaz web."}

@app.get("/admin/importar")
async def view_importar(request: Request):
    """
    Renderiza la interfaz de carga de CSV para el Sprint 1
    """
    return templates.TemplateResponse("importar.html", {"request": request})