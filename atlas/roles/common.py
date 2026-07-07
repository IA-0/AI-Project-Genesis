"""Cliente LLM mínimo: un rol conoce un provider/model por config, no un SDK concreto (ADR-0004)."""

from __future__ import annotations

from atlas.config import AtlasConfig, RoleRoute


class RoleError(Exception):
    """El rol no pudo completarse (sin API key disponible ni fallback, o error del proveedor)."""


def _api_key_for(provider: str, config: AtlasConfig) -> str | None:
    if provider == "groq":
        return config.groq_api_key
    if provider == "anthropic":
        return config.anthropic_api_key
    raise RoleError(f"proveedor desconocido: {provider}")


def _complete(provider: str, model: str, api_key: str, system: str, user: str) -> str:
    if provider == "groq":
        from groq import Groq

        client = Groq(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            temperature=0.3,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content or ""

    if provider == "anthropic":
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)
        resp = client.messages.create(
            model=model,
            max_tokens=8192,
            temperature=0.3,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(block.text for block in resp.content if block.type == "text")

    raise RoleError(f"proveedor desconocido: {provider}")


def call_role(route: RoleRoute, config: AtlasConfig, system: str, user: str) -> tuple[str, str, bool]:
    """Llama al proveedor primario del rol; si no hay key, cae al fallback (modo degradado, ADR-0004).

    Devuelve (respuesta, "provider/model" efectivamente usado, degraded).
    """
    primary_key = _api_key_for(route.provider, config)
    if primary_key:
        text = _complete(route.provider, route.model, primary_key, system, user)
        return text, f"{route.provider}/{route.model}", False

    if not route.fallback_provider or not route.fallback_model:
        raise RoleError(
            f"falta la API key para {route.provider} y este rol no tiene fallback configurado en atlas.toml"
        )

    fallback_key = _api_key_for(route.fallback_provider, config)
    if not fallback_key:
        raise RoleError(
            f"falta la API key para {route.provider} y también para su fallback {route.fallback_provider}"
        )

    text = _complete(route.fallback_provider, route.fallback_model, fallback_key, system, user)
    return text, f"{route.fallback_provider}/{route.fallback_model}", True


def strip_stray_frontmatter(text: str) -> str:
    """Defensa contra un LLM que ignore la instrucción y devuelva su propio '---' YAML."""
    stripped = text.strip()
    if stripped.startswith("---"):
        parts = stripped.split("---", 2)
        if len(parts) == 3:
            return parts[2].strip()
    return stripped
