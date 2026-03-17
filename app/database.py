import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Construir la URL de conexión a PostgreSQL
# Formato esperado: postgresql://usuario:password@localhost:5432/nombre_bd
SQLALCHEMY_DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# El "engine" es el motor que ejecuta las sentencias SQL en la base de datos
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# La fábrica de sesiones. autocommit=False es vital para que las importaciones del CSV 
# sean seguras (si falla una fila, se hace rollback de todo).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base de la que heredarán todos los modelos (tablas)
Base = declarative_base()

# Dependencia para inyectar la sesión de BD en las rutas de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()