from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Especie, UsuarioAdmin
from app.schemas import EspecieCreate

router = APIRouter()

# Configuramos el motor de plantillas
templates = Jinja2Templates(directory="templates")

# ==========================================
# RUTAS DE LOGIN Y SEGURIDAD (HU 7)
# ==========================================

@router.get("/login", response_class=HTMLResponse, summary="Mostrar pantalla de Login")
async def mostrar_login(request: Request):
    """Renderiza el archivo login.html"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", summary="Validar credenciales del Administrador")
async def procesar_login(
    request: Request,
    correo: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    """Verifica si el correo y la contraseña coinciden con la base de datos"""
    
    # 1. Buscamos al usuario en PostgreSQL
    usuario_db = db.query(UsuarioAdmin).filter(UsuarioAdmin.correo == correo).first()

    # 2. Validamos si existe y si la clave es correcta
    if not usuario_db or usuario_db.password_hash != password:
        # Si falla, recargamos la página pasándole la variable "error"
        return templates.TemplateResponse("login.html", {"request": request, "error": "Correo o contraseña incorrectos"})

    # 3. Si todo es correcto, lo redirigimos al panel de importación
    return RedirectResponse(url="/admin/importar", status_code=status.HTTP_302_FOUND)


# ==========================================
# RUTAS DE GESTIÓN DE ESPECIES (HU 2)
# ==========================================

@router.post("/especies/", summary="Crear especie individualmente", status_code=status.HTTP_201_CREATED)
async def crear_especie_manual(especie: EspecieCreate, db: Session = Depends(get_db)):
    """
    Permite al administrador agregar una especie manual sin usar el CSV.
    """
    # Verificar si ya existe para evitar errores
    especie_existente = db.query(Especie).filter(
        Especie.genero == especie.genero,
        Especie.especie == especie.especie
    ).first()

    if especie_existente:
        raise HTTPException(status_code=400, detail="La especie ya existe en el catálogo.")

    nueva_especie = Especie(**especie.model_dump())
    db.add(nueva_especie)
    db.commit()
    db.refresh(nueva_especie)
    
    return nueva_especie