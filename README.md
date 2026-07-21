# AgriGestor 🌱

Sistema de gestión de parcelas agrícolas desarrollado con Django + FastAPI + PostgreSQL.

## Descripción

AgriGestor permite a agricultores y técnicos de campo registrar y gestionar:
- Parcelas agrícolas con datos de suelo y ubicación
- Ciclos de cultivo con seguimiento fenológico
- Aplicaciones de insumos (fertilizantes, herbicidas, riego)
- Reportes de rendimiento, costos y utilidad por ciclo

Desarrollado para el contexto agrícola de Nayarit, México.

## Stack tecnológico

| Tecnología | Uso |
|---|---|
| Django 5.0 | ORM, modelos, panel de administración |
| FastAPI 0.111 | API REST con documentación automática |
| PostgreSQL 16 | Base de datos relacional |
| Pydantic v2 | Validación de datos y schemas |
| JWT (python-jose) | Autenticación stateless |

## Requisitos

- Python 3.11+
- PostgreSQL 14+

## Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/agrigestor.git
cd agrigestor
```

### 2. Crear y activar el entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Edita .env con tus valores reales
```

### 5. Crear la base de datos en PostgreSQL
```bash
psql postgres
```
```sql
CREATE DATABASE agrigestor_db;
CREATE USER agrigestor_user WITH PASSWORD 'tu-password';
GRANT ALL PRIVILEGES ON DATABASE agrigestor_db TO agrigestor_user;
\c agrigestor_db
GRANT ALL ON SCHEMA public TO agrigestor_user;
\q
```

### 6. Aplicar migraciones
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 7. Levantar los servidores

Django Admin:
```bash
python manage.py runserver
```

FastAPI:
```bash
uvicorn api.main:app --reload --port 8001
```

## Documentación de la API

Con el servidor corriendo abre:
- Swagger UI: http://127.0.0.1:8001/docs
- ReDoc: http://127.0.0.1:8001/redoc
- Django Admin: http://127.0.0.1:8000/admin

## Endpoints principales

### Autenticación
| Método | Endpoint | Descripción |
|---|---|---|
| POST | /api/v1/auth/registro | Crear cuenta |
| POST | /api/v1/auth/login | Obtener token JWT |
| GET | /api/v1/auth/yo | Datos del usuario autenticado |

### Parcelas
| Método | Endpoint | Descripción |
|---|---|---|
| GET | /api/v1/parcelas/ | Listar parcelas |
| POST | /api/v1/parcelas/ | Crear parcela |
| GET | /api/v1/parcelas/{id}/ | Detalle de parcela |
| PATCH | /api/v1/parcelas/{id}/ | Actualizar parcela |
| DELETE | /api/v1/parcelas/{id}/ | Eliminar parcela (soft delete) |

### Cultivos
| Método | Endpoint | Descripción |
|---|---|---|
| GET | /api/v1/parcelas/{id}/cultivos/ | Listar cultivos |
| POST | /api/v1/parcelas/{id}/cultivos/ | Crear cultivo |
| PATCH | /api/v1/parcelas/{id}/cultivos/{id}/estado/ | Cambiar estado fenológico |
| PATCH | /api/v1/parcelas/{id}/cultivos/{id}/finalizar/ | Registrar cosecha |

### Insumos
| Método | Endpoint | Descripción |
|---|---|---|
| GET | /api/v1/parcelas/{id}/cultivos/{id}/insumos/ | Listar insumos |
| POST | /api/v1/parcelas/{id}/cultivos/{id}/insumos/ | Registrar insumo |
| GET | /api/v1/parcelas/{id}/cultivos/{id}/insumos/resumen/costos/ | Resumen de costos |

### Reportes
| Método | Endpoint | Descripción |
|---|---|---|
| GET | /api/v1/reportes/resumen/ | Panel general |
| GET | /api/v1/reportes/rendimiento/ | Rendimiento por parcela |
| GET | /api/v1/reportes/ciclo/{id}/ | Reporte financiero de un ciclo |
| GET | /api/v1/reportes/comparativa/?especie=maiz | Comparativa por especie |

## Autor

Edgar Omar Palacios Manjarrez — Ingeniero en Sistemas e Ingeniero Agrónomo  
Santiago Ixcuintla, Nayarit, México