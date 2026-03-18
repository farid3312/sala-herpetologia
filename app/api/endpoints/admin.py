from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Especie, UsuarioAdmin
from app.schemas import EspecieCreate
from app.services import especie_service # Importamos tu nuevo servicio
from app.schemas import EjemplarBase # Asegúrate de importar esto arriba
from app.services import ejemplar_service # Importamos el nuevo servicio
from app.schemas import EspecieUpdate # <-- Importante arriba
from app.schemas import EjemplarUpdate # <-- Importante arriba

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

    # 3. Si todo es correcto, lo redirigimos al panel principal de admin
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)

@router.get("/dashboard", response_class=HTMLResponse, summary="Panel principal de Administrador")
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """
    Carga el panel de administración y obtiene todas las especies 
    directamente de la base de datos para mostrarlas en la tabla.
    """
    # Consultamos todas las especies de la tabla 'especies'
    especies_db = db.query(Especie).all()
    
    # Enviamos la lista de especies al template admin.html
    return templates.TemplateResponse("admin.html", {
        "request": request, 
        "especies": especies_db
    })


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

@router.post("/especies/{especie_id}/ejemplares", summary="Añadir ejemplar físico", status_code=status.HTTP_201_CREATED)
def crear_ejemplar_endpoint(especie_id: int, ejemplar_in: EjemplarBase, db: Session = Depends(get_db)):
    """
    Registra un espécimen físico (frasco, taxidermia, etc.) y lo vincula a una especie existente.
    El ID de la especie se toma de la URL para garantizar la integridad de la relación.
    """
    try:
        # Extraemos el diccionario validado por Pydantic
        datos_dict = ejemplar_in.model_dump()
        
        # Delegamos al motor lógico
        nuevo_ejemplar = ejemplar_service.crear_ejemplar(db, especie_id, datos_dict)
        
        return {
            "estado": "exito",
            "mensaje": f"El ejemplar con código {nuevo_ejemplar.numero_coleccion} fue vinculado a la especie ID {especie_id}.",
            "numero_coleccion": nuevo_ejemplar.numero_coleccion  # Corregido: Usamos la llave primaria real
        }
    except ValueError as e:
        # Error de negocio (ej. especie no existe o código repetido)
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # Error de base de datos
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/especies/{especie_id}", summary="Eliminar especie del catálogo", status_code=status.HTTP_200_OK)
def borrar_especie_endpoint(especie_id: int, db: Session = Depends(get_db)):
    """
    Elimina una especie de forma segura. 
    Retornará error si la especie tiene ejemplares vinculados.
    """
    try:
        # Delegamos la responsabilidad de validación al servicio
        especie_eliminada = especie_service.eliminar_especie(db, especie_id)
        
        return {
            "estado": "exito",
            "mensaje": f"La especie '{especie_eliminada.genero} {especie_eliminada.especie}' fue eliminada permanentemente del sistema."
        }
    except ValueError as e:
        # Error 400: Violación de regla de negocio (ej. tiene ejemplares o no existe)
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # Error 500: Falla de infraestructura
        raise HTTPException(status_code=500, detail=str(e))
@router.delete("/ejemplares/{numero_coleccion}", summary="Dar de baja un ejemplar", status_code=status.HTTP_200_OK)
def borrar_ejemplar_endpoint(numero_coleccion: str, db: Session = Depends(get_db)):
    """
    Elimina un espécimen físico de la base de datos usando su número de colección.
    """
    try:
        # Nota: no usamos especie_service, usamos ejemplar_service
        ejemplar_eliminado = ejemplar_service.eliminar_ejemplar(db, numero_coleccion)
        
        return {
            "estado": "exito",
            "mensaje": f"El espécimen {ejemplar_eliminado.numero_coleccion} ha sido dado de baja del inventario exitosamente."
        }
    except ValueError as e:
        # Aquí usamos 404 (Not Found) porque estamos buscando un recurso específico que no existe
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/especies/{especie_id}", summary="Actualizar datos de una especie", status_code=status.HTTP_200_OK)
def modificar_especie_endpoint(especie_id: int, especie_in: EspecieUpdate, db: Session = Depends(get_db)):
    """
    Modifica los campos de una especie existente.
    Solo se actualizarán los campos que se envíen en el JSON.
    """
    try:
        # exclude_unset=True es MAGIA de Pydantic. 
        # Solo extrae los campos que el usuario realmente mandó en el JSON, ignorando los nulos.
        datos_a_modificar = especie_in.model_dump(exclude_unset=True)
        
        # Si mandaron un JSON vacío ({}), no hay nada que hacer
        if not datos_a_modificar:
            raise ValueError("No se enviaron datos para actualizar.")

        especie_actualizada = especie_service.actualizar_especie(db, especie_id, datos_a_modificar)
        
        return {
            "estado": "exito",
            "mensaje": f"La especie {especie_actualizada.genero} {especie_actualizada.especie} fue actualizada.",
            "cambios_aplicados": datos_a_modificar
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.patch("/ejemplares/{numero_coleccion}", summary="Actualizar datos de un ejemplar", status_code=status.HTTP_200_OK)
def modificar_ejemplar_endpoint(numero_coleccion: str, ejemplar_in: EjemplarUpdate, db: Session = Depends(get_db)):
    """
    Modifica parcialmente los datos de un espécimen físico.
    Los datos morfométricos (JSON) se fusionan, no se sobrescriben destructivamente.
    """
    try:
        # extraemos solo lo que el usuario envió explícitamente
        datos_a_modificar = ejemplar_in.model_dump(exclude_unset=True)
        
        if not datos_a_modificar:
            raise ValueError("No se enviaron datos para actualizar.")

        # Llamamos a nuestro motor lógico
        ejemplar_actualizado = ejemplar_service.actualizar_ejemplar(db, numero_coleccion, datos_a_modificar)
        
        return {
            "estado": "exito",
            "mensaje": f"El espécimen {ejemplar_actualizado.numero_coleccion} fue actualizado.",
            "morfometria_resultante": ejemplar_actualizado.datos_morfometricos
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/especies/{especie_id}", summary="Obtener detalle de especie", status_code=status.HTTP_200_OK)
def leer_especie_endpoint(especie_id: int, db: Session = Depends(get_db)):
    """
    Retorna todos los datos de una especie. Ideal para llenar formularios de edición.
    """
    try:
        especie = especie_service.obtener_especie(db, especie_id)
        return especie
    except ValueError as e:
        # 404 Not Found: El recurso solicitado no existe
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/ejemplares/{numero_coleccion}", summary="Obtener detalle de ejemplar", status_code=status.HTTP_200_OK)
def leer_ejemplar_endpoint(numero_coleccion: str, db: Session = Depends(get_db)):
    """
    Retorna los datos físicos de un espécimen JUNTO con la información de su especie.
    """
    try:
        resultado = ejemplar_service.obtener_ejemplar_con_especie(db, numero_coleccion)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/especies/{especie_id}/ejemplares", summary="Listar ejemplares de una especie")
def listar_ejemplares_de_especie(especie_id: int, db: Session = Depends(get_db)):
    """Devuelve la lista de todos los frascos físicos asociados a una especie biológica."""
    # Importar EjemplarMuseo arriba si no lo tienes en este archivo
    from app.models import EjemplarMuseo 
    
    ejemplares = db.query(EjemplarMuseo).filter(EjemplarMuseo.especie_id == especie_id).all()
    return ejemplares