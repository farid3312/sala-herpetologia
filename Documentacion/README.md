# 📚 DOCUMENTACIÓN COMPLETA - MUSEO INTERACTIVO HERPETOLOGÍA

---

## 🚀 ACCESO RÁPIDO

> **¿Primera vez aquí?** Elige una opción:

| Opción                  | Descripción                             | Ir a                                                 |
| ----------------------- | --------------------------------------- | ---------------------------------------------------- |
| 🌐 **Portal Visual**    | Interfaz gráfica con navegación por rol | [index.html](./index.html)                           |
| 📍 **Punto de Inicio**  | Guía rápida según tu rol                | [INICIO_AQUI.md](./INICIO_AQUI.md)                   |
| 🗺️ **Portal Unificado** | Todos los documentos en un solo lugar   | [PORTAL_DOCUMENTACION.md](./PORTAL_DOCUMENTACION.md) |
| 👋 **Bienvenida**       | Introducción a la documentación         | [BIENVENIDA.md](./BIENVENIDA.md)                     |

**Recomendación:** Si es tu primera vez, abre `index.html` en tu navegador.

---

## 📋 TABLA DE CONTENIDOS

1. [Visión General](#visión-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Estructura de Carpetas](#estructura-de-carpetas)
4. [Requisitos Previos](#requisitos-previos)
5. [Instalación y Configuración](#instalación-y-configuración)
6. [Base de Datos](#base-de-datos)
7. [API REST](#api-rest)
8. [Frontend](#frontend)
9. [Servicios Principales](#servicios-principales)
10. [Guía de Desarrollo](#guía-de-desarrollo)
11. [Escalabilidad](#escalabilidad)
12. [Solución de Problemas](#solución-de-problemas)

---

## 🎯 VISIÓN GENERAL

**Museo Interactivo Herpetología** es una aplicación web desarrollada con **FastAPI** y **PostgreSQL** que permite:

- 📱 **Galería interactiva** de especies de anfibios y reptiles
- 💬 **Chat educativo IA** con Ollama para guiar a los visitantes
- 📊 **Gestión de inventario** de especímenes del museo
- 📥 **Importación masiva** de datos desde archivos CSV
- 🔐 **Panel administrativo** con autenticación JWT
- 🌐 **Interfaz responsiva** con Jinja2 templates

**Tipo de Proyecto**: Backend educativo interactivo
**Stack Tecnológico**: Python 3.9+, FastAPI 0.135.1, PostgreSQL, SQLAlchemy, Pydantic
**Licencia**: Proyecto académico

---

## 🏗️ ARQUITECTURA DEL SISTEMA

### Diagrama de Capas

\\\
┌─────────────────────────────────────────┐
│ INTERFAZ DE USUARIO │
│ (Jinja2 Templates + HTML + Bootstrap) │
└────────────────┬────────────────────────┘
│
┌────────────────▼────────────────────────┐
│ CAPA DE API (FastAPI) │
│ ├─ /api/chat (IA) │
│ ├─ /api/importar-csv (Datos) │
│ ├─ /api/admin/_ (Gestión) │
│ └─ /herpetologia/_ (Galería) │
└────────────────┬────────────────────────┘
│
┌────────────────▼────────────────────────┐
│ CAPA DE SERVICIOS (Lógica) │
│ ├─ import_service │
│ ├─ especie_service │
│ └─ ejemplar_service │
└────────────────┬────────────────────────┘
│
┌────────────────▼────────────────────────┐
│ CAPA DE MODELOS (Datos) │
│ ├─ UsuarioAdmin │
│ ├─ Especie │
│ └─ EjemplarMuseo │
└────────────────┬────────────────────────┘
│
┌────────────────▼────────────────────────┐
│ PostgreSQL (Base de Datos) │
└─────────────────────────────────────────┘
\\\

---

## 📁 ESTRUCTURA DE CARPETAS

\\\
museo*interactivo/
│
├── app/ # Núcleo de la aplicación
│ ├── **init**.py
│ ├── main.py # Punto de entrada, configuración de FastAPI
│ ├── database.py # Conexión a PostgreSQL
│ ├── models.py # Modelos SQLAlchemy
│ ├── schemas.py # Esquemas Pydantic (validación)
│ │
│ ├── api/ # Enrutadores REST
│ │ ├── **init**.py
│ │ ├── api_router.py # Agregador de rutas
│ │ │
│ │ └── endpoints/ # Puntos finales específicos
│ │ ├── **init**.py
│ │ ├── visitor.py # Rutas públicas (galería, chat)
│ │ ├── data_import.py # Importación de CSV
│ │ └── admin.py # Panel administrativo
│ │
│ └── services/ # Lógica de negocio
│ ├── **init**.py
│ ├── import_service.py # Procesamiento de CSV
│ ├── especie_service.py # CRUD de especies
│ └── ejemplar_service.py # Gestión de ejemplares físicos
│
├── static/ # Archivos estáticos
│ ├── favicon.ico
│ ├── fondo admin.webp
│ └── [imágenes, CSS, JS]
│
├── templates/ # Plantillas HTML (Jinja2)
│ ├── base.html # Layout base
│ ├── index.html # Galería de especies
│ ├── detalle.html # Ficha técnica de especie
│ ├── admin.html # Dashboard admin
│ ├── importar.html # Formulario de importación
│ ├── salas.html # Mapa de salas
│ ├── proximamente.html # Salas en construcción
│ └── login.html # Acceso administrativo
│
├── data/ # Almacenamiento de imágenes y datos
│ ├── temp*\*.csv # Archivos CSV temporales
│ └── [imágenes de especies]
│
├── requirements.txt # Dependencias del proyecto
├── .env # Variables de entorno (NO COMMITEAR)
├── .gitignore
├── test_db.py # Script para probar conexión a BD
└── README.md # Esta documentación
\\\

---

## 📦 REQUISITOS PREVIOS

### Software Obligatorio

- **Python 3.9+** (recomendado 3.10 o 3.11)
- **PostgreSQL 12+** (base de datos)
- **Ollama** (para el chatbot IA local - opcional)
- **Git** (para control de versiones)

### Herramientas Opcionales

- **pgAdmin** o **DBeaver** (gestión visual de PostgreSQL)
- **Postman** o **Insomnia** (prueba de endpoints)
- **VS Code** con extensión Python

---

## 🚀 INSTALACIÓN Y CONFIGURACIÓN

### Paso 1: Clonar el Repositorio

\\\ash
git clone https://github.com/farid3312/sala-herpetologia.git
cd sala-herpetologia
\\\

### Paso 2: Crear Entorno Virtual

\\\ash

# En Windows

python -m venv venv
venv\\Scripts\\activate

# En macOS/Linux

python3 -m venv venv
source venv/bin/activate
\\\

### Paso 3: Instalar Dependencias

\\\ash
pip install -r requirements.txt
\\\

### Paso 4: Configurar Variables de Entorno

Crea un archivo \.env\ en la raíz del proyecto:

\\\env

# PostgreSQL

DB_USER=postgres
DB_PASSWORD=tu_contraseña_segura
DB_HOST=localhost
DB_PORT=5432
DB_NAME=museo_interactivo

# JWT (para autenticación)

JWT_SECRET_KEY=tu_clave_secreta_muy_segura_cambiar_en_produccion
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Ollama (si usas IA local)

OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=phi3

# Entorno

ENVIRONMENT=development # development, staging, production
\\\

### Paso 5: Crear Base de Datos PostgreSQL

\\\ash

# Conectar a PostgreSQL como superusuario

psql -U postgres

# Crear base de datos

CREATE DATABASE museo_interactivo;

# Crear usuario con permisos

CREATE USER museo_user WITH PASSWORD 'tu_contraseña_segura';
GRANT ALL PRIVILEGES ON DATABASE museo_interactivo TO museo_user;

# Salir

\\q
\\\

### Paso 6: Probar Conexión a Base de Datos

\\\ash
python test_db.py
\\\

**Salida esperada:**
\\\
✅ Conexión al motor de base de datos exitosa.
✅ Sesión de base de datos operativa.
✅ Tablas sincronizadas (creadas si no existían).
\\\

### Paso 7: Iniciar la Aplicación

\\\ash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
\\\

**Navegadores:**

- 🌐 Aplicación: http://localhost:8000
- 📚 Documentación API: http://localhost:8000/docs (Swagger UI)
- 🔍 Alternativa: http://localhost:8000/redoc (ReDoc)

---

## 🗄️ BASE DE DATOS

### Modelo de Datos

#### 1. **Tabla: usuarios_admin**

Gestiona usuarios administradores con autenticación JWT.

\\\sql
CREATE TABLE usuarios_admin (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
nombre_completo VARCHAR(150) NOT NULL,
correo VARCHAR(150) UNIQUE NOT NULL,
password_hash VARCHAR(255) NOT NULL,
creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
\\\

**Campos:**

- \id\: Identificador único (UUID)
- \
  ombre_completo\: Nombre del administrador
- \correo\: Email único para login
- \password_hash\: Contraseña hasheada (nunca se guarda en texto plano)
- \creado_en\: Timestamp de creación

---

#### 2. **Tabla: especies**

Almacena información taxonómica de las especies.

\\\sql
CREATE TABLE especies (
id SERIAL PRIMARY KEY,
grupo VARCHAR(50) NOT NULL, -- 'Anfibio' o 'Reptil'
orden VARCHAR(100),
familia VARCHAR(100),
genero VARCHAR(100),
especie VARCHAR(100),
nombre_comun VARCHAR(150) INDEXED, -- Búsqueda rápida
dieta TEXT, -- Descripción de alimentación
habitat TEXT, -- Hábitat natural
curiosidades TEXT, -- Datos educativos
nivel_toxicidad TEXT, -- 'No tóxico', 'Moderado', 'Altamente tóxico'
url_imagen TEXT, -- Ruta de imagen
url_audio TEXT, -- Audio descriptivo
UNIQUE(genero, especie) -- Evita duplicados taxonómicos
);
\\\

**Propósito:**

- Registro central de biodiversidad
- Información educativa para visitantes
- Base para el chatbot IA

**Índices:**

- \
  ombre_comun\ → búsquedas rápidas
- \UNIQUE(genero, especie)\ → evita duplicados

---

#### 3. **Tabla: ejemplares_museo**

Inventario físico de los especímenes en el museo.

\\\sql
CREATE TABLE ejemplares_museo (
numero_coleccion VARCHAR(50) PRIMARY KEY, -- Identificador de frasco/vitrina
especie_id INTEGER FOREIGN KEY -> especies.id,
tipo_coleccion VARCHAR(50) DEFAULT 'Referencia',
en_exhibicion BOOLEAN DEFAULT false, -- ¿Está en exhibición pública?
fecha_determinacion DATE,
latitud_decimal NUMERIC(10, 8), -- Coordenada GPS decimal
longitud_decimal NUMERIC(11, 8),
departamento VARCHAR(100), -- Ubicación geográfica (ej: Cauca)
municipio VARCHAR(100), -- Municipio de origen
datos_morfometricos JSONB DEFAULT '{}', -- Medidas: {lt, lc, peso, pie, tibia_pie, oreja, antebrazo}
registrado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (especie_id) REFERENCES especies(id) ON DELETE RESTRICT
);
\\\

**Propósito:**

- Gestión del inventario físico
- Seguimiento de especímenes
- Datos de colecta geográfica

**Protección de Integridad:**

- \ON DELETE RESTRICT\: Impide eliminar una especie si tiene ejemplares asignados

---

### Relaciones entre Tablas

\\\
usuarios_admin (1) ──────────────────── (N) [sesiones administrativas]

especies (1) ──────────── (N) ejemplares_museo
↑
└─ Información taxonómica
└─ Datos educativos
└─ Recursos multimedia

ejemplares_museo (N) ──────────── (1) especies
└─ Inventario del museo
└─ Ubicación física
└─ Medidas morfométricas
\\\

---

## 🔌 API REST

### Autenticación

Todos los endpoints administrativos requieren **JWT Token**.

#### Login

\\\http
POST /api/admin/login
Content-Type: application/json

{
"correo": "admin@museo.com",
"password": "contraseña123"
}
\\\

**Respuesta (200):**
\\\json
{
"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
"token_type": "bearer",
"expires_in": 86400
}
\\\

### Endpoints Públicos (Visitantes)

#### 1. Página de Inicio

\\\http
GET /
\\\
Muestra el mapa interactivo de salas.

#### 2. Galería de Especies

\\\http
GET /herpetologia
\\\
Lista todas las especies con tarjetas interactivas.

**Datos devueltos:**

- ID, nombre común, grupo, imagen, enlace a detalle

#### 3. Ficha Técnica de Especie

\\\http
GET /especie/{id_especie}
\\\

**Ejemplo:**
\\\
GET /especie/5
\\\

**Respuesta HTML con:**

- Clasificación taxonómica completa
- Descripción, hábitat, dieta
- Curiosidades científicas
- Nivel de toxicidad
- Imagen y audio

#### 4. Chat Educativo IA

\\\http
POST /api/chat
Content-Type: application/json

{
"pregunta": "¿Cómo es la cobra real?",
"especie_id": "general" // O ID específico de especie
}
\\\

**Flujo del Chat:**

1. Usuario pregunta sobre una especie
2. Backend busca datos en PostgreSQL
3. Si la especie existe, inyecta información en el prompt
4. Ollama (IA local) genera respuesta educativa
5. Respuesta se devuelve al frontend

**Respuesta:**
\\\json
{
"respuesta": "La cobra real es el reptil más largo del mundo. Es una serpiente constrictora que puede alcanzar hasta 5.5 metros..."
}
\\\

### Endpoints Administrativos (Requieren JWT)

#### 1. Importar CSV

\\\http
POST /importar-csv/
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: archivo.csv
\\\

**Formato esperado del CSV:**
\\\
grupo,orden,familia,genero,especie,nombre_comun,dieta,habitat,curiosidades,nivel_toxicidad,url_imagen,url_audio
Anfibio,Anura,Hylidae,Hypsiboas,punctatus,Rana verde,Insectos,Árboles tropicales,Emite sonidos nocturnos,No tóxico,/data/rana.jpg,/data/rana.mp3
\\\

**Respuesta (200):**
\\\json
{
"mensaje": "Importación finalizada con éxito",
"detalles": {
"filas_procesadas": 150,
"especies_creadas": 142,
"ejemplares_importados": 8500,
"errores": 0
}
}
\\\

#### 2. Crear Especie Manual

\\\http
POST /api/admin/especies
Authorization: Bearer {token}
Content-Type: application/json

{
"grupo": "Reptil",
"genero": "Python",
"especie": "bivittatus",
"nombre_comun": "Serpiente verde",
"familia": "Pythonidae",
"dieta": "Mamíferos pequeños",
"habitat": "Bosques tropicales de Asia",
"curiosidades": "Tiene termorreceptores para detectar presas"
}
\\\

#### 3. Listar Especies

\\\http
GET /api/admin/especies
Authorization: Bearer {token}
\\\

#### 4. Actualizar Especie

\\\http
PUT /api/admin/especies/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
"nombre_comun": "Nuevo nombre",
"dieta": "Información actualizada"
}
\\\

#### 5. Eliminar Especie

\\\http
DELETE /api/admin/especies/{id}
Authorization: Bearer {token}
\\\

**Protección:** No permite eliminar si hay ejemplares asignados.

---

## 🎨 FRONTEND

### Estructura de Plantillas

#### 1. **base.html**

Template base con:

- Bootstrap 5 para responsividad
- Navbar de navegación
- Footer con información
- Estilos globales

#### 2. **salas.html**

Mapa interactivo de salas:

- Herpetología (implementada)
- Ornitología (próximamente)
- Entomología (próximamente)
- Mastozoología (próximamente)
- Geología y Paleontología (próximamente)
- Oceanografía (próximamente)
- Arqueología (próximamente)

#### 3. **index.html**

Galería de especies con:

- Cards con imagen, nombre científico y común
- Búsqueda y filtrado por grupo (Anfibio/Reptil)
- Enlace a ficha técnica individual

#### 4. **detalle.html**

Ficha técnica completa:

- Clasificación taxonómica
- Descripción y curiosidades
- Chat IA integrado para preguntas
- Galería de imágenes
- Reproductor de audio

#### 5. **admin.html**

Panel administrativo:

- Dashboard con estadísticas
- CRUD de especies
- Gestión de ejemplares
- Reportes

#### 6. **importar.html**

Formulario de importación CSV:

- Drag & drop para archivos
- Validación de formato
- Barra de progreso
- Reporte de errores/éxitos

---

## 🔧 SERVICIOS PRINCIPALES

### 1. **import_service.py**

**Función:** \procesar_csv_museo(ruta_archivo, db)\

**Flujo:**
\\\

1. Lee archivo CSV con Pandas
2. Valida columnas requeridas
3. Para cada fila:
   a. Normaliza datos (mayúsculas, tildes, espacios)
   b. Busca o crea especie taxonómica
   c. Crea ejemplar físico
   d. Asocia medidas morfométricas (JSONB)
4. Aplica transacción (todo o nada)
5. Devuelve reporte de importación
   \\\

**Manejo de Errores:**

- Si falla una fila, **toda la importación se deshace** (ACID)
- Devuelve detalles específicos del error

### 2. **especie_service.py**

**Funciones CRUD:**

#### \crear_especie_manual(db, datos_especie)\

- Valida unicidad de género+especie
- Normaliza texto
- Maneja errores transaccionales

#### \eliminar_especie(db, especie_id)\

- **Protección crítica:** Impide eliminar si hay ejemplares
- Cascada segura

#### \ctualizar_especie(db, especie_id, datos_actualizacion)\

- Actualización parcial (PATCH)
- Detecta colisiones taxonómicas
- Normaliza datos

#### \obtener_especie(db, especie_id)\

- Búsqueda por ID
- Lanza ValueError si no existe

### 3. **ejemplar_service.py**

**Funciones:**

- \crear_ejemplar\ - Registra especímen físico
- \listar_ejemplares_por_especie\ - Inventario
- \ctualizar_datos_morfometricos\ - Medidas
- \cambiar_estado_exhibicion\ - On/Off para exposición

---

## 👨‍💻 GUÍA DE DESARROLLO

### Flujo de Trabajo

#### 1. Crear Nueva Ruta API

Archivo: \pp/api/endpoints/nueva_ruta.py\

\\\python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Especie

router = APIRouter(prefix="/api/nueva", tags=["nueva"])

@router.get("/ejemplo")
async def mi_ruta(db: Session = Depends(get_db)):
\"\"\"Descripción de la ruta.\"\"\"
datos = db.query(Especie).all()
return {"datos": datos}
\\\

Luego, registrar en \pp/api/api_router.py\:

\\\python
from app.api.endpoints.nueva_ruta import router as nueva_router

api_router.include_router(nueva_router)
\\\

#### 2. Crear Nuevo Modelo

Archivo: \pp/models.py\

\\\python
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class MiModelo(Base):
**tablename** = "mi_tabla"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    especie_id = Column(Integer, ForeignKey("especies.id"))

    especie = relationship("Especie", back_populates="mi_modelo")

\\\

#### 3. Crear Esquema Pydantic

Archivo: \pp/schemas.py\

\\\python
from pydantic import BaseModel, Field
from typing import Optional

class MiModeloBase(BaseModel):
nombre: str = Field(..., min_length=1)

class MiModeloCreate(MiModeloBase):
pass

class MiModeloResponse(MiModeloBase):
id: int

    class Config:
        from_attributes = True

\\\

#### 4. Crear Servicio

Archivo: \pp/services/mi_servicio.py\

\\\python
from sqlalchemy.orm import Session
from app.models import MiModelo
from app.schemas import MiModeloCreate

def crear_mi_objeto(db: Session, datos: MiModeloCreate):
objeto = MiModelo(\*\*datos.dict())
db.add(objeto)
db.commit()
db.refresh(objeto)
return objeto
\\\

### Testing

Prueba rápida con \curl\:

\\\ash

# Obtener todas las especies

curl http://localhost:8000/herpetologia

# Chat

curl -X POST http://localhost:8000/api/chat \\
-H "Content-Type: application/json" \\
-d '{"pregunta":"¿Cómo es la serpiente?","especie_id":"general"}'
\\\

---

## 📈 ESCALABILIDAD

### Mejoras para Producción

#### 1. **Caché Redis**

\\\python
from redis import Redis

redis_client = Redis(host='localhost', port=6379, db=0)

# Cachear especies (1 hora)

ESPECIES_CACHE_TTL = 3600
cached = redis_client.get('all_species')
\\\

#### 2. **Base de Datos**

- Usar replicas de lectura para \SELECT\
- Implementar particionamiento por grupo (Anfibio/Reptil)
- Índices adicionales en búsquedas frecuentes

#### 3. **API**

- Rate limiting por IP
- Compresión gzip
- CDN para imágenes
- Paginación en listados

#### 4. **Contenedorización**

Crear \Dockerfile\:

\\\dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
\\\

Crear \docker-compose.yml\:

\\\yaml
version: '3.8'

services:
postgres:
image: postgres:15
environment:
POSTGRES_DB: museo_interactivo
POSTGRES_PASSWORD: contraseña
ports: - "5432:5432"

api:
build: .
depends_on: - postgres
ports: - "8000:8000"
environment:
DB_HOST: postgres
DB_USER: postgres
DB_PASSWORD: contraseña
\\\

Ejecutar:
\\\ash
docker-compose up -d
\\\

### Monitoreo

Agregar Prometheus + Grafana para métricas.

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error: Connection refused (PostgreSQL)

**Causa:** PostgreSQL no está corriendo.

**Solución:**
\\\ash

# Windows

pg_ctl -D "C:\\Program Files\\PostgreSQL\\15\\data" start

# macOS

brew services start postgresql

# Linux

sudo systemctl start postgresql
\\\

### Error: "Módulo no encontrado"

**Causa:** Entorno virtual no activado.

**Solución:**
\\\ash

# Windows

venv\\Scripts\\activate

# macOS/Linux

source venv/bin/activate

pip install -r requirements.txt
\\\

### Error: JWT Token inválido

**Causa:** Token expirado o clave secreta cambió.

**Solución:**

- Hacer login nuevamente
- Verificar JWT_SECRET_KEY en .env

### Error: "La especie tiene ejemplares asociados"

**Causa:** Intentar eliminar especie con inventario.

**Solución:**

- Reasignar ejemplares a otra especie
- O eliminar los ejemplares primero

### Error: CSV no se importa

**Causa:** Formato incorrecto.

**Solución:**

1. Verificar columnas coincidan con schema
2. Validar que grupo sea "Anfibio" o "Reptil"
3. Revisar logs en consola de Uvicorn

---

## 📞 CONTACTO Y SOPORTE

**Proyecto:** Museo Interactivo Herpetología
**Universidad:** Universidad del Cauca
**Repositorio:** https://github.com/farid3312/sala-herpetologia

---

## 📝 NOTAS IMPORTANTES

1. ✅ **Nunca comitear .env** (contiene secretos)
2. ✅ **Cambiar JWT_SECRET_KEY en producción**
3. ✅ **Usar HTTPS en producción**
4. ✅ **Hacer backup regular de PostgreSQL**
5. ✅ **Monitorear logs de Uvicorn**

---

**Documentación Generada:** 2026-06-06
**Versión del Proyecto:** 1.0.0
**Stack:** FastAPI 0.135.1 | PostgreSQL 12+ | Python 3.9+
