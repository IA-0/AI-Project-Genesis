# ORCHESTRATION_PLAYBOOK

Principios de orquestación multi-agente aprendidos en este proyecto. Cada entrada se agrega en el momento en que el principio aparece en la práctica, con el ejemplo concreto que lo disparó. El objetivo es que Federico pueda rearmar este circuito en cualquier proyecto futuro sin asistencia.

Formato de cada entrada: **qué es** (2-3 líneas), **el caso real que lo disparó acá**, **cómo aplicarlo de nuevo**.

---

## 1. El repo como memoria compartida

**Qué es.** Los agentes no comparten contexto entre sí: cada sesión de Claude Code, Codex o Aider arranca sabiendo solo lo que hay en el repo. Todo lo que vive únicamente en un chat (una decisión, un brief, un plan) es invisible para el resto de la flota — y para vos mismo en otra máquina. El commit es el mensaje; si no está commiteado, para el circuito no existe.

**Caso real (2026-07-06).** El MASTER_PROMPT v3 da por existente la definición de Atlas ("PROJECT_BRIEF.md — ya existe") porque se escribió en sesiones anteriores de chat. Pero esas versiones nunca se commitearon: al retomar el proyecto desde federicopc, ni el repo, ni el remoto, ni ningún archivo local contenían qué es Atlas. La Fase 1 entera quedó bloqueada esperando que un humano recupere información que un `git pull` debería haber traído.

**Cómo aplicarlo.** Al cerrar cualquier sesión de trabajo con un agente, preguntarse: ¿lo que se decidió acá está en un archivo commiteado y pusheado? Si la respuesta es no, la próxima sesión (o el próximo agente, o la otra máquina) arranca de cero. Los entregables no son las conversaciones: son los commits.

---

## 2. Verificación cruzada

**Qué es.** Antes de aceptar el output de un agente, alguien independiente lo revisa: otro modelo (de otra familia — dos instancias del mismo modelo comparten los mismos puntos ciegos) o un humano. Aplica a decisiones tanto como a código. Lo innegociable es que nadie acepta su propio output sin otro par de ojos.

**Caso real (2026-07-06).** El `<analisis>` de ADR-0001 (escrito por Fable) iba a revisarse con Codex CLI bajo consigna adversarial ("buscá el criterio peor evaluado"). El sandbox de Codex en Windows no pudo leer el repo (error de permisos) y el mecanismo se simplificó: el revisor independiente del ADR es Federico, que lo lee completo antes del checkpoint. Cambió el revisor, no el principio — y el cambio de mecanismo quedó documentado en el ADR mismo.

**Cómo aplicarlo.** Para cada entregable importante, definir quién lo revisa *antes* de producirlo y que sea alguien distinto de quien lo escribió. Si el revisor es un modelo, darle una consigna que lo empuje a objetar (pedir "buscá el error" rinde más que "¿está bien?"). Documentar la revisión junto al entregable, no en un chat que se pierde. Y si la herramienta de revisión falla, se degrada a un revisor más simple — no se saltea la revisión.

---

## 3. Enrutamiento por costo/capacidad

**Qué es.** Cada tarea va a la herramienta más barata que la resuelve bien. El modelo caro se reserva para lo ambiguo y de alto apalancamiento (descubrimiento, arquitectura, criterio, revisión); lo ya bien especificado (boilerplate, refactors chicos, tests repetitivos) baja a modelos baratos o gratuitos. No es tacañería: es asignar capacidad de razonamiento donde cambia el resultado.

**Caso real (2026-07-06).** La ventana de suscripción de Fable cierra el 2026-07-07. Federico reordenó la Fase 2 para que los dos días de mayor ambigüedad (Día 1 descubrimiento, Día 2 arquitectura) salgan con Fable antes del cierre, y los días de ejecución sobre spec ya escrita (Día 3 scaffolding, Día 4 demo) queden para Sonnet/Aider. La restricción de costo definió el cronograma — se movió el trabajo caro hacia la ventana barata, no al revés.

**Cómo aplicarlo.** Antes de asignar una tarea, preguntar: ¿esto necesita criterio o ya está especificado? Si ya está especificado, mandarlo al modelo más barato que lo resuelve bien. Señales de mal enrutamiento: el modelo caro escribiendo código mecánico, o el barato tomando decisiones de arquitectura.

---

*Próximos principios esperados en este proyecto (se documentan cuando aparezcan en la práctica): paralelización, aislamiento de fallas.*
