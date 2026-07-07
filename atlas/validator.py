"""Contratos entre roles: frontmatter YAML (pydantic) + headings obligatorios por tipo (ADR-0003, §5).

Diseño: el frontmatter lo arma siempre el código (`assemble`), nunca el LLM — es la parte
del contrato que tiene que ser exacta, y un LLM generándola a mano es una fuente de errores
que el validador tendría que atajar por las malas. El LLM solo escribe el cuerpo Markdown.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError


class TipoArtefacto(str, Enum):
    PREGUNTAS = "preguntas"
    RESPUESTAS = "respuestas"
    SPEC_FUNCIONAL = "spec_funcional"
    BACKLOG = "backlog"
    ARQUITECTURA = "arquitectura"


class InputRef(BaseModel):
    path: str
    sha256: str


class Supuesto(BaseModel):
    pregunta_id: str
    texto: str


class Frontmatter(BaseModel):
    tipo: TipoArtefacto
    schema_version: int = 1
    role: str
    model: str
    inputs: list[InputRef] = Field(default_factory=list)
    assumptions: list[Supuesto] = Field(default_factory=list)
    modo_degradado: bool = False


# Headings obligatorios por tipo (§5 de ARCHITECTURE.md). "preguntas" se valida aparte
# porque su estructura es por-pregunta, no por heading fijo (ver check_preguntas_body).
REQUIRED_HEADINGS: dict[TipoArtefacto, list[str]] = {
    TipoArtefacto.RESPUESTAS: ["Respuestas", "Supuestos adoptados"],
    TipoArtefacto.SPEC_FUNCIONAL: [
        "Visión",
        "Actores",
        "Reglas de negocio",
        "Historias de usuario",
        "Supuestos",
    ],
    TipoArtefacto.BACKLOG: ["Criterio de priorización", "Items", "Supuestos"],
    TipoArtefacto.ARQUITECTURA: [
        "Stack justificado",
        "Modelo de datos",
        "Contratos de API",
        "Consistencia con restricciones",
        "Supuestos",
    ],
}

# Los 6 campos del contrato de cada pregunta (§3 de la spec).
REQUIRED_PREGUNTA_FIELDS = [
    "Pregunta",
    "Desbloquea",
    "Supuesto default",
    "Riesgo",
    "Respuesta",
]

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    frontmatter: Frontmatter | None = None
    body: str = ""


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_frontmatter(text: str) -> tuple[str, str] | None:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    return m.group(1), m.group(2)


def check_headings(tipo: TipoArtefacto, body: str) -> list[str]:
    errors = []
    heading_lines = [
        re.sub(r"^#+\s*", "", line).strip().lower()
        for line in body.splitlines()
        if line.strip().startswith("#")
    ]
    for required in REQUIRED_HEADINGS[tipo]:
        if not any(required.lower() in h for h in heading_lines):
            errors.append(f'falta la sección obligatoria "{required}"')
    return errors


def check_preguntas_body(body: str, max_preguntas: int) -> list[str]:
    errors = []
    blocks = re.split(r"(?m)^##\s*P(\d+)", body)
    # re.split con grupo de captura intercala texto-antes, id, texto-bloque, id, texto-bloque...
    ids = blocks[1::2]
    contents = blocks[2::2]
    if not ids:
        return ['no se encontró ninguna pregunta ("## P1", "## P2", ...)']
    if len(ids) > max_preguntas:
        errors.append(f"hay {len(ids)} preguntas, el máximo permitido es {max_preguntas} (RN-5)")
    for pid, content in zip(ids, contents):
        for req_field in REQUIRED_PREGUNTA_FIELDS:
            if req_field.lower() not in content.lower():
                errors.append(f'P{pid}: falta el campo "{req_field}"')
    return errors


def validate_artifact(tipo: TipoArtefacto, text: str, max_preguntas: int = 10) -> ValidationResult:
    split = split_frontmatter(text)
    if split is None:
        return ValidationResult(ok=False, errors=["el artefacto no tiene frontmatter YAML delimitado por ---"])
    raw_fm, body = split

    try:
        fm_data = yaml.safe_load(raw_fm) or {}
    except yaml.YAMLError as e:
        return ValidationResult(ok=False, errors=[f"frontmatter YAML inválido: {e}"])

    try:
        frontmatter = Frontmatter.model_validate(fm_data)
    except ValidationError as e:
        return ValidationResult(ok=False, errors=[str(e)], body=body)

    if frontmatter.tipo != tipo:
        return ValidationResult(
            ok=False,
            errors=[f'tipo declarado "{frontmatter.tipo.value}" no coincide con el esperado "{tipo.value}"'],
            frontmatter=frontmatter,
            body=body,
        )

    if tipo == TipoArtefacto.PREGUNTAS:
        errors = check_preguntas_body(body, max_preguntas)
    else:
        errors = check_headings(tipo, body)

    return ValidationResult(ok=not errors, errors=errors, frontmatter=frontmatter, body=body)


def assemble(
    tipo: TipoArtefacto,
    role: str,
    model: str,
    body: str,
    inputs: list[InputRef] | None = None,
    assumptions: list[Supuesto] | None = None,
    modo_degradado: bool = False,
    schema_version: int = 1,
) -> str:
    """Arma el artefacto final: frontmatter determinístico + cuerpo (del LLM o generado)."""
    fm = Frontmatter(
        tipo=tipo,
        schema_version=schema_version,
        role=role,
        model=model,
        inputs=inputs or [],
        assumptions=assumptions or [],
        modo_degradado=modo_degradado,
    )
    fm_yaml = yaml.safe_dump(
        fm.model_dump(mode="json"), sort_keys=False, allow_unicode=True, default_flow_style=False
    )
    body = body.strip("\n")
    return f"---\n{fm_yaml}---\n\n{body}\n"


def input_ref(path: Path, base_dir: Path) -> InputRef:
    return InputRef(path=str(path.relative_to(base_dir)).replace("\\", "/"), sha256=sha256_of(path))
