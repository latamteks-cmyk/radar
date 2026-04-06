# Documento de Requisitos: Radar Trading Intelligence Platform

## Introducción

Radar Trading Intelligence Platform es un sistema de análisis, priorización y ejecución asistida para trading sobre MetaTrader 5 (MT5). El sistema monitorea continuamente un universo configurable de activos, calcula pivotes e indicadores técnicos con base en datos del broker, incorpora el calendario económico nativo de MT5, detecta candidatos operativos mediante una librería de `trigger_type`, enriquece el contexto con Machine Learning y consultas API LLM, y aplica control de riesgo antes de permitir una operación.

El sistema opera con una arquitectura modular basada en **Clean Architecture**, **DDD simplificado**, **CQRS** para los modelos de lectura y escritura y **eventos internos** para desacoplar módulos. MT5 funciona como adaptador de mercado y ejecución; el estado operativo, la configuración y la trazabilidad residen en la base de datos y en los servicios del backend.

El flujo principal es:

`Configuración → Preparación de Jornada → Datos de Mercado → Pivotes/Indicadores/Eventos → Radar → Trigger Library → Signal Intelligence (ML + LLM) → Riesgo → Policy Gate → Ejecución → Seguimiento → Auditoría`

El sistema debe poder operar en tres modos:
- **Monitor Only**: sólo radar, snapshots, triggers y alertas.
- **Paper Trading**: decisiones completas con ejecución simulada.
- **Live Trading Controlado**: ejecución real con límites, políticas y trazabilidad completa.

---

## Objetivos del Proyecto

1. Construir un radar de mercado multi-activo sobre MT5, con configuración centralizada y comportamiento auditable.
2. Detectar condiciones candidatas operables en M15 y/o M5, usando contexto H4, pivotes diarios y eventos económicos.
3. Reducir dependencia operativa de consultas repetidas a MT5 mediante persistencia operativa y caché.
4. Estandarizar la lógica de activación mediante una **Trigger Library** reusable, configurable y versionada.
5. Enriquecer el análisis con Machine Learning y LLM sin delegar en ellos la decisión final de riesgo o ejecución.
6. Mantener separación estricta entre análisis, riesgo, ejecución y observabilidad.
7. Garantizar trazabilidad completa desde la actualización de mercado hasta la orden, decisión de bloqueo o cierre.

---

## Alcance

### En alcance
- Integración con MetaTrader 5 para símbolos, OHLC, sesiones, eventos económicos y ejecución.
- UI web para configuración, monitoreo, radar, auditoría y operación.
- Catálogo de activos administrable y agrupado por tipo.
- Cálculo de pivotes diarios y bandas de evaluación.
- Cálculo incremental de indicadores por nueva vela cerrada.
- Librería de `trigger_type` con reglas OO.
- Pipeline de Signal Intelligence con ML y LLM.
- Gestión de riesgo, Policy Gate y ejecución desacoplada.
- Seguimiento de órdenes y posiciones.
- Auditoría, métricas, logging y replay.

### Fuera de alcance inicial
- Backtesting visual completo dentro de la UI.
- Optimización automática de hiperparámetros en producción.
- Soporte multi-broker distinto de MT5 en la primera versión.
- Microservicios distribuidos desde la primera entrega.
- Gestión de portafolios institucionales multi-cuenta complejos.

---

## Glosario

- **Radar Trading Intelligence Platform**: El sistema descrito en este documento.
- **MT5 Adapter**: Componente que integra MetaTrader 5 con el backend para datos, sesiones, eventos y ejecución.
- **Configuration / Control Plane**: Módulo responsable de la configuración maestra y la publicación de la configuración activa.
- **Scheduler / Pre-Session Engine**: Subsistema que prepara la jornada, congela pivotes y publica la configuración operativa del día.
- **Market Cache / Operational DB**: Capa de persistencia operativa y lectura rápida usada por el radar y la UI.
- **Radar Engine**: Componente que monitorea símbolos, evalúa snapshots y detecta candidatos operativos.
- **Trigger Library**: Librería OO de tipos de trigger reutilizables y configurables.
- **Trigger_Type**: Tipo de activación o patrón de negocio que describe una condición candidata operable.
- **Signal Intelligence**: Capa que transforma un trigger en un contexto enriquecido mediante ML, LLM y reglas de fusión.
- **Prompt Template Service**: Módulo que resuelve plantillas de prompt por activo, trigger y contexto.
- **Policy Gate**: Capa determinística que aplica reglas duras antes de autorizar ejecución.
- **Risk & Portfolio Engine**: Módulo que aprueba o rechaza candidatos según riesgo, exposición y límites de cuenta.
- **Execution Engine**: Componente que envía órdenes y traduce decisiones autorizadas a operaciones en MT5.
- **Order Monitoring**: Módulo que sigue el ciclo de vida de órdenes y posiciones.
- **Audit / Replay**: Subsistema responsable de trazabilidad, reproducción de jornadas y análisis posterior.
- **correlation_id**: UUID v4 que une todo el flujo desde snapshot de mercado hasta decisión/orden/evento.
- **request_id**: Identificador único por solicitud de orden que garantiza idempotencia.
- **TradingDayConfig**: Configuración operativa resuelta para la jornada actual.
- **Asset Profile**: Perfil que define comportamiento, sesiones, triggers, prompts y riesgo de un activo o grupo de activos.
- **PivotSet**: Conjunto de pivotes activos calculados para un símbolo en una jornada o sesión.
- **RadarSnapshot**: Registro persistido del estado operativo del símbolo en una actualización dada.
- **TriggerActivation**: Registro de una activación de trigger con contexto, score, razones y referencias.
- **TradeCandidate**: Señal contextual enriquecida y aún no ejecutada.
- **Economic Event Window**: Ventana temporal pre/post evento que modifica el modo operativo del activo.
- **Cooldown**: Tiempo mínimo entre activaciones equivalentes para evitar duplicados y ruido.
- **Broker Truth**: Principio por el que el estado real del broker/MT5 prevalece sobre la base local ante discrepancias.
- **Paper Trading**: Modo en el que se simula la ejecución sin enviar órdenes reales.
- **Live Trading**: Modo en el que se envían órdenes reales a MT5.
- **M5 / M15 / H4**: Timeframes operativos del sistema.
- **OHLC**: Open, High, Low, Close de una vela.
- **ATR**: Average True Range, indicador de volatilidad.
- **RSI**: Relative Strength Index, indicador de momentum.
- **Session Profile**: Perfil de horarios y comportamiento operativo de una clase de activo.
- **Risk Mode**: Estado operativo de riesgo: `NORMAL`, `CAUTION`, `BLOCK_PRE_EVENT`, `BLOCK_POST_EVENT`, `BLOCKED`.
- **State Machine**: Máquina de estados del radar por símbolo.

---

## Stakeholders

- **Product Owner**: define prioridades, criterios de aceptación y reglas de negocio.
- **Equipo Backend**: implementa dominio, casos de uso, persistencia e integraciones.
- **Equipo UI/Frontend**: implementa experiencia de configuración, radar, observabilidad y operación.
- **Equipo Quant/Trading**: define triggers, indicadores, riesgo, prompts y políticas operativas.
- **Operador/Usuario Final**: configura activos, supervisa alertas, revisa auditoría y, según modo, habilita ejecución.
- **QA / Testing**: verifica funcionalidad, regresión, estabilidad y cumplimiento de criterios de aceptación.
- **DevOps / Infraestructura**: despliega, monitorea, asegura continuidad y backup/recovery.

---

## Arquitectura y Contextos del Sistema

El sistema debe estructurarse en los siguientes bounded contexts y módulos principales:

1. **Configuration / Control Plane**
2. **Scheduler / Pre-Session Engine**
3. **MT5 Adapter**
4. **Market Cache / Operational DB**
5. **Asset Catalog**
6. **Pivot Engine**
7. **Indicator Engine**
8. **Event Intelligence**
9. **Radar Engine**
10. **Trigger Library**
11. **Signal Intelligence**
12. **Prompt Template Service**
13. **Machine Learning Service**
14. **LLM Orchestrator**
15. **Risk & Portfolio Engine**
16. **Policy Gate**
17. **Execution Engine**
18. **Order Monitoring**
19. **Audit / Metrics / Replay**
20. **UI Web / BFF**

Cada contexto debe exponer interfaces claras, evitar acoplamiento directo innecesario y persistir su estado relevante fuera de memoria.

---

## Estados Globales del Sistema

El sistema debe soportar, como mínimo, los siguientes estados globales:

- `STARTING`
- `READY`
- `MONITOR_ONLY`
- `PAPER_ONLY`
- `LIVE_ENABLED`
- `DEGRADED`
- `INTRADAY_FREEZE`
- `CIRCUIT_ACTIVE`
- `EMERGENCY_STOP`
- `STOPPED_GRACEFUL`
- `FORCED_STOP`

Las transiciones válidas deben estar controladas por el Orchestrator y registradas en auditoría.

---

## Estados del Radar por Símbolo

Cada símbolo bajo monitoreo debe soportar una máquina de estados con, al menos, los siguientes estados:

- `IDLE`
- `WATCHLIST`
- `IN_ZONE`
- `TRIGGERED`
- `UNDER_ANALYSIS`
- `APPROVED`
- `BLOCKED`
- `COOLDOWN`

Toda transición debe quedar registrada con timestamp, `correlation_id`, `config_version` y causa.

---

## Requisitos Funcionales

### RF-CP — Configuration / Control Plane

#### UC-CP-01 Gestión de configuración activa
El sistema debe permitir crear, editar, publicar y versionar la configuración maestra del sistema.

**Criterios funcionales:**
- Debe existir configuración en estado `draft` y `published`.
- Toda publicación debe generar una nueva `config_version`.
- Toda modificación debe registrar usuario, fecha, motivo y diff de cambios.

#### UC-CP-02 Configuración por perfiles
El sistema debe permitir definir perfiles por tipo de activo para riesgo, prompts, triggers, sesiones e indicadores.

#### UC-CP-03 Overrides por símbolo
El sistema debe permitir sobrescribir la configuración heredada del perfil por tipo de activo a nivel símbolo.

#### UC-CP-04 Gestión de tiempos pre-jornada
El sistema debe permitir configurar, como mínimo:
- minutos previos al inicio de jornada para análisis;
- hora de inicio de sesión por mercado/perfil;
- ventanas pre/post evento;
- timeframes operativos permitidos.

---

### RF-AC — Asset Catalog

#### UC-AC-01 Descubrimiento de activos
El sistema debe sincronizar desde MT5 la lista de símbolos disponibles.

#### UC-AC-02 Clasificación de activos
El sistema debe clasificar los símbolos por tipo de activo, al menos en:
- índices;
- forex majors;
- forex minors;
- metales;
- energía;
- acciones;
- criptos, si están disponibles.

#### UC-AC-03 Activación/desactivación de activos
El sistema debe permitir activar o desactivar un activo para ser monitoreado por el radar.

#### UC-AC-04 Asignación de perfiles
El sistema debe permitir asociar por símbolo:
- perfil de riesgo;
- perfil de prompts;
- perfil de triggers;
- perfil de sesiones.

---

### RF-MD — Market Data

#### UC-MD-01 Ingesta de barras
El sistema debe almacenar barras OHLC de, al menos, H4, M15 y M5 para los activos habilitados.

#### UC-MD-02 Detección de nueva vela
El sistema debe detectar la llegada de una nueva vela cerrada por símbolo y timeframe.

#### UC-MD-03 Persistencia operativa
El sistema debe persistir las barras y snapshots necesarios para que Radar, UI y Auditoría no dependan de consultas repetidas a MT5.

#### UC-MD-04 Integridad de datos
El sistema debe validar integridad mínima de datos OHLC y registrar anomalías de mercado o gaps relevantes.

---

### RF-PV — Pivot Engine

#### UC-PV-01 Cálculo de pivotes diarios
El sistema debe calcular pivotes diarios a partir de OHLC de períodos cerrados provenientes del broker en MT5.

#### UC-PV-02 Congelamiento de pivotes
Los pivotes vigentes de una jornada deben permanecer congelados hasta el siguiente rollover o cambio de sesión configurado.

#### UC-PV-03 Bandas de evaluación
El sistema debe generar bandas configurables alrededor de los niveles pivote para evaluar cercanía o entrada en zona.

#### UC-PV-04 Versionado del cálculo
El sistema debe registrar el origen, timestamp y versión del cálculo de cada `PivotSet`.

---

### RF-IN — Indicator Engine

#### UC-IN-01 Contexto H4
El sistema debe calcular indicadores estructurales en H4 para determinar el sesgo de mercado.

#### UC-IN-02 Indicadores de ejecución
El sistema debe calcular indicadores para M15 y/o M5 según configuración del activo o perfil.

#### UC-IN-03 Cálculo incremental
El sistema debe recalcular indicadores sólo al incorporarse una nueva vela cerrada y sobre la ventana mínima necesaria.

#### UC-IN-04 Patrones
El sistema debe soportar patrones o setups multi-vela reutilizables y versionados.

---

### RF-EV — Event Intelligence

#### UC-EV-01 Lectura del calendario económico
El sistema debe consumir los eventos económicos nativos de MT5 con su importancia, timestamp y datos relevantes.

#### UC-EV-02 Asociación de eventos a activos
El sistema debe mapear automáticamente los eventos a los activos según tipo de activo, moneda o mercado asociado.

#### UC-EV-03 Ventanas operativas
El sistema debe construir ventanas pre y post evento que modifiquen el modo operativo del activo.

#### UC-EV-04 Overrides de evento
El sistema debe permitir exclusiones o asociaciones manuales de eventos a símbolos desde la configuración.

---

### RF-RD — Radar Engine

#### UC-RD-01 Monitoreo continuo
El radar debe monitorear continuamente los activos habilitados y evaluar su contexto operativo en cada actualización relevante.

#### UC-RD-02 Snapshot por actualización
El radar debe persistir un `RadarSnapshot` por cada actualización considerada relevante del símbolo.

#### UC-RD-03 Condición operativa del día
El radar debe registrar y mantener actualizada la condición operativa diaria por símbolo y tipo de activo.

#### UC-RD-04 Confluencia técnico-fundamental
El radar debe considerar pivotes, indicadores, patrones, contexto H4 y ventanas de evento para detectar candidatos.

#### UC-RD-05 Salida del radar
Cuando identifique una condición candidata, el radar debe preparar un contexto estructurado y emitir un evento interno hacia la siguiente capa.

---

### RF-TL — Trigger Library

#### UC-TL-01 Librería de trigger types
El sistema debe implementar una librería OO de `trigger_type` reusable y configurable.

#### UC-TL-02 Catálogo inicial de triggers
La librería debe soportar, al menos:
- `pivot_approach`
- `pivot_breakout`
- `pivot_rejection`
- `trend_alignment`
- `event_proximity`
- `technical_fundamental_confluence`
- `volatility_regime_change`
- `session_open_setup`
- `news_risk_block`
- `post_event_reentry`

#### UC-TL-03 Cooldown e idempotencia
Cada trigger debe soportar cooldown configurable, deduplicación e idempotencia por símbolo, tipo de trigger y contexto.

#### UC-TL-04 Registro de activación
Cada activación debe registrar:
- tipo de trigger;
- prioridad;
- pre-score;
- `reason_codes`;
- referencia a snapshot;
- versión de trigger;
- `config_version`.

#### UC-TL-05 Activación/configuración por perfil
Debe ser posible activar o desactivar triggers por perfil y por símbolo.

---

### RF-SI — Signal Intelligence

#### UC-SI-01 Construcción de contexto enriquecido
El sistema debe transformar la activación de un trigger en un `SignalCandidate` con contexto técnico, fundamental y operativo.

#### UC-SI-02 Integración con ML
El sistema debe permitir solicitar un score o clasificación de régimen/anomalía a una capa de Machine Learning.

#### UC-SI-03 Integración con LLM
El sistema debe permitir consultar un LLM sólo cuando un candidato lo justifique según reglas de negocio.

#### UC-SI-04 Fusión de señales
El sistema debe combinar resultados de triggers, ML y LLM en una recomendación contextual única.

#### UC-SI-05 Explainability
El candidato resultante debe indicar score, confianza, contradicciones y causa dominante.

---

### RF-PT — Prompt Template Service

#### UC-PT-01 Plantillas por tipo de activo
El sistema debe definir plantillas de prompt por tipo de activo.

#### UC-PT-02 Overrides por símbolo
El sistema debe permitir ajustes específicos por símbolo.

#### UC-PT-03 Variantes por trigger
El sistema debe permitir variantes de prompt por tipo de trigger y escenario operativo.

#### UC-PT-04 Payload estructurado
El servicio debe construir payloads JSON estructurados para el LLM.

#### UC-PT-05 Versionado de prompts
Cada plantilla usada debe tener versión, hash y trazabilidad en auditoría.

---

### RF-ML — Machine Learning Service

#### UC-ML-01 Score cuantitativo
El sistema debe poder generar un score cuantitativo de apoyo para clasificar candidatos o régimen.

#### UC-ML-02 Modo degradado
Si la capa ML no está disponible, el sistema debe poder continuar en modo degradado según política configurada.

---

### RF-LLM — LLM Orchestrator

#### UC-LLM-01 Consulta controlada
El sistema debe realizar consultas al LLM con timeout, retry, rate limit y control de costos.

#### UC-LLM-02 Validación de salida
La respuesta del LLM debe validarse contra un esquema estructurado antes de ser aceptada.

#### UC-LLM-03 Fallback seguro
Si la consulta falla o devuelve un esquema inválido, el sistema debe registrar el error y aplicar fallback configurado.

#### UC-LLM-04 Trazabilidad completa
Toda consulta y respuesta LLM debe quedar registrada para auditoría.

---

### RF-RK — Risk & Portfolio Engine

#### UC-RK-01 Aprobación pretrade
Todo `TradeCandidate` debe ser evaluado por la capa de riesgo antes de pasar a ejecución.

#### UC-RK-02 Límites de riesgo
El sistema debe soportar, como mínimo:
- riesgo máximo por trade;
- pérdida máxima diaria;
- exposición máxima abierta;
- exposición correlacionada máxima;
- límites por tipo de activo;
- restricciones por evento.

#### UC-RK-03 Decisión de riesgo
La capa debe emitir `RiskApproved` o `RiskRejected` con causa explícita.

#### UC-RK-04 Modos de riesgo
Debe existir, al menos, soporte para perfiles de riesgo `conservative`, `normal` y `controlled_aggressive`.

---

### RF-PG — Policy Gate

#### UC-PG-01 Reglas duras pre-ejecución
El sistema debe verificar antes de ejecutar:
- mercado abierto;
- activo habilitado;
- spread dentro de umbral;
- cooldown cumplido;
- ausencia de duplicados;
- salud mínima de dependencias.

#### UC-PG-02 Autorización final
La capa debe emitir `ExecutionAuthorized` o `ExecutionBlocked`.

---

### RF-EX — Execution Engine

#### UC-EX-01 Modo paper y modo live
El sistema debe soportar ejecución simulada y ejecución real.

#### UC-EX-02 Órdenes idempotentes
Toda orden debe tener `request_id` único para evitar duplicación.

#### UC-EX-03 Trazabilidad de ejecución
Cada orden debe poder vincularse a:
- `correlation_id`;
- `TriggerActivation`;
- `TradeCandidate`;
- `RiskDecision`;
- `RadarSnapshot`.

#### UC-EX-04 Cancelación y modificación
La capa debe soportar cancelación o modificación de órdenes cuando la política operativa lo requiera.

---

### RF-OM — Order Monitoring

#### UC-OM-01 Seguimiento de órdenes
El sistema debe monitorear el ciclo de vida completo de órdenes pendientes, enviadas, llenadas, rechazadas o canceladas.

#### UC-OM-02 Seguimiento de posiciones
El sistema debe monitorear posiciones abiertas, cierres parciales y cierres finales.

#### UC-OM-03 Gestión operativa
El sistema debe soportar trailing, break-even, time-stop y reglas equivalentes cuando estén habilitadas.

#### UC-OM-04 Reconciliación con broker
La capa debe reconciliar su estado con MT5 y aplicar el principio de `Broker Truth`.

---

### RF-AU — Audit / Metrics / Replay

#### UC-AU-01 Auditoría técnica y funcional
El sistema debe registrar todos los eventos relevantes del flujo de negocio y operación.

#### UC-AU-02 Métricas
El sistema debe registrar métricas operativas, técnicas y de salud por módulo.

#### UC-AU-03 Replay
El sistema debe permitir reconstruir una jornada a partir de snapshots, triggers, decisiones y órdenes.

#### UC-AU-04 Trazabilidad por correlation_id
Toda búsqueda por `correlation_id` debe permitir reconstruir el flujo end-to-end.

---

### RF-UI — UI Web

#### UC-UI-01 Dashboard
La UI debe mostrar una vista consolidada del estado del sistema.

#### UC-UI-02 Página Radar
La UI debe mostrar por símbolo:
- tipo de activo;
- estado del radar;
- condición operativa del día;
- pivotes activos;
- contexto H4;
- trigger actual;
- proximidad a evento;
- riesgo permitido;
- última decisión.

#### UC-UI-03 Página de configuración
La UI debe permitir configurar:
- tiempos previos al inicio de jornada;
- lista de activos habilitados;
- triggers activos;
- perfiles de riesgo;
- plantillas de prompt;
- indicadores y pivotes;
- sesiones y horarios.

#### UC-UI-04 Observabilidad
La UI debe disponer de páginas de auditoría, logs, métricas, salud y estado del sistema.

---

## Requisitos de Datos

### RD-01 Identificadores
Todas las entidades relevantes deben soportar identificadores únicos estables.

### RD-02 Versionado
Debe existir versionado para:
- configuración;
- triggers;
- prompts;
- indicadores/modelos;
- políticas de riesgo.

### RD-03 Retención
El sistema debe soportar políticas de retención por tipo de dato:
- barras;
- snapshots;
- activaciones;
- consultas LLM;
- órdenes y posiciones;
- auditoría.

### RD-04 Integridad
Los datos críticos del pipeline no deben perder su trazabilidad ni su referencia cruzada.

---

## Requisitos No Funcionales

### RNF-01 Arquitectura
El sistema debe seguir Clean Architecture con separación entre dominio, aplicación, infraestructura y presentación.

### RNF-02 Modularidad
Los contextos funcionales deben poder evolucionar de forma relativamente independiente.

### RNF-03 Orientación a objetos
La lógica de negocio reusable, especialmente Trigger Library, debe implementarse siguiendo OOP con composición, interfaces y patrones Strategy/Factory.

### RNF-04 Persistencia
El estado crítico no debe residir exclusivamente en memoria.

### RNF-05 Rendimiento
El sistema debe minimizar recálculos innecesarios y usar cálculo incremental por última vela cerrada.

### RNF-06 Escalabilidad
La arquitectura debe permitir evolucionar de monolito modular a servicios separados sin rediseñar el dominio.

### RNF-07 Observabilidad
Todos los módulos deben emitir logs estructurados, métricas y eventos de auditoría.

### RNF-08 Disponibilidad
El sistema debe soportar degradación segura y continuar operando según política en ausencia de componentes no críticos.

### RNF-09 Seguridad
Las credenciales y secretos no deben almacenarse en código fuente ni exponerse en logs.

### RNF-10 Idempotencia
Las operaciones críticas de integración y ejecución deben ser idempotentes.

### RNF-11 Auditabilidad
Cada orden, bloqueo o consulta LLM debe ser explicable y reconstruible.

### RNF-12 Mantenibilidad
El sistema debe estar documentado y versionado, y cada módulo debe exponer interfaces claras.

### RNF-13 Compatibilidad operativa
El sistema debe poder desplegarse en servidor local y evolucionar a VM sin cambios sustanciales de arquitectura.

---

## Restricciones Técnicas

1. La fuente primaria de datos de mercado y ejecución es MT5.
2. Los pivotes no deben depender de datos de páginas web para operar.
3. El sistema debe soportar M15 y/o M5 como timeframes operativos seleccionables.
4. H4 debe usarse como contexto estructural.
5. El calendario económico debe basarse en los criterios nativos de MT5.
6. El backend y la UI deben poder ejecutarse localmente.
7. La primera versión debe ser operable como monolito modular.

---

## Supuestos

1. MT5 está instalado, accesible y correctamente configurado en el entorno operativo.
2. Los símbolos necesarios existen en el servidor del broker conectado.
3. La latencia local entre MT5 y backend es aceptable para el modelo de operación planteado.
4. El universo inicial de activos será manejable para un despliegue local.
5. El LLM es una capa de apoyo contextual y no de decisión autónoma final.

---

## Riesgos de Negocio y Técnicos

1. Dependencia operativa de la disponibilidad de MT5.
2. Riesgo de exceso de escritura en la base operativa si se persiste demasiado granularmente por tick.
3. Riesgo de ruido si los triggers no incorporan cooldown y deduplicación.
4. Riesgo de inconsistencia si no se aplica correctamente `Broker Truth`.
5. Riesgo de respuestas no confiables del LLM si no se validan por esquema.
6. Riesgo de sobreacoplamiento si la lógica de negocio se implementa dentro del adaptador MT5.

---

## Criterios de Aceptación de Alto Nivel

1. El sistema puede sincronizar activos desde MT5 y activarlos/desactivarlos desde la UI.
2. El sistema puede preparar la jornada según configuración y horarios definidos.
3. El sistema calcula pivotes e indicadores de forma confiable y persistida.
4. El radar produce snapshots y detecta triggers con trazabilidad.
5. La Trigger Library puede activarse/configurarse por perfil y símbolo.
6. Signal Intelligence puede enriquecer candidatos con ML/LLM sin perder explicabilidad.
7. Ninguna operación llega a ejecución sin aprobación de riesgo y Policy Gate.
8. El sistema puede operar en monitor-only, paper y live.
9. Todas las decisiones y órdenes son auditables y reproducibles.
10. La UI permite configurar, monitorear y auditar el sistema de forma coherente con la arquitectura.

---

## Trazabilidad Inicial de Casos de Uso

- `UC-CP-*` → Configuration / Control Plane
- `UC-AC-*` → Asset Catalog
- `UC-MD-*` → Market Data / Operational DB
- `UC-PV-*` → Pivot Engine
- `UC-IN-*` → Indicator Engine
- `UC-EV-*` → Event Intelligence
- `UC-RD-*` → Radar Engine
- `UC-TL-*` → Trigger Library
- `UC-SI-*` → Signal Intelligence
- `UC-PT-*` → Prompt Template Service
- `UC-ML-*` → Machine Learning Service
- `UC-LLM-*` → LLM Orchestrator
- `UC-RK-*` → Risk & Portfolio Engine
- `UC-PG-*` → Policy Gate
- `UC-EX-*` → Execution Engine
- `UC-OM-*` → Order Monitoring
- `UC-AU-*` → Audit / Metrics / Replay
- `UC-UI-*` → UI Web

---

## Fases de Despliegue Recomendadas

1. **Fase A — Monitor Only**
   - catálogo de activos;
   - configuración;
   - mercado persistido;
   - pivotes;
   - indicadores;
   - eventos;
   - radar;
   - trigger library;
   - UI básica;
   - auditoría.

2. **Fase B — Paper Trading**
   - signal intelligence;
   - prompts;
   - ML/LLM;
   - riesgo;
   - policy gate;
   - ejecución simulada;
   - seguimiento.

3. **Fase C — Live Trading Controlado**
   - ejecución real;
   - reconciliación con broker;
   - hardening;
   - observabilidad completa;
   - políticas de continuidad y recuperación.

---

## Requisitos de Documentación Técnica

1. Cada módulo debe tener documentación técnica actualizada.
2. Todo cambio de contrato JSON debe versionarse y documentarse.
3. Toda modificación de reglas de trigger, prompt o riesgo debe registrarse en release notes técnicas.
4. Debe existir documentación operativa mínima para arranque, parada, recovery y troubleshooting.

---

## Criterios de Calidad

1. Código con tipado y convenciones homogéneas.
2. Pruebas unitarias, integración y funcionales por fase.
3. Separación entre entornos local, paper y live.
4. No se aceptan flujos críticos sin trazabilidad por `correlation_id`.
5. No se aceptan decisiones operativas sin causa explícita y auditable.

