# Atlas

De una frase de negocio a un repo con especificación funcional, arquitectura y backlog priorizado —
listo para que un agente de código lo tome como input. Pipeline de 3 roles LLM con validación
estructural entre etapas, sin framework de agentes, sin base de datos, sin UI.

## El problema

El gap entre "tengo una idea de negocio" y "algo que un equipo puede construir" es un dolor real de
developers independientes y PyMEs: el cliente tiene la idea, nadie tiene la spec. Atlas automatiza esa
primera pasada — no reemplaza al analista funcional, le da un punto de partida trazable en minutos en
vez de en días.

## Antes / después

**Entra**, por CLI, una sola frase:

> "Quiero un sistema para administrar clínicas veterinarias."

**Sale** un repo Markdown (`workspace/<slug>/out/`):

| Archivo | Contenido |
|---|---|
| `10_spec_funcional.md` | Visión, actores, reglas de negocio, historias de usuario con criterios de aceptación trazables a la pregunta que las origina |
| `20_backlog.md` | Backlog priorizado — cada ítem con valor de negocio y dependencias técnicas explícitas, no solo una etiqueta Must/Should |
| `30_arquitectura.md` | Stack justificado línea por línea, modelo de datos, contratos de API, consistencia explícita con las restricciones relevadas |
| `supuestos.md` | Auditoría de todo lo que se asumió sin confirmar, para revisar con el cliente real antes de construir |

Ejemplo completo ya generado: [`docs/atlas/examples/veterinaria/GOLDEN_CASE.md`](docs/atlas/examples/veterinaria/GOLDEN_CASE.md).

## Cómo correrlo (3 comandos)

```bash
pip install -r requirements.txt
export GROQ_API_KEY="tu-key"     # gratis en https://console.groq.com/keys
python demo.py
```

Esto corre el golden case (clínica veterinaria) de punta a punta y te dice dónde quedó el repo
generado. Para tu propio caso de uso, los mismos 4 pasos que corre `demo.py` por separado:

```bash
python -m atlas init "tu frase de negocio"
python -m atlas questions <slug>   # opcional: respondé en 01_preguntas.md, si no se adoptan defaults
python -m atlas run <slug>
python -m atlas export <slug>
```

Sin `ANTHROPIC_API_KEY` corre igual — modo degradado, todo sobre Groq, marcado en el frontmatter del
artefacto de arquitectura (ver ADR-0004 abajo).

## Arquitectura en 5 líneas

- Pipeline secuencial de 3 roles LLM (Analista Funcional → Product Owner → Arquitecto) con validación
  entre etapas; sin framework de agentes — el filesystem del workspace es el estado ([ADR-0002](docs/adr/ADR-0002.md)).
- Un solo formato de punta a punta: Markdown + frontmatter YAML, legible por humano y validable por
  máquina, sin transformación final ([ADR-0003](docs/adr/ADR-0003.md)).
- Enrutamiento de modelo por rol, no un modelo único: Groq para generación con contrato estricto,
  Claude para el único rol de criterio puro ([ADR-0004](docs/adr/ADR-0004.md)).
- Reintento con el error del validador anexado al prompt (una vez) antes de cortar con un error
  legible — nunca se propaga un artefacto inválido entre roles.
- Orquestador reanudable: una etapa con artefacto válido y sin cambios en su input no se vuelve a
  pagar ni a regenerar.

Detalle completo: [`docs/atlas/ARCHITECTURE.md`](docs/atlas/ARCHITECTURE.md) · spec funcional:
[`docs/atlas/FUNCTIONAL_SPEC.md`](docs/atlas/FUNCTIONAL_SPEC.md) · todos los ADRs en
[`docs/adr/`](docs/adr/).

## Post-MVP

Fuera de alcance a propósito (ver [ADR-0001](docs/adr/ADR-0001.md) y
[`ARCHITECTURE.md` §12](docs/atlas/ARCHITECTURE.md#12-post-mvp) para el detalle completo):
loop de descubrimiento interactivo, UI, multi-tenant, deploy a VPS, casos de uso adicionales más allá
de la veterinaria, gestión de sprints, y una vuelta dedicada al prompt de preguntas del Analista (el
few-shot mejoró historias y backlog, pero no las preguntas mismas).
