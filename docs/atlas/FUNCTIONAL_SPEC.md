# Atlas — Especificación funcional del MVP (Fase 2, Día 1)

- **Fecha:** 2026-07-06 · **Autor:** Fable (Claude Code) · **Valida:** Federico
- **Insumos:** `docs/context/PROJECT_BRIEF.md`, `docs/adr/ADR-0001.md` (recortes vinculantes)
- **Entregable par:** `docs/atlas/examples/veterinaria/GOLDEN_CASE.md` (caso de uso real aplicado)

## 1. Visión del producto

Una frase de negocio entra; sale un repo Markdown con especificación funcional, propuesta de arquitectura y backlog priorizado, listo para que un agente de código lo implemente. El MVP demuestra el pipeline end-to-end para **un solo caso de uso** (clínica veterinaria); la generalización queda post-MVP.

## 2. Actores

| Actor | Tipo | Qué hace |
|---|---|---|
| Usuario operador | Humano | Developer independiente o consultor: ingresa la frase, responde (una vez) las preguntas, recibe el repo generado. |
| Analista Funcional | Agente LLM | Genera las preguntas mínimas y, con las respuestas, la spec funcional (visión, actores, reglas, historias con criterios de aceptación). |
| Product Owner | Agente LLM | Convierte las historias en backlog priorizado con criterio explícito. |
| Arquitecto | Agente LLM | Propone stack, modelo de datos y contratos de API consistentes con las restricciones relevadas. |
| Validador estructural | Componente no-LLM | Chequea que cada artefacto tenga las secciones obligatorias antes de pasarlo al siguiente rol. |

**Decisión de alcance (revisable en Día 2):** el MVP corre con 3 roles LLM. UX se descarta porque no hay UI en el MVP; QA se sustituye por el validador estructural más los criterios de aceptación que ya escribe el Analista; DevOps no aplica sin deploy (recorte 2 del ADR-0001).

## 3. Motor de preguntas mínimas

El corazón del Día 1. Principios de diseño:

- **P-1 — One-shot** (recorte 1, ADR-0001): una sola ronda de preguntas, respondida una sola vez. Sin loop interactivo en el MVP.
- **P-2 — Minimalidad por costo de omisión:** una pregunta entra al set solo si su no-respuesta deja un artefacto posterior incompleto o apoyado en un supuesto de riesgo alto. Cada pregunta declara qué artefacto desbloquea; si no desbloquea nada, no se pregunta.
- **P-3 — Cap duro:** máximo 10 preguntas. El default esperado es 6-8.
- **P-4 — Supuesto por defecto:** toda pregunta lleva una respuesta asumida. Si el usuario no responde, el supuesto se adopta y queda marcado como **"supuesto no validado"** en los artefactos finales. El pipeline nunca se bloquea esperando input.
- **P-5 — Taxonomía fija de 6 ejes:** Actores y roles · Alcance y caso de éxito · Datos y entidades · Reglas de negocio · Restricciones e integraciones · Prioridad.

**Contrato de cada pregunta** (campos obligatorios):

```
id | eje | pregunta | qué artefacto desbloquea | supuesto default | riesgo si el supuesto es erróneo (alto/medio/bajo)
```

**Flujo:** frase → Analista genera `preguntas.md` → usuario responde lo que quiera/pueda → `respuestas.md` (respuestas + supuestos adoptados) → el pipeline consume `respuestas.md`, nunca la conversación.

## 4. Reglas de negocio del pipeline

- **RN-1 — Secuencia fija del MVP:** Analista Funcional → Product Owner → Arquitecto. Cada rol produce exactamente un artefacto.
- **RN-2 — El repo como memoria compartida, dentro del producto:** cada rol consume solo el artefacto persistido del rol anterior. Nada viaja por contexto conversacional entre roles.
- **RN-3 — Trazabilidad:** todo artefacto declara sus supuestos y cita las preguntas/respuestas que lo originan. Desde cualquier historia de usuario se puede llegar al supuesto que la sostiene.
- **RN-4 — Validación entre etapas:** si un artefacto no pasa el chequeo estructural, se reintenta una vez con el error como feedback; si vuelve a fallar, el pipeline corta con un error legible. No se propaga un artefacto inválido.
- **RN-5 — Límites duros:** máximo 10 preguntas; cero interactividad después de la ronda única de respuestas.

## 5. Historias de usuario del MVP

Formato: prioridad (Must/Should) · historia · criterios de aceptación (CA).

**US-01 (Must) — Ingreso de la frase.** Como developer independiente, quiero iniciar un proyecto pasando una frase de negocio por CLI, para arrancar sin escribir ningún documento previo.
- CA-1: `atlas init "<frase>"` crea un workspace con la frase persistida.
- CA-2: frase vacía o ausente → error claro y código de salida distinto de 0.
- CA-3: correr de nuevo no pisa un workspace existente sin confirmación explícita.

**US-02 (Must) — Preguntas mínimas.** Como usuario, quiero recibir un set mínimo de preguntas con supuestos por defecto, para refinar la idea en una sola pasada.
- CA-1: cada pregunta cumple el contrato del §3 (los 6 campos, sin excepción).
- CA-2: nunca más de 10 preguntas.
- CA-3: la salida es un `preguntas.md` legible por un humano sin conocer Atlas.

**US-03 (Must) — Respuesta one-shot.** Como usuario, quiero responder una sola vez (o no responder), para que el pipeline avance sin bloquearse nunca.
- CA-1: toda pregunta sin respuesta adopta su supuesto default y queda marcada "supuesto no validado".
- CA-2: el pipeline corre completo incluso con cero respuestas del usuario.

**US-04 (Must) — Spec funcional generada.** Como usuario, quiero obtener la especificación funcional del sistema pedido, para tener el "qué" construible.
- CA-1: contiene visión, actores, reglas de negocio e historias de usuario en formato estándar ("Como…, quiero…, para…") con criterios de aceptación.
- CA-2: cada historia cita la pregunta o supuesto que la origina (RN-3).

**US-05 (Must) — Propuesta de arquitectura.** Como usuario, quiero obtener stack, modelo de datos y contratos de API, para tener el "cómo".
- CA-1: el stack se justifica en una línea por elección (no es una lista suelta).
- CA-2: modelo de datos con entidades, atributos mínimos y relaciones.
- CA-3: consistente con las restricciones declaradas en `respuestas.md` (si dice "sin migración", la arquitectura no propone migración).

**US-06 (Must) — Backlog priorizado.** Como usuario, quiero un backlog ordenado y trazable, para saber por dónde empezar a construir.
- CA-1: cada ítem del backlog referencia la historia que implementa.
- CA-2: la prioridad declara su criterio (valor de negocio y dependencias técnicas).
- CA-3: el orden es ejecutable: ningún ítem depende de uno posterior.

**US-07 (Must) — Export a repo Markdown.** Como usuario, quiero que todo se exporte como un repo con estructura estándar, para dárselo directo a un agente de código.
- CA-1: un comando produce el árbol completo de archivos.
- CA-2: la estructura está documentada y es idéntica entre corridas.
- CA-3: el repo generado se entiende sin contexto externo (incluye su propio README).

**US-08 (Should) — Auditoría de supuestos.** Como usuario, quiero ver todos los supuestos no validados en un solo lugar, para saber qué revisar con el cliente antes de construir.
- CA-1: existe un archivo resumen con cada supuesto no validado, su riesgo y qué artefactos afecta.

## 6. Fuera de alcance del MVP (vinculante por ADR-0001)

UI, loop de descubrimiento interactivo, multi-tenant, deploy a VPS, casos de uso adicionales, gestión de sprints, roles UX/QA/DevOps como agentes.

## 7. Criterio de cierre del Día 1

Este documento más el golden case (`examples/veterinaria/GOLDEN_CASE.md`) leídos y validados por Federico. El golden case funciona como **fixture de aceptación** del pipeline: en el Día 3, el pipeline implementado debe producir, para la misma frase de entrada, un output equivalente en estructura y cobertura al golden case.
