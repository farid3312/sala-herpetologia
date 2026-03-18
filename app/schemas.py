from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import date
from decimal import Decimal

# ==========================================
# ESQUEMAS PARA ESPECIES
# ==========================================
class EspecieBase(BaseModel):
    grupo: str = Field(..., description="Clasificación principal")
    orden: Optional[str] = None
    familia: Optional[str] = None
    genero: Optional[str] = None
    especie: Optional[str] = None
    nombre_comun: Optional[str] = None
    dieta: Optional[str] = None
    habitat: Optional[str] = None
    curiosidades: Optional[str] = None
    nivel_toxicidad: Optional[str] = None
    url_imagen: Optional[str] = None
    url_audio: Optional[str] = None

    # Validación estricta: Solo permitimos estos dos grupos biológicos
    @field_validator("grupo")
    def validar_grupo(cls, v):
        if v not in ["Anfibio", "Reptil"]:
            raise ValueError(f"Grupo no válido: {v}. Debe ser 'Anfibio' o 'Reptil'")
        return v

class EspecieCreate(EspecieBase):
    pass # Usado al crear una nueva especie desde el CSV o panel admin

# ==========================================
# ESQUEMAS PARA EJEMPLARES FÍSICOS
# ==========================================
class EjemplarBase(BaseModel):
    numero_coleccion: str = Field(..., min_length=3)
    tipo_coleccion: Optional[str] = "Referencia"
    en_exhibicion: bool = False
    fecha_determinacion: Optional[date] = None
    
    # Usamos Decimal para mantener la precisión matemática de las coordenadas
    latitud_decimal: Optional[Decimal] = None
    longitud_decimal: Optional[Decimal] = None
    
    departamento: Optional[str] = None
    municipio: Optional[str] = None
    
    # El diccionario que albergará lt, lc, peso, etc. (El JSONB en PostgreSQL)
    datos_morfometricos: Optional[Dict[str, Any]] = Field(default_factory=dict)

class EjemplarCreate(EjemplarBase):
    especie_id: int # Clave foránea que lo conecta con la especie

# ==========================================
# ESQUEMA DE LECTURA (Respuesta de la API)
# ==========================================
class EjemplarResponse(EjemplarBase):
    registrado_en: date
    
    class Config:
        from_attributes = True # Permite que Pydantic lea modelos de SQLAlchemy
class EspecieUpdate(BaseModel):
    # Todos los campos son opcionales para permitir actualizaciones parciales (PATCH/PUT)
    grupo: Optional[str] = Field(None, description="Clasificación principal (Anfibio/Reptil)")
    genero: Optional[str] = None
    especie: Optional[str] = None
    nombre_comun: Optional[str] = None
    familia: Optional[str] = None
    orden: Optional[str] = None
    dieta: Optional[str] = None
    habitat: Optional[str] = None
    curiosidades: Optional[str] = None
    nivel_toxicidad: Optional[str] = None
    url_imagen: Optional[str] = None
    url_audio: Optional[str] = None

    # Reutilizamos tu excelente validador de grupo si es que deciden enviarlo
    @field_validator("grupo")
    def validar_grupo(cls, v):
        if v is not None and v not in ["Anfibio", "Reptil"]:
            raise ValueError(f"Grupo no válido: {v}. Debe ser 'Anfibio' o 'Reptil'")
        return v
class EjemplarUpdate(BaseModel):
    # Opcional: Permitimos reasignar el frasco a otra especie (útil si hubo un error de identificación biológica)
    especie_id: Optional[int] = None 
    tipo_coleccion: Optional[str] = None
    en_exhibicion: Optional[bool] = None
    fecha_determinacion: Optional[date] = None
    latitud_decimal: Optional[Decimal] = None
    longitud_decimal: Optional[Decimal] = None
    departamento: Optional[str] = None
    municipio: Optional[str] = None
    
    # El diccionario de métricas. Pydantic verificará que al menos sea un JSON válido.
    datos_morfometricos: Optional[Dict[str, Any]] = None