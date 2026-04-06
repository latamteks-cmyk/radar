# Radar Trading Intelligence Platform

Sistema modular de análisis, priorización, control de riesgo y ejecución asistida/automatizada para activos operados desde MetaTrader 5 (MT5).

## 📋 Descripción

Radar es una plataforma integral que:

- **Monitorea** continuamente un universo configurable de activos
- **Calcula** pivotes e indicadores técnicos con base en datos del broker
- **Incorpora** el calendario económico nativo de MT5
- **Detecta** candidatos operativos mediante una librería de `trigger_type`
- **Enriquece** el contexto con Machine Learning y consultas API LLM
- **Aplica** control de riesgo antes de permitir una operación
- **Ejecuta** órdenes con trazabilidad completa (modo paper o live)

## 🏗️ Arquitectura

El sistema sigue una **arquitectura modular por dominios** basada en:

- **Clean Architecture**: Separación estricta entre dominio, aplicación, infraestructura y presentación
- **DDD Simplificado**: Entidades, value objects y bounded contexts claros
- **CQRS**: Modelos separados para lectura y escritura
- **Eventos Internos**: Desacoplamiento entre módulos

### Pipeline Principal

```
Configuración → Preparación de Jornada → Datos de Mercado → Pivotes/Indicadores/Eventos 
→ Radar → Trigger Library → Signal Intelligence (ML + LLM) → Riesgo → Policy Gate 
→ Ejecución → Seguimiento → Auditoría
```

## 📁 Estructura del Proyecto

```
radar2/
├── src/                          # Código fuente
│   ├── domain/                   # Capa de dominio (reglas de negocio puras)
│   ├── application/              # Capa de aplicación (casos de uso)
│   ├── infrastructure/           # Capa de infraestructura (MT5, DB, cache)
│   └── presentation/             # Capa de presentación (API, UI web)
├── tests/                        # Pruebas
│   ├── unit/                     # Pruebas unitarias
│   ├── integration/              # Pruebas de integración
│   └── functional/               # Pruebas funcionales
├── db/                           # Base de datos y migraciones
├── config/                       # Configuración (settings, perfiles, triggers)
├── documentacion/                # Documentación OFICIAL del proyecto
│   ├── architecture/             # Documentos de arquitectura
│   ├── data-model/               # Modelos de datos
│   ├── api/                      # Contratos de API
│   ├── runbooks/                 # Guías operativas
│   └── adr/                      # Architecture Decision Records
├── informes/                     # Informes del proyecto
│   ├── requisitos/               # Documentos de requisitos
│   ├── analisis/                 # Análisis y estudios
│   ├── reportes/                 # Reportes de progreso
│   └── investigacion/            # Investigación y POCs
└── scripts/                      # Scripts de utilidad
```

Para la estructura completa, ver [DIRECTORY_STRUCTURE.md](DIRECTORY_STRUCTURE.md).

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.10+
- PostgreSQL 15+
- MetaTrader 5 Terminal Build 3000+
- (Opcional) Redis para cache

### Instalación

1. **Clonar el repositorio**

```bash
git clone <repository-url>
cd radar2
```

2. **Crear entorno virtual**

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Instalar dependencias**

```bash
pip install -e ".[dev]"
```

4. **Configurar variables de entorno**

```bash
copy .env.example .env
# Editar .env con tus configuraciones
```

5. **Configurar base de datos**

```bash
# Crear base de datos PostgreSQL
createdb radar_trading

# Ejecutar migraciones
alembic upgrade head
```

6. **Ejecutar aplicación**

```bash
# Backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (en otro terminal)
cd src/presentation/web
npm install
npm run dev
```

## 📖 Documentación

- [Directrices del Proyecto](PROJECT_GUIDELINES.md)
- [Estructura de Directorios](DIRECTORY_STRUCTURE.md)
- [Documentación Oficial](documentacion/)
- [Informes](informes/)

## 🧪 Ejecutar Pruebas

```bash
# Todas las pruebas
pytest

# Pruebas unitarias
pytest tests/unit/

# Pruebas de integración
pytest tests/integration/

# Pruebas funcionales
pytest tests/functional/

# Con coverage
pytest --cov=src --cov-report=html
```

## 🎯 Modos de Operación

El sistema puede operar en tres modos:

1. **Monitor Only**: Solo radar, snapshots, triggers y alertas
2. **Paper Trading**: Decisiones completas con ejecución simulada
3. **Live Trading Controlado**: Ejecución real con límites, políticas y trazabilidad completa

## ⚙️ Configuración

La configuración se gestiona en:

- `config/settings/` - Configuración por entorno
- `config/profiles/` - Perfiles por tipo de activo
- `config/triggers/` - Configuración de triggers
- `config/prompts/` - Plantillas de prompts
- `config/risk/` - Políticas de riesgo

## 📊 Fases de Implementación

El proyecto se implementa de forma incremental:

- ✅ **Fase 0**: Fundaciones y arquitectura base
- ⏳ **Fase 1**: Bootstrap del sistema
- ⏳ **Fase 2**: Configuration / Control Plane
- ⏳ **Fase 3**: MT5 Adapter y Asset Catalog
- ⏳ **Fase 4**: Operational DB y Market Cache
- ⏳ **Fase 5-15**: Módulos restantes

Ver [Radar_Trading_Task_Plan.md](Radar_Trading_Task_Plan.md) para el plan completo.

## 🔒 Seguridad

- Secretos en variables de entorno o vault
- RBAC para UI y APIs
- Rate limiting en endpoints críticos
- Audit trail de todas las operaciones
- Validación de esquemas en frontera

## 📝 Licencia

MIT License - Ver [LICENSE](LICENSE) para detalles.

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📧 Contacto

Tu Nombre - your.email@example.com

Project Link: [https://github.com/yourusername/radar-trading-platform](https://github.com/yourusername/radar-trading-platform)

## ⚠️ Disclaimer

Este software es para uso educativo y de investigación. El trading de instrumentos financieros conlleva riesgos significativos. Los desarrolladores no son responsables de pérdidas financieras resultantes del uso de este software.

**Usar bajo propia responsabilidad.**
