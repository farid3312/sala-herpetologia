# test_db.py
from app.database import SessionLocal, engine, Base
from sqlalchemy import text

def test_connection():
    try:
        # 1. Intentar conectar
        with engine.connect() as connection:
            print("✅ Conexión al motor de base de datos exitosa.")
            
        # 2. Intentar crear una sesión y ejecutar un comando simple
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        print("✅ Sesión de base de datos operativa.")
        
        # 3. Intentar crear las tablas
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas sincronizadas (creadas si no existían).")
        
        db.close()
    except Exception as e:
        print(f"❌ ERROR: No se pudo conectar a la base de datos.")
        print(f"Detalle: {e}")

if __name__ == "__main__":
    test_connection()