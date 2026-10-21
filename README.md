# Palmascorinto · Evidencias y avance de obra

Sitio estático para GitHub Pages. No usa base de datos: los datos viven en el propio repositorio.

> La versión con Supabase (login, subida directa de archivos) está guardada en la rama `supabase-version`.

## Estructura

```
index.html          Página principal
app.js              Renderiza el resumen, filtros y registros
styles.css          Estilos
project.js          Datos del proyecto: nombre, fechas, áreas y fases (editar)
data/entries.json   Registros: reportes y evidencias
media/              Fotos, videos y PDF, en subcarpetas por fecha (media/2026-10-19/...)
CNAME               Dominio personalizado
```

## Cómo se agrega un registro

1. Sube los archivos a `media/AAAA-MM-DD/` (por ejemplo `media/2026-10-19/cocina-1.jpg`).
2. Agrega un objeto al arreglo de `data/entries.json`:

```json
{
  "id": "5",
  "kind": "reporte",
  "area": "Cocina",
  "title": "Reporte semanal: cocina",
  "description": "Qué se hizo.",
  "progress_pct": 35,
  "pendientes": "Qué falta",
  "date": "2026-10-19",
  "files": [
    { "name": "cocina-1.jpg", "path": "media/2026-10-19/cocina-1.jpg", "type": "image/jpeg" }
  ]
}
```

- `kind`: `"reporte"` (lleva `progress_pct`) o `"evidencia"` (sin porcentaje).
- `type`: `image/jpeg`, `image/png`, `video/mp4` o `application/pdf`.
- El avance por área toma el reporte más reciente de cada área.

## Fases y áreas

Edita `project.js`: áreas, fechas y el estado de cada fase (`pendiente`, `en curso`, `terminada`).

## Privacidad

El repositorio y el sitio son públicos y no hay login. Lo que se suba a `media/` o a `data/` lo puede ver cualquiera que tenga el enlace, y el historial de Git conserva lo que se borre. No subas direcciones exactas, contratos, costos ni datos personales.

## Publicación y DNS

- GitHub Pages: Settings > Pages > `main` / root, dominio `palmascorinto.xyz`.
- DNS: 4 registros A (`185.199.108.153`, `.109.153`, `.110.153`, `.111.153`) y un CNAME `www` hacia `sebastianmtzdlp.github.io`.
