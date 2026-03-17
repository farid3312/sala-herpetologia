import uuid
from sqlalchemy import Column, Integer, String, Boolean, Text, Date, Numeric, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# Importamos la Base que acabamos de crear en database.py
from app.database import Base

class UsuarioAdmin(Base):
    __tablename__ = "usuarios_admin"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre_completo = Column(String(150), nullable=False)
    correo = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    creado_en = Column(TIMESTAMP, server_default=func.now())

class Especie(Base):
    """
    Almacena la información biológica general. 
    Se relaciona con las columnas del CSV: grupo, orden, familia, genero, especie, etc.
    """
    __tablename__ = "especies"
    
    id = Column(Integer, primary_key=True, index=True)
    grupo = Column(String(50), nullable=False)
    orden = Column(String(100))
    familia = Column(String(100))
    genero = Column(String(100))
    especie = Column(String(100))
    nombre_comun = Column(String(150), index=True) # Indexado para búsquedas rápidas
    dieta = Column(Text)
    habitat = Column(Text)
    curiosidades = Column(Text)
    nivel_toxicidad = Column(Text)
    url_imagen = Column(Text)
    url_audio = Column(Text)

    # Relación bidireccional con los ejemplares físicos
    ejemplares = relationship("EjemplarMuseo", back_populates="especie_info")

class EjemplarMuseo(Base):
    """
    Almacena el inventario físico (las piezas reales en Popayán).
    Se relaciona con las columnas del CSV: numero_coleccion, fecha_determinacion, coordenadas, etc.
    """
    __tablename__ = "ejemplares_museo"
    
    numero_coleccion = Column(String(50), primary_key=True)
    especie_id = Column(Integer, ForeignKey("especies.id", ondelete="RESTRICT"))
    tipo_coleccion = Column(String(50), default="Referencia")
    en_exhibicion = Column(Boolean, default=False)
    fecha_determinacion = Column(Date)
    
    # Coordenadas geográficas (Ej: Popayán 2.4411, -76.6022)
    latitud_decimal = Column(Numeric(10, 8))
    longitud_decimal = Column(Numeric(11, 8))
    
    departamento = Column(String(100))
    municipio = Column(String(100))
    
    # Aquí irá el diccionario con: lt, lc, peso, pie, tibia_pie, oreja, antebrazo
    datos_morfometricos = Column(JSONB, default=dict) 
    
    registrado_en = Column(TIMESTAMP, server_default=func.now())

    # Relación bidireccional con la especie biológica
    especie_info = relationship("Especie", back_populates="ejemplares")