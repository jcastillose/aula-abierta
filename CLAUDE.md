# Aula Abierta

Tablero diario de ofertas de empleo en educación escolar, publicado en https://jcastillose.github.io/aula-abierta/. Proyecto hermano de `jcastillose/obra-abierta`.

## Cómo funciona
- Una tarea programada de Claude (Cowork) corre una vez al día con el texto de `prompt-tarea-diaria.md`. Busca ofertas, escribe `cambios.json` y ejecuta `scripts/merge.py`, que produce `data.json` y `runs.json`.
- `scripts/publish.py` sube esos dos archivos por la API de GitHub usando un token guardado fuera del repositorio.
- `index.html` es estático y lee `data.json` al abrirse.

## Reglas para trabajar en este repositorio
- El repositorio es público: no escribir el nombre, teléfono, correo ni referencias de la persona, ni tokens.
- La tarea diaria nunca edita `index.html`, este archivo, el prompt ni los scripts. Esos cambios se hacen aquí, a mano o con Claude Code.
- `prompt-tarea-diaria.md` es la fuente de verdad del prompt. Si se modifica, hay que copiar el texto nuevo a la tarea programada; no se sincroniza solo.
- Los valores de `sector`, `dependencia` y `region` están definidos en `scripts/merge.py` y en `index.html`; si se cambia uno, cambiar ambos.
- Toda la lógica determinista (ids, estados, retiros, orden, bitácora) vive en `scripts/merge.py`. No duplicarla en el prompt.

## Mantenimiento habitual
- Leer las notas recientes de `runs.json` para ver qué fuentes fallan y ajustar la sección "Fuentes" del prompt.
- Probar el script: `python3 scripts/merge.py data.json runs.json cambios.json` sobre copias.
- Publicar a mano: `python3 scripts/publish.py <ruta-token> . data.json runs.json`.
