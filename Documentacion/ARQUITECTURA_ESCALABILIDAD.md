# 🏗️ ARQUITECTURA Y ESCALABILIDAD

## 📐 ARQUITECTURA DEL SISTEMA

### Diagrama General
```
┌─────────────────────────────────────────────────────────────┐
│                   CLIENTE (Navegador)                       │
│              HTML + JavaScript + Bootstrap                  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  FASTAPI (Puerto 8000)                      │
│  ├─ CORS Middleware (permite peticiones cruzadas)           │
│  ├─ Static Files (CSS, JS, imágenes)                        │
│  └─ Jinja2 Templates (renderización HTML)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
    ┌────────┐      ┌────────┐      ┌────────┐
    │Endpoints│      │Services│      │Security│
    │(Rutas)  │      │(Lógica)│      │(JWT)   │
    └────────┘      └────────┘      └────────┘
        │                ▼                │
        └────────────────┼────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  SQLAlchemy ORM                             │
│        (Traduce modelos Python a SQL)                       │
└────────────────────────┬────────────────────────────────────┘
                         │ SQL Queries
                         ▼
┌─────────────────────────────────────────────────────────────┐
│             PostgreSQL Database                             │
│  ├─ usuarios_admin (autenticación)                          │
│  ├─ especies (catálogo)                                     │
│  └─ ejemplares_museo (inventario)                           │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Ollama (IA Local)                         │
│              (Chat educativo con phi3)                      │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 FLUJO DE DATOS

### 1. Visitante Accede a Galería

```
1. GET /herpetologia
       │
       ▼
2. FastAPI endpoint
       │
       ▼
3. Query: SELECT * FROM especies
       │
       ▼
4. PostgreSQL devuelve 150 especies
       │
       ▼
5. Jinja2 renderiza HTML
       │
       ▼
6. Navegador renderiza galería
       │
       ▼
7. Bootstrap CSS da estilo
       │
       ▼
8. Usuario ve 150 tarjetas
```

### 2. Chat IA en Tiempo Real

```
1. Usuario: "¿Es venenosa la cobra?"
       │
       ▼
2. POST /api/chat con pregunta
       │
       ▼
3. Backend busca "cobra" en BD
       │
       ▼
4. Encuentra Cobra Real (ID: 42)
       │
       ▼
5. Construye prompt con datos de BD
       │
       ▼
6. Envía a Ollama (IA local)
       │
       ▼
7. Ollama procesa prompt
       │
       ▼
8. Devuelve respuesta educativa
       │
       ▼
9. Backend envía JSON al cliente
       │
       ▼
10. JavaScript renderiza chat
```

### 3. Admin Importa 1000 Especies

```
1. Admin carga archivo CSV (1000 filas)
       │
       ▼
2. POST /importar-csv/ (requiere JWT)
       │
       ▼
3. Backend valida token
       │
       ▼
4. Pandas lee CSV
       │
       ▼
5. Para CADA fila:
   ├─ Normaliza datos
   ├─ Busca especie por genero+especie
   ├─ Si NO existe: CREATE
   ├─ Si existe: UPDATE
   ├─ Crea ejemplar físico
   ├─ Guarda coordenadas GPS
   └─ Guarda medidas (JSONB)
       │
       ▼
6. Si TODO OK → COMMIT ✓
   Si ALGO FALLA → ROLLBACK ✗
       │
       ▼
7. Admin recibe reporte:
   {
     "filas_procesadas": 1000,
     "especies_creadas": 850,
     "ejemplares": 5000,
     "errores": 0
   }
```

## 🎯 CAPAS DE LA APLICACIÓN

### Layer 1: Presentación (Frontend)
```
templates/
├─ base.html → Layout base
├─ index.html → Galería
├─ detalle.html → Ficha técnica
├─ admin.html → Dashboard
├─ importar.html → Upload CSV
└─ login.html → Autenticación

Static Files:
├─ bootstrap.min.css
├─ custom.css
├─ app.js
└─ imágenes/
```

### Layer 2: API (FastAPI)
```
app/api/
├─ api_router.py → Agregador de rutas
└─ endpoints/
   ├─ visitor.py → Públicas
   ├─ admin.py → Administrativas
   └─ data_import.py → Importación
```

### Layer 3: Lógica de Negocio (Services)
```
app/services/
├─ import_service.py → Procesamiento CSV
├─ especie_service.py → CRUD Especies
└─ ejemplar_service.py → Gestión inventario
```

### Layer 4: Modelos (ORM)
```
app/
├─ models.py → Definición de tablas
├─ schemas.py → Validación Pydantic
└─ database.py → Conexión PostgreSQL
```

### Layer 5: Base de Datos
```
PostgreSQL
├─ usuarios_admin
├─ especies
└─ ejemplares_museo
```

## 🚀 ESTRATEGIAS DE ESCALABILIDAD

### Escala Horizontal (Más Servidores)

#### 1. Load Balancer (Nginx)
```nginx
upstream api {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://api;
    }
}
```

#### 2. Docker & Kubernetes
```yaml
# Ejecutar múltiples instancias
docker-compose up --scale api=3

# Kubernetes
replicas: 3
```

### Escala Vertical (Más Recursos)

#### 1. Caché (Redis)
```python
import redis
cache = redis.Redis(host='localhost', port=6379)

# Cachear especies (1 hora)
CACHE_KEY = 'all_species'
cached = cache.get(CACHE_KEY)
if not cached:
    especies = db.query(Especies).all()
    cache.setex(CACHE_KEY, 3600, json.dumps(especies))
else:
    especies = json.loads(cached)
```

#### 2. Base de Datos Optimizada

**Índices:**
```sql
CREATE INDEX idx_nombre_comun ON especies(nombre_comun);
CREATE INDEX idx_genero_especie ON especies(genero, especie);
CREATE INDEX idx_en_exhibicion ON ejemplares_museo(en_exhibicion);
```

**Particionamiento:**
```sql
-- Particionar por grupo
CREATE TABLE especies_anfibios PARTITION OF especies
    FOR VALUES IN ('Anfibio');

CREATE TABLE especies_reptiles PARTITION OF especies
    FOR VALUES IN ('Reptil');
```

#### 3. Query Optimization
```python
# LENTO: N queries
for especie in db.query(Especie).all():
    print(especie.ejemplares)

# RÁPIDO: 1 query
from sqlalchemy.orm import joinedload
especies = db.query(Especie).options(
    joinedload(Especie.ejemplares)
).all()
```

### Compresión & CDN

#### 1. Gzip (FastAPI)
```python
from fastapi.middleware.gzip import GZIPMiddleware

app.add_middleware(GZIPMiddleware, minimum_size=1000)
```

#### 2. CloudFlare CDN
```
Configurar en DNS para servir imágenes y CSS desde edge servers
```

## 📊 MONITOREO Y MÉTRICAS

### Prometheus + Grafana

```python
from prometheus_client import Counter, Histogram
from fastapi_prometheus import PrometheusMiddleware

app.add_middleware(PrometheusMiddleware)

# Métricas personalizadas
requests_total = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration', 'Request duration')
```

### Logs Centralizados

```python
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
```

## 🔐 SEGURIDAD EN PRODUCCIÓN

### HTTPS (SSL/TLS)

```bash
# Generar certificados Let's Encrypt
certbot certonly --standalone -d tudominio.com

# En nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/letsencrypt/live/tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tudominio.com/privkey.pem;
}
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/chat")
@limiter.limit("10/minute")
async def chat(request: Request, chat_data: ChatRequest):
    pass
```

### CORS Restringido

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tudominio.com"],  # No ["*"]
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Validación de Entrada

```python
from pydantic import BaseModel, validator

class EspecieCreate(BaseModel):
    grupo: str
    nombre_comun: str
    
    @validator('grupo')
    def validate_grupo(cls, v):
        if v not in ['Anfibio', 'Reptil']:
            raise ValueError('Grupo inválido')
        return v
```

## 📦 DESPLIEGUE A PRODUCCIÓN

### Opción 1: Servidor Dedicado (DigitalOcean, Linode)

```bash
# 1. Clonar repo
git clone https://github.com/farid3312/sala-herpetologia.git

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear .env de producción
DB_HOST=prod-db.example.com
JWT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')

# 4. Ejecutar con Gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 5. Ejecutar con Supervisor (auto-restart)
[program:museo]
command=/path/to/venv/bin/gunicorn app.main:app --bind 0.0.0.0:8000
directory=/path/to/proyecto
user=www-data
autostart=true
autorestart=true
```

### Opción 2: Docker & Container Registry

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app app
COPY templates templates
COPY static static

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build & Push
docker build -t myrepo/museo:1.0.0 .
docker push myrepo/museo:1.0.0

# Deploy
docker run -d -p 8000:8000 myrepo/museo:1.0.0
```

### Opción 3: Heroku

```bash
# 1. Crear app
heroku create mi-museo

# 2. Agregar PostgreSQL
heroku addons:create heroku-postgresql:standard-0

# 3. Deploy
git push heroku main

# 4. Ver logs
heroku logs --tail
```

## 🌱 ROADMAP DE ESCALABILIDAD

### Fase 1: MVP (Actual)
- ✅ Monolito en un servidor
- ✅ PostgreSQL local
- ✅ API REST básica

### Fase 2: Crecimiento (1000 usuarios/día)
- ⭕ Redis para caché
- ⭕ Load Balancer (Nginx)
- ⭕ Logs centralizados
- ⭕ Backup automatizado

### Fase 3: Escala (10000 usuarios/día)
- ⭕ Microservicios (Chat, Importación)
- ⭕ PostgreSQL con replicas
- ⭕ Elasticsearch para búsqueda
- ⭕ CDN global

### Fase 4: Empresarial (100000 usuarios/día)
- ⭕ Kubernetes
- ⭕ GraphQL API
- ⭕ Machine Learning (recomendaciones)
- ⭕ Análisis en tiempo real

---

Documentación: 2026-06-06 | Versión: 1.0.0
