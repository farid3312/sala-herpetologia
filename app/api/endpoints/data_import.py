from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import shutil
import os

# Importamos la dependencia de la base de datos y nuestro servicio
from app.database import get_db
from app.services.import_service import procesar_csv_museo

# Creamos un enrutador específico para esta funcionalidad
router = APIRouter()

@router.post("/importar-csv/", summary="Importar catálogo desde archivo CSV")
async def importar_datos_csv(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """
    Recibe un archivo CSV del administrador, lo guarda temporalmente 
    y ejecuta el servicio de importación masiva.
    """
    # 1. Validación de seguridad básica
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400, 
            detail="Formato inválido. El archivo debe ser un .csv"
        )
    
    # 2. Creación de un entorno seguro temporal
    # Guardamos el archivo en la carpeta 'data/' temporalmente para que Pandas lo lea
    temp_file_path = f"data/temp_{file.filename}"
    os.makedirs("data", exist_ok=True)
    
    try:
        # Copiamos el contenido del archivo subido al disco local
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 3. Delegación de la lógica pesada
        # Aquí es donde ocurre la magia transaccional que programamos antes
        resultado = procesar_csv_museo(temp_file_path, db)
        
        return {
            "mensaje": "Importación finalizada con éxito", 
            "detalles": resultado
        }
        
    except Exception as e:
        # Si algo falla en el servicio (ej. Pydantic rechaza un dato), lanzamos un error 500
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # 4. Clean Code: Limpieza de recursos
        # Pase lo que pase (éxito o error), borramos el archivo temporal para no llenar el disco
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)