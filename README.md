# aula-abierta

Tablero diario de ofertas de empleo en educación escolar en las regiones Metropolitana, de Valparaíso y de O'Higgins, publicado en
**https://jcastillose.github.io/aula-abierta/**

Una tarea programada busca ofertas una vez al día, verifica cada aviso abriendo su enlace y actualiza `data.json`. La página lee ese archivo cada vez que alguien la abre.

| Archivo | Qué contiene |
| --- | --- |
| `index.html` | El tablero. Estático. |
| `data.json` | Ofertas vigentes, perfil buscado y fecha de actualización. |
| `runs.json` | Bitácora de cada ejecución. |
| `prompt-tarea-diaria.md` | Instrucciones de la tarea programada. |
| `scripts/merge.py` | Fusión determinista de hallazgos, estados y retiros. |
| `scripts/publish.py` | Publicación por la API de GitHub. |
| `CLAUDE.md` | Guía para mantener el proyecto con Claude Code. |
| `robots.txt` | Pide a los buscadores no indexar el sitio. |

Cargos buscados, por prioridad: dirección; inspectoría general y convivencia escolar; jefatura de UTP y coordinación académica; docencia de Historia, Geografía y Ciencias Sociales.

Una oferta se retira siete días después de vencido su plazo o de cerrada, o tras 30 días sin poder verificarla. Nunca por antigüedad.
