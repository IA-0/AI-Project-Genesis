"""Rol Analista Funcional: genera 01_preguntas.md (US-02) y 10_spec_funcional.md (US-04)."""

from __future__ import annotations

from atlas.config import AtlasConfig
from atlas.roles.common import call_role, strip_stray_frontmatter

EJES = [
    "Actores y roles",
    "Alcance y caso de éxito",
    "Datos y entidades",
    "Reglas de negocio",
    "Restricciones e integraciones",
    "Prioridad",
]

PREGUNTAS_SYSTEM = f"""Sos el Analista Funcional de Atlas, un pipeline que convierte una frase de negocio
en documentación de ingeniería. Tu tarea acá es generar el motor de preguntas mínimas (§3 de la spec
funcional de Atlas).

Principios de diseño, sin excepción:
- One-shot: una sola ronda de preguntas, no hay ida y vuelta.
- Minimalidad por costo de omisión: una pregunta entra solo si su no-respuesta deja un artefacto
  posterior incompleto o apoyado en un supuesto de riesgo alto. Si no desbloquea nada, no se pregunta.
- Cap duro de 10 preguntas. Lo esperable son 6 a 8.
- Toda pregunta lleva un supuesto default razonable, para que el pipeline nunca se bloquee.
- Taxonomía fija de 6 ejes, usá cada uno donde aplique (no hace falta una pregunta por eje):
  {", ".join(EJES)}.

Formato de salida OBLIGATORIO — devolvé SOLO el cuerpo Markdown, sin frontmatter YAML, sin
delimitadores ---, sin texto antes o después. Una sección por pregunta, en este formato exacto:

## P1 — <eje>
- **Pregunta:** <la pregunta>
- **Desbloquea:** <qué artefacto o decisión posterior desbloquea>
- **Supuesto default:** <la respuesta que se asume si el usuario no contesta>
- **Riesgo:** <Alto|Medio|Bajo>
- **Respuesta:**

(la línea "Respuesta:" queda vacía a propósito — la completa el usuario). Seguí con ## P2, ## P3, etc.
No agregues ninguna sección fuera de este patrón."""

SPEC_SYSTEM = """Sos el Analista Funcional de Atlas. Con las respuestas ya consolidadas (o los supuestos
adoptados donde no hubo respuesta), generá la especificación funcional del sistema pedido (US-04).

Reglas:
- Trazabilidad (RN-3): cada historia de usuario cita entre paréntesis la(s) pregunta(s) que la origina,
  formato "(origen: P2, P4)". Cualquier regla de negocio relevante también puede citar su origen.
- Las restricciones e integraciones relevadas (ej. sin migración de datos, single/multi-tenant, canal de
  integración) van dentro de "Reglas de negocio" — son reglas del sistema tanto como las de dominio.
- Historias en formato estándar "Como…, quiero…, para…" con prioridad (Must/Should/Could) y criterios
  de aceptación (CA) verificables, no vagos.
- No inventes actores, entidades ni reglas que no se desprendan de las respuestas/supuestos dados.

Formato de salida OBLIGATORIO — devolvé SOLO el cuerpo Markdown, sin frontmatter YAML, con exactamente
estos headings de nivel 2, en este orden:

## Visión
## Actores
## Reglas de negocio
## Historias de usuario
## Supuestos

En "Supuestos", listá cada supuesto no validado que efectivamente usaste, con su riesgo."""


def generate_preguntas(frase: str, config: AtlasConfig, feedback: str | None = None) -> tuple[str, str]:
    route = config.route_for("analista")
    user = f'Frase de negocio: "{frase}"'
    if feedback:
        user += (
            "\n\nTu intento anterior no pasó el validador estructural. Corregí exactamente esto "
            f"y volvé a generar el documento completo:\n{feedback}"
        )
    text, model_used, _degraded = call_role(route, config, PREGUNTAS_SYSTEM, user)
    return strip_stray_frontmatter(text), model_used


def generate_spec(respuestas_body: str, config: AtlasConfig, feedback: str | None = None) -> tuple[str, str]:
    route = config.route_for("analista")
    user = f"Respuestas consolidadas:\n\n{respuestas_body}"
    if feedback:
        user += (
            "\n\nTu intento anterior no pasó el validador estructural. Corregí exactamente esto "
            f"y volvé a generar el documento completo:\n{feedback}"
        )
    text, model_used, _degraded = call_role(route, config, SPEC_SYSTEM, user)
    return strip_stray_frontmatter(text), model_used
