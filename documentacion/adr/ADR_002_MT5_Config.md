# ADR-002 — Configuración de múltiples cuentas MT5 desde la opción Configuración

**Estado:** Aprobado
**Fecha:** 2026-04-05
**Decisor:** Software Architecture
**Ámbito:** Configuración / MT5 Adapter / Security / UI Web / Asset Catalog / Execution

---

## 1. Título

Adoptar un **módulo de configuración de cuentas MT5** accesible desde **Configuración → Cuentas MT5**, con soporte para **múltiples cuentas**, selección controlada de cuenta activa por contexto operativo y almacenamiento seguro de credenciales y parámetros de conexión.

---

## 2. Contexto

El sistema debe operar sobre MetaTrader 5 y, por diseño, puede necesitar trabajar con más de una cuenta, por ejemplo:

* cuenta de desarrollo;
* cuenta paper/demo;
* cuenta live micro;
* cuenta live principal;
* cuentas separadas por broker, estrategia o entorno.

Se requiere que la configuración de estas cuentas esté centralizada en la UI, dentro de la opción **Configuración**, y no dispersa en archivos manuales o variables duras de código.

Además, se identifican estos requisitos:

1. Debe existir una pantalla de configuración de cuentas MT5 dentro del módulo de Configuración.
2. El sistema debe soportar varias cuentas registradas.
3. Debe existir una forma controlada de identificar cuál cuenta está habilitada para uso operativo.
4. El sistema debe separar claramente:

   * la definición de la cuenta,
   * su disponibilidad técnica,
   * y su habilitación operativa.
5. La configuración debe ser auditable.
6. Las credenciales no deben almacenarse en texto plano visible.

---

## 3. Problema

¿Cómo diseñar la configuración de cuentas MT5 para que:

* soporte múltiples cuentas;
* sea fácil de administrar desde UI;
* no comprometa seguridad;
* permita distinguir ambientes y estados operativos;
* y mantenga coherencia con Clean Architecture y buenas prácticas de sistemas de trading?

---

## 4. Decisión

Se adopta el siguiente diseño:

### 4.1 Ubicación funcional

La gestión de cuentas MT5 será accesible desde:

**Configuración → Cuentas MT5**

### 4.2 Modelo de gestión

Las cuentas MT5 se modelarán como un **catálogo persistente de cuentas**, administrado desde la base de datos del sistema.

Cada cuenta será una entidad independiente, con su propia configuración y estado.

### 4.3 Soporte multi-cuenta

El sistema soportará múltiples cuentas MT5 registradas simultáneamente.

No se asume una sola cuenta global.

### 4.4 Separación de estados

Se separan tres conceptos:

* **Cuenta registrada**: existe en la base.
* **Cuenta disponible**: la conexión y validación técnica con MT5 son correctas.
* **Cuenta habilitada**: puede ser usada por los módulos operativos del sistema.

### 4.5 Activación operativa

Una cuenta puede estar registrada y disponible, pero no necesariamente habilitada para operación.

La habilitación debe ser una decisión explícita.

### 4.6 Regla de operación por entorno

Se define que una cuenta debe pertenecer a un tipo de entorno operativo, por ejemplo:

* `DEV`
* `DEMO`
* `PAPER`
* `LIVE_MICRO`
* `LIVE`

### 4.7 Selección de cuenta activa

La arquitectura no asumirá una sola “cuenta activa” global rígida.
En su lugar, cada cuenta podrá tener uno de estos estados:

* registrada;
* habilitada;
* predeterminada para un entorno o perfil.

Esto permite que el sistema evolucione hacia:

* una cuenta por entorno;
* una cuenta por estrategia;
* o varias cuentas activas según reglas futuras.

En la versión inicial, se permitirá marcar una **cuenta predeterminada por entorno**.

### 4.8 Seguridad

Las credenciales sensibles de MT5 no deben guardarse en texto plano legible desde UI.

Se adopta esta política:

* la UI no expone contraseñas completas;
* los secretos se almacenan cifrados o referenciados por secret store;
* la lectura completa del secreto no se devuelve a la UI;
* la actualización de credenciales se realiza por reemplazo, no por lectura.

### 4.9 Validación técnica

Cada cuenta podrá ejecutar una validación técnica manual o automática para comprobar:

* acceso al terminal o adaptador MT5;
* login correcto;
* servidor correcto;
* estado de conexión;
* tipo de cuenta;
* moneda base;
* broker;
* disponibilidad.

### 4.10 No eliminación física obligatoria

Las cuentas no deben borrarse físicamente como acción normal.
Se prefiere:

* `ACTIVE`
* `INACTIVE`
* `ARCHIVED`

Esto preserva trazabilidad histórica y auditoría.

---

## 5. Estructura del modelo adoptado

### 5.1 Entidad principal `MT5Account`

Campos mínimos recomendados:

* `id`
* `account_name`
* `broker_name`
* `server_name`
* `login`
* `password_secret_ref` o `password_encrypted`
* `terminal_path`
* `environment_type`
* `is_enabled`
* `availability_status`
* `is_default_for_environment`
* `last_validation_at`
* `last_validation_status`
* `created_at`
* `updated_at`
* `archived_at`

### 5.2 Estado de disponibilidad

`availability_status`:

* `UNKNOWN`
* `AVAILABLE`
* `UNAVAILABLE`
* `INVALID_CREDENTIALS`
* `TERMINAL_NOT_FOUND`
* `CONNECTION_ERROR`

### 5.3 Estado de ciclo de vida

`lifecycle_status`:

* `ACTIVE`
* `INACTIVE`
* `ARCHIVED`

### 5.4 Tabla de auditoría

`mt5_account_audit_log`:

* `id`
* `account_id`
* `action`
* `old_value`
* `new_value`
* `changed_by`
* `changed_at`
* `reason`

### 5.5 Tabla de validación

`mt5_account_validation_log`:

* `id`
* `account_id`
* `validation_started_at`
* `validation_finished_at`
* `status`
* `error_message`
* `broker_response_summary`

---

## 6. Reglas de negocio adoptadas

### RN-MT5-01

La gestión de cuentas MT5 se realiza desde **Configuración → Cuentas MT5**.

### RN-MT5-02

El sistema debe soportar múltiples cuentas MT5 registradas.

### RN-MT5-03

Cada cuenta debe estar asociada a un entorno operativo.

### RN-MT5-04

La disponibilidad técnica y la habilitación operativa son atributos distintos.

### RN-MT5-05

Una cuenta no disponible no puede ser usada por módulos operativos.

### RN-MT5-06

La contraseña no debe mostrarse en texto claro desde la UI.

### RN-MT5-07

Toda creación, edición, habilitación, deshabilitación o archivado de cuenta debe quedar auditado.

### RN-MT5-08

Debe permitirse definir una cuenta predeterminada por entorno.

### RN-MT5-09

No debe haber dos cuentas predeterminadas activas para el mismo entorno.

### RN-MT5-10

Las cuentas archivadas no pueden ser seleccionadas para operación.

### RN-MT5-11

El sistema debe permitir validar la cuenta antes de habilitarla.

### RN-MT5-12

Una cuenta con credenciales inválidas debe quedar marcada con estado técnico correspondiente y no podrá ser usada.

---

## 7. Comportamiento funcional adoptado

### 7.1 Crear cuenta MT5

1. El usuario entra a **Configuración → Cuentas MT5**.
2. El usuario selecciona **Agregar cuenta**.
3. El sistema solicita:

   * nombre visible;
   * broker;
   * servidor;
   * login;
   * contraseña;
   * ruta del terminal o adaptador;
   * entorno.
4. El sistema valida formato.
5. El sistema persiste la cuenta.
6. El sistema almacena el secreto de forma segura.
7. La cuenta queda creada en estado:

   * `lifecycle_status = ACTIVE`
   * `availability_status = UNKNOWN`
   * `is_enabled = false`

### 7.2 Validar cuenta

1. El usuario selecciona **Validar conexión**.
2. El sistema intenta conectarse vía adaptador MT5.
3. El sistema registra resultado.
4. La cuenta pasa a:

   * `AVAILABLE`, si la validación fue exitosa;
   * o a un estado técnico de error si falla.

### 7.3 Habilitar cuenta

1. El usuario marca la cuenta como habilitada.
2. El sistema verifica que la cuenta esté disponible.
3. El sistema actualiza `is_enabled = true`.
4. Si se marca como predeterminada del entorno, el sistema desmarca cualquier otra del mismo entorno.

### 7.4 Deshabilitar cuenta

1. El usuario desmarca la cuenta.
2. El sistema actualiza `is_enabled = false`.
3. La cuenta permanece registrada.

### 7.5 Archivar cuenta

1. El usuario selecciona **Archivar**.
2. El sistema impide que sea usada operativamente.
3. El sistema mantiene historial, auditoría y referencias históricas.

---

## 8. Ubicación en la arquitectura

### 8.1 UI Web

Nueva pantalla dentro de Configuración:

**Configuración → Cuentas MT5**

Funciones:

* listar cuentas;
* crear cuenta;
* editar cuenta;
* validar cuenta;
* habilitar/deshabilitar;
* marcar predeterminada por entorno;
* archivar.

### 8.2 Configuration / Control Plane

Responsable de:

* persistir configuración de cuentas;
* aplicar reglas de unicidad por entorno;
* publicar configuraciones activas.

### 8.3 MT5 Adapter

Responsable de:

* probar conectividad;
* recuperar metadata básica de cuenta;
* informar errores técnicos.

### 8.4 Execution / Runtime Resolver

Responsable de:

* resolver qué cuenta usar según entorno o contexto operativo;
* rechazar operación si no existe cuenta válida.

### 8.5 Audit Layer

Responsable de:

* registrar todo cambio administrativo;
* registrar validaciones;
* registrar cambios de estado.

---

## 9. Alternativas consideradas

### Alternativa A — Una sola cuenta global en archivo `.env`

**Rechazada.**

**Motivos:**

* no soporta múltiples cuentas;
* dificulta administración operativa;
* poca trazabilidad;
* mala evolución futura.

### Alternativa B — Guardar credenciales en texto plano en la base

**Rechazada.**

**Motivos:**

* mala práctica de seguridad;
* alto riesgo operativo;
* exposición innecesaria.

### Alternativa C — Varias cuentas pero sin validación técnica

**Rechazada.**

**Motivos:**

* mala experiencia;
* errores detectados demasiado tarde;
* mayor riesgo de fallos en ejecución.

### Alternativa D — Permitir varias cuentas predeterminadas para el mismo entorno

**Rechazada.**

**Motivos:**

* ambigüedad operativa;
* complejidad innecesaria en la primera versión.

---

## 10. Consecuencias

### Positivas

* soporte real para múltiples cuentas;
* mejor separación entre configuración y operación;
* escalabilidad para varios brokers o entornos;
* mejor seguridad;
* mayor trazabilidad;
* alineación con sistemas serios de trading.

### Negativas

* más complejidad de modelo y UI;
* necesidad de validación técnica y auditoría;
* necesidad de gestión segura de secretos.

---

## 11. Criterios de aceptación arquitectónica

La decisión se considera correctamente implementada cuando:

1. Existe una pantalla **Configuración → Cuentas MT5**.
2. Se pueden registrar varias cuentas MT5.
3. Cada cuenta tiene entorno, estado técnico y estado operativo.
4. Se puede validar una cuenta desde UI.
5. Se puede habilitar o deshabilitar una cuenta.
6. Se puede marcar una cuenta predeterminada por entorno.
7. No existen dos cuentas predeterminadas para el mismo entorno.
8. Las contraseñas no se muestran en texto claro.
9. Toda modificación queda auditada.
10. Las cuentas no disponibles no pueden ser usadas por la operación.

---

## 12. Recomendaciones de implementación

### 12.1 Campos mínimos para la primera versión

* nombre de cuenta;
* broker;
* servidor;
* login;
* contraseña;
* ruta del terminal;
* entorno;
* habilitada;
* disponible;
* predeterminada del entorno.

### 12.2 Acciones UI mínimas

* crear;
* editar;
* validar;
* habilitar/deshabilitar;
* archivar;
* filtrar por entorno y estado.

### 12.3 Recomendación de UX

Mostrar en tabla:

* nombre;
* broker;
* servidor;
* login parcial o enmascarado;
* entorno;
* disponibilidad;
* habilitada;
* predeterminada;
* última validación.

### 12.4 Convenciones recomendadas

Usar en código:

* `mt5_account`
* `environment_type`
* `availability_status`
* `is_enabled`
* `is_default_for_environment`

---

## 13. Resumen ejecutivo

Se adopta una **configuración multi-cuenta de MT5** administrada desde **Configuración → Cuentas MT5**, con:

* soporte para varias cuentas;
* separación entre disponibilidad técnica y habilitación operativa;
* una cuenta predeterminada por entorno;
* almacenamiento seguro de credenciales;
* auditoría completa;
* y preparación para evolución futura sin rediseño del modelo.
