from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
import httpx

# Importaciones corregidas según la estructura real del proyecto
from app.database import get_db
from app.models import Especie
from pydantic import BaseModel
import unicodedata

router = APIRouter()

class ChatRequest(BaseModel):
    pregunta: str
    especie_id: str

def limpiar_texto(texto: str) -> str:
    """Elimina tildes, mayúsculas y espacios invisibles a los lados."""
    if not texto: return ""
    texto_normalizado = unicodedata.normalize('NFD', str(texto))
    texto_sin_tildes = ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
    return texto_sin_tildes.lower().strip() # .strip() es la clave aquí

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
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import httpx
# IMPORTANTE: Asegúrate de importar tu sesión de BD y tu modelo
# from app.db.database import get_db
# from app.models.especie import Especie

# (Tus rutas anteriores y el modelo ChatRequest van aquí)

@router.post("/api/chat")
async def procesar_chat(request: ChatRequest, db: Session = Depends(get_db)):
    # 1. Reglas estrictas, cortas y sin contradicciones lógicas
    contexto_base = (
        "Eres el guía virtual experto del Museo de Historia Natural de la Universidad del Cauca. "
        "Tu objetivo es educar a los visitantes de forma precisa, científica y breve (máximo 3 oraciones) para que conteste rapido. "
        "REGLA 1 (Prioridad Absoluta): Para describir el hábitat, dieta, nivel de toxicidad o curiosidades "
        "específicas del animal, DEBES usar estrictamente la 'INFORMACIÓN DE LA ESPECIE' proporcionada en la base de datos y relaciona los nombre parecidos de las especies por si estan mal escritos. "
        "ademas si no hay una especie en la base de datos por la cual se pregunto, en el mensaje tiene que decir no esta en nuestra base de datos brevemente y de primero en el mensaje, ese mensaje es de IMPORTANCIA, pero si contesta lo que pide"
        "REGLA 2 (Conocimiento Extra): Si el visitante hace una pregunta sobre biología general, evolución, "
        "o pide detalles científicos que no están en la información proporcionada, PUEDES usar tu conocimiento "
        "científico previo para responder y complementar de forma educativa. "
        "REGLA 3: Nunca inventes datos numéricos ni geográficos si no estás 100% seguro, " 
    )
    
    informacion_bd = ""
    
    try:
        if request.especie_id != "general":
            especie = db.query(Especie).filter(Especie.id == int(request.especie_id)).first()
            if especie:
                informacion_bd = (
                    f"Especie: {especie.nombre_comun} ({especie.genero} {especie.especie})\n"
                    f"Dieta: {especie.dieta} | Hábitat: {especie.habitat}\n"
                    f"Toxicidad: {especie.nivel_toxicidad} | Curiosidades: {especie.curiosidades}\n"
                )
            else:
                informacion_bd = "[INSTRUCCIÓN PARA LA IA: Dile al visitante que no tenemos datos de esa especie.]"
        
        else:
            # Tu buscador funciona perfecto, lo dejamos igual usando request.pregunta
            pregunta_limpia = limpiar_texto(request.pregunta)
            
            todas_las_especies = db.query(Especie).all()
            especies_encontradas = []
            
            for esp in todas_las_especies:
                nombre_limpio = limpiar_texto(esp.nombre_comun)
                if nombre_limpio in pregunta_limpia:
                    especies_encontradas.append(esp)
            
            if especies_encontradas:
                informacion_bd = "\n--- INFORMACIÓN ENCONTRADA EN LA BASE DE DATOS ---\n"
                for esp in especies_encontradas:
                    informacion_bd += (
                        f"Especie: {esp.nombre_comun} ({esp.genero} {esp.especie})\n"
                        f"Dieta: {esp.dieta} | Hábitat: {esp.habitat}\n"
                        f"Toxicidad: {esp.nivel_toxicidad}\n"
                        f"Curiosidades: {esp.curiosidades}\n"
                        f"---\n"
                    )
            else:
                # El backend maneja el error, no le pedimos a la IA que decida
                informacion_bd = "\n[INSTRUCCIÓN PARA LA IA: La especie consultada NO está en la base de datos. Informa esto amablemente y usa tu conocimiento general para responder la pregunta biológica del usuario.]\n"

    except Exception as e:
        print(f"Error CRÍTICO en búsqueda BD: {e}")

    # 3. Ensamblaje claro (Separando el contexto de la pregunta con etiquetas)
    prompt_final = f"INSTRUCCIONES:\n{contexto_base}\n\n{informacion_bd}\n\nPREGUNTA DEL VISITANTE: {request.pregunta}\n\nRESPUESTA DEL GUÍA:"

    # 4. Llamada a Ollama (IA Local)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "phi3",
                    "prompt": prompt_final,
                    "stream": False,
                    "options": {
                        "temperature": 0.1 # <-- CLAVE: Reducimos la creatividad casi a cero para matar al "loro habilidoso"
                    }
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                return {"respuesta": "Mi cerebro local está descansando. Intenta de nuevo en un momento."}
            
            data = response.json()
            return {"respuesta": data["response"]}

        except httpx.ConnectError:
            return {"respuesta": "Error: No puedo conectar con Ollama."}
        except Exception as e:
            return {"respuesta": f"Tuve un mareo científico. Error: {str(e)}"}