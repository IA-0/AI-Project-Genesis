# AI_FLEET_SETUP

Estado real de la flota de agentes por entorno. Se actualiza cada vez que se instala, verifica o descarta una herramienta. Complementa la tabla `<ai_fleet>` del master prompt (que describe el plan; esto describe lo que de verdad está andando).

## Entorno: federicopc (Windows 11, usuario `feder`)

Última actualización: 2026-07-06.

| Herramienta | Estado | Detalle |
|---|---|---|
| **Claude Code (Fable)** | ✅ Verificado | Operando sobre el repo en rama `agent/claude`; commits y push funcionando. Ventana de suscripción de Fable cierra el 2026-07-07 — después queda por créditos. |
| **gh CLI** | ✅ Verificado | Autenticado con dos cuentas (`IA-0` activa, `federicoramos67`). Scopes acotados: `repo`, `workflow`, `gist`, `read:org`. |
| **Aider** | ⏳ Instalado (v0.86.2), pendiente de API key | Instalación vía `aider-install`, en PATH (`~/.local/bin`). Falta `GROQ_API_KEY` (o `DEEPSEEK_API_KEY`) en el entorno para verificarlo con un commit de prueba en `agent/aider`. |
| **Codex CLI** | ⚠️ Descartado del flujo obligatorio | v0.142.5 instalada y logueada con ChatGPT, pero su sandbox de Windows no puede crear procesos (`CreateProcessAsUserW failed: 5`) y no lee el repo. Queda como fallback opcional; si se retoma, investigar el flag de sandbox o usarlo pasando contenido por stdin. |
| **Antigravity CLI** | ❌ No instalado | Post-MVP en este entorno. Pendiente elegir cuál de las 4 cuentas de Google usar. |
| **n8n / Docker / Python 3.11 / Node** | ✅ Presentes | Infraestructura de base ya instalada. |

## Configuración de Aider (cuando esté la key)

1. Federico setea la key como variable de usuario (nunca en un archivo del repo):
   `[System.Environment]::SetEnvironmentVariable('GROQ_API_KEY','<key>','User')` y abrir terminal nueva.
2. Verificación: `aider --model groq/llama-3.3-70b-versatile --message "responde ok" --no-git` y después un commit de prueba en rama `agent/aider`.
3. Regla de ramas: Aider commitea automático — configurarlo siempre parado en `agent/aider`, nunca en `main`.

## Credenciales — reglas activas

- Ninguna key en archivos del repo. `.gitignore` cubre `.env` y artefactos locales de Aider (`.aider*`).
- Tokens con scope mínimo (`repo`); nada de `admin:org`.
- Pegar un secreto = pausa obligatoria de Federico; los agentes no lo automatizan.

## Entorno: fede-central2 (Debian 13) — pendiente

Replicar este setup vía `git pull` + reinstalación de CLIs. Nada verificado ahí todavía.
