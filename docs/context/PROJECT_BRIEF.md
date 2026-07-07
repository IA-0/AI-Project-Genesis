# PROJECT_BRIEF — Atlas

> Reconstrucción de la definición original de Atlas, respondiendo las 5 preguntas de descubrimiento de la Fase 1. Fuente: el diseño original del proyecto (chats previos al repo). Este documento es el insumo para `ADR-0001.md`.

## 1. Qué es

**Atlas** es un sistema open source que convierte una idea de negocio expresada en una frase ("quiero un sistema para administrar clínicas veterinarias") en un proyecto ejecutable: especificación funcional completa, arquitectura y backlog priorizado. Lo hace orquestando roles de un equipo de producto real — analista funcional, arquitecto de software, Product Owner, UX, QA y DevOps — como agentes de IA que trabajan en secuencia sobre la misma idea.

El nombre viene de eso: Atlas sostiene y mapea el mundo completo de un proyecto antes de que exista una línea de código.

## 2. Problema

Developers independientes, PyMEs y equipos chicos reciben ideas de negocio vagas y pierden días (o directamente fracasan) convirtiéndolas en algo construible: no hay historias de usuario, no hay modelo de datos, no hay criterio de priorización. Hoy eso se resuelve a mano, o con chats sueltos de ChatGPT/Claude que producen texto sin estructura, sin trazabilidad y sin llegar nunca a un backlog ejecutable.

Verificable: es exactamente el problema que yo (Federico) sufrí construyendo automatizaciones para PyMEs — el cliente tiene la idea, nadie tiene la spec.

## 3. Alcance mínimo (los 4 días)

El MVP es el pipeline end-to-end para **un solo caso de uso elegido** (no el sistema genérico):

1. **Input:** una frase de negocio.
2. **Descubrimiento:** motor de preguntas mínimas necesarias para refinar la idea (no un cuestionario de cien ítems).
3. **Salida funcional:** visión de producto, actores, reglas de negocio, historias de usuario en formato estándar ("Como [perfil], quiero [acción], para [beneficio]") con criterios de aceptación.
4. **Salida técnica:** propuesta de arquitectura (stack, modelo de datos, APIs) y backlog priorizado.
5. **Formato:** todo exportado como archivos Markdown a un repo — el output de Atlas es un repo listo para que un agente de código lo implemente.

Todo lo demás (UI, multi-tenant, más casos de uso, gestión de sprints) queda explícitamente fuera del MVP.

## 4. Stack

Piezas ya validadas, sin tecnología nueva salvo justificación en un ADR:

- **Python** como lenguaje principal del orquestador.
- **Groq** (y/o DeepSeek vía Aider) para los roles mecánicos/baratos del pipeline.
- **Claude (Fable/Sonnet vía Claude Code)** para los roles de criterio: arquitectura y revisión.
- **n8n self-hosted** solo si el flujo lo justifica; no es obligatorio en el MVP.
- **Docker** para empaquetar, **VPS Oracle Cloud Free Tier** como target de despliegue.
- **GitHub** como memoria compartida y formato de entrega (el output de Atlas es un repo).

## 5. Carrera

Atlas apunta primero a **Análisis Funcional + IA/Automatización**: demuestra en un solo repo la habilidad de convertir negocio en especificación (análisis funcional), y la de orquestar múltiples sistemas de IA con criterio de ingeniería (arquitectura, trade-offs, verificación cruzada). El público objetivo del lanzamiento en LinkedIn son CTOs, tech leads y reclutadores técnicos; la métrica de éxito está en `NORTH_STAR.md`, no acá.

---

**Nota para el ADR-0001:** Atlas es la hipótesis, no la conclusión. Aplicar `<evaluation_criteria>` del MASTER_PROMPT sobre esta definición; si algún criterio falla (especialmente el #3, funcional en 4 días part-time), el ADR debe decirlo y proponer el recorte o el reemplazo.
