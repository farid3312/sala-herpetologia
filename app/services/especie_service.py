from sqlalchemy.orm import Session
from app.models import Especie, EjemplarMuseo

# Asumiendo que tienes tus esquemas Pydantic definidos, si no, lo ajustaremos
# from app.schemas import EspecieCreate 

def crear_especie_manual(db: Session, datos_especie: dict):
    """
    Servicio para crear una especie individual con validación taxonómica.
    Aplica principios de Clean Code aislando la lógica de negocio.
    """
    
    # 1. Normalización de Datos (Evitar duplicados por errores de tipeo)
    genero_limpio = datos_especie.get('genero', '').strip().capitalize()
    especie_limpia = datos_especie.get('especie', '').strip().lower()
    
    if not genero_limpio or not especie_limpia:
        raise ValueError("El género y la especie son campos obligatorios.")

    # 2. Consulta de Validación (¿Ya existe en PostgreSQL?)
    especie_existente = db.query(Especie).filter(
        Especie.genero == genero_limpio,
        Especie.especie == especie_limpia
    ).first()

    if especie_existente:
        # Detenemos la ejecución antes de tocar la base de datos
        raise ValueError(f"La especie taxonómica '{genero_limpio} {especie_limpia}' ya está registrada en el catálogo.")

    # 3. Empaquetado de los datos normalizados
    nueva_especie = Especie(
        grupo=datos_especie.get('grupo', '').strip().capitalize(),
        genero=genero_limpio,
        especie=especie_limpia,
        nombre_comun=datos_especie.get('nombre_comun', '').strip(),
        familia=datos_especie.get('familia', '').strip().capitalize(),
        orden=datos_especie.get('orden', '').strip().capitalize(),
        dieta=datos_especie.get('dieta'),
        habitat=datos_especie.get('habitat'),
        curiosidades=datos_especie.get('curiosidades'),
        nivel_toxicidad=datos_especie.get('nivel_toxicidad'),
        url_imagen=datos_especie.get('url_imagen'),
        url_audio=datos_especie.get('url_audio')
    )

    # 4. Inserción (El C de CRUD)
    try:
        db.add(nueva_especie)
        db.commit()
        db.refresh(nueva_especie)
        return nueva_especie
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Error crítico al guardar en la base de datos: {str(e)}")
    
def eliminar_especie(db: Session, especie_id: int):
    """
    Elimina una especie biológica garantizando la integridad referencial.
    Impide el borrado si existen especímenes físicos asociados en el museo.
    """
    # 1. Buscar la especie (¿Existe lo que queremos borrar?)
    especie = db.query(Especie).filter(Especie.id == especie_id).first()
    if not especie:
        raise ValueError(f"Operación denegada: La especie con ID {especie_id} no existe en el catálogo.")

    # 2. Verificación de Seguridad (El escudo relacional)
    # Contamos cuántos ejemplares físicos tienen este especie_id
    ejemplares_asociados = db.query(EjemplarMuseo).filter(EjemplarMuseo.especie_id == especie_id).count()

    if ejemplares_asociados > 0:
        # Abortamos la misión para proteger el inventario
        raise ValueError(
            f"No se puede eliminar la especie '{especie.genero} {especie.especie}'. "
            f"Actualmente tiene {ejemplares_asociados} ejemplar(es) físico(s) registrado(s). "
            "Debe reasignar o eliminar los ejemplares primero."
        )

    # 3. Borrado Seguro
    try:
        db.delete(especie)
        db.commit()
        return especie # Devolvemos la especie borrada por si el controlador quiere mostrar su nombre
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Error crítico en la base de datos al intentar eliminar: {str(e)}")

def actualizar_especie(db: Session, especie_id: int, datos_actualizacion: dict):
    """
    Actualiza una especie biológica.
    Aplica protección contra colisiones taxonómicas excluyendo el ID actual.
    """
    # 1. Buscar el registro original
    especie_db = db.query(Especie).filter(Especie.id == especie_id).first()
    if not especie_db:
        raise ValueError(f"No se encontró la especie con ID {especie_id}.")

    # 2. Extraer valores para la validación de unicidad
    # Si envían un nuevo género/especie, lo normalizamos. Si no, usamos el que ya está en la BD.
    nuevo_genero = datos_actualizacion.get("genero", especie_db.genero)
    if nuevo_genero: nuevo_genero = nuevo_genero.strip().capitalize()

    nueva_especie = datos_actualizacion.get("especie", especie_db.especie)
    if nueva_especie: nueva_especie = nueva_especie.strip().lower()

    # 3. La Verificación Crítica (¿El cambio choca con OTRO registro?)
    if (nuevo_genero != especie_db.genero) or (nueva_especie != especie_db.especie):
        colision = db.query(Especie).filter(
            Especie.genero == nuevo_genero,
            Especie.especie == nueva_especie,
            Especie.id != especie_id  # ¡Clave! Excluimos el registro que estamos editando
        ).first()
        
        if colision:
            raise ValueError(f"El cambio taxonómico a '{nuevo_genero} {nueva_especie}' choca con el registro ID {colision.id}.")

    # 4. Aplicar los cambios dinámicamente (Partial Update)
    for clave, valor in datos_actualizacion.items():
        if valor is not None:  # Solo actualizamos los campos que realmente enviaron
            # Aplicar limpieza de texto para campos críticos
            if clave == "genero": valor = valor.strip().capitalize()
            elif clave == "especie": valor = valor.strip().lower()
            elif isinstance(valor, str): valor = valor.strip()
            
            setattr(especie_db, clave, valor)

    # 5. Guardar
    try:
        db.commit()
        db.refresh(especie_db)
        return especie_db
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Error crítico al actualizar la base de datos: {str(e)}")
def obtener_especie(db: Session, especie_id: int):
    """
    Busca una especie por su ID biológico.
    """
    especie = db.query(Especie).filter(Especie.id == especie_id).first()
    if not especie:
        # Usamos ValueError para que el controlador sepa que debe lanzar un 404
        raise ValueError(f"No se encontró ninguna especie con el ID {especie_id}.")
    return especie