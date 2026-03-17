import pandas as pd
from sqlalchemy.orm import Session
from app.models import Especie, EjemplarMuseo
from app.schemas import EspecieCreate, EjemplarCreate

def procesar_csv_museo(archivo_csv, db: Session):
    """
    Procesa un archivo CSV y carga los datos en PostgreSQL de forma relacional.
    Garantiza que no se dupliquen especies y empaqueta la morfometría en JSONB.
    """
    try:
        # 1. Cargar el DataFrame
        df = pd.read_csv(archivo_csv)
        
        # Reemplazar los NaN (Not a Number) de Pandas por None (NULL en SQL)
        # Esto es vital para que SQLAlchemy y Pydantic no fallen al validar vacíos
        df = df.astype(object).where(pd.notna(df), None)
        
        registros_insertados = 0
        
        # 2. Iterar sobre cada fila del CSV
        for index, row in df.iterrows():
            
            # --- A. EMPAQUETADO DINÁMICO (JSONB) ---
            claves_morfologicas = ['lt', 'lc', 'peso', 'pie', 'tibia_pie', 'oreja', 'antebrazo']
            datos_morfo = {}
            for clave in claves_morfologicas:
                if row.get(clave) is not None:
                    datos_morfo[clave] = row[clave]

            # --- B. LÓGICA DE ESPECIE (Evitar duplicados) ---
            # Buscamos si la especie ya existe en la base de datos por género y especie
            especie_db = db.query(Especie).filter(
                Especie.genero == row.get('genero'),
                Especie.especie == row.get('especie')
            ).first()

            if not especie_db:
                # Validar con Pydantic antes de instanciar el modelo
                especie_valida = EspecieCreate(
                    grupo=row.get('grupo'),
                    orden=row.get('orden'),
                    familia=row.get('familia'),
                    genero=row.get('genero'),
                    especie=row.get('especie'),
                    nombre_comun=row.get('nombre_comun'),
                    dieta=row.get('dieta'),
                    habitat=row.get('habitat'),
                    curiosidades=row.get('curiosidades'),
                    nivel_toxicidad=row.get('nivel_toxicidad'),
                    url_imagen=row.get('url_imagen'),
                    url_audio=row.get('url_audio')
                )
                
                # Crear la nueva especie en SQLAlchemy
                especie_db = Especie(**especie_valida.model_dump())
                db.add(especie_db)
                # flush() empuja los datos a la BD para generar el ID, pero NO hace commit definitivo
                db.flush() 

            # --- C. LÓGICA DEL EJEMPLAR FÍSICO ---
            # Verificamos que el ejemplar no haya sido cargado previamente
            ejemplar_existente = db.query(EjemplarMuseo).filter(
                EjemplarMuseo.numero_coleccion == row.get('numero_coleccion')
            ).first()

            if not ejemplar_existente:
                ejemplar_valido = EjemplarCreate(
                    numero_coleccion=row.get('numero_coleccion'),
                    especie_id=especie_db.id, # Conectamos con el ID de la especie (nueva o existente)
                    tipo_coleccion=row.get('tipo_coleccion', 'Referencia'),
                    en_exhibicion=bool(row.get('en_exhibicion', False)),
                    fecha_determinacion=row.get('fecha_determinacion'),
                    latitud_decimal=row.get('latitud_decimal'),
                    longitud_decimal=row.get('longitud_decimal'),
                    departamento=row.get('departamento'),
                    municipio=row.get('municipio'),
                    datos_morfometricos=datos_morfo # Inyectamos el diccionario limpio
                )
                
                nuevo_ejemplar = EjemplarMuseo(**ejemplar_valido.model_dump())
                db.add(nuevo_ejemplar)
                registros_insertados += 1

        # 3. Confirmar la Transacción (Commit)
        # Si llegamos aquí sin errores, guardamos todo definitivamente
        db.commit()
        return {"estado": "éxito", "registros_nuevos": registros_insertados}

    except Exception as e:
        # ROLLBACK: Si falla la fila 50, se deshacen los cambios de la 1 a la 49
        db.rollback()
        raise Exception(f"Error crítico en la importación (Fila {index + 2}): {str(e)}")