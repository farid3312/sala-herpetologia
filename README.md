🗄️ Diccionario Relacional de Tablas Principales
El esquema de la base de datos se compone de las siguientes entidades estructuradas:

usuarios_admin: Controla el acceso autenticado al panel administrativo del museo.

id (UUID, PK): Identificador único global.

nombre_completo (VARCHAR): Nombre del administrador.

correo (VARCHAR, UNIQUE): Correo electrónico para el login.

password_hash (VARCHAR): Credenciales cifradas.

creado_en (TIMESTAMP): Registro de auditoría de creación.

especies: Catálogo taxonómico y biológico generalizado.

id (INT, PK): Identificador secuencial.

grupo (VARCHAR): Restringido a las categorías de la sala ('Anfibio' / 'Reptil').

orden, familia, genero, especie (VARCHAR): Clasificación científica. Restricción crítica UNIQUE(genero, especie) para evitar duplicidades biológicas.

nombre_comun (VARCHAR, INDEX): Indexado para búsquedas rápidas desde la plataforma web y tótems.

dieta, habitat, curiosidades, nivel_toxicidad (TEXT): Datos divulgativos para el visitante.

urls_multimedia (ARRAY/TEXT): Enlaces a imágenes y recursos audiovisuales del ejemplar.

ejemplares_museo: Inventario físico real de los individuos presentes en la colección física o exhibición del museo.

numero_coleccion (VARCHAR, PK): Código único interno asignado por el museo.

especie_id (INT, FK): Relación directa con la tabla de especies.

en_exhibicion (BOOL): Estado actual de visibilidad física para el público.

latitud / longitud (NUMERIC): Coordenadas decimales del punto de colecta original del espécimen.

departamento, municipio (VARCHAR): Ubicación geográfica de procedencia.

datos_morfometricos (JSONB): Datos específicos y variables del individuo (longitud hocico-cloaca, peso, estado de la cola, fórmulas escamáticas, etc.).

estadisticas_trivia: Ingesta de datos analíticos provenientes de los juegos y dinámicas gamificadas de la sala.

id (INT, PK): Identificador único de evento.

tipo_juego (VARCHAR): Clasificación de la dinámica lúdica.

id_pregunta (INT): Identificador de la pregunta formulada.

opcion_correcta (INT) / respuesta_usuario (INT): Comparativa de opciones para evaluación.

acierto (BOOL): Bandera de éxito para cálculo inmediato de score.

fecha_registro (TIMESTAMP): Marca temporal para análisis cronológico de conocimiento del visitante.

registro_visitantes: Monitoreo y control del flujo de accesos a la sala de exhibición.

id (INT, PK): Identificador de registro.

origen (VARCHAR): Canal de entrada del visitante, discriminado entre 'qr' (escaneo de tótems) o 'directo' (navegación o pantallas físicas).

fecha_acceso (TIMESTAMP): Registro cronológico de visitas para generación de reportes de tráfico.

interacciones_chatbot: Historial detallado de consultas guiadas por Inteligencia Artificial conversacional dentro de la sala.

id (INT, PK): Identificador único del mensaje/sesión.

especie_consultada (VARCHAR): Filtro de tracking sobre qué tipo de reptil o anfibio genera más interés.

pregunta_usuario (TEXT): Transcripción de la duda del usuario.

respuesta_ia (TEXT): Réplica generada por el asistente virtual.

fecha_interaccion (TIMESTAMP): Estampa de tiempo de la interacción.

🗄️ Diccionario Relacional de Tablas Principales
El esquema de la base de datos se compone de las siguientes entidades estructuradas:

usuarios_admin: Controla el acceso autenticado al panel administrativo del museo.

id (UUID, PK): Identificador único global.

nombre_completo (VARCHAR): Nombre del administrador.

correo (VARCHAR, UNIQUE): Correo electrónico para el login.

password_hash (VARCHAR): Credenciales cifradas.

creado_en (TIMESTAMP): Registro de auditoría de creación.

especies: Catálogo taxonómico y biológico generalizado.

id (INT, PK): Identificador secuencial.

grupo (VARCHAR): Restringido a las categorías de la sala ('Anfibio' / 'Reptil').

orden, familia, genero, especie (VARCHAR): Clasificación científica. Restricción crítica UNIQUE(genero, especie) para evitar duplicidades biológicas.

nombre_comun (VARCHAR, INDEX): Indexado para búsquedas rápidas desde la plataforma web y tótems.

dieta, habitat, curiosidades, nivel_toxicidad (TEXT): Datos divulgativos para el visitante.

urls_multimedia (ARRAY/TEXT): Enlaces a imágenes y recursos audiovisuales del ejemplar.

ejemplares_museo: Inventario físico real de los individuos presentes en la colección física o exhibición del museo.

numero_coleccion (VARCHAR, PK): Código único interno asignado por el museo.

especie_id (INT, FK): Relación directa con la tabla de especies.

en_exhibicion (BOOL): Estado actual de visibilidad física para el público.

latitud / longitud (NUMERIC): Coordenadas decimales del punto de colecta original del espécimen.

departamento, municipio (VARCHAR): Ubicación geográfica de procedencia.

datos_morfometricos (JSONB): Datos específicos y variables del individuo (longitud hocico-cloaca, peso, estado de la cola, fórmulas escamáticas, etc.).

estadisticas_trivia: Ingesta de datos analíticos provenientes de los juegos y dinámicas gamificadas de la sala.

id (INT, PK): Identificador único de evento.

tipo_juego (VARCHAR): Clasificación de la dinámica lúdica.

id_pregunta (INT): Identificador de la pregunta formulada.

opcion_correcta (INT) / respuesta_usuario (INT): Comparativa de opciones para evaluación.

acierto (BOOL): Bandera de éxito para cálculo inmediato de score.

fecha_registro (TIMESTAMP): Marca temporal para análisis cronológico de conocimiento del visitante.

registro_visitantes: Monitoreo y control del flujo de accesos a la sala de exhibición.

id (INT, PK): Identificador de registro.

origen (VARCHAR): Canal de entrada del visitante, discriminado entre 'qr' (escaneo de tótems) o 'directo' (navegación o pantallas físicas).

fecha_acceso (TIMESTAMP): Registro cronológico de visitas para generación de reportes de tráfico.

interacciones_chatbot: Historial detallado de consultas guiadas por Inteligencia Artificial conversacional dentro de la sala.

id (INT, PK): Identificador único del mensaje/sesión.

especie_consultada (VARCHAR): Filtro de tracking sobre qué tipo de reptil o anfibio genera más interés.

pregunta_usuario (TEXT): Transcripción de la duda del usuario.

respuesta_ia (TEXT): Réplica generada por el asistente virtual.

fecha_interaccion (TIMESTAMP): Estampa de tiempo de la interacción.

**Configuración del Entorno
Clonar el repositorio:**

bash''
git clone [https://github.com/farid3312/sala-herpetologia.git](https://github.com/farid3312/sala-herpetologia.git)
cd sala-herpetologia
''
Crear y activar un entorno virtual.
Instalar las dependencias del sistema

Configurar las variables de entorno (.env):
bash´´
DATABASE_URL=postgresql://usuario:password@localhost:5432/sala_herpetologia
SECRET_KEY=tu_clave_secreta_aqui


👥 Desarrolladores y Créditos
Proyecto desarrollado para la optimización tecnológica de la Sala de Herpetología del Museo de Historia Natural de la Universidad del Cauca por:

Farid Carvajal

Brandon Orte

