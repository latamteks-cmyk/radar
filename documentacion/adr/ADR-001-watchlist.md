# ADR-001 — Watchlist como catálogo persistente sincronizado con MT5

**Estado:** Aprobado
**Fecha:** 2026-04-05
**Decisor:** Software Architecture
**Ámbito:** Configuración / Watchlist / MT5 Adapter / Asset Catalog / UI Web

---

## 1. Título

Adoptar una **Watchlist persistente en base de datos**, sincronizada incrementalmente con MT5, accesible desde **Configuración → Watchlist**, con separación explícita entre:

* **disponibilidad del símbolo en MT5**, y
* **activación del símbolo para el radar**.

---

## 2. Contexto

El sistema necesita una pantalla de configuración para administrar los activos monitoreados por el radar. La fuente primaria de símbolos es MT5, pero no es recomendable depender de llamadas directas a MT5 para renderizar cada vez la pantalla o para mantener el estado operativo del usuario.

Se identifican estos requisitos de negocio:

1. La opción debe abrirse desde el botón **Watchlist** dentro de **Configuración**.
2. Si la base local no tiene catálogo de símbolos, el sistema debe consultar MT5 y crear la lista inicial.
3. La lista debe almacenarse en base de datos y quedar agrupable por tipo de activo.
4. Cada símbolo debe poder activarse o desactivarse por el usuario mediante una casilla de selección.
5. Cada símbolo debe tener al menos una condición de disponibilidad:

   * `DISPONIBLE`
   * `NO_DISPONIBLE`
6. Si el catálogo ya existe, al abrir Watchlist se debe volver a consultar MT5 y sincronizar:

   * agregar nuevos símbolos;
   * actualizar símbolos existentes;
   * marcar como `NO_DISPONIBLE` los que ya no existan en MT5.
7. La solución debe alinearse con buenas prácticas de arquitectura, persistencia, auditoría y UX.

Además, se detecta una necesidad de diseño: no mezclar el estado “el usuario quiere usar este activo” con “el broker/MT5 expone este símbolo actualmente”.

---

## 3. Problema

¿Cómo diseñar la funcionalidad **Watchlist** para que:

* sea consistente con Clean Architecture;
* no dependa en tiempo real de MT5 para cada render;
* conserve trazabilidad histórica;
* permita activación/desactivación por usuario;
* soporte sincronización incremental;
* y sea robusta ante cambios en el catálogo de símbolos del broker?

---

## 4. Decisión

Se adopta el siguiente diseño:

### 4.1 Nombre funcional y técnico

Se usará el nombre **Watchlist** en UI, documentación, código, API y base de datos.

> No se adopta `wacthlist`, por inconsistencia ortográfica y por impacto negativo en mantenibilidad.

### 4.2 Patrón principal

La Watchlist será un **catálogo persistente de activos**, almacenado en la base de datos del sistema, cuya **fuente de verdad externa** es MT5.

### 4.3 Comportamiento al abrir la pantalla

Al entrar a **Configuración → Watchlist**, el sistema:

1. carga primero el catálogo local;
2. inicia una sincronización con MT5;
3. actualiza la vista con el resultado de la sincronización;
4. si MT5 falla, mantiene visible el último catálogo persistido y muestra estado degradado.

### 4.4 Carga inicial

Si no existe catálogo local, el sistema:

1. consulta a MT5 la lista de símbolos disponibles;
2. crea el catálogo inicial;
3. clasifica los símbolos por tipo de activo;
4. deja todos los símbolos en:

   * `availability_status = DISPONIBLE`
   * `is_enabled = false` por defecto, salvo política explícita.

### 4.5 Sincronización incremental

Si el catálogo ya existe, el sistema compara la lista local con la lista actual de MT5:

* **nuevo en MT5 y no existente en DB** → insertar;
* **existente en DB y en MT5** → actualizar y marcar `DISPONIBLE`;
* **existente en DB y ausente en MT5** → marcar `NO_DISPONIBLE`.

### 4.6 Persistencia histórica

Los símbolos **no se eliminan físicamente** cuando desaparecen de MT5.
Se mantienen en la base por trazabilidad y sólo cambia su disponibilidad.

### 4.7 Separación de estados

Se adoptan dos atributos distintos:

* `availability_status`

  * `DISPONIBLE`
  * `NO_DISPONIBLE`

* `is_enabled`

  * `true`
  * `false`

### 4.8 Regla operativa

Un símbolo puede estar marcado por el usuario como habilitado, pero si está `NO_DISPONIBLE`, **no puede ser utilizado por el radar ni por capas operativas**.

### 4.9 Agrupación

La clasificación por tipo de activo se persiste en DB y se usa en UI para agrupar y filtrar.

---

## 5. Decisiones de arquitectura derivadas

### 5.1 Ubicación en la arquitectura

La funcionalidad Watchlist se distribuye así:

* **UI Web**

  * pantalla Watchlist dentro de Configuración

* **Configuration / Control Plane**

  * orquesta lectura y actualización del catálogo

* **MT5 Adapter**

  * consulta lista de símbolos disponibles

* **Asset Catalog**

  * persiste y clasifica símbolos

* **Audit Layer**

  * registra cambios manuales y sincronizaciones

### 5.2 Responsabilidad por capa

#### UI

* mostrar la watchlist;
* permitir activar/desactivar símbolos;
* mostrar disponibilidad;
* mostrar última sincronización;
* permitir filtrado por tipo y estado.

#### Application Layer

* coordinar la carga inicial;
* ejecutar sincronización incremental;
* validar reglas de negocio.

#### Infrastructure Layer

* consultar símbolos en MT5;
* persistir catálogo y logs de sincronización.

#### Domain Layer

* reglas de consistencia de `Asset`;
* restricciones entre `availability_status` e `is_enabled`.

---

## 6. Modelo de datos adoptado

### 6.1 Tabla principal `assets`

Campos mínimos:

* `id`
* `symbol`
* `display_name`
* `asset_type`
* `availability_status`
* `is_enabled`
* `source`
* `first_seen_at`
* `last_seen_at`
* `updated_at`

### 6.2 Tabla `asset_sync_log`

Campos:

* `id`
* `sync_started_at`
* `sync_finished_at`
* `status`
* `inserted_count`
* `updated_count`
* `unavailable_count`
* `error_message`

### 6.3 Tabla `asset_audit_log`

Campos:

* `id`
* `asset_id`
* `action`
* `old_value`
* `new_value`
* `changed_by`
* `changed_at`
* `reason`

---

## 7. Reglas de negocio adoptadas

### RN-01

La Watchlist sólo se accede desde **Configuración → Watchlist**.

### RN-02

Al abrir la pantalla, se debe intentar sincronización con MT5.

### RN-03

Si no existe catálogo local, se debe construir desde MT5.

### RN-04

Los símbolos deben quedar persistidos y agrupables por tipo de activo.

### RN-05

`availability_status` y `is_enabled` son atributos distintos.

### RN-06

Los símbolos que desaparezcan de MT5 no se eliminan; se marcan `NO_DISPONIBLE`.

### RN-07

Un símbolo `NO_DISPONIBLE` no puede ser consumido por Radar, Trigger Library, Risk ni Execution.

### RN-08

Toda activación/desactivación manual debe quedar auditada.

### RN-09

Los nuevos símbolos se insertan desactivados por defecto.

### RN-10

Si MT5 no está disponible, la pantalla debe mostrar el último catálogo persistido.

---

## 8. Flujo funcional adoptado

### 8.1 Primera carga

1. Usuario abre **Configuración → Watchlist**.
2. Sistema detecta que no existe catálogo.
3. Sistema consulta MT5.
4. Sistema inserta símbolos.
5. Sistema clasifica por tipo de activo.
6. Sistema muestra la lista.

### 8.2 Carga recurrente

1. Usuario abre **Configuración → Watchlist**.
2. Sistema carga catálogo local.
3. Sistema consulta MT5.
4. Sistema sincroniza:

   * inserta nuevos;
   * actualiza existentes;
   * marca ausentes como `NO_DISPONIBLE`.
5. Sistema refleja cambios en pantalla.

### 8.3 Activación manual

1. Usuario marca casilla de un símbolo.
2. Sistema valida disponibilidad.
3. Sistema guarda `is_enabled = true`.
4. Sistema audita el cambio.

### 8.4 Desactivación manual

1. Usuario desmarca casilla.
2. Sistema guarda `is_enabled = false`.
3. Sistema audita el cambio.

---

## 9. Alternativas consideradas

### Alternativa A — Consultar MT5 directamente en cada apertura sin persistencia

**Rechazada.**

**Motivos:**

* acoplamiento fuerte a MT5;
* peor rendimiento;
* sin trazabilidad histórica;
* sin soporte robusto ante fallo de MT5;
* mala experiencia de usuario.

### Alternativa B — Eliminar símbolos ausentes físicamente de la base

**Rechazada.**

**Motivos:**

* pérdida de historial;
* rompe auditoría;
* riesgo de inconsistencias con configuraciones previas;
* complica debugging y replay.

### Alternativa C — Un solo campo para disponibilidad/activación

**Rechazada.**

**Motivos:**

* mezcla conceptos distintos;
* complica reglas operativas;
* reduce claridad del modelo de dominio.

### Alternativa D — Activar automáticamente los nuevos símbolos descubiertos

**Rechazada.**

**Motivos:**

* riesgo operativo;
* cambios no controlados en el universo monitoreado;
* rompe principio de opt-in del usuario.

---

## 10. Consecuencias

### Positivas

* catálogo consistente y persistente;
* menor dependencia de MT5 para lectura;
* trazabilidad histórica;
* sincronización incremental;
* UI más estable;
* mejor separación de responsabilidades;
* alineación con buenas prácticas de sistemas similares.

### Negativas

* más complejidad que una consulta directa;
* necesidad de lógica de sincronización;
* necesidad de auditoría y manejo de estados;
* clasificación inicial de activos puede requerir revisión manual.

---

## 11. Impacto en componentes

### Configuration / Control Plane

Debe exponer casos de uso:

* cargar watchlist;
* sincronizar watchlist;
* activar símbolo;
* desactivar símbolo.

### MT5 Adapter

Debe exponer:

* `GetAvailableSymbols()`

### Asset Catalog

Debe soportar:

* inserción inicial;
* sincronización incremental;
* clasificación;
* actualización de disponibilidad.

### UI Web

Debe añadir:

* botón `Watchlist` en Configuración;
* vista de tabla agrupable;
* filtros;
* checkboxes;
* indicadores de sincronización.

### Audit

Debe registrar:

* sincronizaciones;
* activaciones manuales;
* desactivaciones manuales;
* cambios de disponibilidad.

---

## 12. Criterios de aceptación arquitectónica

La decisión se considera correctamente implementada cuando:

1. Existe una pantalla **Configuración → Watchlist**.
2. Si no existe catálogo local, se construye desde MT5.
3. Si el catálogo existe, se sincroniza incrementalmente con MT5.
4. Los símbolos nuevos se insertan.
5. Los símbolos ausentes pasan a `NO_DISPONIBLE`.
6. Los símbolos están agrupados por tipo de activo.
7. Cada símbolo tiene checkbox de activación.
8. La activación y disponibilidad están separadas.
9. La UI sigue funcionando aunque MT5 falle, mostrando el último catálogo persistido.
10. Toda acción manual y toda sincronización queda auditada.

---

## 13. Notas de implementación

### Convenciones recomendadas

* usar `watchlist` en nombres de clases, endpoints, módulos y rutas;
* usar enums para `availability_status`;
* no usar borrado físico;
* no activar automáticamente nuevos activos;
* aplicar soft-state con timestamps `first_seen_at` y `last_seen_at`.

### Endpoints sugeridos

* `GET /config/watchlist`
* `POST /config/watchlist/sync`
* `PATCH /config/watchlist/{symbol}/enable`
* `PATCH /config/watchlist/{symbol}/disable`

### Casos de error a contemplar

* MT5 no disponible;
* símbolo sin clasificación;
* error parcial de sincronización;
* conflicto de actualización concurrente;
* intento de activar símbolo no disponible.

---

## 14. Resumen ejecutivo

Se adopta una **Watchlist persistente, sincronizada con MT5, auditable y controlada por el usuario**, con separación formal entre:

* **disponibilidad del símbolo en MT5**, y
* **activación del símbolo para el radar**.

Esta decisión mejora robustez, trazabilidad, mantenibilidad y coherencia con la arquitectura general del sistema.