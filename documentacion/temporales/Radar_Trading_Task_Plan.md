# Plan de Implementación: Radar Trading Architecture

## Overview

Implementación incremental del sistema de radar de señales para trading sobre MT5, siguiendo Clean Architecture, orientación a objetos, persistencia operativa y cálculo incremental por vela cerrada. El pipeline objetivo es:

`Configuration / Control Plane → Scheduler / Pre-Session → MT5 Adapter → Market Cache / Operational DB → Radar Engine → Trigger Library → Signal Intelligence (ML / LLM) → Risk & Portfolio → Policy Gate → Execution → Order Monitoring → Audit / Metrics / Replay`

Cada fase termina con:
- checklist técnico completado;
- pruebas funcionales ejecutadas;
- actualización de documentación técnica;
- criterio de salida validado.

## Convenciones de trabajo

- [ ] Mantener arquitectura modular por dominios: `configuration`, `market_data`, `events`, `radar`, `triggers`, `signal_intelligence`, `risk`, `execution`, `order_monitoring`, `audit`.
- [ ] Aplicar Clean Architecture en cada módulo: `domain`, `application`, `infrastructure`, `presentation`.
- [ ] Usar programación orientada a objetos con composición, `Strategy`, `Factory`, `Repository` y `DTOs` cuando aplique.
- [ ] Todo cambio funcional debe incluir pruebas unitarias o de integración según el nivel afectado.
- [ ] Todo cambio en contratos, entidades, endpoints, eventos o reglas debe actualizar documentación técnica.
- [ ] Todo flujo crítico debe propagar `correlation_id` y `config_version`.
- [ ] No acoplar lógica de negocio compleja dentro de MT5; MT5 actúa como adaptador de datos/ejecución.
- [ ] Los indicadores deben recalcularse solo con la última vela cerrada y la mínima ventana necesaria.
- [ ] Toda decisión operativa debe ser auditable de extremo a extremo.

## Estructura sugerida del repositorio

```text
/src
  /domain
  /application
  /infrastructure
  /presentation
/docs
  /architecture
  /adr
  /api
  /data-model
  /runbooks
/tests
  /unit
  /integration
  /functional
/db
  /migrations
```

## Definition of Done global

- [ ] Código implementado y revisado.
- [ ] Tests de la fase en verde.
- [ ] Logs y manejo de errores incorporados.
- [ ] Métricas mínimas expuestas si aplica.
- [ ] Documentación técnica actualizada.
- [ ] Checklist de la fase marcado.
- [ ] Criterio de salida validado por el equipo.

---

## Fase 0. Fundaciones, alcance y arquitectura base

### Objetivo
Aterrizar alcance, dominios, contratos iniciales y normas de construcción.

### Tasks
- [ ] Definir alcance funcional de la versión 1.
- [ ] Confirmar tipos de activos soportados en la primera entrega.
- [ ] Confirmar timeframes iniciales: `H4`, `M15`, `M5`.
- [ ] Confirmar modalidad inicial: `alert-only`, `paper`, `live-disabled`.
- [ ] Definir bounded contexts y responsabilidades.
- [ ] Definir nomenclatura para símbolos, triggers, perfiles, eventos y versiones.
- [ ] Crear diagrama de arquitectura lógica.
- [ ] Crear diagrama del pipeline runtime.
- [ ] Definir contratos de alto nivel entre capas.
- [ ] Definir estrategia de despliegue local y preparación para VM.
- [ ] Definir política de versionado de configuración, prompts, reglas y modelos.
- [ ] Crear ADRs iniciales para decisiones arquitectónicas críticas.

### Pruebas funcionales
- [ ] Validar que el documento de arquitectura refleja todos los dominios y dependencias.
- [ ] Validar que cada componente tiene una responsabilidad única.
- [ ] Validar que el flujo extremo a extremo está definido sin ambigüedades.

### Documentación técnica
- [ ] Actualizar `docs/architecture/software-architecture.md`.
- [ ] Crear `docs/adr/ADR-001-architecture-style.md`.
- [ ] Crear `docs/adr/ADR-002-mt5-adapter-boundary.md`.
- [ ] Crear `docs/adr/ADR-003-operational-db.md`.

### Criterio de salida
- [ ] Arquitectura base aprobada.
- [ ] Alcance cerrado para v1.
- [ ] ADRs iniciales aprobados.

---

## Fase 1. Bootstrap del backend, frontend y observabilidad mínima

### Objetivo
Levantar el esqueleto técnico del sistema.

### Tasks
- [ ] Crear repositorio y estructura modular del proyecto.
- [ ] Configurar entorno local, variables y perfiles por ambiente.
- [ ] Implementar servicio base backend y health check.
- [ ] Implementar BFF o API base para la UI.
- [ ] Crear shell de la UI con navegación por módulos.
- [ ] Configurar logging estructurado con `correlation_id`.
- [ ] Configurar manejo de errores global.
- [ ] Configurar linting, formatting y tipado estático.
- [ ] Configurar pipelines de build y test.
- [ ] Añadir monitoreo básico de salud del sistema.

### Pruebas funcionales
- [ ] Verificar que backend y UI levantan localmente.
- [ ] Verificar endpoint `/health`.
- [ ] Verificar que logs incluyen `correlation_id`.
- [ ] Verificar navegación básica entre módulos de la UI.

### Documentación técnica
- [ ] Actualizar `docs/runbooks/local-setup.md`.
- [ ] Crear `docs/architecture/module-map.md`.
- [ ] Crear `docs/api/base-endpoints.md`.

### Criterio de salida
- [ ] Plataforma base ejecutable localmente.
- [ ] Observabilidad mínima disponible.

---

## Fase 2. Configuration / Control Plane

### Objetivo
Construir la fuente única de verdad de la configuración.

### Tasks
- [ ] Diseñar entidades: `SystemConfig`, `AssetProfile`, `TriggerProfile`, `PromptProfile`, `RiskProfile`, `SessionProfile`.
- [ ] Crear migraciones de tablas de configuración.
- [ ] Implementar lectura/escritura de configuración.
- [ ] Implementar versionado y publicación de configuración.
- [ ] Implementar modo `draft` y `published`.
- [ ] Implementar rollback de configuración.
- [ ] Implementar validación semántica de perfiles.
- [ ] Crear UI de configuración general.
- [ ] Crear UI de perfiles por tipo de activo.
- [ ] Crear UI de overrides por símbolo.
- [ ] Registrar auditoría de cambios.

### Pruebas funcionales
- [ ] Crear configuración base y publicarla.
- [ ] Editar configuración y validar nueva versión.
- [ ] Ejecutar rollback y verificar consistencia.
- [ ] Verificar que un cambio inválido es rechazado.
- [ ] Verificar trazabilidad de autor, fecha y razón del cambio.

### Documentación técnica
- [ ] Actualizar `docs/data-model/configuration-model.md`.
- [ ] Crear `docs/api/configuration-api.md`.
- [ ] Crear `docs/runbooks/config-publication.md`.

### Criterio de salida
- [ ] Existe una configuración activa única y versionada.
- [ ] Toda configuración es auditable.

---

## Fase 3. MT5 Adapter y Asset Catalog

### Objetivo
Sincronizar activos desde MT5 y construir el catálogo administrable.

### Tasks
- [ ] Implementar `MT5 Adapter` para símbolos, barras, sesiones, eventos y ejecución.
- [ ] Implementar sincronización de activos disponibles desde MT5.
- [ ] Diseñar entidad `Asset` y sus perfiles asociados.
- [ ] Crear clasificación automática por tipo de activo.
- [ ] Crear corrección manual por UI.
- [ ] Implementar activación/desactivación de activos para radar.
- [ ] Asociar perfiles de riesgo, prompts, triggers y sesiones por símbolo.
- [ ] Registrar estado de sincronización con MT5.
- [ ] Implementar refresh manual y automático del catálogo.

### Pruebas funcionales
- [ ] Verificar que los símbolos de MT5 se sincronizan correctamente.
- [ ] Verificar clasificación automática y corrección manual.
- [ ] Verificar activación/desactivación desde UI.
- [ ] Verificar asociación de perfiles por símbolo.
- [ ] Verificar que activos desactivados no son elegibles para el radar.

### Documentación técnica
- [ ] Actualizar `docs/architecture/integration-mt5.md`.
- [ ] Crear `docs/data-model/asset-catalog.md`.
- [ ] Crear `docs/api/assets-api.md`.

### Criterio de salida
- [ ] Catálogo de activos sincronizado y administrable.
- [ ] MT5 Adapter estable para lectura de símbolos.

---

## Fase 4. Operational DB, Market Cache y snapshots de mercado

### Objetivo
Persistir datos operativos para evitar consultas repetidas a MT5.

### Tasks
- [ ] Diseñar tablas: `bars`, `market_snapshots`, `runtime_symbol_state`.
- [ ] Implementar ingesta de barras desde MT5.
- [ ] Detectar nuevas velas cerradas por timeframe.
- [ ] Persistir OHLC de `H4`, `M15`, `M5`.
- [ ] Persistir `bid`, `ask`, `spread` cuando aplique.
- [ ] Implementar cache en memoria del último snapshot por símbolo.
- [ ] Implementar políticas de retención y limpieza.
- [ ] Añadir validaciones de integridad OHLC.
- [ ] Crear consultas optimizadas para último estado por símbolo.

### Pruebas funcionales
- [ ] Verificar ingesta histórica inicial.
- [ ] Verificar ingesta incremental con nueva vela cerrada.
- [ ] Verificar que el radar puede leer desde DB/cache sin consultar MT5 directamente.
- [ ] Verificar integridad de OHLC y orden temporal.
- [ ] Verificar idempotencia ante velas duplicadas.

### Documentación técnica
- [ ] Actualizar `docs/data-model/market-data-model.md`.
- [ ] Crear `docs/runbooks/market-data-recovery.md`.
- [ ] Crear `docs/architecture/operational-storage.md`.

### Criterio de salida
- [ ] La base operativa es la fuente de lectura del sistema.
- [ ] Existe cache del último estado por símbolo.

---

## Fase 5. Scheduler / Pre-Session Engine

### Objetivo
Preparar automáticamente la jornada y la configuración operativa diaria.

### Tasks
- [ ] Implementar scheduler interno.
- [ ] Configurar jobs `T-60`, `T-30`, `T-15`, `session_open`.
- [ ] Implementar `TradingDayConfig`.
- [ ] Resolver lista de activos activos del día.
- [ ] Disparar preparación de pivotes.
- [ ] Disparar actualización de eventos.
- [ ] Disparar consolidación de contexto H4.
- [ ] Registrar ejecución y resultado de jobs.
- [ ] Implementar reintentos e idempotencia.
- [ ] Crear UI de estado del scheduler.

### Pruebas funcionales
- [ ] Verificar ejecución automática de jobs pre-session.
- [ ] Verificar idempotencia por símbolo y jornada.
- [ ] Verificar generación correcta de `TradingDayConfig`.
- [ ] Verificar estado `PREPARED`, `PARTIAL`, `FAILED`.

### Documentación técnica
- [ ] Actualizar `docs/architecture/scheduler-pre-session.md`.
- [ ] Crear `docs/runbooks/daily-preparation.md`.

### Criterio de salida
- [ ] La jornada puede prepararse automáticamente.
- [ ] Existe trazabilidad del proceso previo a apertura.

---

## Fase 6. Pivot Engine

### Objetivo
Calcular pivotes confiables con OHLC cerrados del broker.

### Tasks
- [ ] Diseñar entidad `PivotSet`.
- [ ] Crear tabla `pivot_sets`.
- [ ] Implementar pivotes `Classic`.
- [ ] Implementar fuente `broker day` y `session-based` si se habilita.
- [ ] Congelar pivotes hasta el siguiente rollover.
- [ ] Implementar bandas configurables alrededor de niveles.
- [ ] Persistir metadatos del cálculo: H, L, C, timestamp, versión.
- [ ] Crear UI de consulta de pivotes por símbolo.
- [ ] Crear UI de configuración de bandas y tipo de cálculo.

### Pruebas funcionales
- [ ] Verificar cálculo correcto de `PP`, `R1`, `S1`, `R2`, `S2`.
- [ ] Verificar que el cálculo usa solo período cerrado.
- [ ] Verificar congelamiento durante la jornada.
- [ ] Verificar actualización en el siguiente rollover.
- [ ] Verificar visualización correcta en UI.

### Documentación técnica
- [ ] Actualizar `docs/architecture/pivot-engine.md`.
- [ ] Crear `docs/data-model/pivot-model.md`.
- [ ] Crear `docs/runbooks/pivot-recalculation.md`.

### Criterio de salida
- [ ] Cada símbolo activo tiene un `PivotSet` vigente y auditado.

---

## Fase 7. Indicator Engine incremental

### Objetivo
Calcular indicadores con actualización por última vela cerrada.

### Tasks
- [ ] Diseñar entidad `IndicatorSnapshot`.
- [ ] Crear tabla `indicator_snapshots`.
- [ ] Definir catálogo inicial de indicadores v1.
- [ ] Implementar sesgo H4.
- [ ] Implementar indicadores de ejecución para M15.
- [ ] Implementar indicadores de ejecución para M5.
- [ ] Implementar actualización incremental por nueva vela.
- [ ] Implementar recálculo parcial para patrones multi-vela.
- [ ] Versionar fórmulas de indicadores.
- [ ] Crear UI técnica de indicadores por símbolo/timeframe.

### Pruebas funcionales
- [ ] Verificar que no se recalcula todo el histórico al llegar una nueva vela.
- [ ] Verificar consistencia entre snapshot previo y nuevo snapshot.
- [ ] Verificar cálculo correcto de indicadores seleccionados.
- [ ] Verificar que patrones multi-vela recalculan solo la ventana mínima.
- [ ] Verificar visibilidad del snapshot técnico en UI.

### Documentación técnica
- [ ] Actualizar `docs/architecture/indicator-engine.md`.
- [ ] Crear `docs/data-model/indicator-model.md`.
- [ ] Crear `docs/runbooks/indicator-rebuild.md`.

### Criterio de salida
- [ ] Indicadores disponibles de forma incremental y persistida.

---

## Fase 8. Event Intelligence

### Objetivo
Incorporar calendario económico de MT5 y su impacto por activo.

### Tasks
- [ ] Diseñar entidad `EconomicEventSnapshot`.
- [ ] Crear tabla `economic_events`.
- [ ] Implementar carga de eventos del día desde MT5.
- [ ] Persistir importancia, país/divisa, actual, forecast y previo.
- [ ] Implementar mapeo automático evento → activo.
- [ ] Implementar ventanas pre/post evento.
- [ ] Implementar estados `NORMAL`, `CAUTION`, `BLOCK_PRE_EVENT`, `BLOCK_POST_EVENT`.
- [ ] Crear overrides manuales por símbolo.
- [ ] Crear UI de eventos y filtros.
- [ ] Mostrar eventos asociados por activo.

### Pruebas funcionales
- [ ] Verificar carga de eventos del día.
- [ ] Verificar asociación correcta según clase de activo.
- [ ] Verificar creación de ventanas pre y post evento.
- [ ] Verificar modo operativo derivado por símbolo.
- [ ] Verificar overrides manuales desde UI.

### Documentación técnica
- [ ] Actualizar `docs/architecture/event-intelligence.md`.
- [ ] Crear `docs/data-model/economic-events-model.md`.
- [ ] Crear `docs/runbooks/event-windows.md`.

### Criterio de salida
- [ ] Cada activo puede tener contexto macro operativo vigente.

---

## Fase 9. Radar Engine

### Objetivo
Construir el motor de estado por símbolo y snapshots operativos.

### Tasks
- [ ] Diseñar entidad `RadarSnapshot`.
- [ ] Crear tabla `radar_snapshots`.
- [ ] Definir máquina de estados: `IDLE`, `WATCHLIST`, `IN_ZONE`, `TRIGGERED`, `UNDER_ANALYSIS`, `BLOCKED`.
- [ ] Implementar evaluación por nueva vela M5/M15.
- [ ] Implementar evaluación de cercanía a pivotes.
- [ ] Implementar evaluación de contexto H4.
- [ ] Implementar evaluación de patrones e indicadores.
- [ ] Implementar evaluación de proximidad a evento.
- [ ] Persistir condición operativa del día por símbolo y tipo de activo.
- [ ] Publicar `RadarSnapshotCreated`.
- [ ] Crear UI del radar por símbolo.

### Pruebas funcionales
- [ ] Verificar transición correcta de estados del radar.
- [ ] Verificar creación de snapshot por actualización relevante.
- [ ] Verificar registro de condición operativa del día por símbolo.
- [ ] Verificar que activos deshabilitados no entran al radar.
- [ ] Verificar visualización de estado en UI.

### Documentación técnica
- [ ] Actualizar `docs/architecture/radar-engine.md`.
- [ ] Crear `docs/data-model/radar-snapshot-model.md`.
- [ ] Crear `docs/runbooks/radar-state-machine.md`.

### Criterio de salida
- [ ] El radar observa, evalúa y registra sin ejecutar órdenes.

---

## Fase 10. Trigger Library

### Objetivo
Crear una librería OO y configurable de `trigger_type`.

### Tasks
- [ ] Diseñar `TriggerBase`, `TriggerContext`, `TriggerResult`.
- [ ] Diseñar `TriggerFactory` y `TriggerRegistry`.
- [ ] Crear tabla `trigger_activations`.
- [ ] Implementar triggers iniciales:
  - [ ] `pivot_approach`
  - [ ] `pivot_breakout`
  - [ ] `pivot_rejection`
  - [ ] `trend_alignment`
  - [ ] `event_proximity`
  - [ ] `technical_fundamental_confluence`
  - [ ] `volatility_regime_change`
  - [ ] `session_open_setup`
  - [ ] `news_risk_block`
  - [ ] `post_event_reentry`
- [ ] Implementar prioridad y supresión por conflicto.
- [ ] Implementar cooldown por símbolo/tipo de trigger.
- [ ] Implementar deduplicación.
- [ ] Persistir `reason_codes` y `pre_score`.
- [ ] Activar/desactivar triggers desde configuración.
- [ ] Crear UI de librería de triggers.

### Pruebas funcionales
- [ ] Verificar activación correcta por contexto.
- [ ] Verificar que el mismo trigger no se duplica en cooldown.
- [ ] Verificar supresión por conflicto entre triggers.
- [ ] Verificar persistencia de `reason_codes` y snapshot asociado.
- [ ] Verificar activación/desactivación desde UI.

### Documentación técnica
- [ ] Actualizar `docs/architecture/trigger-library.md`.
- [ ] Crear `docs/data-model/trigger-model.md`.
- [ ] Crear `docs/runbooks/trigger-tuning.md`.

### Criterio de salida
- [ ] La lógica de activación está encapsulada y es auditable.

---

## Fase 11. Signal Intelligence y Prompt Template Service

### Objetivo
Transformar triggers en payloads estructurados para ML/LLM.

### Tasks
- [ ] Diseñar `SignalCandidate`.
- [ ] Diseñar `PromptTemplate`.
- [ ] Crear tablas `prompt_templates`, `llm_requests`, `llm_results`.
- [ ] Implementar plantillas por tipo de activo.
- [ ] Implementar overrides por símbolo.
- [ ] Implementar variantes por trigger.
- [ ] Implementar render de payload JSON.
- [ ] Implementar validación de esquema de entrada.
- [ ] Implementar `render_hash` y deduplicación.
- [ ] Crear UI de plantillas de prompt.
- [ ] Crear UI de historial de consultas.

### Pruebas funcionales
- [ ] Verificar selección correcta de plantilla por activo y trigger.
- [ ] Verificar override por símbolo.
- [ ] Verificar render consistente del JSON.
- [ ] Verificar deduplicación por `render_hash`.
- [ ] Verificar historial visible en UI.

### Documentación técnica
- [ ] Actualizar `docs/architecture/signal-intelligence.md`.
- [ ] Crear `docs/data-model/prompt-template-model.md`.
- [ ] Crear `docs/api/prompt-template-api.md`.

### Criterio de salida
- [ ] Cada trigger puede generar un payload consistente y versionado.

---

## Fase 12. Machine Learning Service y LLM Orchestrator

### Objetivo
Añadir scoring cuantitativo y evaluación contextual controlada.

### Tasks
- [ ] Diseñar `MLScoreResult`.
- [ ] Diseñar contratos `LLMRequestPayload` y `LLMResponse`.
- [ ] Implementar pipeline de features para ML.
- [ ] Implementar scoring de régimen/prioridad.
- [ ] Integrar ML con Signal Intelligence.
- [ ] Implementar cliente de API LLM.
- [ ] Implementar timeout y retries.
- [ ] Implementar validación fuerte de salida LLM.
- [ ] Implementar normalización de respuesta LLM.
- [ ] Registrar request/response con trazabilidad completa.
- [ ] Crear UI de estado ML y consultas LLM.
- [ ] Implementar fallback y modo degradado.

### Pruebas funcionales
- [ ] Verificar scoring ML con inputs válidos.
- [ ] Verificar que el sistema sigue operando si ML falla.
- [ ] Verificar timeout, retry y fallback en LLM.
- [ ] Verificar rechazo de respuestas LLM inválidas.
- [ ] Verificar trazabilidad completa de request/response.

### Documentación técnica
- [ ] Actualizar `docs/architecture/ml-llm-integration.md`.
- [ ] Crear `docs/api/llm-contracts.md`.
- [ ] Crear `docs/runbooks/llm-fallback.md`.

### Criterio de salida
- [ ] ML y LLM enriquecen contexto sin comprometer robustez.

---

## Fase 13. Signal Orchestrator, Risk & Portfolio y Policy Gate

### Objetivo
Convertir triggers enriquecidos en candidatos aprobables y seguros.

### Tasks
- [ ] Diseñar `TradeCandidate`.
- [ ] Diseñar `RiskDecision`.
- [ ] Crear tabla `risk_decisions`.
- [ ] Implementar fusión de trigger + ML + LLM + contexto.
- [ ] Resolver conflictos entre técnico y fundamental.
- [ ] Implementar recomendaciones: `operate`, `reduce_risk`, `wait`, `block`.
- [ ] Implementar validaciones de riesgo por trade.
- [ ] Implementar límites diarios y exposición agregada.
- [ ] Implementar correlación por clase de activo.
- [ ] Implementar validación por evento y spread.
- [ ] Implementar `Policy Gate` para reglas duras.
- [ ] Crear UI de candidatos y decisiones de riesgo.

### Pruebas funcionales
- [ ] Verificar creación de `TradeCandidate` con explicación.
- [ ] Verificar aprobación y rechazo por riesgo.
- [ ] Verificar bloqueo por spread, horario, evento y activo deshabilitado.
- [ ] Verificar trazabilidad desde trigger hasta `RiskDecision`.
- [ ] Verificar visualización en UI.

### Documentación técnica
- [ ] Actualizar `docs/architecture/risk-and-policy.md`.
- [ ] Crear `docs/data-model/trade-candidate-model.md`.
- [ ] Crear `docs/runbooks/risk-rejection-codes.md`.

### Criterio de salida
- [ ] Ningún candidato llega a ejecución sin aprobación explícita.

---

## Fase 14. Execution Engine y Order Monitoring

### Objetivo
Enviar órdenes y seguir su ciclo de vida de forma desacoplada.

### Tasks
- [ ] Diseñar `OrderIntent`, `OrderExecution`, `PositionLifecycle`.
- [ ] Crear tablas `orders`, `order_events`, `positions`, `position_events`.
- [ ] Implementar `paper mode`.
- [ ] Implementar `live mode` con flag explícito.
- [ ] Implementar envío de órdenes.
- [ ] Implementar cancelación/modificación.
- [ ] Implementar seguimiento de órdenes y posiciones.
- [ ] Implementar fills parciales, cierre parcial, trailing, breakeven si aplica.
- [ ] Implementar reconciliación contra broker.
- [ ] Crear UI de órdenes y posiciones.

### Pruebas funcionales
- [ ] Verificar ejecución en `paper mode`.
- [ ] Verificar que `live mode` no se activa accidentalmente.
- [ ] Verificar ciclo completo orden → posición → cierre.
- [ ] Verificar reconciliación ante discrepancias.
- [ ] Verificar trazabilidad con `correlation_id` end-to-end.

### Documentación técnica
- [ ] Actualizar `docs/architecture/execution-and-monitoring.md`.
- [ ] Crear `docs/runbooks/order-lifecycle.md`.
- [ ] Crear `docs/api/execution-api.md`.

### Criterio de salida
- [ ] El sistema puede operar en paper con trazabilidad completa.

---

## Fase 15. Audit, Metrics, Replay, seguridad y preparación para VM

### Objetivo
Hacer el sistema robusto, auditable y desplegable.

### Tasks
- [ ] Diseñar `AuditRecord`.
- [ ] Implementar logs estructurados completos.
- [ ] Implementar métricas por módulo.
- [ ] Implementar trazas por `correlation_id`.
- [ ] Implementar replay de jornada.
- [ ] Implementar dashboard de salud del sistema.
- [ ] Implementar RBAC básico en UI y APIs.
- [ ] Externalizar secretos y credenciales.
- [ ] Añadir circuit breakers y rate limits.
- [ ] Optimizar consultas DB y concurrencia.
- [ ] Probar despliegue en VM.
- [ ] Crear backup/restore y recovery básico.
- [ ] Crear manual operativo.

### Pruebas funcionales
- [ ] Verificar replay completo de una jornada.
- [ ] Verificar que cada orden puede reconstruirse desde auditoría.
- [ ] Verificar alertas de salud del sistema.
- [ ] Verificar roles y acceso restringido.
- [ ] Verificar despliegue funcional en VM.

### Documentación técnica
- [ ] Actualizar `docs/architecture/observability-and-security.md`.
- [ ] Crear `docs/runbooks/backup-restore.md`.
- [ ] Crear `docs/runbooks/production-operations.md`.
- [ ] Crear `docs/runbooks/vm-deployment.md`.

### Criterio de salida
- [ ] Sistema auditable, operable y listo para entorno controlado.

---

## Checkpoints funcionales obligatorios

### Checkpoint A — Data Foundation
- [ ] Validar flujo: MT5 → Asset Catalog → Bars → Operational DB.
- [ ] Confirmar consistencia temporal y de OHLC.
- [ ] Confirmar que la UI puede consultar estado del mercado.

### Checkpoint B — Analysis Foundation
- [ ] Validar flujo: Bars → Pivot Engine → Indicator Engine → Event Intelligence → Radar.
- [ ] Confirmar que el radar genera snapshots y estados correctos.

### Checkpoint C — Trigger Foundation
- [ ] Validar flujo: Radar → Trigger Library → TriggerActivation.
- [ ] Confirmar cooldown, deduplicación y trazabilidad.

### Checkpoint D — Intelligence Foundation
- [ ] Validar flujo: Trigger → Signal Intelligence → ML / LLM → TradeCandidate.
- [ ] Confirmar payloads, respuestas y manejo de fallos.

### Checkpoint E — Trading Foundation
- [ ] Validar flujo: TradeCandidate → Risk → Policy Gate → Execution → Order Monitoring.
- [ ] Confirmar que el sistema funciona en `paper mode` extremo a extremo.

### Checkpoint F — Production Readiness
- [ ] Validar auditoría, replay, métricas, seguridad y despliegue en VM.

---

## Backlog transversal de documentación técnica

- [ ] Mantener actualizado `docs/architecture/software-architecture.md` en cada fase.
- [ ] Mantener actualizado el mapa de entidades y relaciones.
- [ ] Mantener actualizado el catálogo de eventos de dominio.
- [ ] Mantener actualizado el catálogo de endpoints y contratos.
- [ ] Mantener actualizado el catálogo de triggers.
- [ ] Mantener actualizado el catálogo de prompts y perfiles.
- [ ] Mantener actualizado el runbook operativo.
- [ ] Mantener actualizado el changelog arquitectónico.

---

## Notas

- Este plan toma como referencia el estilo incremental con checkpoints y criterios de validación del archivo adjunto `tasks.md`, pero lo adapta a la arquitectura objetivo del radar con MT5, librería de triggers, base operativa, cálculo incremental y separación por dominios.  
- La primera operación automática recomendada es en `paper mode`.  
- `live mode` debe quedar bloqueado hasta cerrar pruebas funcionales, auditoría y hardening.
