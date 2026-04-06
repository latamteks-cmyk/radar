# Directrices del Proyecto: Radar Trading Intelligence Platform

## Principios Arquitectónicos

### 1. Clean Architecture + DDD Simplificado
- **Capas separadas**: domain, application, infrastructure, presentation
- **Dependencias hacia adentro**: capas externas dependen de capas internas
- **Entidades de dominio** en `src/domain/entities/`
- **Interfaces** en `src/domain/interfaces/`
- **Value Objects** en `src/domain/value_objects/`
- **Casos de uso** en `src/application/{modulo}/`

### 2. Modularidad por Dominios
- Cada bounded context es un módulo independiente
- Interfaces claras entre módulos
- Sin acoplamiento directo innecesario
- Eventos internos para comunicación entre dominios

### 3. Persistencia Operativa
- PostgreSQL como fuente de verdad operativa
- Market Cache para lecturas rápidas
- Evitar consultas repetidas a MT5
- Trazabilidad completa con `correlation_id`

### 4. Cálculo Incremental
- Indicadores se actualizan con vela cerrada
- Mínima ventana de recálculo
- Versionado de fórmulas y modelos
- Snapshots persistidos para replay

### 5. Fail-Safe por Diseño
- Prioridad: preservación de capital
- Modo degradado cuando sea posible
- Circuit breakers y rate limits
- Broker Truth ante discrepancias

## Estructura de Directorios

### Carpetas Obligatorias
- `informes/` - Todos los informes del proyecto (requisitos, análisis, reportes)
- `documentacion/` - Solo documentación oficial del proyecto

### Convenciones de Nomenclatura
- **Python**: snake_case para módulos/funciones, PascalCase para clases
- **Tests**: prefijo `test_` para archivos y funciones de prueba
- **Migraciones**: formato `YYYYMMDD_HHMMSS_description.py`
- **Configuración**: YAML para config, JSON para datos

## Ejecución por Fases

### Cada Fase Debe Incluir:
1. ✅ Checklist técnico completado
2. ✅ Pruebas unitarias y de integración
3. ✅ Documentación técnica actualizada
4. ✅ Criterio de salida validado

### Orden de Implementación:
1. **Fase 0**: Fundaciones y arquitectura base
2. **Fase 1**: Bootstrap del sistema
3. **Fase 2**: Configuration / Control Plane
4. **Fase 3**: MT5 Adapter y Asset Catalog
5. **Fase 4**: Operational DB y Market Cache
6. **Fase 5**: Scheduler / Pre-Session Engine
7. **Fase 6**: Pivot Engine
8. **Fase 7**: Indicator Engine
9. **Fase 8**: Event Intelligence
10. **Fase 9**: Radar Engine
11. **Fase 10**: Trigger Library
12. **Fase 11**: Signal Intelligence
13. **Fase 12**: ML y LLM Integration
14. **Fase 13**: Risk & Policy
15. **Fase 14**: Execution y Monitoring
16. **Fase 15**: Audit, Metrics y Deploy

##质量标准

### Código:
- Type hints obligatorios (`mypy`)
- Docstrings en funciones públicas
- Tests para lógica de negocio crítica
- Revisión de código antes de merge

### Documentación:
- ADRs para decisiones arquitectónicas
- API contracts versionados
- Runbooks para operaciones
- Data model actualizado

### Operación:
- Logs estructurados con `correlation_id`
- Métricas por módulo
- Health checks periódicos
- Backup/rollback procedures

## Gestión de Configuración

### Versionado:
- **SemVer** para releases
- **Config version** para cambios de configuración
- **Model version** para ML/indicadores
- **Trigger version** para cambios en triggers

### Entornos:
- `local` - Desarrollo local
- `test` - Pruebas funcionales
- `staging` - Pre-producción
- `production` - Operación real

## Seguridad

- Secretos en variables de entorno o vault
- RBAC para UI y APIs
- Rate limiting en endpoints críticos
- Audit trail de todas las operaciones
- Validación de esquemas en frontera
