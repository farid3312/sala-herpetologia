# 🔌 DOCUMENTACIÓN API Y MODELOS

## 📊 MODELO ENTIDAD-RELACIÓN

El proyecto tiene tres tablas principales interconectadas:

### 1. USUARIOS_ADMIN

```
id (UUID) → Identificador único
nombre_completo → Nombre del administrador
correo (UNIQUE) → Email para login
password_hash → Contraseña encriptada
creado_en → Fecha de creación
```

### 2. ESPECIES

```
id (INT) → PK
grupo → "Anfibio" o "Reptil"
orden, familia, genero, especie → Clasificación taxonómica
nombre_comun → Búsqueda rápida (INDEXED)
dieta, habitat, curiosidades → Información educativa
nivel_toxicidad → Nivel de peligro
url_imagen, url_audio → Multimedia
UNIQUE(genero, especie) → No duplicados
```

### 3. EJEMPLARES_MUSEO

```
numero_coleccion (PK) → ID del frasco/especimen
especie_id (FK) → Vinculación con especies
tipo_coleccion → Tipo de referencia
en_exhibicion → Visible en galería
fecha_determinacion → Fecha de identificación
latitud_decimal, longitud_decimal → Coordenadas GPS
departamento, municipio → Ubicación geográfica
datos_morfometricos (JSONB) → Medidas: {lt, lc, peso, pie, tibia_pie, oreja, antebrazo}
registrado_en → Fecha de registro
```

## 🌐 RUTAS PÚBLICAS (Sin Autenticación)

### GET /

```
Respuesta: HTML (salas.html)
Descripción: Mapa interactivo de salas del museo
Acceso: Todos los visitantes
```

### GET /herpetologia

```
Respuesta: HTML (index.html) - Galería completa
Descripción: Lista de especies con tarjetas interactivas
Renderiza: Todas las especies desde PostgreSQL
```

### GET /especie/{id_especie}

```
Ejemplo: GET /especie/5
Parámetro: id_especie (int)
Respuesta: HTML (detalle.html) con ficha técnica completa
Incluye: Chat IA integrado para preguntas
```

### POST /api/chat

```
Content-Type: application/json

Body:
{
    "pregunta": "¿Cómo es la serpiente cobra?",
    "especie_id": "general"
}

Respuesta:
{
    "respuesta": "La cobra es una serpiente venenosa..."
}

Proceso:
1. Usuario pregunta
2. Backend busca en PostgreSQL
3. Si existe especie: inyecta datos en prompt
4. Ollama (IA local) genera respuesta
5. Devuelve respuesta al frontend

Códigos:
- 200: OK
- 400: Pregunta vacía
- 500: Error en Ollama
```

## 🔐 RUTAS ADMINISTRATIVAS (Requieren JWT)

### POST /api/admin/login

```
Content-Type: application/json

Body:
{
    "correo": "admin@museo.com",
    "password": "contraseña123"
}

Respuesta (200):
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400
}

Para futuras peticiones:
Authorization: Bearer {access_token}
```

### GET /admin/importar

```
Authorization: Bearer {token}

Respuesta: HTML (importar.html)
Descripción: Formulario para subir CSV
```

### POST /importar-csv/

```
Authorization: Bearer {token}
Content-Type: multipart/form-data

Body:
- file: archivo.csv

Respuesta (200):
{
    "mensaje": "Importación finalizada con éxito",
    "detalles": {
        "filas_procesadas": 1000,
        "especies_creadas": 850,
        "ejemplares_importados": 5000,
        "errores": 0
    }
}

Formato CSV esperado:
grupo,orden,familia,genero,especie,nombre_comun,dieta,habitat,curiosidades,nivel_toxicidad,url_imagen,url_audio
Anfibio,Anura,Hylidae,Hypsiboas,punctatus,Rana verde,Insectos,Árboles,Emite sonidos,No tóxico,/data/rana.jpg,/data/rana.mp3
```

### POST /api/admin/especies

```
Authorization: Bearer {token}
Content-Type: application/json

Body:
{
    "grupo": "Reptil",
    "orden": "Squamata",
    "familia": "Pythonidae",
    "genero": "Python",
    "especie": "bivittatus",
    "nombre_comun": "Serpiente Verde",
    "dieta": "Mamíferos pequeños",
    "habitat": "Bosques tropicales",
    "curiosidades": "Tiene termorreceptores",
    "nivel_toxicidad": "No tóxico"
}

Respuesta (201): Especie creada
Errores:
- 400: Grupo inválido
- 409: genero+especie ya existe
```

### GET /api/admin/especies

```
Authorization: Bearer {token}

Query Params:
- skip: 0
- limit: 50

Respuesta (200): Array de especies
```

### GET /api/admin/especies/{id}

```
Authorization: Bearer {token}

Parámetro: id (int)
Respuesta: Objeto especie completo
```

### PUT /api/admin/especies/{id}

```
Authorization: Bearer {token}
Content-Type: application/json

Body: Campos a actualizar (todos opcionales)
{
    "nombre_comun": "Nuevo nombre",
    "dieta": "Información actualizada"
}

Respuesta: Especie actualizada
```

### DELETE /api/admin/especies/{id}

```
Authorization: Bearer {token}

Parámetro: id (int)

Respuesta (200): Especie eliminada

Protección:
- No permite eliminar si tiene ejemplares asignados
- Error 400 si intenta violación de FK
```

## 📋 ESQUEMAS PYDANTIC

### EspecieBase

```python
grupo: str                  # "Anfibio" o "Reptil" (validado)
orden: Optional[str]
familia: Optional[str]
genero: Optional[str]
especie: Optional[str]
nombre_comun: Optional[str]
dieta: Optional[str]
habitat: Optional[str]
curiosidades: Optional[str]
nivel_toxicidad: Optional[str]
url_imagen: Optional[str]
url_audio: Optional[str]
```

### EjemplarBase

```python
numero_coleccion: str           # Identificador único
tipo_coleccion: Optional[str]   # "Referencia", "Estudio"
en_exhibicion: bool
fecha_determinacion: Optional[date]
latitud_decimal: Optional[Decimal]
longitud_decimal: Optional[Decimal]
departamento: Optional[str]
municipio: Optional[str]
datos_morfometricos: Optional[Dict]  # {lt, lc, peso, pie, ...}
```

## 🔒 AUTENTICACIÓN JWT

### Detalles Técnicos

- Algoritmo: HS256
- Validez: 24 horas
- Payload:
  ```json
  {
    "sub": "admin@museo.com",
    "exp": 1719334470,
    "iat": 1719248070
  }
  ```

### Manejo de Errores

- 401: Token inválido o faltante
- 403: Token expirado
- 422: Validación fallida

## 🧪 EJEMPLOS PRÁCTICOS

### Con curl

Login:

```bash
curl -X POST http://localhost:8000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"correo":"admin@museo.com","password":"1234"}'
```

Crear especie:

```bash
TOKEN="tu_token_aqui"
curl -X POST http://localhost:8000/api/admin/especies \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "grupo": "Reptil",
    "genero": "Naja",
    "especie": "naja",
    "nombre_comun": "Cobra Real",
    "dieta": "Otras serpientes"
  }'
```

Chat:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Es peligrosa la cobra?",
    "especie_id": "general"
  }'
```

### Con Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Login
login_resp = requests.post(
    f"{BASE_URL}/api/admin/login",
    json={"correo": "admin@museo.com", "password": "1234"}
)
token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Crear especie
resp = requests.post(
    f"{BASE_URL}/api/admin/especies",
    json={"grupo": "Reptil", "genero": "Python", "especie": "molurus"},
    headers=headers
)
print(resp.json())

# Chat
resp = requests.post(
    f"{BASE_URL}/api/chat",
    json={"pregunta": "¿Cómo es?", "especie_id": "general"}
)
print(resp.json())
```

## 💾 CONSULTAS SQL ÚTILES

```sql
-- Total de especies
SELECT COUNT(*) FROM especies;

-- Por grupo
SELECT grupo, COUNT(*) FROM especies GROUP BY grupo;

-- Buscar por nombre
SELECT * FROM especies WHERE nombre_comun ILIKE '%cobra%';

-- Inventario total
SELECT COUNT(*) FROM ejemplares_museo;

-- En exhibición
SELECT COUNT(*) FROM ejemplares_museo WHERE en_exhibicion = true;

-- Ubicación geográfica
SELECT
    e.numero_coleccion,
    s.nombre_comun,
    e.departamento,
    e.municipio
FROM ejemplares_museo e
JOIN especies s ON e.especie_id = s.id;
```

## 📈 CÓDIGOS HTTP

- 200: OK - Solicitud exitosa
- 201: Created - Recurso creado
- 400: Bad Request - Datos inválidos
- 401: Unauthorized - No autenticado
- 403: Forbidden - Token expirado
- 404: Not Found - Recurso no existe
- 409: Conflict - Duplicado
- 422: Unprocessable Entity - Validación fallida
- 500: Internal Server Error - Error servidor

---

Documentación: 2026-06-06 | Versión: 1.0.0
