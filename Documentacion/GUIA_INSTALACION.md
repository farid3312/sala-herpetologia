# 🏛️ GUÍA DE INSTALACIÓN Y CONFIGURACIÓN RÁPIDA

## 📋 Requisitos Mínimos (Windows, macOS, Linux)

### 1. PostgreSQL
- Descargar desde: https://www.postgresql.org/download/
- Instalar e inicializar
- Usuario por defecto: postgres

### 2. Python 3.10+
- Descargar desde: https://www.python.org/downloads/
- Verificar: python --version

### 3. Git (Opcional pero recomendado)
- Descargar desde: https://git-scm.com/download/

---

## ⚡ INSTALACIÓN RÁPIDA (5 MINUTOS)

### Paso 1: Preparar Entorno
\\\ash
# Clonar proyecto
git clone https://github.com/farid3312/sala-herpetologia.git
cd sala-herpetologia

# Crear carpeta data si no existe
mkdir data

# Crear entorno virtual
python -m venv venv

# Activar entorno
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate
\\\

### Paso 2: Instalar Dependencias
\\\ash
pip install -r requirements.txt
\\\

### Paso 3: Crear archivo .env
Crear archivo \.env\ en raíz del proyecto:

\\\
DB_USER=postgres
DB_PASSWORD=1234
DB_HOST=localhost
DB_PORT=5432
DB_NAME=museo_interactivo
JWT_SECRET_KEY=tu-clave-super-secreta-cambiar-en-produccion
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=phi3
ENVIRONMENT=development
\\\

### Paso 4: Crear Base de Datos
\\\ash
# Abrir PostgreSQL
psql -U postgres

# Ejecutar en la terminal de PostgreSQL:
CREATE DATABASE museo_interactivo;
CREATE USER museo_user WITH PASSWORD '1234';
GRANT ALL PRIVILEGES ON DATABASE museo_interactivo TO museo_user;
\\q
\\\

### Paso 5: Probar Conexión
\\\ash
python test_db.py
\\\

### Paso 6: Iniciar Servidor
\\\ash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
\\\

**Abrir en navegador:** http://localhost:8000 ✅

---

## 🎓 ESTRUCTURA DE CAPAS EXPLICADA

### LAYER 1: BASE DE DATOS (PostgreSQL)
\\\
┌─────────────────────────────────────┐
│  USUARIOS | ESPECIES | EJEMPLARES   │
│  (Tablas con 3 relaciones clave)    │
└─────────────────────────────────────┘
\\\

### LAYER 2: MODELOS (SQLAlchemy)
- Traduce tablas SQL en clases Python
- Permite querys en lenguaje natural
- Ejemplo: \db.query(Especie).filter(...)\

### LAYER 3: ESQUEMAS (Pydantic)
- Valida datos de entrada
- Asegura tipos correctos
- Ejemplo: \
ombre_comun: str\ ✓, \
ombre_comun: int\ ✗

### LAYER 4: SERVICIOS
- Lógica de negocio aislada
- Manejo de errores
- Transacciones seguras

### LAYER 5: ENDPOINTS (FastAPI)
- Reciben peticiones HTTP
- Llaman servicios
- Devuelven JSON

### LAYER 6: FRONTEND (Jinja2 + HTML)
- Muestra datos al usuario
- Interactúa con endpoints
- Chat con IA integrado

---

## 🔐 SEGURIDAD

### ✅ Lo que ESTÁ protegido:
- ✓ Contraseñas hasheadas (bcrypt)
- ✓ JWT tokens con expiración
- ✓ CORS configurado
- ✓ Validación de datos con Pydantic

### ⚠️ Lo que FALTA en Producción:
- [ ] HTTPS obligatorio
- [ ] Rate limiting
- [ ] Logs de auditoría
- [ ] Backup automático BD
- [ ] Variables de entorno en secretos

### 🔒 Cambios para Producción:

\\\python
# En app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["tudominio.com"],  # No ["*"]
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
\\\

\\\ash
# En .env (NUNCA comitear)
ENVIRONMENT=production
JWT_SECRET_KEY=  # Generar aleatoria
\\\

---

## 📊 CASOS DE USO

### 1️⃣ Un Visitante Abre la Aplicación

\\\
1. Browser → GET / → servidor FastAPI
2. FastAPI → salas.html (Jinja2)
3. HTML renderizado en browser
4. Visitante ve mapa de salas
5. Click en "Herpetología"
6. GET /herpetologia → consulta BD
7. FastAPI: SELECT * FROM especies
8. PostgreSQL devuelve 150 especies
9. Jinja2 renderiza 150 tarjetas
10. Visitante ve galería completa
\\\

### 2️⃣ Visitante Hace Pregunta al Chatbot

\\\
1. Usuario escribe: "¿Es venenosa la cobra?"
2. JS envía: POST /api/chat
3. Backend busca "cobra" en BD
4. Encuentra: Cobra Real (ID: 42)
5. Inyecta datos en prompt para Ollama
6. Ollama (IA local) procesa prompt
7. Devuelve respuesta educativa
8. JS renderiza respuesta en chat
\\\

### 3️⃣ Admin Importa CSV con 1000 especies

\\\
1. Admin sube archivo: especies.csv
2. POST /importar-csv/ (requiere JWT)
3. Backend: procesar_csv_museo()
4. Pandas lee archivo
5. Para cada fila:
   - Normaliza datos
   - Crea/busca especie en BD
   - Crea ejemplar
   - Guarda coordenadas
   - Guarda medidas (JSONB)
6. Si TODO OK: COMMIT ✓
7. Si ALGO FALLA: ROLLBACK ✗ (seguridad)
8. Admin recibe reporte
\\\

---

## 🚀 OPERACIONES COMUNES

### Agregar Nueva Especie Manualmente

\\\ash
# Opción 1: Por UI Admin
1. Login en /admin
2. Click "Nueva Especie"
3. Llenar formulario
4. Submit

# Opción 2: Por API (curl)
curl -X POST http://localhost:8000/api/admin/especies \\
  -H "Authorization: Bearer {tu_token}" \\
  -H "Content-Type: application/json" \\
  -d '{
    "grupo": "Reptil",
    "genero": "Boa",
    "especie": "constrictor",
    "nombre_comun": "Boa Constrictora",
    "dieta": "Mamíferos",
    "habitat": "Selva tropical"
  }'
\\\

### Buscar Especie

\\\ash
# Por nombre común
GET /herpetologia?buscar=cobra

# Por ID
GET /especie/42

# Toda la info
SELECT * FROM especies WHERE nombre_comun ILIKE '%cobra%';
\\\

### Actualizar Información

\\\ash
curl -X PUT http://localhost:8000/api/admin/especies/42 \\
  -H "Authorization: Bearer {token}" \\
  -H "Content-Type: application/json" \\
  -d '{"curiosidades": "Nueva información científica"}'
\\\

### Eliminar Especie

\\\ash
curl -X DELETE http://localhost:8000/api/admin/especies/42 \\
  -H "Authorization: Bearer {token}"
\\\

⚠️ **Nota:** Solo si no tiene ejemplares asociados

---

## 🐛 ERRORES COMUNES Y SOLUCIONES

| Error | Causa | Solución |
|-------|-------|----------|
| \ModuleNotFoundError: No module named 'fastapi'\ | Dependencias no instaladas | \pip install -r requirements.txt\ |
| \SQLALCHEMY_DATABASE_URL connection failed\ | PostgreSQL no está corriendo | Iniciar PostgreSQL |
| \Invalid .env file\ | Variables faltantes | Copiar template de .env.example |
| \JWT token expired\ | Token vencido | Login nuevamente |
| \Foreign key constraint failed\ | Ejemplar asignado a especie | Reasignar o eliminar ejemplar |

---

## 📈 MÉTRICAS DE RENDIMIENTO

### Consultas Optimizadas

\\\python
# LENTO ❌
especies = db.query(Especie).all()
for especie in especies:
    print(especie.ejemplares)  # N queries

# RÁPIDO ✓
especies = db.query(Especie).options(
    joinedload(Especie.ejemplares)
).all()  # 1 query
\\\

### Índices de Base de Datos

\\\sql
-- Crear índices para búsquedas rápidas
CREATE INDEX idx_nombre_comun ON especies(nombre_comun);
CREATE INDEX idx_genero_especie ON especies(genero, especie);
CREATE FULLTEXT INDEX idx_search ON especies(nombre_comun, habitat, curiosidades);
\\\

---

## 🎯 HOJA DE RUTA FUTURA

- [ ] Multi-idioma (EN, ES, PT)
- [ ] Integración Stripe (venta de tours)
- [ ] App móvil nativa (React Native)
- [ ] Realidad aumentada (especies 3D)
- [ ] Mapa interactivo con GPS
- [ ] Sistema de reservas
- [ ] Blog educativo
- [ ] API pública (GraphQL)
- [ ] Analytics avanzado
- [ ] Sistema de recomendaciones (ML)

---

## 📞 SOPORTE TÉCNICO

**Stack Stack:** Python + FastAPI + PostgreSQL
**Documentación Oficial FastAPI:** https://fastapi.tiangolo.com
**Forum PostgreSQL:** https://www.postgresql.org/community/

---

**Generado:** 2026-06-06
**Versión:** 1.0.0
**Licencia:** MIT (Proyecto Académico)

