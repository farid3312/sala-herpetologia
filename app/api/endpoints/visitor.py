from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates

router = APIRouter()

# Configuramos el motor de plantillas igual que en main.py
templates = Jinja2Templates(directory="templates")

# ==========================================
# BASE DE DATOS SIMULADA (MOCK DB - FASE 1)
# ==========================================
especies_mock = [
    {
        "id": 1,
        "nombre_comun": "Rana Dardo Dorada",
        "nombre_cientifico": "Phyllobates terribilis",
        "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Phyllobates_terribilis_02.jpg/800px-Phyllobates_terribilis_02.jpg",
        "dieta": "Pequeños insectos, principalmente hormigas.",
        "habitat": "Selvas tropicales húmedas de la costa pacífica.",
        "curiosidades": "Es considerado el vertebrado más tóxico del mundo."
    },
    {
        "id": 2,
        "nombre_comun": "Iguana Verde",
        "nombre_cientifico": "Iguana iguana",
        "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Portrait_of_an_Iguana.jpg/800px-Portrait_of_an_Iguana.jpg",
        "dieta": "Herbívora (hojas, flores, frutos).",
        "habitat": "Bosques tropicales, áreas con vegetación densa cerca del agua.",
        "curiosidades": "Poseen una excelente visión y pueden ver sombras a grandes distancias."
    }
]

# ==========================================
# RUTAS DEL VISITANTE TRADUCIDAS
# ==========================================

# 1. Página Principal (Menú de Salas)
@router.get("/")
async def inicio(request: Request):
    # En FastAPI siempre debemos pasar el objeto "request" al template
    return templates.TemplateResponse("salas.html", {"request": request})

# 2. Salas en Construcción
@router.get("/sala/{nombre_sala}")
async def sala_proximamente(request: Request, nombre_sala: str):
    nombres_bonitos = {
        "ornitologia": "Ornitología",
        "entomologia": "Entomología",
        "mastozoologia": "Mastozoología",
        "paleontologia": "Geología y Paleontología",
        "oceanografia": "Oceanografía",
        "arqueologia": "Arqueología"
    }
    nombre_mostrar = nombres_bonitos.get(nombre_sala.lower(), nombre_sala.capitalize())
    return templates.TemplateResponse("proximamente.html", {"request": request, "sala": nombre_mostrar})

# 3. Sala de Herpetología (Galería)
@router.get("/herpetologia")
async def galeria(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "especies": especies_mock})

# 4. Ficha Técnica Individual
@router.get("/especie/{id_especie}")
async def detalle_especie(request: Request, id_especie: int):
    especie_encontrada = next((e for e in especies_mock if e["id"] == id_especie), None)
    if especie_encontrada is None:
        raise HTTPException(status_code=404, detail="Especie no encontrada")
    
    return templates.TemplateResponse("detalle.html", {"request": request, "especie": especie_encontrada})