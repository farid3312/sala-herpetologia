# 📋 GUÍA DE OPERACIONES DIARIAS

## 🚀 INICIAR LA APLICACIÓN

### Método 1: Desarrollo Local

```bash
# 1. Activar entorno virtual
cd museo_interactivo
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 2. Verificar PostgreSQL está activo
psql -U postgres -d museo_interactivo -c "SELECT 1;"

# 3. Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. Verificar en navegador
# http://localhost:8000 ✅
```

### Método 2: Con Docker

```bash
# 1. Build imagen
docker build -t museo:latest .

# 2. Ejecutar con compose
docker-compose up

# 3. Ver logs
docker-compose logs -f api

# 4. Detener
docker-compose down
```

## 🔐 GESTIÓN DE ADMINISTRADORES

### Crear Nuevo Admin (Primera Vez)

```bash
# Conectar a PostgreSQL
psql -U museo_user -d museo_interactivo

# Insertar admin (password debe estar hasheado)
INSERT INTO usuarios_admin (nombre_completo, correo, password_hash, creado_en)
VALUES (
    'Juan Pérez',
    'juan@museo.com',
    '$2b$12$...',  # Hash bcrypt
    NOW()
);
```

O desde Python:

```python
from passlib.context import CryptContext
from app.database import SessionLocal
from app.models import UsuarioAdmin
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()
hashed_pwd = pwd_context.hash("micontraseña123")

nuevo_admin = UsuarioAdmin(
    id=uuid.uuid4(),
    nombre_completo="Juan Pérez",
    correo="juan@museo.com",
    password_hash=hashed_pwd
)

db.add(nuevo_admin)
db.commit()
print("✅ Admin creado")
```

## 📥 IMPORTAR DATOS MASIVOS

### Preparar CSV

```csv
grupo,orden,familia,genero,especie,nombre_comun,dieta,habitat,curiosidades,nivel_toxicidad,url_imagen,url_audio
Anfibio,Anura,Hylidae,Hypsiboas,punctatus,Rana verde,Insectos,Árboles tropicales,Emite sonidos nocturnos,No tóxico,/data/rana.jpg,/data/rana.mp3
Reptil,Squamata,Viperidae,Crotalus,horridus,Serpiente de cascabel,Pequeños mamíferos,Bosques secos,Tiene cascabel,Altamente tóxico,/data/cascabel.jpg,/data/cascabel.mp3
```

### Ejecutar Importación

```bash
# 1. Login para obtener token
TOKEN=$(curl -s -X POST http://localhost:8000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"correo":"admin@museo.com","password":"1234"}' \
  | jq -r '.access_token')

# 2. Subir archivo
curl -X POST http://localhost:8000/importar-csv/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@especies.csv"

# 3. Verificar resultado
{
    "mensaje": "Importación finalizada con éxito",
    "detalles": {
        "filas_procesadas": 150,
        "especies_creadas": 145,
        "ejemplares_importados": 8500,
        "errores": 0
    }
}
```

## 🐛 DEBUGGING Y TROUBLESHOOTING

### Ver Logs de FastAPI

```bash
# En terminal donde corre uvicorn
# Los logs aparecen en tiempo real:
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Application startup complete
INFO: GET /herpetologia - "200 OK"
INFO: POST /api/chat - "200 OK"
```

### Consultar Base de Datos

```bash
# Conectar a PostgreSQL
psql -U museo_user -d museo_interactivo

# Ver tablas
\dt

# Ver datos
SELECT * FROM especies LIMIT 10;
SELECT COUNT(*) FROM ejemplares_museo;

# Búsqueda específica
SELECT * FROM especies WHERE nombre_comun ILIKE '%cobra%';

# Salir
\q
```

### Probar Endpoints desde CLI

```bash
# Ver todas las especies
curl http://localhost:8000/herpetologia

# Detalle de especie
curl http://localhost:8000/especie/5

# Chat IA
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"pregunta":"¿Es venenosa?","especie_id":"general"}'

# Ver documentación API
curl http://localhost:8000/docs
```

## 📊 MANTENIMIENTO RUTINARIO

### Diario (9:00 AM)

```bash
# 1. Verificar que el servicio esté corriendo
curl http://localhost:8000/docs

# 2. Revisar logs
tail -f logs/app.log

# 3. Verificar BD
psql -U museo_user -d museo_interactivo -c "SELECT COUNT(*) FROM especies;"

# 4. Verificar Ollama (si usas IA)
curl http://localhost:11434/api/tags
```

### Semanal (Viernes)

```bash
# 1. Backup de base de datos
pg_dump -U museo_user museo_interactivo > backup_$(date +%Y%m%d).sql

# 2. Revisar errores
grep ERROR logs/app.log | tail -20

# 3. Estadísticas
SELECT 
    COUNT(*) as total_especies,
    COUNT(DISTINCT grupo) as grupos
FROM especies;
```

### Mensual (Primer día)

```bash
# 1. Actualizar dependencias
pip install --upgrade -r requirements.txt

# 2. Ejecutar tests
pytest tests/ -v

# 3. Generar reporte de uso
SELECT 
    DATE_TRUNC('month', creado_en) as mes,
    COUNT(*) as nuevas_especies
FROM especies
GROUP BY DATE_TRUNC('month', creado_en)
ORDER BY mes DESC;

# 4. Limpiar archivos temporales
rm data/temp_*
```

## 🆘 PROBLEMAS COMUNES Y SOLUCIONES

### Error: "Connection refused (PostgreSQL)"

**Síntomas:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solución:**
```bash
# Windows
pg_ctl -D "C:\Program Files\PostgreSQL\15\data" start

# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql

# Verificar
psql -U postgres -c "SELECT 1;"
```

### Error: "Token inválido o expirado"

**Síntomas:**
```
HTTPException: 401 Unauthorized
```

**Solución:**
```bash
# Hacer login nuevamente
curl -X POST http://localhost:8000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"correo":"admin@museo.com","password":"1234"}'

# Usar nuevo token en peticiones futuras
```

### Error: "No se puede eliminar la especie"

**Síntomas:**
```
"No se puede eliminar la especie porque tiene 50 ejemplar(es) asignado(s)"
```

**Solución:**
```sql
-- 1. Ver ejemplares asignados
SELECT * FROM ejemplares_museo WHERE especie_id = 5;

-- 2. Reasignar a otra especie
UPDATE ejemplares_museo SET especie_id = 42 WHERE especie_id = 5;

-- 3. O eliminar los ejemplares
DELETE FROM ejemplares_museo WHERE especie_id = 5;

-- 4. Ahora sí eliminar la especie
DELETE FROM especies WHERE id = 5;
```

### Error: "Ollama no responde"

**Síntomas:**
```
httpx.ConnectError: Unable to connect to http://localhost:11434
```

**Solución:**
```bash
# 1. Verificar si Ollama está corriendo
curl http://localhost:11434/api/tags

# 2. Si no responde, iniciar Ollama
ollama serve

# 3. Descargar modelo (si es primera vez)
ollama pull phi3

# 4. Probar nuevamente
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"pregunta":"Hola","especie_id":"general"}'
```

## 🔍 MONITOREO DE PERFORMANCE

### Ver Consultas Lentas

```python
# En app/main.py
import logging
from sqlalchemy import event

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    print(f"⏱️  Query Time: {statement[:100]}...")
```

### Contar Requests

```bash
# Ver requests en último minuto
tail -f logs/app.log | grep -c "GET\|POST\|PUT\|DELETE"

# Requests por endpoint
tail -f logs/app.log | awk '{print $7}' | sort | uniq -c | sort -rn

# Tiempo promedio de respuesta
tail -f logs/app.log | awk -F' ms$' '{sum+=$NF; count++} END {print "Promedio:", sum/count "ms"}'
```

## 🔄 ACTUALIZAR CÓDIGO EN PRODUCCIÓN

### Proceso Seguro

```bash
# 1. Clonar cambios
git pull origin main

# 2. Ejecutar tests
pytest tests/ -v

# 3. Backup de BD (por si acaso)
pg_dump museo_interactivo > backup_before_deploy.sql

# 4. Detener aplicación (0 downtime possible)
# Opción A: Reload sin reiniciar
pkill -HUP gunicorn

# Opción B: Blue-Green Deployment
# Ejecutar nueva versión en puerto 8001
# Cambiar Load Balancer a 8001
# Detener puerto 8000

# 5. Verificar
curl http://localhost:8000/docs

# 6. Ver logs
tail -f logs/app.log
```

## 📈 GENERAR REPORTES

### Especies Totales por Grupo

```sql
SELECT 
    grupo,
    COUNT(*) as cantidad,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as porcentaje
FROM especies
GROUP BY grupo
ORDER BY cantidad DESC;
```

### Ejemplares por Departamento

```sql
SELECT 
    departamento,
    COUNT(*) as ejemplares,
    COUNT(DISTINCT especie_id) as especies
FROM ejemplares_museo
GROUP BY departamento
ORDER BY ejemplares DESC
LIMIT 10;
```

### Actividad de Administradores

```sql
SELECT 
    correo,
    creado_en,
    DATE(creado_en) as fecha_creacion,
    COUNT(*) OVER (PARTITION BY correo) as actividad_total
FROM usuarios_admin
ORDER BY creado_en DESC;
```

## 🛡️ SEGURIDAD: Checklist Diario

```bash
# ✅ Verificar .env no está versionado
git status | grep .env

# ✅ Cambiar JWT_SECRET_KEY cada mes
openssl rand -hex 32

# ✅ Revisar logs de error
grep ERROR logs/app.log | wc -l

# ✅ Verificar conexiones HTTPS (producción)
curl -I https://tudominio.com

# ✅ Verificar CORS restringido (no ["*"])
curl -I -H "Origin: https://otro-dominio.com" http://localhost:8000

# ✅ Verificar SQL injection imposible (Pydantic validation)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"pregunta":"; DROP TABLE especies; --","especie_id":"general"}'
  # Debe fallar o ser ignorado
```

---

Documentación: 2026-06-06 | Versión: 1.0.0
