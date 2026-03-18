from sqlalchemy.orm import Session
from app.models import Especie, EjemplarMuseo # Asegúrate de que este sea el nombre real de tu clase en models.py
from typing import Any, Dict # Asegúrate de tener esto arriba
from sqlalchemy.orm.attributes import flag_modified # IMPORTANTE para que SQLAlchemy detecte cambios en JSONB


def crear_ejemplar(db: Session, especie_id: int, datos_ejemplar: dict):
    """
    Servicio para registrar un espécimen físico.
    Aplica validaciones relacionales y de unicidad.
    """
    # 1. Validar Integridad Referencial (¿Existe la especie?)
    especie_padre = db.query(Especie).filter(Especie.id == especie_id).first()
    if not especie_padre:
        raise ValueError(f"Operación denegada: La especie con ID {especie_id} no existe en el catálogo.")

    # 2. Validar Unicidad del Ejemplar (No pueden haber dos frascos con el mismo código)
    numero_col = datos_ejemplar.get("numero_coleccion", "").strip()
    ejemplar_existente = db.query(EjemplarMuseo).filter(EjemplarMuseo.numero_coleccion == numero_col).first()
    
    if ejemplar_existente:
        raise ValueError(f"El número de colección '{numero_col}' ya pertenece a otro ejemplar en el museo.")

    # 3. Empaquetar y construir el objeto físico
    nuevo_ejemplar = EjemplarMuseo(
        especie_id=especie_id, # Lo asignamos nosotros, no el usuario
        numero_coleccion=numero_col,
        tipo_coleccion=datos_ejemplar.get("tipo_coleccion", "Referencia"),
        en_exhibicion=datos_ejemplar.get("en_exhibicion", False),
        fecha_determinacion=datos_ejemplar.get("fecha_determinacion"),
        latitud_decimal=datos_ejemplar.get("latitud_decimal"),
        longitud_decimal=datos_ejemplar.get("longitud_decimal"),
        departamento=datos_ejemplar.get("departamento"),
        municipio=datos_ejemplar.get("municipio"),
        # JSONB para métricas variables (peso, longitud hocico-cloaca, etc.)
        datos_morfometricos=datos_ejemplar.get("datos_morfometricos", {}) 
    )

    # 4. Guardar en PostgreSQL
    try:
        db.add(nuevo_ejemplar)
        db.commit()
        db.refresh(nuevo_ejemplar)
        return nuevo_ejemplar
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Error crítico al guardar el ejemplar: {str(e)}")
    
def eliminar_ejemplar(db: Session, numero_coleccion: str):
    """
    Da de baja un espécimen físico del inventario del museo.
    """
    # 1. Buscar el ejemplar por su llave primaria (texto)
    ejemplar = db.query(EjemplarMuseo).filter(EjemplarMuseo.numero_coleccion == numero_coleccion).first()
    
    if not ejemplar:
        # Si no existe, no hay nada que borrar
        raise ValueError(f"Operación denegada: El ejemplar con código '{numero_coleccion}' no existe en el inventario.")

    # 2. Borrado seguro
    try:
        db.delete(ejemplar)
        db.commit()
        return ejemplar
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Error crítico en la base de datos al intentar dar de baja el ejemplar: {str(e)}")
from sqlalchemy.orm.attributes import flag_modified # IMPORTANTE para que SQLAlchemy detecte cambios en JSONB

def actualizar_ejemplar(db: Session, numero_coleccion: str, datos_actualizacion: Dict[str, Any]):
    """
    Actualiza los datos físicos de un espécimen.
    Realiza un 'merge' inteligente de los datos morfométricos en formato JSONB.
    """
    # 1. Buscar el frasco físico
    ejemplar_db = db.query(EjemplarMuseo).filter(EjemplarMuseo.numero_coleccion == numero_coleccion).first()
    if not ejemplar_db:
        raise ValueError(f"No se encontró ningún ejemplar con el código {numero_coleccion}.")

    # 2. Validación de reasignación taxonómica
    # Si el usuario quiere cambiar a qué especie pertenece el frasco, verificamos que la nueva exista
    nueva_especie_id = datos_actualizacion.get("especie_id")
    if nueva_especie_id is not None:
        especie_existe = db.query(Especie).filter(Especie.id == nueva_especie_id).first()
        if not especie_existe:
            raise ValueError(f"Operación denegada: Intenta reasignar a la especie ID {nueva_especie_id}, pero no existe en el catálogo.")

    # 3. Fusión inteligente del JSONB (Morfometría)
    if "datos_morfometricos" in datos_actualizacion and datos_actualizacion["datos_morfometricos"] is not None:
        # Extraemos el diccionario actual de la BD (si está vacío, iniciamos uno nuevo)
        morfometria_actual = ejemplar_db.datos_morfometricos or {}
        
        # Actualizamos el diccionario actual con los datos nuevos que llegaron en la petición
        morfometria_actual.update(datos_actualizacion["datos_morfometricos"])
        
        # Reasignamos y avisamos a SQLAlchemy que este campo específico (JSON) fue modificado
        ejemplar_db.datos_morfometricos = morfometria_actual
        flag_modified(ejemplar_db, "datos_morfometricos")
        
        # Eliminamos esta clave del diccionario de actualización para que el bucle de abajo no lo sobrescriba mal
        del datos_actualizacion["datos_morfometricos"]

    # 4. Actualización dinámica del resto de campos estáticos (departamento, en_exhibicion, etc.)
    for clave, valor in datos_actualizacion.items():
        if valor is not None:
            if isinstance(valor, str): valor = valor.strip()
            setattr(ejemplar_db, clave, valor)

    # 5. Guardar en PostgreSQL
    try:
        db.commit()
        db.refresh(ejemplar_db)
        return ejemplar_db
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Error crítico al actualizar el ejemplar en la base de datos: {str(e)}")

def obtener_ejemplar_con_especie(db: Session, numero_coleccion: str):
    """
    Busca un espécimen físico y, analíticamente, extrae también 
    los datos taxonómicos de su especie padre para facilitar el frontend.
    """
    ejemplar = db.query(EjemplarMuseo).filter(EjemplarMuseo.numero_coleccion == numero_coleccion).first()
    if not ejemplar:
        raise ValueError(f"No se encontró el espécimen con código {numero_coleccion}.")

    # Buscamos al padre (la especie) usando el ID que tiene el frasco
    especie_padre = db.query(Especie).filter(Especie.id == ejemplar.especie_id).first()

    # Retornamos un diccionario estructurado, listo para el frontend
    return {
        "datos_fisicos": ejemplar,
        "datos_biologicos": especie_padre
    }