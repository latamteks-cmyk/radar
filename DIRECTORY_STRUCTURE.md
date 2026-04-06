# Radar Trading Intelligence Platform - Estructura del Proyecto

## Estructura de Directorios Completa

```
radar2/
│
├── src/                              # Código fuente principal
│   ├── domain/                       # Capa de dominio (reglas de negocio)
│   │   ├── entities/                 # Entidades del dominio
│   │   │   ├── asset.py
│   │   │   ├── asset_profile.py
│   │   │   ├── trading_day_config.py
│   │   │   ├── session_profile.py
│   │   │   ├── pivot_set.py
│   │   │   ├── indicator_snapshot.py
│   │   │   ├── economic_event_snapshot.py
│   │   │   ├── radar_snapshot.py
│   │   │   ├── trigger_activation.py
│   │   │   ├── prompt_template.py
│   │   │   ├── llm_request.py
│   │   │   ├── llm_result.py
│   │   │   ├── ml_result.py
│   │   │   ├── trade_candidate.py
│   │   │   ├── risk_decision.py
│   │   │   ├── order_intent.py
│   │   │   ├── order_execution.py
│   │   │   ├── position_lifecycle.py
│   │   │   └── audit_record.py
│   │   │
│   │   ├── value_objects/            # Value Objects
│   │   │   ├── correlation_id.py
│   │   │   ├── request_id.py
│   │   │   ├── trigger_type.py
│   │   │   ├── risk_mode.py
│   │   │   ├── session_phase.py
│   │   │   ├── bar_time.py
│   │   │   ├── pivot_band.py
│   │   │   └── prompt_profile_id.py
│   │   │
│   │   ├── interfaces/               # Interfaces del dominio
│   │   │   ├── i_market_gateway.py
│   │   │   ├── i_trigger.py
│   │   │   ├── i_risk_policy.py
│   │   │   ├── i_llm_client.py
│   │   │   ├── i_config_store.py
│   │   │   ├── i_execution_gateway.py
│   │   │   └── i_audit_sink.py
│   │   │
│   │   └── enums.py                  # Enumeraciones del dominio
│   │
│   ├── application/                  # Capa de aplicación (casos de uso)
│   │   ├── configuration/            # Configuration / Control Plane
│   │   │   ├── services/
│   │   │   │   ├── config_service.py
│   │   │   │   ├── profile_service.py
│   │   │   │   └── validation_service.py
│   │   │   ├── dto/
│   │   │   │   ├── config_draft.py
│   │   │   │   └── config_published.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── scheduler/                # Scheduler / Pre-Session Engine
│   │   │   ├── services/
│   │   │   │   ├── scheduler_service.py
│   │   │   │   ├── pre_session_analyzer.py
│   │   │   │   └── trading_day_preparer.py
│   │   │   ├── jobs/
│   │   │   │   ├── t_minus_60.py
│   │   │   │   ├── t_minus_30.py
│   │   │   │   ├── t_minus_15.py
│   │   │   │   └── session_open.py
│   │   │   └── dto/
│   │   │       └── trading_day_config.py
│   │   │
│   │   ├── asset_catalog/            # Asset Catalog
│   │   │   ├── services/
│   │   │   │   ├── asset_discovery.py
│   │   │   │   ├── asset_classifier.py
│   │   │   │   └── asset_profile_manager.py
│   │   │   └── dto/
│   │   │       └── asset_info.py
│   │   │
│   │   ├── pivot_engine/             # Pivot Engine
│   │   │   ├── services/
│   │   │   │   ├── pivot_calculator.py
│   │   │   │   ├── pivot_freezer.py
│   │   │   │   └── band_builder.py
│   │   │   ├── strategies/
│   │   │   │   ├── classic_pivots.py
│   │   │   │   └── session_pivots.py
│   │   │   └── dto/
│   │   │       └── pivot_calculation.py
│   │   │
│   │   ├── indicator_engine/         # Indicator Engine
│   │   │   ├── services/
│   │   │   │   ├── indicator_updater.py
│   │   │   │   ├── h4_bias_calculator.py
│   │   │   │   └── pattern_detector.py
│   │   │   ├── indicators/
│   │   │   │   ├── trend/
│   │   │   │   │   ├── ma_calculator.py
│   │   │   │   │   ├── ema_calculator.py
│   │   │   │   │   └── macd_calculator.py
│   │   │   │   ├── momentum/
│   │   │   │   │   ├── rsi_calculator.py
│   │   │   │   │   └── stochastic_calculator.py
│   │   │   │   └── volatility/
│   │   │   │       ├── atr_calculator.py
│   │   │   │       └── bollinger_calculator.py
│   │   │   └── dto/
│   │   │       └── indicator_values.py
│   │   │
│   │   ├── event_intelligence/       # Event Intelligence
│   │   │   ├── services/
│   │   │   │   ├── event_loader.py
│   │   │   │   ├── event_mapper.py
│   │   │   │   └── window_builder.py
│   │   │   └── dto/
│   │   │       └── event_context.py
│   │   │
│   │   ├── radar/                    # Radar Engine
│   │   │   ├── services/
│   │   │   │   ├── radar_evaluator.py
│   │   │   │   ├── state_machine.py
│   │   │   │   └── snapshot_creator.py
│   │   │   ├── evaluators/
│   │   │   │   ├── pivot_proximity.py
│   │   │   │   ├── indicator_context.py
│   │   │   │   └── event_context.py
│   │   │   └── dto/
│   │   │       └── radar_snapshot.py
│   │   │
│   │   ├── triggers/                 # Trigger Library
│   │   │   ├── base/
│   │   │   │   ├── trigger_base.py
│   │   │   │   ├── trigger_context.py
│   │   │   │   └── trigger_result.py
│   │   │   ├── factory/
│   │   │   │   └── trigger_factory.py
│   │   │   ├── registry/
│   │   │   │   └── trigger_registry.py
│   │   │   ├── implementations/
│   │   │   │   ├── pivot_approach.py
│   │   │   │   ├── pivot_breakout.py
│   │   │   │   ├── pivot_rejection.py
│   │   │   │   ├── trend_alignment.py
│   │   │   │   ├── event_proximity.py
│   │   │   │   ├── technical_fundamental_confluence.py
│   │   │   │   ├── volatility_regime_change.py
│   │   │   │   ├── session_open_setup.py
│   │   │   │   ├── news_risk_block.py
│   │   │   │   └── post_event_reentry.py
│   │   │   └── dto/
│   │   │       └── trigger_activation.py
│   │   │
│   │   ├── signal_intelligence/      # Signal Intelligence
│   │   │   ├── services/
│   │   │   │   ├── signal_builder.py
│   │   │   │   ├── prompt_selector.py
│   │   │   │   └── signal_merger.py
│   │   │   └── dto/
│   │   │       └── signal_candidate.py
│   │   │
│   │   ├── prompt_templates/         # Prompt Template Service
│   │   │   ├── services/
│   │   │   │   ├── template_resolver.py
│   │   │   │   ├── prompt_renderer.py
│   │   │   │   └── version_manager.py
│   │   │   └── dto/
│   │   │       └── prompt_payload.py
│   │   │
│   │   ├── ml/                       # Machine Learning Service
│   │   │   ├── services/
│   │   │   │   ├── regime_scorer.py
│   │   │   │   ├── priority_scorer.py
│   │   │   │   └── anomaly_detector.py
│   │   │   ├── models/
│   │   │   │   └── model_registry.py
│   │   │   └── dto/
│   │   │       └── ml_score.py
│   │   │
│   │   ├── llm/                      # LLM Orchestrator
│   │   │   ├── services/
│   │   │   │   ├── llm_client.py
│   │   │   │   ├── response_validator.py
│   │   │   │   └── fallback_handler.py
│   │   │   └── dto/
│   │   │       └── llm_response.py
│   │   │
│   │   ├── risk/                     # Risk & Portfolio Engine
│   │   │   ├── services/
│   │   │   │   ├── risk_validator.py
│   │   │   │   ├── exposure_checker.py
│   │   │   │   └── daily_limit_checker.py
│   │   │   ├── policies/
│   │   │   │   ├── conservative_policy.py
│   │   │   │   ├── normal_policy.py
│   │   │   │   └── controlled_aggressive_policy.py
│   │   │   └── dto/
│   │   │       └── risk_decision.py
│   │   │
│   │   ├── policy_gate/              # Policy Gate
│   │   │   ├── services/
│   │   │   │   ├── market_open_checker.py
│   │   │   │   ├── spread_checker.py
│   │   │   │   └── duplicate_checker.py
│   │   │   └── dto/
│   │   │       └── policy_decision.py
│   │   │
│   │   ├── execution/                # Execution Engine
│   │   │   ├── services/
│   │   │   │   ├── order_builder.py
│   │   │   │   ├── order_submitter.py
│   │   │   │   └── order_manager.py
│   │   │   ├── modes/
│   │   │   │   ├── paper_execution.py
│   │   │   │   └── live_execution.py
│   │   │   └── dto/
│   │   │       └── execution_result.py
│   │   │
│   │   ├── order_monitoring/         # Order Monitoring
│   │   │   ├── services/
│   │   │   │   ├── order_tracker.py
│   │   │   │   ├── position_tracker.py
│   │   │   │   └── reconciliation.py
│   │   │   ├── rules/
│   │   │   │   ├── trailing_rules.py
│   │   │   │   └── breakeven_rules.py
│   │   │   └── dto/
│   │   │       └── position_event.py
│   │   │
│   │   └── audit/                    # Audit / Metrics / Replay
│   │       ├── services/
│   │       │   ├── audit_recorder.py
│   │       │   ├── metrics_collector.py
│   │       │   └── day_replayer.py
│   │       └── dto/
│   │           └── audit_record.py
│   │
│   ├── infrastructure/               # Capa de infraestructura
│   │   ├── mt5/                      # MT5 Adapter
│   │   │   ├── adapter/
│   │   │   │   ├── mt5_gateway.py
│   │   │   │   ├── mt5_connector.py
│   │   │   │   └── mt5_data_handler.py
│   │   │   ├── dto/
│   │   │   │   ├── mt5_bar.py
│   │   │   │   ├── mt5_event.py
│   │   │   │   └── mt5_session.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── persistence/              # Persistencia (PostgreSQL)
│   │   │   ├── repositories/
│   │   │   │   ├── asset_repository.py
│   │   │   │   ├── bar_repository.py
│   │   │   │   ├── pivot_repository.py
│   │   │   │   ├── indicator_repository.py
│   │   │   │   ├── event_repository.py
│   │   │   │   ├── radar_snapshot_repository.py
│   │   │   │   ├── trigger_repository.py
│   │   │   │   ├── config_repository.py
│   │   │   │   ├── risk_repository.py
│   │   │   │   ├── order_repository.py
│   │   │   │   └── audit_repository.py
│   │   │   ├── models/               # SQLAlchemy models
│   │   │   │   ├── asset_model.py
│   │   │   │   ├── bar_model.py
│   │   │   │   ├── pivot_model.py
│   │   │   │   ├── indicator_model.py
│   │   │   │   ├── event_model.py
│   │   │   │   ├── radar_snapshot_model.py
│   │   │   │   ├── trigger_model.py
│   │   │   │   ├── config_model.py
│   │   │   │   ├── risk_model.py
│   │   │   │   ├── order_model.py
│   │   │   │   └── audit_model.py
│   │   │   ├── database.py
│   │   │   └── connection.py
│   │   │
│   │   ├── cache/                    # Cache en memoria
│   │   │   ├── market_cache.py
│   │   │   └── config_cache.py
│   │   │
│   │   ├── logging/                  # Logging estructurado
│   │   │   ├── structured_logger.py
│   │   │   └── correlation_filter.py
│   │   │
│   │   ├── config/                   # Gestión de configuración
│   │   │   ├── settings.py
│   │   │   ├── config_loader.py
│   │   │   └── secrets_manager.py
│   │   │
│   │   └── events/                   # Event Bus interno
│   │       └── event_bus.py
│   │
│   ├── presentation/                 # Capa de presentación
│   │   ├── api/                      # API REST (FastAPI)
│   │   │   ├── routes/
│   │   │   │   ├── health.py
│   │   │   │   ├── assets.py
│   │   │   │   ├── radar.py
│   │   │   │   ├── triggers.py
│   │   │   │   ├── signals.py
│   │   │   │   ├── risk.py
│   │   │   │   ├── orders.py
│   │   │   │   ├── audit.py
│   │   │   │   └── config.py
│   │   │   ├── middleware/
│   │   │   │   ├── correlation_middleware.py
│   │   │   │   └── error_middleware.py
│   │   │   ├── schemas/
│   │   │   │   ├── asset_schema.py
│   │   │   │   ├── radar_schema.py
│   │   │   │   ├── trigger_schema.py
│   │   │   │   └── order_schema.py
│   │   │   └── dependencies.py
│   │   │
│   │   └── web/                      # UI Web (React/Next.js)
│   │       ├── src/
│   │       │   ├── pages/
│   │       │   │   ├── dashboard/
│   │       │   │   ├── radar/
│   │       │   │   ├── assets/
│   │       │   │   ├── triggers/
│   │       │   │   ├── signals/
│   │       │   │   ├── orders/
│   │       │   │   ├── audit/
│   │       │   │   └── config/
│   │       │   ├── components/
│   │       │   ├── hooks/
│   │       │   ├── utils/
│   │       │   └── styles/
│   │       ├── public/
│   │       └── package.json
│   │
│   └── main.py                       # Punto de entrada
│
├── tests/                            # Pruebas
│   ├── unit/                         # Pruebas unitarias
│   │   ├── domain/
│   │   │   ├── test_entities.py
│   │   │   └── test_value_objects.py
│   │   ├── application/
│   │   │   ├── test_configuration/
│   │   │   ├── test_scheduler/
│   │   │   ├── test_pivot_engine/
│   │   │   ├── test_indicator_engine/
│   │   │   ├── test_radar/
│   │   │   ├── test_triggers/
│   │   │   ├── test_risk/
│   │   │   └── test_execution/
│   │   └── infrastructure/
│   │       ├── test_mt5_adapter/
│   │       └── test_persistence/
│   │
│   ├── integration/                  # Pruebas de integración
│   │   ├── test_mt5_integration.py
│   │   ├── test_database.py
│   │   ├── test_api.py
│   │   └── test_pipeline.py
│   │
│   ├── functional/                   # Pruebas funcionales
│   │   ├── test_trading_flow.py
│   │   ├── test_radar_flow.py
│   │   └── test_execution_flow.py
│   │
│   └── fixtures/                     # Fixtures para tests
│       ├── test_data.py
│       └── mocks.py
│
├── db/                               # Base de datos
│   ├── migrations/                   # Migraciones Alembic
│   │   ├── versions/
│   │   └── env.py
│   ├── seeds/                        # Datos de prueba
│   │   └── seed_data.py
│   └── scripts/                      # Scripts SQL
│       └── create_extensions.sql
│
├── config/                           # Configuración
│   ├── settings/
│   │   ├── default.yaml
│   │   ├── development.yaml
│   │   ├── testing.yaml
│   │   └── production.yaml
│   ├── profiles/                     # Perfiles por tipo de activo
│   │   ├── forex.yaml
│   │   ├── indices.yaml
│   │   ├── metals.yaml
│   │   ├── energy.yaml
│   │   └── crypto.yaml
│   ├── triggers/                     # Configuración de triggers
│   │   └── triggers.yaml
│   ├── prompts/                      # Plantillas de prompts
│   │   └── prompts.yaml
│   └── risk/                         # Políticas de riesgo
│       └── risk_policies.yaml
│
├── scripts/                          # Scripts de utilidad
│   ├── setup.sh
│   ├── run_tests.sh
│   ├── run_migrations.sh
│   ├── seed_db.sh
│   └── backup_db.sh
│
├── docker/                           # Configuración Docker
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .dockerignore
│
├── documentacion/                    # Documentación OFICIAL del proyecto
│   ├── architecture/                 # Documentos de arquitectura
│   │   ├── software-architecture.md
│   │   ├── module-map.md
│   │   ├── integration-mt5.md
│   │   ├── operational-storage.md
│   │   ├── scheduler-pre-session.md
│   │   ├── pivot-engine.md
│   │   ├── indicator-engine.md
│   │   ├── event-intelligence.md
│   │   ├── radar-engine.md
│   │   ├── trigger-library.md
│   │   ├── signal-intelligence.md
│   │   ├── ml-llm-integration.md
│   │   ├── risk-and-policy.md
│   │   ├── execution-and-monitoring.md
│   │   └── observability-and-security.md
│   │
│   ├── data-model/                   # Modelos de datos
│   │   ├── configuration-model.md
│   │   ├── asset-catalog.md
│   │   ├── market-data-model.md
│   │   ├── pivot-model.md
│   │   ├── indicator-model.md
│   │   ├── economic-events-model.md
│   │   ├── radar-snapshot-model.md
│   │   ├── trigger-model.md
│   │   ├── prompt-template-model.md
│   │   ├── trade-candidate-model.md
│   │   └── order-lifecycle-model.md
│   │
│   ├── api/                          # Contratos de API
│   │   ├── base-endpoints.md
│   │   ├── configuration-api.md
│   │   ├── assets-api.md
│   │   ├── prompt-template-api.md
│   │   ├── llm-contracts.md
│   │   └── execution-api.md
│   │
│   ├── runbooks/                     # Guías operativas
│   │   ├── local-setup.md
│   │   ├── config-publication.md
│   │   ├── market-data-recovery.md
│   │   ├── daily-preparation.md
│   │   ├── pivot-recalculation.md
│   │   ├── indicator-rebuild.md
│   │   ├── event-windows.md
│   │   ├── radar-state-machine.md
│   │   ├── trigger-tuning.md
│   │   ├── llm-fallback.md
│   │   ├── risk-rejection-codes.md
│   │   ├── order-lifecycle.md
│   │   ├── backup-restore.md
│   │   ├── production-operations.md
│   │   └── vm-deployment.md
│   │
│   ├── adr/                          # Architecture Decision Records
│   │   ├── ADR-001-architecture-style.md
│   │   ├── ADR-002-mt5-adapter-boundary.md
│   │   ├── ADR-003-operational-db.md
│   │   └── ADR-004-incremental-calculation.md
│   │
│   └── changelog.md                  # Registro de cambios arquitectónicos
│
├── informes/                         # INFORMES del proyecto
│   ├── requisitos/                   # Documentos de requisitos
│   │   ├── Project_Requirements_Radar.md
│   │   └── requisitos-fase-1.md
│   ├── analisis/                     # Análisis y estudios
│   │   ├── analisis-mercado.md
│   │   └── analisis-tecnico.md
│   ├── reportes/                     # Reportes de progreso
│   │   ├── reporte-semanal.md
│   │   └── reporte-fase-0.md
│   └── investigacion/                # Investigación y POCs
│       ├── investigacion-llm.md
│       └── investigacion-ml.md
│
├── logs/                             # Logs de ejecución
│   ├── application.log
│   ├── audit.log
│   └── errors.log
│
├── notebooks/                        # Notebooks para experimentación
│   ├── analysis/
│   └── experiments/
│
├── .env.example                      # Variables de entorno de ejemplo
├── .env                              # Variables de entorno (NO commitear)
├── .gitignore
├── .dockerignore
├── pyproject.toml                    # Configuración del proyecto Python
├── requirements.txt                  # Dependencias
├── requirements-dev.txt              # Dependencias de desarrollo
├── README.md                         # README principal
├── PROJECT_GUIDELINES.md             # Directrices del proyecto
├── LICENSE
└── docker-compose.yml
```

## Principios de la Estructura

### 1. **Separación de Responsabilidades**
- `src/domain/` - Reglas de negocio puras (sin dependencias externas)
- `src/application/` - Casos de uso y orquestación
- `src/infrastructure/` - Implementaciones concretas (DB, MT5, etc.)
- `src/presentation/` - APIs y UI

### 2. **Modularidad por Dominio**
Cada dominio tiene su propia estructura:
```
domain_name/
├── services/       # Servicios del dominio
├── dto/           # Objetos de transferencia
├── strategies/    # Estrategias específicas (si aplica)
└── exceptions.py  # Excepciones del dominio
```

### 3. **Documentación vs Informes**
- **`documentacion/`**: Solo documentación OFICIAL del proyecto (arquitectura, APIs, modelos, runbooks, ADRs)
- **`informes/`**: Requisitos, análisis, reportes de progreso, investigación

### 4. **Pruebas en Cada Fase**
- `tests/unit/` - Pruebas unitarias por dominio
- `tests/integration/` - Pruebas de integración entre componentes
- `tests/functional/` - Pruebas de flujo completo

### 5. **Configuración Externa**
- `config/settings/` - Configuración por entorno
- `config/profiles/` - Perfiles por tipo de activo
- `config/triggers/` - Configuración de triggers
- `config/prompts/` - Plantillas de prompts
- `config/risk/` - Políticas de riesgo

### 6. **Base de Datos**
- `db/migrations/` - Migraciones versionadas
- `db/seeds/` - Datos de prueba
- `db/scripts/` - Scripts SQL auxiliares

### 7. **Scripts de Utilidad**
- Setup, tests, migraciones, backups en `scripts/`
- Configuración Docker en `docker/`

## Flujo de Trabajo por Fase

Cada fase debe:
1. Crear/actualizar código en `src/`
2. Añadir pruebas en `tests/`
3. Actualizar documentación en `documentacion/`
4. Generar informes de progreso en `informes/`
5. Ejecutar y validar todas las pruebas

## Convenciones Importantes

### Nomenclatura:
- **Módulos**: `snake_case` (ej: `pivot_engine`)
- **Clases**: `PascalCase` (ej: `PivotCalculator`)
- **Funciones**: `snake_case` (ej: `calculate_pivots`)
- **Tests**: prefijo `test_` (ej: `test_pivot_calculation`)

### Migraciones:
- Formato: `YYYYMMDD_HHMMSS_description.py`
- Una migración por cambio de schema
- Siempre incluir rollback

### Configuración:
- YAML para configuración estructurada
- JSON para datos operativos
- `.env` para secretos (NUNCA commitear)

### Documentación:
- ADRs para decisiones arquitectónicas importantes
- Runbooks para operaciones recurrentes
- Data models actualizados con cada cambio
