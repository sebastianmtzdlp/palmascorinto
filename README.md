# Palmas 441 · palmascorinto.xyz

Sitio estático (GitHub Pages) con la presentación tipo preventa y el seguimiento de la obra.
El diario de obra, los reportes y los datos del sitio se generan con `tools/build_report.py`.

Las instrucciones completas para operar el proyecto (flujo diario, formato de datos y reglas) están en **CLAUDE.md**.

Resumen: Miguel le pasa a Claude sus notas y fotos del día → Claude guarda `diario/AAAA-MM-DD/dia.json`,
corre `python3 tools/build_report.py` y publica con `git push`.
