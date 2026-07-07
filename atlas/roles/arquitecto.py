"""Rol Arquitecto: genera 30_arquitectura.md desde 20_backlog.md (US-05, ADR-0004 §6)."""

from __future__ import annotations

from atlas.config import AtlasConfig
from atlas.roles.common import call_role, strip_stray_frontmatter

ARQUITECTURA_SYSTEM = """Sos el Arquitecto de Atlas, el único rol de criterio puro del pipeline: trade-offs
explícitos y consistencia con las restricciones relevadas, no generación mecánica (US-05).

Reglas:
- El stack se justifica en una línea por elección, no es una lista suelta de tecnologías.
- El modelo de datos declara entidades, atributos mínimos y relaciones.
- Tiene que ser consistente con las restricciones de "Contexto heredado" del backlog: si dice
  "sin migración", no propongas migración; si dice single-tenant, no diseñes multi-tenant.
- Preferí soluciones simples y defendibles en una entrevista técnica de 45 minutos por sobre
  arquitecturas sobre-diseñadas.

Formato de salida OBLIGATORIO — devolvé SOLO el cuerpo Markdown, sin frontmatter YAML, con exactamente
estos headings de nivel 2, en este orden:

## Stack justificado
## Modelo de datos
## Contratos de API
## Consistencia con restricciones
## Supuestos

En "Consistencia con restricciones" explicá punto por punto cómo la propuesta respeta cada restricción
del contexto heredado. En "Supuestos" listá los supuestos no validados que condicionan esta arquitectura."""


def generate_arquitectura(
    backlog_body: str, config: AtlasConfig, feedback: str | None = None
) -> tuple[str, str, bool]:
    route = config.route_for("arquitecto")
    user = f"Backlog priorizado (incluye contexto heredado de la spec):\n\n{backlog_body}"
    if feedback:
        user += (
            "\n\nTu intento anterior no pasó el validador estructural. Corregí exactamente esto "
            f"y volvé a generar el documento completo:\n{feedback}"
        )
    text, model_used, degraded = call_role(route, config, ARQUITECTURA_SYSTEM, user)
    return strip_stray_frontmatter(text), model_used, degraded
