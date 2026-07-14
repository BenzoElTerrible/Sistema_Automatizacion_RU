# Sistema de Automatización de Resoluciones Universitarias

Sistema web desarrollado para apoyar al Departamento de Postgrado de la Universidad de Talca en la creación, gestión y respaldo de Resoluciones Universitarias (RU).

La aplicación permite administrar resoluciones, consultar antecedentes históricos y generar documentos en formato Word.

## Funcionalidades principales

- Registro, consulta, modificación y eliminación de resoluciones universitarias.
- Carga y almacenamiento de archivos PDF asociados a una resolución.
- Verificación de la integridad de los archivos mediante hash SHA-256 y tamaño.
- Gestión de tipos de resolución, programas de postgrado y textos de vistos.
- Consulta de resoluciones históricas por carrera.
- Registro y validación de nombramientos de directores.
- Descarga conjunta de respaldos en formato ZIP.
- Generación asistida de resoluciones en Word.

## Tecnologías utilizadas

- **Python 3.12:** lenguaje principal del proyecto.
- **Django 5.2:** framework web y capa de acceso a datos.
- **Django REST Framework 3.15:** construcción de los endpoints de la aplicación.
- **PostgreSQL 17:** base de datos relacional.
- **python-docx:** generación de resoluciones en formato Word (`.docx`).
- **psycopg 3.2:** conexión entre Django y PostgreSQL.
- **python-decouple:** lectura de variables de entorno.
- **HTML y CSS:** interfaz web renderizada mediante plantillas de Django.
- **Docker y Docker Compose:** creación y ejecución reproducible del entorno.
- **Git y GitHub:** control de versiones y colaboración del equipo.

## Arquitectura del proyecto

El sistema está dividido en tres aplicaciones Django:

| Aplicación | Responsabilidad |
| --- | --- |
| `base` | Administra datos maestros, como tipos de programa, tipos de RU, carreras de postgrado y vistos. |
| `generador` | Construye resoluciones mediante un formulario y genera archivos Word. |
| `repositorio` | Gestiona el registro, consulta, actualización, eliminación, integridad y respaldo de las resoluciones. |

Estructura principal:

```text
Sistema_Automatizacion_RU/
├── app/
│   ├── apps/
│   │   ├── base/
│   │   ├── generador/
│   │   └── repositorio/
│   ├── config/
│   └── manage.py
├── .env.example
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Requisitos previos

La forma recomendada de ejecutar el proyecto es con Docker. Para ello se necesita:

- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Docker Compose, incluido en las versiones actuales de Docker Desktop

Para una instalación manual también se requiere Python 3.12 y PostgreSQL 17.

## Instalación con Docker

### 1. Clonar el repositorio

```bash
git clone https://github.com/BenzoElTerrible/Sistema_Automatizacion_RU.git
cd Sistema_Automatizacion_RU
```

### 2. Crear el archivo de variables de entorno

En Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

En Linux o macOS:

```bash
cp .env.example .env
```

El archivo `.env` contiene datos locales y no debe subirse a Git.

### 3. Construir e iniciar los contenedores

```bash
docker compose up --build -d
```

### 4. Aplicar las migraciones

```bash
docker compose exec web python manage.py migrate
```

### 5. Cargar los datos iniciales

Los fixtures deben cargarse en el siguiente orden:

```bash
docker compose exec web python manage.py loaddata tipos_programa
docker compose exec web python manage.py loaddata tipos_ru
docker compose exec web python manage.py loaddata carreras_postgrado
```

### 6. Abrir el sistema

- Aplicación: <http://localhost:8000/>
- Administración de Django: <http://localhost:8000/admin/>
- Gestión de resoluciones: <http://localhost:8000/resoluciones/gestion/>
- Creación de resoluciones: <http://localhost:8000/resoluciones/crear/>
- Gestión de vistos: <http://localhost:8000/resoluciones/vistos/>

Para revisar los registros de ejecución:

```bash
docker compose logs -f web
```

Para detener el sistema:

```bash
docker compose down
```

## Ejecución de pruebas

```bash
docker compose exec web python manage.py test
```

## Flujo general del sistema

1. El usuario registra o consulta una resolución desde la interfaz web.
2. Las vistas de Django y los endpoints de Django REST Framework validan la solicitud.
3. Los datos se almacenan en PostgreSQL mediante los modelos de Django.
4. Los archivos asociados se guardan en el volumen de medios y se verifica su integridad.
5. El módulo generador utiliza los datos ingresados para producir documentos en formato Word.

## Buenas prácticas para colaborar

Antes de comenzar una tarea, actualice su rama:

```bash
git pull
```

Realice commits pequeños y descriptivos:

```bash
git add .
git commit -m "Agrega descripción breve del cambio"
git push
```

No se deben subir al repositorio:

- El archivo `.env`.
- Contraseñas, claves privadas o credenciales reales.
- Entornos virtuales.
- Archivos temporales o datos locales de PostgreSQL.
- Documentos cargados localmente en el directorio `media`.

Proyecto desarrollado para la asignatura Ingeniería del Software de la Universidad de Talca.
