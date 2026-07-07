"""Demo reproducible de Atlas: corre el golden case de punta a punta (frase -> repo exportado).

Requiere GROQ_API_KEY en el entorno (gratis en https://console.groq.com/keys). Sin
ANTHROPIC_API_KEY corre igual, en modo degradado (ADR-0004, todo Groq) — no hace falta
para ver el pipeline funcionando de punta a punta.

Uso:
    python demo.py
"""

from __future__ import annotations

import os

from atlas.config import load_config
from atlas.exporter import export_workspace
from atlas.orchestrator import StageError, init_workspace, run_pipeline, run_questions_stage

FRASE = "Quiero un sistema para administrar clínicas veterinarias."
SLUG = "demo-veterinaria"


def main() -> int:
    if not os.environ.get("GROQ_API_KEY"):
        print("Falta GROQ_API_KEY en el entorno. Conseguí una gratis en https://console.groq.com/keys y corré:")
        print('  export GROQ_API_KEY="tu-key"          (bash/zsh)')
        print('  $env:GROQ_API_KEY = "tu-key"           (PowerShell)')
        return 1

    print(f'Frase de negocio: "{FRASE}"')
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("(sin ANTHROPIC_API_KEY: el rol Arquitecto corre en modo degradado sobre Groq, ADR-0004)")
    print()

    try:
        workspace = init_workspace(FRASE, slug=SLUG, force=True)
        print(f"[1/4] workspace creado en {workspace}")

        config = load_config()

        preguntas = run_questions_stage(workspace, config)
        print(f"[2/4] preguntas generadas -> {preguntas.path}")
        print("      (el golden case corre con cero respuestas: se adoptan todos los supuestos default)")

        for stage in run_pipeline(workspace, config):
            print(f"      [3/4] {stage.name}: {stage.status} ({stage.model_used or stage.detail or ''})")

        out_dir = export_workspace(workspace)
    except (StageError, ValueError) as e:
        print(f"\nerror: {e}")
        return 1

    print(f"[4/4] repo exportado en {out_dir}")
    print("\nMirá el resultado:")
    print(f"  {out_dir / '10_spec_funcional.md'}")
    print(f"  {out_dir / '20_backlog.md'}")
    print(f"  {out_dir / '30_arquitectura.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
