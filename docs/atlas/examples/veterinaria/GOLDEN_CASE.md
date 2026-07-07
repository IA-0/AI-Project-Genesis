# Golden case — clínica veterinaria

- **Rol de este documento:** fixture de aceptación del pipeline (ver §7 de `FUNCTIONAL_SPEC.md`). Es el output de referencia que Atlas debe poder producir automáticamente en el Día 3.
- **Estado de las respuestas:** los supuestos los generó Fable y están **pendientes de validación por Federico** — este documento demuestra a la vez el caso límite de US-03: el pipeline corriendo con cero respuestas del usuario, solo supuestos default.

## Entrada

> "Quiero un sistema para administrar clínicas veterinarias."

## Preguntas mínimas generadas

Aplicando el contrato del §3 de la spec (6 ejes, cap de 10, supuesto default por pregunta). El motor generó 8.

| id | Eje | Pregunta | Qué desbloquea | Supuesto default | Riesgo |
|---|---|---|---|---|---|
| P1 | Actores | ¿Quiénes van a usar el sistema y con qué permisos? | Actores de la spec funcional | Recepcionista, veterinario/a y dueño de la clínica (admin) | Medio |
| P2 | Alcance | ¿Cuál es el proceso que más duele hoy? | Definición del MVP del cliente | La gestión de turnos y el ausentismo por falta de recordatorios | **Alto** |
| P3 | Datos | ¿Qué información mínima necesitan registrar? | Modelo de datos | Cliente (dueño), mascota, turno, consulta/historia clínica, veterinario | Medio |
| P4 | Reglas | ¿Cómo funciona la agenda? | Reglas de negocio de turnos | Sin solapamiento por veterinario; turnos de 30 min | Bajo |
| P5 | Reglas | ¿Quieren recordatorios automáticos y por qué canal? | Historia de recordatorios + integración | Sí, al dueño de la mascota, 24 h antes, por mensajería (WhatsApp) | Medio |
| P6 | Restricciones | ¿Usan algún sistema hoy? ¿Hay datos para migrar? | Restricciones de arquitectura | Papel/Excel; sin migración de datos en el MVP | **Alto** |
| P7 | Restricciones | ¿Una sola clínica o varias sucursales? | Decisión single/multi-tenant | Una sola clínica (single-tenant) | Bajo |
| P8 | Prioridad | ¿Qué tendría que pasar en 30 días para decir "funciona"? | Backlog priorizado + métrica de éxito | 100 % de los turnos registrados en el sistema y menos ausentismo por recordatorios | Medio |

## Historias de usuario del sistema veterinario

Cada historia traza a la pregunta/supuesto que la origina (RN-3). Prioridad: Must/Should/Could.

**HU-01 (Must) — Agendar turno.** Como recepcionista, quiero agendar un turno eligiendo veterinario, fecha y hora, para organizar la atención del día. *(origen: P2, P4)*
- CA-1: no se puede crear un turno que se solape con otro del mismo veterinario (P4).
- CA-2: el turno requiere mascota y dueño existentes o su alta en el momento.
- CA-3: al confirmar, el turno queda visible en la agenda del veterinario asignado.

**HU-02 (Must) — Reagendar o cancelar turno.** Como recepcionista, quiero modificar o cancelar un turno, para reflejar los cambios que piden los clientes. *(origen: P2)*
- CA-1: reagendar re-valida el no-solapamiento.
- CA-2: cancelar exige un motivo y conserva el registro (no se borra el historial).

**HU-03 (Must) — Recordatorio automático.** Como dueño de mascota, quiero recibir un recordatorio 24 h antes del turno, para no olvidarme de asistir. *(origen: P5, P8)*
- CA-1: el recordatorio sale por el canal de mensajería configurado 24 h antes (±15 min).
- CA-2: cada envío registra estado (enviado/fallido); un fallo no interrumpe el resto.
- CA-3: si el turno se cancela o reagenda, el recordatorio pendiente se ajusta.

**HU-04 (Must) — Agenda del día.** Como veterinario/a, quiero ver mi agenda del día, para saber qué pacientes atiendo y en qué orden. *(origen: P1, P4)*
- CA-1: la vista lista solo los turnos propios, ordenados por hora.
- CA-2: cada turno muestra mascota, dueño y motivo si existe.

**HU-05 (Must) — Registrar consulta.** Como veterinario/a, quiero registrar la consulta en la historia clínica de la mascota, para tener continuidad de tratamiento. *(origen: P3)*
- CA-1: la consulta queda vinculada al turno y a la mascota.
- CA-2: campos mínimos: motivo, diagnóstico, tratamiento, próximos pasos.
- CA-3: la historia clínica muestra las consultas en orden cronológico.

**HU-06 (Must) — Alta de cliente y mascota.** Como recepcionista, quiero registrar un dueño con sus mascotas, para poder agendar turnos y llevar historia clínica. *(origen: P3)*
- CA-1: un dueño puede tener varias mascotas.
- CA-2: datos mínimos del dueño: nombre y teléfono de contacto (para recordatorios, P5).

**HU-07 (Should) — Buscar mascota o cliente.** Como recepcionista o veterinario/a, quiero buscar por nombre de mascota o de dueño, para acceder rápido a la historia clínica. *(origen: P3)*
- CA-1: la búsqueda parcial por nombre devuelve resultados de mascotas y dueños.

**HU-08 (Could) — Métricas básicas.** Como dueño/a de la clínica, quiero ver turnos de la semana y tasa de ausentismo, para saber si el sistema está cumpliendo el objetivo de los 30 días. *(origen: P1, P8)*
- CA-1: la métrica de ausentismo distingue turnos asistidos, cancelados y no asistidos.

## Supuestos no validados (US-08 de Atlas)

Los 8 supuestos default están sin validar por el cliente real. Los dos de riesgo **alto** — P2 (que el dolor principal sean los turnos) y P6 (que no haya sistema previo ni migración) — deben confirmarse antes del Día 3: si P2 es erróneo cambia el MVP entero; si P6 es erróneo cambia la arquitectura.
