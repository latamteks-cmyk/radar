# ADR-001: Architecture Style - Clean Architecture + DDD Simplificado

## Estado
**ACCEPTED**

## Contexto

El proyecto Radar Trading Intelligence Platform requiere una arquitectura que permita:

1. **Separación estricta de responsabilidades**: Lógica de negocio aislada de infraestructura
2. **Testabilidad**: Pruebas unitarias y de integración sin mocks complejos
3. **Mantenibilidad**: Evolución independiente de dominios
4. **Trazabilidad**: Auditoría completa de todas las operaciones
5. **Flexibilidad**: Capacidad de cambiar implementaciones (MT5 → otro broker, PostgreSQL → otra DB)

### Restricciones

- Debe operar en entorno local (Windows 10/11)
- Debe poder evolucionar a VM sin rediseño
- Primera versión como monolito modular
- Python 3.10+ como lenguaje principal

## Decisión

Implementar **Clean Architecture** con elementos de **DDD simplificado**:

### Capas Arquitectónicas

```
Presentation Layer (API, UI)
    ↓ (depende de)
Application Layer (Use Cases, Services)
    ↓ (depende de)
Domain Layer (Entities, Interfaces, Value Objects)
    ↑ (depende de)
Infrastructure Layer (MT5, DB, Cache, Config)
```

### Regla Fundamental

**Las dependencias apuntan SIEMPRE hacia adentro.**

- Domain NO conoce Application, Infrastructure ni Presentation
- Application conoce Domain pero NO Infrastructure
- Infrastructure implementa interfaces definidas en Domain
- Presentation orquesta Application

### Bounded Contexts

Dividir el sistema en dominios con responsabilidades claras:

1. Configuration / Control Plane
2. Scheduler / Pre-Session Engine
3. Asset Catalog
4. Market Data / Operational DB
5. Pivot Engine
6. Indicator Engine
7. Event Intelligence
8. Radar Engine
9. Trigger Library
10. Signal Intelligence
11. ML Service
12. LLM Orchestrator
13. Risk & Portfolio Engine
14. Policy Gate
15. Execution Engine
16. Order Monitoring
17. Audit / Metrics / Replay

### Patrones de Diseño

| Patrón | Uso |
|--------|-----|
| Strategy | Triggers, Risk Policies, Execution Modes |
| Factory | TriggerFactory, OrderBuilder |
| Repository | Persistencia de entidades |
| Observer | Event Bus interno |
| State Machine | Radar Engine por símbolo |

## Consecuencias

### Positivas

✅ **Separación de responsabilidades**: Cada capa tiene un rol claro

✅ **Testabilidad**: Domain se prueba sin infraestructura

✅ **Flexibilidad**: Cambiar DB, broker o UI sin tocar lógica

✅ **Mantenibilidad**: Evolución independiente de dominios

✅ **Claridad**: Nuevos desarrolladores entienden rápidamente

✅ **Inversión de dependencias**: Interfaces en Domain, implementaciones en Infrastructure

### Negativas

❌ **Complejidad inicial**: Más archivos y estructura que un script simple

❌ **Curva de aprendizaje**: Equipo debe entender Clean Architecture

❌ **Overhead**: Capas adicionales pueden parecer excesivas al inicio

❌ **Disciplina requerida**: Fácil violar la regla de dependencias si no se revisa código

## Implementación

### Estructura de Directorios

```
src/
├── domain/
│   ├── entities/          # Entidades de negocio puras
│   ├── value_objects/     # Value Objects inmutables
│   └── interfaces/        # Interfaces que Infrastructure implementa
├── application/
│   ├── {dominio}/
│   │   ├── services/      # Servicios de aplicación
│   │   └── dto/           # DTOs para comunicación
├── infrastructure/
│   ├── mt5/               # Implementación MT5 Adapter
│   ├── persistence/       # Implementación repositorios
│   ├── cache/             # Implementación cache
│   └── config/            # Configuración
└── presentation/
    ├── api/               # API REST (FastAPI)
    └── web/               # UI Web (Next.js)
```

### Ejemplo de Código

```python
# Domain interface
class IMarketGateway(ABC):
    @abstractmethod
    def fetch_bars(self, symbol: str, timeframe: str) -> List[OHLCVBar]: ...

# Infrastructure implementation
class MT5Gateway(IMarketGateway):
    def fetch_bars(self, symbol: str, timeframe: str) -> List[OHLCVBar]:
        # MT5-specific code
        ...

# Application service using interface
class MarketDataService:
    def __init__(self, gateway: IMarketGateway):
        self._gateway = gateway  # Dependency injection
    
    def get_latest_bars(self, symbol: str) -> List[OHLCVBar]:
        return self._gateway.fetch_bars(symbol, "M15")
```

## Alternativas Consideradas

### 1. Arquitectura en Capas Tradicional (UI → BL → DAL)

**Rechazada porque**: 
- Acoplamiento entre capas
- Difícil testabilidad
- Lógica de negocio mezclada con infraestructura

### 2. Microservicios desde el Inicio

**Rechazada porque**:
- Complejidad operativa innecesaria para entorno local
- Overhead de despliegue y monitoreo
- Equipo pequeño en fase inicial

### 3. Scripts con Funciones

**Rechazada porque**:
- No escala a complejidad del dominio
- Difícil mantenimiento
- Sin separación de responsabilidades

## Referencias

- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design - Eric Evans](https://www.domainlanguage.com/ddd/)
- [Dependency Inversion Principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)

## Notas de Implementación

- Revisar en cada PR que las dependencias respeten la regla
- Usar inyección de dependencias siempre
- Interfaces en Domain, implementaciones en Infrastructure
- Documentar violaciones justificadas como excepciones
