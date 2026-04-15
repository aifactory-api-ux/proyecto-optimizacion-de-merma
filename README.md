# Merma Optimization System

Sistema de optimización de merma para productos perecederos.

## Visión del Proyecto

Este sistema busca abordar la ineficiencia actual en la gestión de inventario de productos perecederos, caracterizada por la falta de visibilidad, predicción y decisiones reactivas que resultan en sobrestock y alta merma.

## Características Principales

- **Predicción de Demanda**: Modelo predictivo por tienda y producto
- **Análisis Histórico**: Visualización de ventas, inventario y merma
- **Sistema de Alertas**: Identificación de riesgo de merma
- **Motor de Recomendaciones**: Reposición, descuento, no reposición
- **Dashboard de Visualización**: Métricas y tendencias en tiempo real

## Stack Tecnológico

- **Backend**: Python 3.11 + FastAPI
- **Frontend**: React 18 + TypeScript
- **Base de Datos**: PostgreSQL 15
- **Caché**: Redis 7
- **Infraestructura**: Docker, AWS (EC2, RDS, S3)

## Requisitos Previos

- Docker 26.1.3+
- Docker Compose 2.27.0+
- 4GB RAM mínimo
- 10GB espacio en disco

## Instalación

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd merma-optimization
```

### 2. Configurar variables de entorno

El archivo `.env.example` contiene todas las variables requeridas. El script `run.sh` creará automáticamente un `.env` desde este archivo.

```bash
# Configuración de base de datos
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=merma_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Configuración de Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Configuración JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración AWS (opcional)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET=

# Configuración de aplicación
DEBUG=False
CORS_ORIGINS=["http://localhost:3000"]
```

### 3. Ejecutar la aplicación

```bash
./run.sh
```

Este script:
- Verifica que Docker esté instalado
- Crea el archivo `.env` desde `.env.example`
- Construye las imágenes de Docker
- Inicia todos los servicios
- Espera a que los servicios estén saludables
- Muestra las URLs de acceso

## Acceso a la Aplicación

| Servicio | URL | Credenciales por defecto |
|----------|-----|--------------------------|
| Frontend | http://localhost:3000 | admin / admin123 |
| API Docs | http://localhost:8080/docs | - |
| PostgreSQL | localhost:5432 | postgres / (configurado) |
| Redis | localhost:6379 | - |

## API Endpoints

### Autenticación
- `POST /api/v1/auth/login` - Iniciar sesión

### Dashboard
- `GET /api/v1/dashboard/metrics` - Métricas consolidadas

### Alertas
- `GET /api/v1/alerts` - Lista de alertas activas

### Merma
- `GET /api/v1/waste/by-product` - Merma por producto
- `GET /api/v1/waste/trend` - Tendencia de merma

### Predicción
- `GET /api/v1/demand/prediction` - Predicción de demanda

## Estructura del Proyecto

```
├── backend/
│   ├── app/
│   │   ├── api/          # Endpoints REST
│   │   ├── core/         # Configuración y seguridad
│   │   ├── models/       # Modelos SQLAlchemy
│   │   ├── schemas/      # Modelos Pydantic
│   │   ├── services/     # Lógica de negocio
│   │   ├── db/           # Conexión a base de datos
│   │   ├── aws/          # Integración S3
│   │   ├── ingestion/    # Ingestión de datos
│   │   └── tasks/        # Tareas programadas
│   ├── shared/           # Utilidades compartidas
│   └── tests/            # Pruebas unitarias
├── frontend/
│   ├── src/
│   │   ├── api/          # Cliente API
│   │   ├── components/   # Componentes React
│   │   ├── hooks/        # Custom hooks
│   │   ├── types/        # Tipos TypeScript
│   │   └── utils/        # Utilidades
│   └── public/           # Archivos estáticos
├── docker-compose.yml    # Orquestación de servicios
├── .env.example          # Plantilla de variables
├── run.sh                # Script de inicio
└── README.md             # Este archivo
```

## Desarrollo

### Comandos útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar un servicio específico
docker-compose restart backend

# Acceder a la base de datos
docker exec -it merma-postgres psql -U postgres -d merma_db

# Ver estado de servicios
docker-compose ps
```

### Pruebas

```bash
# En el directorio backend
pytest tests/

# Coverage
pytest tests/ --cov=app --cov-report=html
```

## Despliegue en AWS

### Requisitos AWS

1. **RDS PostgreSQL 15**: Base de datos gestionada
2. **EC2**: Instancia para ejecutar contenedores
3. **S3**: Almacenamiento de datasets históricos
4. **ElastiCache (opcional)**: Redis gestionado

### Pasos de Despliegue

1. Crear instancia EC2 con Ubuntu 22.04 LTS
2. Configurar RDS PostgreSQL
3. Configurar bucket S3
4. Construir imágenes y push a ECR (opcional)
5. Configurar docker-compose con variables de producción
6. Configurar SSL/TLS con Nginx

### Configuración de Producción

```bash
# Variables de entorno requeridas
POSTGRES_HOST=<rds-endpoint>.cluster-xxx.us-east-1.rds.amazonaws.com
POSTGRES_USER=admin
POSTGRES_PASSWORD=<strong-password>
JWT_SECRET_KEY=<production-secret>
AWS_REGION=us-east-1
```

## Mantenimiento

### Backup de Base de Datos

```bash
docker exec -it merma-postgres pg_dump -U postgres merma_db > backup.sql
```

### Monitoreo

- Ver logs: `docker-compose logs -f backend`
- Estado de salud: `docker inspect merma-backend --format='{{.State.Health.Status}}'`
- Métricas: Acceder al endpoint `/health`

## Licencia

MIT License

## Contacto

Para soporte técnico: soporte@merma-optimization.com
