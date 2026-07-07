"""Máquina secuencial de etapas del pipeline: reanudable, con reintento único por etapa (RN-4).

Una etapa está completa si su artefacto existe, valida, y sus inputs no cambiaron desde que se
generó (si cambiaron, se invalida y se regenera — comentario de ejemplo en ARCHITECTURE.md §5).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml

from atlas.config import AtlasConfig
from atlas.roles import analista, arquitecto, po
from atlas.roles.common import RoleError
from atlas.validator import Supuesto, TipoArtefacto, ValidationResult, assemble, input_ref, validate_artifact

WORKSPACE_ROOT_DEFAULT = Path(__file__).resolve().parent.parent / "workspace"

PREGUNTAS_FILE = "01_preguntas.md"
RESPUESTAS_FILE = "02_respuestas.md"
SPEC_FILE = "10_spec_funcional.md"
BACKLOG_FILE = "20_backlog.md"
ARQUITECTURA_FILE = "30_arquitectura.md"
STATE_FILE = "state.yaml"


class WorkspaceExistsError(Exception):
    pass


class StageError(Exception):
    """Una etapa agotó sus reintentos (RN-4) o no pudo llamar al proveedor (sin API key)."""


@dataclass
class StageResult:
    name: str
    status: str  # "ok" | "skipped" | "error"
    path: Path | None = None
    model_used: str | None = None
    detail: str | None = None


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text[:60] or "workspace"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_state(workspace: Path) -> dict:
    return yaml.safe_load((workspace / STATE_FILE).read_text(encoding="utf-8")) or {}


def _save_state(workspace: Path, state: dict) -> None:
    (workspace / STATE_FILE).write_text(
        yaml.safe_dump(state, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )


def _record_stage(workspace: Path, stage: str, **fields) -> None:
    state = _load_state(workspace)
    state.setdefault("etapas", {})[stage] = {"completed_at": _now(), **fields}
    _save_state(workspace, state)


def init_workspace(frase: str, root: Path | None = None, slug: str | None = None, force: bool = False) -> Path:
    if not frase or not frase.strip():
        raise ValueError("la frase de negocio no puede estar vacía (CA-2, US-01)")

    root = root or WORKSPACE_ROOT_DEFAULT
    slug = slug or slugify(frase)
    workspace = root / slug

    if workspace.exists() and not force:
        raise WorkspaceExistsError(
            f'ya existe un workspace en "{workspace}". Usá --force para pisarlo (CA-3, US-01).'
        )

    workspace.mkdir(parents=True, exist_ok=True)
    state = {
        "frase": frase.strip(),
        "slug": slug,
        "created_at": _now(),
        "etapas": {},
    }
    _save_state(workspace, state)
    return workspace


def _is_fresh(workspace: Path, output_name: str, tipo: TipoArtefacto, input_names: list[str], max_preguntas: int) -> ValidationResult | None:
    output_path = workspace / output_name
    if not output_path.exists():
        return None
    result = validate_artifact(tipo, output_path.read_text(encoding="utf-8"), max_preguntas)
    if not result.ok or result.frontmatter is None:
        return None
    recorded = {ir.path: ir.sha256 for ir in result.frontmatter.inputs}
    current = {name: input_ref(workspace / name, workspace).sha256 for name in input_names}
    if recorded != current:
        return None
    return result


def run_questions_stage(workspace: Path, config: AtlasConfig) -> StageResult:
    """T3 — genera 01_preguntas.md a partir de la frase persistida en state.yaml."""
    state = _load_state(workspace)
    frase = state["frase"]
    output_path = workspace / PREGUNTAS_FILE

    fresh = _is_fresh(workspace, PREGUNTAS_FILE, TipoArtefacto.PREGUNTAS, [STATE_FILE], config.limits.max_preguntas)
    if fresh is not None:
        return StageResult("preguntas", "skipped", output_path, detail="ya existe y valida")

    feedback = None
    last_errors: list[str] = []
    for attempt in range(config.limits.max_reintentos + 1):
        try:
            body, model_used = analista.generate_preguntas(frase, config, feedback)
        except RoleError as e:
            return StageResult("preguntas", "error", detail=str(e))

        artifact = assemble(
            TipoArtefacto.PREGUNTAS,
            role="analista",
            model=model_used,
            body=body,
            inputs=[input_ref(workspace / STATE_FILE, workspace)],
        )
        result = validate_artifact(TipoArtefacto.PREGUNTAS, artifact, config.limits.max_preguntas)
        if result.ok:
            output_path.write_text(artifact, encoding="utf-8")
            _record_stage(workspace, "preguntas", status="ok", model=model_used)
            return StageResult("preguntas", "ok", output_path, model_used)

        last_errors = result.errors
        feedback = "\n".join(f"- {e}" for e in last_errors)

    _record_stage(workspace, "preguntas", status="error", errors=last_errors)
    raise StageError(
        f"la etapa 'preguntas' no pasó el validador tras {config.limits.max_reintentos + 1} intentos:\n"
        + "\n".join(f"- {e}" for e in last_errors)
    )


_QUESTION_BLOCK_RE = re.compile(r"(?m)^##\s*P(\d+)\s*(?:—|-)\s*(.+)$")
_FIELD_RE = re.compile(r"\*\*([^:*]+):\*\*\s*(.*)")


def parse_preguntas(body: str) -> list[dict]:
    lines = body.splitlines()
    blocks: list[dict] = []
    current: dict | None = None
    for line in lines:
        m = _QUESTION_BLOCK_RE.match(line)
        if m:
            if current:
                blocks.append(current)
            current = {"id": f"P{m.group(1)}", "eje": m.group(2).strip()}
            continue
        if current is None:
            continue
        fm = _FIELD_RE.search(line)
        if fm:
            key = fm.group(1).strip().lower()
            value = fm.group(2).strip()
            if key.startswith("pregunta"):
                current["pregunta"] = value
            elif key.startswith("desbloquea"):
                current["desbloquea"] = value
            elif key.startswith("supuesto default"):
                current["supuesto_default"] = value
            elif key.startswith("riesgo"):
                current["riesgo"] = value
            elif key.startswith("respuesta"):
                current["respuesta"] = value
    if current:
        blocks.append(current)
    return blocks


def ingest_respuestas(workspace: Path, config: AtlasConfig) -> StageResult:
    """T4 — sin LLM: 01_preguntas.md (editado por Federico) -> 02_respuestas.md (US-03)."""
    output_path = workspace / RESPUESTAS_FILE
    fresh = _is_fresh(workspace, RESPUESTAS_FILE, TipoArtefacto.RESPUESTAS, [PREGUNTAS_FILE], config.limits.max_preguntas)
    if fresh is not None:
        return StageResult("respuestas", "skipped", output_path, detail="ya existe y valida")

    preguntas_path = workspace / PREGUNTAS_FILE
    if not preguntas_path.exists():
        raise StageError(f"falta {PREGUNTAS_FILE}: corré 'atlas questions' antes de 'atlas run'")
    preguntas_body = preguntas_path.read_text(encoding="utf-8")
    result = validate_artifact(TipoArtefacto.PREGUNTAS, preguntas_body, config.limits.max_preguntas)
    if not result.ok:
        raise StageError(f"{PREGUNTAS_FILE} no valida, corré 'atlas questions' de nuevo: {result.errors}")

    preguntas = parse_preguntas(result.body)

    filas = []
    supuestos: list[Supuesto] = []
    supuestos_lines = []
    for p in preguntas:
        respuesta = (p.get("respuesta") or "").strip()
        if respuesta:
            valor, origen = respuesta, "usuario"
        else:
            valor, origen = p.get("supuesto_default", ""), "supuesto_adoptado"
            supuestos.append(Supuesto(pregunta_id=p["id"], texto=valor))
            supuestos_lines.append(
                f'- **{p["id"]}** (riesgo {p.get("riesgo", "?").lower()}, eje {p["eje"]}): '
                f'"{valor}" — sin validar por el usuario.'
            )
        filas.append(f'| {p["id"]} | {p["eje"]} | {p.get("pregunta", "")} | {valor} | {origen} |')

    supuestos_body = "\n".join(supuestos_lines) if supuestos_lines else "Ningún supuesto adoptado — el usuario respondió todas las preguntas."

    body = (
        "## Respuestas\n\n"
        "| id | Eje | Pregunta | Valor | Origen |\n"
        "|---|---|---|---|---|\n" + "\n".join(filas) + "\n\n"
        "## Supuestos adoptados\n\n" + supuestos_body
    )

    artifact = assemble(
        TipoArtefacto.RESPUESTAS,
        role="sistema",
        model="-",
        body=body,
        inputs=[input_ref(preguntas_path, workspace)],
        assumptions=supuestos,
    )
    val = validate_artifact(TipoArtefacto.RESPUESTAS, artifact, config.limits.max_preguntas)
    if not val.ok:
        raise StageError(f"error interno armando {RESPUESTAS_FILE}: {val.errors}")

    output_path.write_text(artifact, encoding="utf-8")
    _record_stage(workspace, "respuestas", status="ok", model="-")
    return StageResult("respuestas", "ok", output_path, "-")


def _run_llm_stage(
    workspace: Path,
    stage_name: str,
    output_name: str,
    tipo: TipoArtefacto,
    input_name: str,
    role_name: str,
    generate_fn,
    config: AtlasConfig,
) -> StageResult:
    output_path = workspace / output_name
    fresh = _is_fresh(workspace, output_name, tipo, [input_name], config.limits.max_preguntas)
    if fresh is not None:
        return StageResult(stage_name, "skipped", output_path, detail="ya existe y valida")

    input_path = workspace / input_name
    input_result = validate_artifact(
        {SPEC_FILE: TipoArtefacto.SPEC_FUNCIONAL, BACKLOG_FILE: TipoArtefacto.BACKLOG, RESPUESTAS_FILE: TipoArtefacto.RESPUESTAS}[input_name],
        input_path.read_text(encoding="utf-8"),
        config.limits.max_preguntas,
    )
    if not input_result.ok:
        raise StageError(f"{input_name} no valida, no se puede continuar: {input_result.errors}")

    upstream_assumptions = input_result.frontmatter.assumptions if input_result.frontmatter else []

    feedback = None
    last_errors: list[str] = []
    degraded = False
    for _attempt in range(config.limits.max_reintentos + 1):
        try:
            if role_name == "arquitecto":
                body, model_used, degraded = generate_fn(input_result.body, config, feedback)
            else:
                body, model_used = generate_fn(input_result.body, config, feedback)
        except RoleError as e:
            return StageResult(stage_name, "error", detail=str(e))

        artifact = assemble(
            tipo,
            role=role_name,
            model=model_used,
            body=body,
            inputs=[input_ref(input_path, workspace)],
            assumptions=upstream_assumptions,
            modo_degradado=degraded,
        )
        result = validate_artifact(tipo, artifact, config.limits.max_preguntas)
        if result.ok:
            output_path.write_text(artifact, encoding="utf-8")
            _record_stage(workspace, stage_name, status="ok", model=model_used, degraded=degraded)
            return StageResult(stage_name, "ok", output_path, model_used)

        last_errors = result.errors
        feedback = "\n".join(f"- {e}" for e in last_errors)

    _record_stage(workspace, stage_name, status="error", errors=last_errors)
    raise StageError(
        f"la etapa '{stage_name}' no pasó el validador tras {config.limits.max_reintentos + 1} intentos:\n"
        + "\n".join(f"- {e}" for e in last_errors)
    )


def run_pipeline(workspace: Path, config: AtlasConfig) -> list[StageResult]:
    """T4-T7: ingesta + Analista (spec) + PO (backlog) + Arquitecto (arquitectura), en orden fijo (RN-1)."""
    results = [ingest_respuestas(workspace, config)]

    results.append(
        _run_llm_stage(
            workspace, "spec_funcional", SPEC_FILE, TipoArtefacto.SPEC_FUNCIONAL,
            RESPUESTAS_FILE, "analista", analista.generate_spec, config,
        )
    )
    results.append(
        _run_llm_stage(
            workspace, "backlog", BACKLOG_FILE, TipoArtefacto.BACKLOG,
            SPEC_FILE, "po", po.generate_backlog, config,
        )
    )
    results.append(
        _run_llm_stage(
            workspace, "arquitectura", ARQUITECTURA_FILE, TipoArtefacto.ARQUITECTURA,
            BACKLOG_FILE, "arquitecto", arquitecto.generate_arquitectura, config,
        )
    )
    return results
