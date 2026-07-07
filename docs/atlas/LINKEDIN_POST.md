# Borrador — post de LinkedIn (Día 4)

Sin publicar. Es punto de partida para que Federico edite tono y detalles antes de postear.

---

Le di una frase a un pipeline que armé:

"Quiero un sistema para administrar clínicas veterinarias."

En minutos tenía especificación funcional, backlog priorizado y propuesta de arquitectura — cada
historia de usuario trazable a la pregunta que la originó, cada supuesto no validado marcado como tal
en vez de escondido. Nada de esto reemplaza el análisis funcional; le da a un developer independiente
o una PyME un punto de partida real en lugar de una hoja en blanco.

Se llama Atlas y tiene tres decisiones técnicas que me interesa defender, no solo mostrar:

- Enruta cada rol del pipeline al modelo que le corresponde por costo y capacidad: Groq para
  generación con contrato estricto (preguntas, historias, backlog), Claude para el único rol que
  necesita criterio real — la arquitectura.
- Valida la estructura de cada artefacto antes de pasarlo al rol siguiente. Si falla, reintenta una
  vez con el error puntual del validador; si vuelve a fallar, corta con un mensaje legible. Nunca se
  propaga un artefacto roto al siguiente rol.
- Cada trade-off quedó documentado en un ADR antes de escribir código — el material de defensa en una
  entrevista es la traza de decisiones, no el volumen de líneas.

Repo, con el pipeline completo y el caso de uso corriendo de punta a punta:
https://github.com/IA-0/AI-Project-Genesis

---

Notas de producción (no forman parte del post):

- Confirmar que el repo esté en público antes de postear el link.
- Considerá adjuntar 1-2 capturas de `10_spec_funcional.md` o `30_arquitectura.md` — el antes/después
  se entiende mejor viendo el artefacto real que solo leyéndolo.
- Si preferís gancho con pregunta en vez de afirmación ("¿Cuánto tarda hoy tu equipo en pasar de una
  idea a una spec construible?"), es un swap directo de las primeras 2 líneas.
