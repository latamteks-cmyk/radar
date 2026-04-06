# Arquitectura de Software - Radar Trading Intelligence Platform

## Visión General

Este documento describe la arquitectura completa del sistema Radar Trading Intelligence Platform.

## Principios Arquitectónicos

### 1. Clean Architecture

El sistema implementa Clean Architecture con cuatro capas claramente diferenciadas:

```
┌─────────────────────────────────────────────────────────────┐
│                 PRESENTATION LAYER                          │
│  - API REST (FastAPI)                                       │
│  - UI Web (React/Next.js)                                   │
│  - BFF (Backend for Frontend)                               │
├─────────────────────────────────────────────────────────────┤
│                 APPLICATION LAYER                           │
│  - Casos de uso por dominio                                 │
│  - Servicios de aplicación                                    │
│  - DTOs (Data Transfer Objects)                             │
│  - Orquestación de flujos                                   │
├─────────────────────────────────────────────────────────────┤
│                 DOMAIN LAYER                                │
│  - Entidades de negocio                                     │
│  - Value Objects                                            │
│  - Interfaces de dominio                                    │
│  - Reglas de negocio puras                                  │
├─────────────────────────────────────────────────────────────┤
│                 INFRASTRUCTURE LAYER                        │
│  - MT5 Adapter                                              │
│  - Repositorios (PostgreSQL)                                │
│  - Cache (Redis)                                            │
│  - Logging estructurado                                     │
│  - Configuración                                            │
└─────────────────────────────────────────────────────────────┘
```

### 2. Dependencia de Capas

**Regla de Oro**: Las dependencias apuntan SIEMPRE hacia adentro.

- Presentation → Application → Domain
- Infrastructure → Domain
- Domain NO depende de ninguna otra capa

### 3. Bounded Contexts (DDD Simplificado)

El sistema se divide en los siguientes dominios:

1. **Configuration / Control Plane**
   - Gestión de configuración maestra
   - Versionado y publicación de configs
   - Perfiles por tipo de activo

2. **Scheduler / Pre-Session Engine**
   - Preparación de jornada
   - Jobs pre-session (T-60, T-30, T-15)
   - TradingDayConfig

3. **Asset Catalog**
   - Descubrimiento de activos desde MT5
   - Clasificación automática
   - Asignación de perfiles

4. **Market Data / Operational DB**
   - Ingesta de barras OHLC
   - Persistencia operativa
   - Cache en memoria

5. **Pivot Engine**
   - Cálculo de pivotes diarios
   - Bandas de evaluación
   - Congelamiento de pivotes

6. **Indicator Engine**
   - Cálculo incremental de indicadores
   - Sesgo H4
   - Indicadores M15/M5
   - Patrones multi-vela

7. **Event Intelligence**
   - Calendario económico de MT5
   - Mapeo evento → activo
   - Ventanas pre/post evento

8. **Radar Engine**
   - Máquina de estados por símbolo
   - Snapshots operativos
   - Evaluación de contexto

9. **Trigger Library**
   - Librería OO de trigger_type
   - Strategy + Factory + Registry
   - Cooldown y deduplicación

10. **Signal Intelligence**
    - Construcción de SignalCandidate
    - Fusión de triggers + ML + LLM
    - Selección de prompts

11. **Prompt Template Service**
    - Plantillas por tipo de activo
    - Overrides por símbolo
    - Versionado de prompts

12. **Machine Learning Service**
    - Scoring de régimen
    - Detección de anomalías
    - Modo degradado

13. **LLM Orchestrator**
    - Consulta controlada a LLM
    - Validación de esquemas
    - Fallback seguro

14. **Risk & Portfolio Engine**
    - Validación de riesgo por trade
    - Límites diarios
    - Exposición correlacionada

15. **Policy Gate**
    - Reglas duras pre-ejecución
    - Mercado abierto
    - Spread threshold
    - Cooldown verificado

16. **Execution Engine**
    - Modo paper y live
    - Órdenes idempotentes
    - Trazabilidad completa

17. **Order Monitoring**
    - Tracking de órdenes
    - Tracking de posiciones
    - Reconciliación con broker

18. **Audit / Metrics / Replay**
    - Logging estructurado
    - Métricas por módulo
    - Replay de jornada

## Pipeline de Datos

```
MT5 Market Data
      ↓
MT5 Adapter (bars, events, sessions)
      ↓
Operational DB + Market Cache
      ↓
┌───────────────────────────────────┐
│ Pivot Engine                      │
│ Indicator Engine                  │
│ Event Intelligence                │
└───────────────────────────────────┘
      ↓
Radar Engine (estado por símbolo)
      ↓
Trigger Library (activaciones)
      ↓
Signal Intelligence
      ├──→ ML Service (scoring)
      └──→ LLM Orchestrator (análisis)
            ↓
Risk & Portfolio Engine
      ↓
Policy Gate
      ↓
Execution Engine (paper/live)
      ↓
Order Monitoring
      ↓
Audit / Metrics / Replay
```

## Patrones de Diseño Utilizados

### 1. Strategy Pattern
- **Uso**: Trigger Library, Risk Policies, Execution Modes
- **Beneficio**: Permite cambiar comportamiento en runtime

### 2. Factory Pattern
- **Uso**: TriggerFactory, OrderBuilder
- **Beneficio**: Creación de objetos sin acoplamiento

### 3. Repository Pattern
- **Uso**: Todos los repositorios de persistencia
- **Beneficio**: Abstracción de capa de datos

### 4. Observer Pattern
- **Uso**: Event Bus interno, Radar snapshots
- **Beneficio**: Desacoplamiento entre módulos

### 5. State Machine
- **Uso**: Radar Engine por símbolo
- **Beneficio**: Control explícito de transiciones

## Correlation ID

Todo el flujo de operaciones se rastrea con `correlation_id`:

```
[MT5 Bar] → correlation_id = UUID4()
    ↓
[Pivot Engine] → propaga correlation_id
    ↓
[Radar Engine] → radar_snapshots (con correlation_id)
    ↓
[Trigger Library] → trigger_activations (con correlation_id)
    ↓
[Signal Intelligence] → ml_results, llm_results (con correlation_id)
    ↓
[Risk Engine] → risk_decisions (con correlation_id)
    ↓
[Execution Engine] → orders (con correlation_id)
    ↓
[Audit] → audit_records (searchable by correlation_id)
```

## Modos de Operación

### Monitor Only
- Radar activo
- Snapshots persistidos
- Triggers activados
- Alertas generadas
- **NO** se ejecutan órdenes

### Paper Trading
- Pipeline completo hasta Execution
- Órdenes simuladas
- Trazabilidad completa
- **NO** se envían a MT5

### Live Trading
- Pipeline completo activo
- Órdenes reales a MT5
- Límites y políticas activas
- Trazabilidad y auditoría completas

## Estados del Sistema

### Estados Globales

| Estado | Descripción |
|--------|-------------|
| `STARTING` | Secuencia de inicio |
| `READY` | Sistema operativo |
| `MONITOR_ONLY` | Solo radar y alertas |
| `PAPER_ONLY` | Ejecución simulada |
| `LIVE_ENABLED` | Ejecución real habilitada |
| `DEGRADED` | Componente no crítico con fallos |
| `INTRADAY_FREEZE` | Solo gestión de posiciones |
| `CIRCUIT_ACTIVE` | Riesgo bloquea operaciones |
| `EMERGENCY_STOP` | Kill-switch activo |
| `STOPPED_GRACEFUL` | Apagado limpio |
| `FORCED_STOP` | Apagado forzado |

### Estados del Radar por Símbolo

| Estado | Descripción |
|--------|-------------|
| `IDLE` | Sin contexto relevante |
| `WATCHLIST` | Monitoreo activo |
| `IN_ZONE` | En banda de evaluación |
| `TRIGGERED` | Triggers activados |
| `UNDER_ANALYSIS` | En evaluación ML/LLM |
| `APPROVED` | Candidato aprobado |
| `BLOCKED` | Bloqueado por riesgo/política |
| `COOLDOWN` | En espera post-activación |

## Seguridad

### 1. Secretos
- Variables de entorno para credenciales
- **NUNCA** commitear `.env` al repositorio
- Usar vault en producción

### 2. RBAC
- Roles: Admin, Operator, Viewer
- Permisos granulares por módulo
- Autenticación JWT

### 3. Rate Limiting
- Límites en endpoints críticos
- Protección contra abuso
- Control de costos LLM

### 4. Audit Trail
- Toda operación queda registrada
- Trazabilidad end-to-end
- Replay de jornadas

## Escalabilidad Futura

### Fase 1: Monolito Modular (Actual)
- Todos los módulos en un proceso
- Fácil desarrollo y testing
- Compartir memoria entre módulos

### Fase 2: Servicios Separados
- Ejecutar módulos críticos en procesos separados
- Comunicación vía message queue
- Escalado independiente

### Fase 3: Microservicios
- Docker containers por dominio
- Kubernetes para orquestación
- Event sourcing para auditoría

## Decisiones Arquitectónicas Clave

Ver [documentacion/adr/](../documentacion/adr/) para ADRs detallados.

### ADR-001: Clean Architecture
- **Decisión**: Usar Clean Architecture + DDD simplificado
- **Razón**: Separación de responsabilidades, testabilidad, mantenibilidad

### ADR-002: MT5 Adapter Boundary
- **Decisión**: MT5 solo como adaptador de datos/ejecución
- **Razón**: Lógica de negocio en backend, no en MQL5

### ADR-003: Operational DB
- **Decisión**: PostgreSQL como fuente de verdad operativa
- **Razón**: Evitar consultas repetidas a MT5, habilitar replay

### ADR-004: Incremental Calculation
- **Decisión**: Cálculo solo con vela cerrada y ventana mínima
- **Razón**: Rendimiento, evitar recálculos innecesarios

## Referencias

- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design - Eric Evans](https://www.domainlanguage.com/ddd/)
- [CQRS Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/cqrs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
