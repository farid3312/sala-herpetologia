from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

# Importaciones corregidas según la estructura real del proyecto
from app.database import get_db
from app.models import Especie

router = APIRouter()

# Configuración del motor de plantillas
templates = Jinja2Templates(directory="templates")

# ==========================================
# RUTAS DEL VISITANTE (SALA PÚBLICA)
# ==========================================

# 1. Menú Principal de Salas
@router.get("/", response_class=HTMLResponse)
async def inicio(request: Request):
    """Muestra el mapa de todas las salas del museo"""
    return templates.TemplateResponse("salas.html", {"request": request})

# 2. Sala de Herpetología (Galería con datos de PostgreSQL)
@router.get("/herpetologia", response_class=HTMLResponse)
async def galeria(request: Request, db: Session = Depends(get_db)):
    """
    Obtiene todas las especies reales desde la base de datos 
    para alimentar las tarjetas dinámicas en el index.html.
    """
    especies_db = db.query(Especie).all()
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "especies": especies_db
    })

# 3. Ficha Técnica Individual
@router.get("/especie/{id_especie}", response_class=HTMLResponse)
async def detalle_especie(request: Request, id_especie: int, db: Session = Depends(get_db)):
    """
    Busca una especie por su ID para mostrar su información detallada.
    """
    especie_encontrada = db.query(Especie).filter(Especie.id == id_especie).first()
    
    if not especie_encontrada:
        raise HTTPException(
            status_code=404, 
            detail="La especie solicitada no se encuentra en el catálogo."
        )
    
    return templates.TemplateResponse("detalle.html", {
        "request": request, 
        "especie": especie_encontrada
    })

# 4. Salas en Construcción (Dinámicas)
@router.get("/sala/{nombre_sala}", response_class=HTMLResponse)
async def sala_proximamente(request: Request, nombre_sala: str):
    """Maneja los nombres de las salas que aún no tienen lógica de base de datos"""
    nombres_map = {
        "ornitologia": "Ornitología",
        "entomologia": "Entomología",
        "mastozoologia": "Mastozoología",
        "paleontologia": "Geología y Paleontología",
        "oceanografia": "Oceanografía",
        "arqueologia": "Arqueología"
    }
    nombre_mostrar = nombres_map.get(nombre_sala.lower(), nombre_sala.capitalize())
    
    return templates.TemplateResponse("proximamente.html", {
        "request": request, 
        "sala": nombre_mostrar
    })