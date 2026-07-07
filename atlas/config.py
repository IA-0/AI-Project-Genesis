"""Config de Atlas: routing por rol (atlas.toml) + credenciales (solo env, ver ARCHITECTURE.md §9).

Excepción documentada (corrección de Federico sobre S-D2-2): ANTHROPIC_API_KEY no se lee
de una variable de entorno de usuario porque choca con la facturación de Claude Code en esta
máquina. Se lee de un .env local (python-dotenv) que nunca se commitea (ver .gitignore).
GROQ_API_KEY sí es una variable de entorno real del sistema, sin ese conflicto.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
ATLAS_TOML_DEFAULT = REPO_ROOT / "atlas.toml"


@dataclass(frozen=True)
class RoleRoute:
    provider: str
    model: str
    fallback_provider: str | None = None
    fallback_model: str | None = None


@dataclass(frozen=True)
class Limits:
    max_preguntas: int
    max_reintentos: int


@dataclass(frozen=True)
class AtlasConfig:
    roles: dict[str, RoleRoute]
    limits: Limits
    groq_api_key: str | None = field(repr=False, default=None)
    anthropic_api_key: str | None = field(repr=False, default=None)

    @property
    def degraded_mode(self) -> bool:
        return not self.anthropic_api_key

    def route_for(self, role: str) -> RoleRoute:
        return self.roles[role]


def load_config(toml_path: Path | None = None) -> AtlasConfig:
    load_dotenv(REPO_ROOT / ".env")

    path = toml_path or ATLAS_TOML_DEFAULT
    with open(path, "rb") as f:
        data = tomllib.load(f)

    roles = {
        name: RoleRoute(
            provider=cfg["provider"],
            model=cfg["model"],
            fallback_provider=cfg.get("fallback_provider"),
            fallback_model=cfg.get("fallback_model"),
        )
        for name, cfg in data["roles"].items()
    }
    limits = Limits(
        max_preguntas=data["limits"]["max_preguntas"],
        max_reintentos=data["limits"]["max_reintentos"],
    )
    return AtlasConfig(
        roles=roles,
        limits=limits,
        groq_api_key=os.environ.get("GROQ_API_KEY"),
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
    )
