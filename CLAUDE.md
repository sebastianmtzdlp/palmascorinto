# Palmas 441 · Instrucciones para Claude

Este repositorio es el sitio **palmascorinto.xyz** (GitHub Pages, rama `main`) y el seguimiento de la remodelación del departamento
Palmas 441. Lo opera **Miguel** (capturista, arquitecto en obra); el dueño es **Sebastián**. Tu trabajo, cuando Miguel te pase
sus notas del día, es convertirlas en datos, generar el reporte y publicar.

## Reglas que nunca se rompen
1. **Nada de dinero**: ni presupuestos, costos, precios, anticipos, pagos ni facturas, en ningún archivo publicado. El script rechaza esos textos.
2. **El repo y el sitio son públicos.** No publiques dirección exacta, teléfonos, nombres de trabajadores ni datos personales.
3. **Las notas originales de Miguel NO se publican.** Guárdalas en `notas-privadas/AAAA-MM-DD.md` (está en `.gitignore`).
   En `dia.json` solo va tu resumen limpio.
4. No inventes datos. Si las notas no dicen cuántas personas trabajaron o el avance de un área, pregunta a Miguel o deja el dato igual que el día anterior.
5. Antes de publicar (`git push`), muéstrale a Miguel el resumen de lo que interpretaste y espera su OK.

## Flujo diario (una vez al día)
1. Miguel pega sus notas y suelta las fotos (cada foto con su **pie de foto**; si no lo dice, pregúntale).
2. Guarda las notas tal cual en `notas-privadas/AAAA-MM-DD.md`.
3. Crea la carpeta `diario/AAAA-MM-DD/` con las fotos (JPG) y un `dia.json` (formato abajo).
4. Corre `python3 tools/build_report.py` (comprime fotos, valida, genera el PDF de la semana y actualiza `data/site.json` y `data/entries.json`).
5. Revisa el PDF (`media/reportes/Reporte-Palmas441-semana-NN.pdf`): que no se corte texto y que los números cuadren con las notas.
6. Muestra el resumen a Miguel; con su OK: `git add -A && git commit -m "Avance AAAA-MM-DD" && git push`.

Requisitos del equipo: `pip install pillow playwright && playwright install chromium`.

## Formato de `diario/AAAA-MM-DD/dia.json`
```json
{
  "fecha": "2026-11-21",
  "resumen": "Una o dos frases sobre lo que se hizo hoy.",
  "personal": {"Albañilería": 3, "Electricidad": 2, "Ayudantes": 2, "Supervisión": 1},
  "areas": {
    "Cocina": {"pct": 45, "nota": "Muro retirado, ductos listos. Sigue el piso."}
  },
  "atencion": "Solo si hay algo que requiera una decisión o riesgo para la fecha; si no, cadena vacía.",
  "proxima": ["Nivelar el piso de la cocina.", "Instalar el tablero eléctrico."],
  "fotos": [{"archivo": "cocina-muro.jpg", "pie": "Cocina, muro retirado", "area": "Cocina"}]
}
```
- `personal`: personas que hubo ese día por especialidad (nombres exactos de `data/obra.json`). Los días sin registro cuentan como 0.
- `areas`: **solo las áreas que cambiaron ese día**, con su porcentaje **acumulado** (0-100), no el incremento. Las demás conservan su último valor.
- `atencion`: la deduces tú de las notas (decisiones pendientes, materiales que faltan, riesgos para la fecha, clima, permisos). Es lo que aparece en el recuadro "Atención". Redáctalo en una frase clara, para un cliente no técnico y sin dinero.
- `proxima`: de 3 a 6 puntos para la siguiente semana, según las notas.
- Un día por carpeta. Lunes a sábado; no hay domingos.
- Las fotos van en la misma carpeta; cada una con `pie` obligatorio. Si es HEIC, conviértela a JPG.

## Datos del proyecto: `data/obra.json`
Fechas (`inicio` siempre lunes, `fecha_pactada`, `entrega_estimada`), `plan_acumulado` (avance planeado acumulado por semana,
con un valor por semana de 0 a `semanas`), áreas con su peso, especialidades, fases por semana y `personal_planeado_por_dia` (opcional).
**El plan, los pesos y las fases son provisionales** hasta que Sebastián entregue el plan real: no los cambies sin que él o Miguel lo pidan.
`entrega_estimada` sí puedes proponerla a Miguel cuando el avance real se aparte del plan; cámbiala solo con su confirmación.

## Cómo se calcula el reporte
- Avance general = promedio ponderado (por `peso`) del último porcentaje de cada área.
- Semáforo de fecha: dentro de fecha si el real va a ≤2 puntos del plan; ligero retraso hasta 8 puntos; con retraso si es más.
- Se genera un reporte por semana (`--semana N` para una anterior). Diseño: azul marino y cobre, 3 páginas.
- `ejemplo/` contiene datos de muestra para probar el script (`python3 tools/build_report.py --root ejemplo --salida /tmp/prueba`). No se publican.

## Estructura
```
data/obra.json          configuración del proyecto
diario/AAAA-MM-DD/      dia.json + fotos de cada día
notas-privadas/         notas originales (no se suben a GitHub)
media/reportes/         PDFs generados
data/site.json          (generado) fases, fechas y reportes para el sitio
data/entries.json       (generado) registros y fotos que muestra el sitio
tools/build_report.py   generador
index.html app.js styles.css project.js   sitio (presentación tipo preventa)
```
`project.js` guarda el contenido de la parte de preventa (galería, unidades, contacto). No lo cambies sin que Sebastián lo pida.
