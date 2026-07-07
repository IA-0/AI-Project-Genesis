"""Rol Product Owner: genera 20_backlog.md desde 10_spec_funcional.md (US-06)."""

from __future__ import annotations

from atlas.config import AtlasConfig
from atlas.roles.common import call_role, strip_stray_frontmatter

BACKLOG_SYSTEM = """Sos el Product Owner de Atlas. Convertís las historias de usuario de la spec funcional
en un backlog priorizado y trazable (US-06).

Reglas:
- Cada ítem referencia el HU-id que implementa.
- La prioridad declara su criterio: valor de negocio y dependencias técnicas explícitas.
- El orden es ejecutable: ningún ítem depende de uno que aparece después en la lista.
- RN-2 del pipeline: el Arquitecto que sigue en la cadena SOLO va a leer este backlog, no la spec
  funcional completa. Por eso el backlog tiene que incluir, en una sección "Contexto heredado", las
  reglas de negocio y restricciones (incluyendo restricciones e integraciones) tal como están en la
  spec — sin resumir de más, son la base para que la arquitectura sea consistente con ellas (US-05-CA-3).

Formato de salida OBLIGATORIO — devolvé SOLO el cuerpo Markdown, sin frontmatter YAML, con exactamente
estos headings de nivel 2, en este orden:

## Contexto heredado
## Criterio de priorización
## Items
## Supuestos

En "Contexto heredado" copiá las reglas de negocio (incluidas restricciones) de la spec funcional.
En "Items" cada entrada referencia su HU-id y su prioridad. En "Supuestos" listá los supuestos no
validados que siguen siendo relevantes para priorizar."""


def generate_backlog(spec_body: str, config: AtlasConfig, feedback: str | None = None) -> tuple[str, str]:
    route = config.route_for("po")
    user = f"Especificación funcional:\n\n{spec_body}"
    if feedback:
        user += (
            "\n\nTu intento anterior no pasó el validador estructural. Corregí exactamente esto "
            f"y volvé a generar el documento completo:\n{feedback}"
        )
    text, model_used, _degraded = call_role(route, config, BACKLOG_SYSTEM, user)
    return strip_stray_frontmatter(text), model_used
