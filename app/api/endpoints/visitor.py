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
from app.models import EstadisticaTrivia
import unicodedata
from typing import Optional
from app.models import RegistroVisitante
from app.models import Especie, InteraccionChatbot

router = APIRouter()

class ResultadoTrivia(BaseModel):
    tipoJuego: str  # Nuevo campo
    idPregunta: int
    opcionCorrecta: int
    respuestaUsuario: int
    acierto: bool

@router.post("/api/trivia")
async def registrar_respuesta_trivia(resultado: ResultadoTrivia, db: Session = Depends(get_db)):
    try:
        nueva_estadistica = EstadisticaTrivia(
            tipo_juego=resultado.tipoJuego, # Nuevo campo
            id_pregunta=resultado.idPregunta,
            opcion_correcta=resultado.opcionCorrecta,
            respuesta_usuario=resultado.respuestaUsuario,
            acierto=resultado.acierto
        )
        db.add(nueva_estadistica)
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}

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
async def inicio(request: Request, origen: Optional[str] = None, db: Session = Depends(get_db)):
    """Muestra el mapa de todas las salas del museo y registra todos los accesos"""
    
    # 1. Definimos la etiqueta lógicamente
    tipo_origen = "qr" if origen == "qr" else "directo"
    
    # 2. Guardamos SIEMPRE en la base de datos, sin condicionales que lo bloqueen
    nuevo_registro = RegistroVisitante(origen=tipo_origen)
    db.add(nuevo_registro)
    db.commit()

    # 3. Retornamos la vista principal
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
    informacion_bd = ""
    especie_encontrada = False # Bandera de control
    
    try:
        # 1. BÚSQUEDA EXACTA Y DIFUSA EN PYTHON
        if request.especie_id != "general":
            especie = db.query(Especie).filter(Especie.id == int(request.especie_id)).first()
            if especie:
                informacion_bd = (
                    f"Especie: {especie.nombre_comun} ({especie.genero} {especie.especie})\n"
                    f"Dieta: {especie.dieta} | Hábitat: {especie.habitat}\n"
                    f"Toxicidad: {especie.nivel_toxicidad} | Curiosidades: {especie.curiosidades}\n"
                )
                especie_encontrada = True
        else:
            pregunta_limpia = limpiar_texto(request.pregunta)
            todas_las_especies = db.query(Especie).all()
            especies_coincidentes = []
            
            for esp in todas_las_especies:
                if limpiar_texto(esp.nombre_comun) in pregunta_limpia:
                    especies_coincidentes.append(esp)
            
            if especies_coincidentes:
                informacion_bd = "\n--- INFORMACIÓN EN LA BASE DE DATOS ---\n"
                for esp in especies_coincidentes:
                    informacion_bd += (
                        f"Especie: {esp.nombre_comun} ({esp.genero} {esp.especie})\n"
                        f"Dieta: {esp.dieta} | Hábitat: {esp.habitat}\n"
                        f"Toxicidad: {esp.nivel_toxicidad} | Curiosidades: {esp.curiosidades}\n---\n"
                    )
                especie_encontrada = True

    except Exception as e:
        print(f"Error CRÍTICO en búsqueda BD: {e}")

    # 2. EL TRUCO MAESTRO: PROMPT DINÁMICO
    # Le quitamos la confusión a la IA. Python le da una orden directa sin condicionales.
    
    if especie_encontrada:
        mensaje_sistema = (
            "Eres el guía virtual experto del Museo de Historia Natural de la Universidad del Cauca. "
            "Tu objetivo es educar de forma precisa, científica y breve (máximo 3 oraciones). "
            "REGLA DE ORO: Tienes la información exacta de la base de datos a continuación. "
            "DEBES formular tu respuesta basándote ESTRICTAMENTE en estos datos:\n"
            f"{informacion_bd}"
        )
    else:
        # Aquí cumplimos tu regla al pie de la letra, forzándola estructuralmente
        mensaje_sistema = (
            "Eres el guía virtual experto del Museo de Historia Natural de la Universidad del Cauca. "
            "Tu objetivo es educar de forma precisa, científica y breve (máximo 3 oraciones). "
            "REGLA DE ORO: El visitante preguntó por un animal que NO tenemos en el catálogo del museo. "
            "DEBES iniciar tu respuesta diciendo textualmente: 'No está en nuestra base de datos, pero...' "
            "y luego debes contestar lo que pide usando tu conocimiento general en biología."
        )

    # 3. LLAMADA A OLLAMA (Usando el endpoint correcto para Chat / Roles)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:11434/api/chat", # <-- CAMBIAMOS /generate POR /chat
                json={
                    "model": "phi3",
                    "messages": [
                        {"role": "system", "content": mensaje_sistema},
                        {"role": "user", "content": request.pregunta}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.4 # Creatividad moderada, segura por el control estricto de roles
                    }
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                return {"respuesta": "Mi cerebro local está descansando. Intenta de nuevo en un momento."}
            
            data = response.json()
            respuesta_generada = data["message"]["content"]
            # --- NUEVO: IMPLEMENTACIÓN HU 22 (Clean Code: Registro asíncrono idealmente, pero síncrono por simplicidad) ---
            # Importa InteraccionChatbot en la parte superior de tu archivo
            try:
                nueva_interaccion = InteraccionChatbot(
                    especie_consultada=str(request.especie_id),
                    pregunta_usuario=request.pregunta,
                    respuesta_ia=respuesta_generada
                )
                db.add(nueva_interaccion)
                db.commit()
            except Exception as error_db:
                print(f"Error no crítico: No se pudo guardar el log del chat. {error_db}")
                db.rollback() # Evita que el servidor colapse si falla la base de datos
            # ---------------------------------------------------------------------------------------------------

            return {"respuesta": respuesta_generada}

        except httpx.ConnectError:
            return {"respuesta": "Error: No puedo conectar con Ollama."}
        except Exception as e:
            return {"respuesta": f"Tuve un mareo científico. Error: {str(e)}"}