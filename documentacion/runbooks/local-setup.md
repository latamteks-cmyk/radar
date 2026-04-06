# Runbook: Configuración del Entorno Local

## Prerrequisitos

### Software Requerido

| Software | Versión | Propósito |
|----------|---------|-----------|
| Python | 3.10+ | Backend |
| PostgreSQL | 15+ | Base de datos operativa |
| MetaTrader 5 | Build 3000+ | Plataforma de trading |
| Node.js | 18+ (LTS) | Frontend (Next.js) |
| Git | Latest | Control de versiones |

### Software Opcional

| Software | Propósito |
|----------|-----------|
| Redis | Cache en memoria |
| Docker | Contenedores para desarrollo |
| DBeaver / pgAdmin | GUI para PostgreSQL |

## Pasos de Configuración

### 1. Verificar Prerrequisitos

```bash
# Verificar Python
python --version
# Debe mostrar Python 3.10 o superior

# Verificar PostgreSQL
psql --version
# Debe mostrar psql (PostgreSQL) 15 o superior

# Verificar MT5
# Abrir MetaTrader 5 y verificar Build number en Help → About

# Verificar Node.js
node --version
# Debe mostrar v18.x o superior

# Verificar Git
git --version
```

### 2. Clonar Repositorio

```bash
cd C:\Users\gomez\.gemini\antigravity\scratch
git clone <repository-url> radar2
cd radar2
```

### 3. Ejecutar Script de Setup

```bash
# Desde el directorio raíz del proyecto
scripts\setup.bat
```

Este script automáticamente:
- Crea el entorno virtual Python
- Instala todas las dependencias
- Crea archivo `.env` desde template
- Crea directorios necesarios

### 4. Configurar Variables de Entorno

Editar el archivo `.env`:

```bash
# Copiar template si no existe
copy .env.example .env

# Editar con tu editor preferido
notepad .env
```

**Valores mínimos requeridos**:

```env
# Database
DB_PASSWORD=tu_password_de_postgres

# MT5 (si vas a usar MT5)
MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
MT5_LOGIN=tu_login
MT5_PASSWORD=tu_password
MT5_SERVER=tu_servidor

# LLM (si vas usar LLM)
LLM_API_KEY=tu_api_key_de_openai

# Trading Mode (iniciar en paper)
TRADING_MODE=paper
```

### 5. Configurar PostgreSQL

#### 5.1 Crear Usuario y Base de Datos

```bash
# Conectarse a PostgreSQL como usuario postgres
psql -U postgres

# Dentro de psql:
CREATE USER radar_user WITH PASSWORD 'tu_password';
CREATE DATABASE radar_trading OWNER radar_user;
GRANT ALL PRIVILEGES ON DATABASE radar_trading TO radar_user;
\q
```

#### 5.2 Ejecutar Migraciones

```bash
# Activar entorno virtual
venv\Scripts\activate

# Ejecutar migraciones de Alembic
alembic upgrade head
```

### 6. Verificar Backend

```bash
# Iniciar servidor backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# En otro terminal, verificar health check
curl http://localhost:8000/health
```

Respuesta esperada:
```json
{
  "status": "ok",
  "environment": "development",
  "trading_mode": "paper"
}
```

### 7. Configurar Frontend

```bash
# Navegar a directorio de frontend
cd src\presentation\web

# Instalar dependencias de Node
npm install

# Iniciar servidor de desarrollo
npm run dev
```

Abrir navegador en `http://localhost:3000`

### 8. Ejecutar Tests

```bash
# Volver al directorio raíz
cd ..\..\..

# Ejecutar tests
scripts\run_tests.bat
```

Todos los tests deben pasar (o al menos los unitarios básicos).

## Verificación Completa

### Checklist

- [ ] Python 3.10+ instalado y en PATH
- [ ] PostgreSQL 15+ instalado y corriendo
- [ ] MetaTrader 5 instalado y configurado
- [ ] Repositorio clonado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas (`pip list` muestra paquetes)
- [ ] Archivo `.env` configurado
- [ ] Base de datos `radar_trading` creada
- [ ] Migraciones ejecutadas (`alembic current` muestra versión)
- [ ] Backend iniciando sin errores (`uvicorn src.main:app --reload`)
- [ ] Health check responde (`curl http://localhost:8000/health`)
- [ ] Frontend instalado y corriendo (`npm run dev`)
- [ ] Tests pasando (`pytest`)

## Troubleshooting

### Error: PostgreSQL no conecta

**Síntoma**: `psycopg2.OperationalError: could not connect to server`

**Solución**:
```bash
# Verificar que PostgreSQL está corriendo
services.msc
# Buscar "postgresql-x64-15" y verificar que está "Running"

# Verificar conexión
psql -U radar_user -d radar_trading -h localhost
```

### Error: MT5 no encontrado

**Síntoma**: `ModuleNotFoundError: No module named 'MetaTrader5'`

**Solución**:
```bash
# Verificar que MT5 está instalado
dir "C:\Program Files\MetaTrader 5"

# Verificar que el paquete Python está instalado
pip show MetaTrader5

# Si no está instalado
pip install MetaTrader5
```

### Error: Migraciones fallan

**Síntoma**: `alembic.util.exc.CommandError: Target database is not up to date`

**Solución**:
```bash
# Verificar estado actual
alembic current

# Ver migraciones pendientes
alembic history

# Forzar migración a head
alembic upgrade head

# Si hay errores, hacer downgrade y retry
alembic downgrade base
alembic upgrade head
```

### Error: Puerto ya en uso

**Síntoma**: `OSError: [WinError 10048] Only one usage of each socket address`

**Solución**:
```bash
# Verificar qué proceso usa el puerto
netstat -ano | findstr :8000

# Matar proceso o cambiar puerto
uvicorn src.main:app --reload --port 8001
```

## Operaciones Comunes

### Iniciar Backend

```bash
venv\Scripts\activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Iniciar Frontend

```bash
cd src\presentation\web
npm run dev
```

### Ejecutar Tests

```bash
venv\Scripts\activate
scripts\run_tests.bat
# O directamente
pytest tests/unit/ -v
```

### Ejecutar Migraciones

```bash
venv\Scripts\activate
alembic upgrade head
```

### Crear Nueva Migración

```bash
alembic revision --autogenerate -m "descripcion_del_cambio"
alembic upgrade head
```

### Ver Logs

```bash
# Logs de aplicación
type logs\application.log

# Logs de auditoría
type logs\audit.log

# En tiempo real (PowerShell)
Get-Content logs\application.log -Wait -Tail 50
```

## Backup y Restore

### Backup de Base de Datos

```bash
# Crear backup
pg_dump -U postgres radar_trading > backups\radar_trading_$(date +%Y%m%d).sql

# Backup comprimido
pg_dump -U postgres -Fc radar_trading > backups\radar_trading_$(date +%Y%m%d).dump
```

### Restore de Base de Datos

```bash
# Desde archivo SQL
psql -U radar_user -d radar_trading < backups\radar_trading_20260405.sql

# Desde dump comprimido
pg_restore -U radar_user -d radar_trading backups\radar_trading_20260405.dump
```

## Referencias

- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [Documentación de Alembic](https://alembic.sqlalchemy.org/)
- [Documentación de PostgreSQL](https://www.postgresql.org/docs/)
- [Documentación de MetaTrader 5](https://www.mql5.com/en/docs)
