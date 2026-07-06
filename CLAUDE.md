# CLAUDE.md

Este archivo se lee automáticamente al arrancar cualquier sesión de Claude Code en este repositorio. Es el punto de entrada, no el contenido.

## Primer paso, siempre

1. Leé `docs/prompts/MASTER_PROMPT.md` completo antes de hacer nada.
2. Confirmá en voz alta (una línea) que entendiste `<execution_mode>` y `<tutor_mode>`.
3. Seguí con `<next_action>` tal como está definido ahí.

## Modelo

Este proyecto se diseñó para correr con Fable en las fases de mayor ambigüedad (Fase 1 Genesis, Día 1 y Día 2 de Atlas: descubrimiento y arquitectura). Verificá con `/status` que el modelo activo sea el esperado antes de arrancar cada fase. No cambies de modelo a mitad de una tarea — hacelo solo en el cierre de una fase, después del commit.

## Regla de ramas (obligatoria para todos los agentes de la flota)

- Nadie commitea directo a `main`.
- Cada agente (Claude Code, Codex CLI, Aider, Antigravity CLI) trabaja en su propia rama: `agent/claude`, `agent/codex`, `agent/aider`, `agent/antigravity`.
- Un PR a `main` necesita revisión de al menos otro agente distinto del que lo escribió (verificación cruzada) antes de mergear.
- Si dos agentes corren en paralelo sobre el mismo archivo, el que termina segundo hace `git pull --rebase` sobre `main` antes de abrir su PR, no fuerza el push.

## Credenciales

- Nunca pegar un PAT o API key con permisos de cuenta completa. Generá tokens con scope acotado al repo (`repo` scope mínimo, no `admin:org` ni similares).
- Ningún archivo de configuración con tokens en texto plano se commitea. Verificá `.gitignore` antes de crear cualquier archivo `.env`, `settings.json` local o config de MCP con credenciales embebidas.
- Si un comando requiere pegar un secreto, es un punto de pausa obligatorio para Federico (ver `<execution_mode>`), no algo que se automatiza sin mirar.

## Patrón de costo (aplica `<ai_fleet>` en la práctica)

Fable escribe planes, specs, ADRs y decisiones de arquitectura como archivos committeados. La ejecución de tareas ya bien definidas (boilerplate, refactors chicos, tests repetitivos) se delega a Sonnet, Codex CLI, Aider o Antigravity CLI según `<ai_fleet>`. Fable no debería estar escribiendo código mecánico que otro modelo resuelve igual de bien y más barato.
