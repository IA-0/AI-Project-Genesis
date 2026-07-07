"""Exporter: arma out/ con estructura estándar + README, git init + commit inicial (US-07, US-08)."""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

from atlas.orchestrator import (
    ARQUITECTURA_FILE,
    BACKLOG_FILE,
    PREGUNTAS_FILE,
    RESPUESTAS_FILE,
    SPEC_FILE,
    parse_preguntas,
)
from atlas.validator import TipoArtefacto, validate_artifact

ARTIFACT_FILES = [PREGUNTAS_FILE, RESPUESTAS_FILE, SPEC_FILE, BACKLOG_FILE, ARQUITECTURA_FILE]

_TIPO_BY_FILE = {
    PREGUNTAS_FILE: TipoArtefacto.PREGUNTAS,
    RESPUESTAS_FILE: TipoArtefacto.RESPUESTAS,
    SPEC_FILE: TipoArtefacto.SPEC_FUNCIONAL,
    BACKLOG_FILE: TipoArtefacto.BACKLOG,
    ARQUITECTURA_FILE: TipoArtefacto.ARQUITECTURA,
}

README_TEMPLATE = """# {frase}

Repo generado automáticamente por Atlas a partir de la frase de negocio de arriba.
Cada archivo es un artefacto validado del pipeline (Analista Funcional → Product Owner → Arquitecto);
listo para que un agente de código lo tome como input.

## Estructura

- `01_preguntas.md` — preguntas mínimas generadas y respondidas (o supuesto adoptado).
- `02_respuestas.md` — respuestas consolidadas + supuestos adoptados.
- `10_spec_funcional.md` — especificación funcional: visión, actores, reglas de negocio, historias de
  usuario con criterios de aceptación.
- `20_backlog.md` — backlog priorizado y trazable a las historias.
- `30_arquitectura.md` — stack justificado, modelo de datos, contratos de API, consistencia con
  restricciones.
- `supuestos.md` — auditoría de todos los supuestos no validados: qué revisar con el cliente real
  antes de construir.

Generado el {fecha}.
"""


class ExportError(Exception):
    pass


def _force_remove_readonly(func, path, _exc_info):
    """git deja objetos read-only; en Windows eso rompe rmtree si no se limpia el atributo."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _rmtree_retrying(path: Path, attempts: int = 6, delay: float = 0.5) -> None:
    """OneDrive/antivirus pueden retener un handle sobre out/.git por un instante tras el commit
    anterior; unos reintentos cortos alcanzan sin tener que pedirle nada al usuario."""
    for attempt in range(attempts):
        try:
            shutil.rmtree(path, onerror=_force_remove_readonly)
            return
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(delay)


def _read_validated(workspace: Path, filename: str) -> tuple[str, object]:
    path = workspace / filename
    if not path.exists():
        raise ExportError(f"falta {filename}: corré 'atlas run' antes de exportar")
    result = validate_artifact(_TIPO_BY_FILE[filename], path.read_text(encoding="utf-8"))
    if not result.ok:
        raise ExportError(f"{filename} no valida, no se puede exportar: {result.errors}")
    return path.read_text(encoding="utf-8"), result


def _build_supuestos_md(workspace: Path) -> str:
    _, preguntas_result = _read_validated(workspace, PREGUNTAS_FILE)
    preguntas_by_id = {p["id"]: p for p in parse_preguntas(preguntas_result.body)}

    affected: dict[str, set[str]] = {}
    for filename in [RESPUESTAS_FILE, SPEC_FILE, BACKLOG_FILE, ARQUITECTURA_FILE]:
        path = workspace / filename
        if not path.exists():
            continue
        result = validate_artifact(_TIPO_BY_FILE[filename], path.read_text(encoding="utf-8"))
        if result.frontmatter:
            for a in result.frontmatter.assumptions:
                affected.setdefault(a.pregunta_id, set()).add(filename)

    lines = ["## Supuestos no validados (US-08)", ""]
    if not affected:
        lines.append("No hay supuestos no validados: el usuario respondió todas las preguntas.")
    else:
        lines.append("| id | Supuesto | Riesgo | Artefactos afectados |")
        lines.append("|---|---|---|---|")
        for pid in sorted(affected, key=lambda x: int(x[1:])):
            p = preguntas_by_id.get(pid, {})
            artefactos = ", ".join(sorted(affected[pid]))
            lines.append(f'| {pid} | {p.get("supuesto_default", "?")} | {p.get("riesgo", "?")} | {artefactos} |')
    return "\n".join(lines) + "\n"


def export_workspace(workspace: Path) -> Path:
    for filename in ARTIFACT_FILES:
        _read_validated(workspace, filename)

    out_dir = workspace / "out"
    if out_dir.exists():
        _rmtree_retrying(out_dir)
    out_dir.mkdir(parents=True)

    for filename in ARTIFACT_FILES:
        shutil.copyfile(workspace / filename, out_dir / filename)

    (out_dir / "supuestos.md").write_text(_build_supuestos_md(workspace), encoding="utf-8")

    state = yaml.safe_load((workspace / "state.yaml").read_text(encoding="utf-8"))
    frase = state.get("frase", workspace.name)
    readme = README_TEMPLATE.format(frase=frase, fecha=datetime.now(timezone.utc).date().isoformat())
    (out_dir / "README.md").write_text(readme, encoding="utf-8")

    subprocess.run(["git", "init", "-q"], cwd=out_dir, check=True)
    subprocess.run(["git", "add", "-A"], cwd=out_dir, check=True)
    subprocess.run(
        ["git", "-c", "user.email=atlas@local", "-c", "user.name=Atlas", "commit", "-q", "-m", "Repo generado por Atlas"],
        cwd=out_dir,
        check=True,
    )

    return out_dir
