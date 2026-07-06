# ORCHESTRATION_PLAYBOOK

Principios de orquestación multi-agente aprendidos en este proyecto. Cada entrada se agrega en el momento en que el principio aparece en la práctica, con el ejemplo concreto que lo disparó. El objetivo es que Federico pueda rearmar este circuito en cualquier proyecto futuro sin asistencia.

Formato de cada entrada: **qué es** (2-3 líneas), **el caso real que lo disparó acá**, **cómo aplicarlo de nuevo**.

---

## 1. El repo como memoria compartida

**Qué es.** Los agentes no comparten contexto entre sí: cada sesión de Claude Code, Codex o Aider arranca sabiendo solo lo que hay en el repo. Todo lo que vive únicamente en un chat (una decisión, un brief, un plan) es invisible para el resto de la flota — y para vos mismo en otra máquina. El commit es el mensaje; si no está commiteado, para el circuito no existe.

**Caso real (2026-07-06).** El MASTER_PROMPT v3 da por existente la definición de Atlas ("PROJECT_BRIEF.md — ya existe") porque se escribió en sesiones anteriores de chat. Pero esas versiones nunca se commitearon: al retomar el proyecto desde federicopc, ni el repo, ni el remoto, ni ningún archivo local contenían qué es Atlas. La Fase 1 entera quedó bloqueada esperando que un humano recupere información que un `git pull` debería haber traído.

**Cómo aplicarlo.** Al cerrar cualquier sesión de trabajo con un agente, preguntarse: ¿lo que se decidió acá está en un archivo commiteado y pusheado? Si la respuesta es no, la próxima sesión (o el próximo agente, o la otra máquina) arranca de cero. Los entregables no son las conversaciones: son los commits.

---

*Próximos principios esperados en este proyecto (se documentan cuando aparezcan en la práctica): enrutamiento por costo/capacidad, verificación cruzada, paralelización, aislamiento de fallas.*
