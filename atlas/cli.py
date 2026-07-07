"""CLI: init | questions | run | export (ARCHITECTURE.md §3)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from atlas.config import load_config
from atlas.exporter import ExportError, export_workspace
from atlas.orchestrator import (
    WORKSPACE_ROOT_DEFAULT,
    StageError,
    WorkspaceExistsError,
    init_workspace,
    run_pipeline,
    run_questions_stage,
)


def _workspace_or_error(slug: str) -> Path | None:
    workspace = WORKSPACE_ROOT_DEFAULT / slug
    if not workspace.exists():
        print(f"error: no existe el workspace '{slug}', corré 'atlas init \"<frase>\" --slug {slug}' primero", file=sys.stderr)
        return None
    return workspace


def _cmd_init(args: argparse.Namespace) -> int:
    try:
        workspace = init_workspace(args.frase, slug=args.slug, force=args.force)
    except (ValueError, WorkspaceExistsError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"workspace creado en {workspace}")
    print(f"Ahora corré: atlas questions {workspace.name}")
    return 0


def _cmd_questions(args: argparse.Namespace) -> int:
    workspace = _workspace_or_error(args.slug)
    if workspace is None:
        return 1
    config = load_config()
    try:
        result = run_questions_stage(workspace, config)
    except StageError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"[{result.status}] {result.name} -> {result.path}")
    if result.status == "ok":
        print(f'Editá {result.path} (campo "Respuesta:" por pregunta) y después corré: atlas run {args.slug}')
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    workspace = _workspace_or_error(args.slug)
    if workspace is None:
        return 1
    config = load_config()
    try:
        results = run_pipeline(workspace, config)
    except StageError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    for r in results:
        print(f"[{r.status}] {r.name} -> {r.path or '-'} ({r.model_used or r.detail or ''})")
    print(f"Listo. Para exportar el repo final: atlas export {args.slug}")
    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    workspace = _workspace_or_error(args.slug)
    if workspace is None:
        return 1
    try:
        out_path = export_workspace(workspace)
    except ExportError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"repo exportado en {out_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="atlas", description="Frase de negocio -> repo Markdown listo para un agente de código.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="crea un workspace a partir de una frase de negocio (US-01)")
    p_init.add_argument("frase")
    p_init.add_argument("--slug", default=None, help="nombre del workspace (default: slug de la frase)")
    p_init.add_argument("--force", action="store_true", help="pisa un workspace existente")
    p_init.set_defaults(func=_cmd_init)

    p_questions = sub.add_parser("questions", help="genera el motor de preguntas mínimas (US-02)")
    p_questions.add_argument("slug")
    p_questions.set_defaults(func=_cmd_questions)

    p_run = sub.add_parser("run", help="corre el pipeline: ingesta de respuestas + spec + backlog + arquitectura")
    p_run.add_argument("slug")
    p_run.set_defaults(func=_cmd_run)

    p_export = sub.add_parser("export", help="arma el repo final en workspace/<slug>/out (US-07, US-08)")
    p_export.add_argument("slug")
    p_export.set_defaults(func=_cmd_export)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
