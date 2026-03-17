from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Especie, UsuarioAdmin
from app.schemas import EspecieCreate

router = APIRouter()

@router.post("/login", summary="Autenticación del Administrador (HU 7)")
async def login_admin(db: Session = Depends(get_db)):
    """
    Aquí implementaremos la validación de credenciales y generación de Token JWT.
    Es el paso previo antes de permitir el acceso al panel.
    """
    return {"mensaje": "Endpoint de login preparado para desarrollo."}

@router.post("/especies/", summary="Crear especie individualmente (HU 2)", status_code=status.HTTP_201_CREATED)
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