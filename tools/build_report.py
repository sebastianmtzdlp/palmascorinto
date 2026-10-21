#!/usr/bin/env python3
"""Genera el reporte semanal (PDF azul y cobre) y los datos del sitio a partir del diario.

Uso (desde la raíz del repo):
    python3 tools/build_report.py                 # reporte de la semana del último día registrado
    python3 tools/build_report.py --semana 4      # una semana concreta
    python3 tools/build_report.py --solo-sitio    # solo actualiza data/*.json (sin PDF)
    python3 tools/build_report.py --root ejemplo --salida /tmp/x   # datos de ejemplo

Lee:   <root>/data/obra.json  y  <root>/diario/AAAA-MM-DD/dia.json
Crea:  media/reportes/Reporte-Palmas441-semana-NN.pdf, data/site.json, data/entries.json
Reglas: el reporte NO lleva dinero. El script se niega a publicar textos con cifras de dinero.
"""
import argparse, json, math, re, sys
from datetime import date, timedelta
from pathlib import Path
from string import Template

REPO = Path(__file__).resolve().parent.parent
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
MES3 = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
DIAS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
DIAS_LARGO = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado']
PAL = dict(P='#14263d', ACC='#b87333', ACCDK='#8f5522', INK='#1a2433', MUT='#5a6675', GRID='#e3e8ee', SOFT='#f1f4f8',
           BRD='#dfe5ec', ROWL='#e7ecf1', BARBG='#e6ebf1', PEND='#d9e0e8', TRACK='rgba(255,255,255,.16)', FILL='rgba(20,38,61,.10)',
           spec=['#14263d', '#b87333', '#4f8fb0', '#8c4a2f', '#a9b8c6', '#6b7280', '#3f9a6b', '#e0a526'])
DINERO = re.compile(r'(\$\s?\d|\b\d[\d,\.]*\s?(pesos|mxn|usd|mil pesos)\b|\bpresupuesto|\bcosto|\bprecio|\banticipo|\bcotizaci|\bpag[oó]\b|\bpagar\b|\bfactura)', re.I)


def d_larga(d):
    return f'{d.day} de {MESES[d.month - 1]} de {d.year}'


def d_corta(d):
    return f'{d.day} {MES3[d.month - 1]} {d.year}'


def rango_semana(lun):
    dom = lun + timedelta(days=6)
    if lun.month == dom.month:
        return f'{lun.day} al {dom.day} de {MESES[dom.month - 1]} de {dom.year}'
    return f'{lun.day} de {MESES[lun.month - 1]} al {dom.day} de {MESES[dom.month - 1]} de {dom.year}'


# ---------------------------------------------------------------- datos
def cargar(root):
    obra = json.loads((root / 'data' / 'obra.json').read_text(encoding='utf-8'))
    inicio = date.fromisoformat(obra['inicio'])
    if inicio.weekday() != 0:
        sys.exit('ERROR: "inicio" en obra.json debe ser un lunes.')
    dias = []
    for p in sorted((root / 'diario').glob('*/dia.json')):
        d = json.loads(p.read_text(encoding='utf-8'))
        d['_fecha'] = date.fromisoformat(d['fecha'])
        d['_dir'] = p.parent
        dias.append(d)
    dias.sort(key=lambda d: d['_fecha'])
    return obra, inicio, dias


def validar(obra, dias):
    errores = []
    areas = {a['nombre'] for a in obra['areas']}
    esp = {e['nombre'] for e in obra['especialidades']}
    for d in dias:
        f = d['fecha']
        if d['_fecha'].weekday() == 6:
            errores.append(f'{f}: es domingo; el reporte cubre lunes a sábado.')
        for k in d.get('personal', {}):
            if k not in esp:
                errores.append(f'{f}: especialidad desconocida "{k}" (agrégala en obra.json o corrige el nombre).')
        for k, v in d.get('areas', {}).items():
            if k not in areas:
                errores.append(f'{f}: área desconocida "{k}".')
            elif not 0 <= v.get('pct', -1) <= 100:
                errores.append(f'{f}: porcentaje fuera de 0-100 en "{k}".')
        textos = [d.get('resumen', ''), d.get('atencion', '')] + list(d.get('proxima', [])) \
            + [v.get('nota', '') for v in d.get('areas', {}).values()] + [x.get('pie', '') for x in d.get('fotos', [])]
        for t in textos:
            if t and DINERO.search(t):
                errores.append(f'{f}: el texto parece mencionar dinero ("{t[:60]}…"). Quítalo: los reportes no llevan cifras de dinero.')
        for x in d.get('fotos', []):
            if not x.get('pie', '').strip():
                errores.append(f'{f}: la foto {x.get("archivo")} no tiene pie de foto.')
    if errores:
        print('\n'.join('ERROR: ' + e for e in errores)); sys.exit(1)


def semana_de(inicio, f):
    return (f - inicio).days // 7 + 1


def estado(obra, inicio, dias, semana):
    """Calcula todo lo que necesita el reporte para la semana indicada."""
    areas = obra['areas']; w_tot = sum(a['peso'] for a in areas)
    pct_hasta = {}

    def overall(hasta):
        last = {}
        for d in dias:
            if d['_fecha'] <= hasta:
                for k, v in d.get('areas', {}).items():
                    last[k] = v
        pcts = {a['nombre']: last.get(a['nombre'], {}).get('pct', 0) for a in areas}
        notas = {a['nombre']: last.get(a['nombre'], {}).get('nota', '') for a in areas}
        tot = sum(a['peso'] * pcts[a['nombre']] for a in areas) / w_tot
        return tot, pcts, notas

    lun = inicio + timedelta(days=7 * (semana - 1))
    dom = lun + timedelta(days=6)
    en_sem = [d for d in dias if lun <= d['_fecha'] <= dom]
    if not en_sem:
        sys.exit(f'No hay días registrados en la semana {semana}.')
    ultimo = en_sem[-1]
    ref = ultimo['_fecha']
    real_ahora, pcts, notas = overall(ref)
    curva = [0.0]
    for w in range(1, semana):
        curva.append(overall(inicio + timedelta(days=7 * w - 1))[0])
    frac = (ref.weekday() + 1) / 6
    curva.append(real_ahora)
    plan = obra['plan_acumulado']
    plan_ahora = plan[semana - 1] + (plan[semana] - plan[semana - 1]) * frac if semana < len(plan) else 100
    # personal
    esp = obra['especialidades']
    mat = {e['nombre']: [0] * 6 for e in esp}
    for d in en_sem:
        for k, v in d.get('personal', {}).items():
            mat[k][d['_fecha'].weekday()] = v
    tot = [sum(mat[e['nombre']][i] for e in esp) for i in range(6)]
    registrados = sorted({d['_fecha'].weekday() for d in en_sem})
    promedio = sum(tot[i] for i in registrados) / len(registrados)
    pico = max(tot)
    # fotos
    fotos = []
    for d in reversed(en_sem):
        for x in d.get('fotos', []):
            fotos.append((d, x))
    return dict(semana=semana, lun=lun, dom=dom, ref=ref, ultimo=ultimo, real=real_ahora, plan_ahora=plan_ahora, curva=curva, frac=frac,
                pcts=pcts, notas=notas, mat=mat, tot=tot, promedio=promedio, pico=pico, dia_pico=DIAS_LARGO[tot.index(pico)],
                fotos=fotos)


# ---------------------------------------------------------------- gráficas
def chart1(p, obra, st):
    W, H = 640, 350; l, r, t, b = 42, 18, 34, 40; pw, ph = W - l - r, H - t - b
    n = obra['semanas']
    X = lambda w: l + w / n * pw
    Y = lambda v: t + (1 - v / 100) * ph
    o = [f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica, Arial, sans-serif">']
    for v in (0, 25, 50, 75, 100):
        o.append(f'<line x1="{l}" x2="{W-r}" y1="{Y(v)}" y2="{Y(v)}" stroke="{p["GRID"]}"/><text x="{l-8}" y="{Y(v)+3}" font-size="9" fill="{p["MUT"]}" text-anchor="end">{v}%</text>')
    for w in range(n + 1):
        o.append(f'<text x="{X(w)}" y="{H-b+16}" font-size="9" fill="{p["MUT"]}" text-anchor="middle">{"S"+str(w) if w else "0"}</text>')
    o.append(f'<text x="{l+pw/2}" y="{H-6}" font-size="9" fill="{p["MUT"]}" text-anchor="middle">Semanas de obra</text>')
    d = 'M' + ' L'.join(f'{X(i):.1f},{Y(v):.1f}' for i, v in enumerate(obra['plan_acumulado']))
    o.append(f'<path d="{d}" fill="none" stroke="{p["ACC"]}" stroke-width="2.2" stroke-dasharray="6 4"/>')
    s = st['semana']; xs = [X(i) for i in range(s)] + [X(s - 1 + st['frac'])]
    pts = ' L'.join(f'{x:.1f},{Y(v):.1f}' for x, v in zip(xs, st['curva']))
    o.append(f'<path d="M{xs[0]:.1f},{Y(0)} L{pts} L{xs[-1]:.1f},{Y(0)} Z" fill="{p["FILL"]}"/>')
    o.append(f'<path d="M{pts}" fill="none" stroke="{p["P"]}" stroke-width="3" stroke-linejoin="round"/>')
    for x, v in zip(xs, st['curva']):
        o.append(f'<circle cx="{x:.1f}" cy="{Y(v):.1f}" r="3.6" fill="#fff" stroke="{p["P"]}" stroke-width="2"/>')
    hx = xs[-1]
    o.append(f'<line x1="{hx:.1f}" x2="{hx:.1f}" y1="{t-6}" y2="{Y(0)}" stroke="#c0392b" stroke-dasharray="3 3"/><text x="{hx:.1f}" y="{t-10}" font-size="8.5" fill="#c0392b" text-anchor="middle">Hoy · semana {s}</text>')
    bx = min(hx + 10, W - r - 112)
    by = min(max(Y(st['real']) - 30, t), H - b - 36)
    o.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="112" height="32" rx="5" fill="#fff" stroke="{p["GRID"]}"/><text x="{bx+8:.1f}" y="{by+13:.1f}" font-size="9" fill="{p["P"]}" font-weight="700">Real: {round(st["real"])}%</text><text x="{bx+8:.1f}" y="{by+25:.1f}" font-size="9" fill="{p["ACCDK"]}" font-weight="700">Proyectado: {round(st["plan_ahora"])}%</text>')
    o.append(f'<text x="{X(n)}" y="{Y(100)-7}" font-size="8.5" fill="{p["MUT"]}" text-anchor="end">Entrega · 100%</text>')
    o.append(f'<line x1="{l}" x2="{l+22}" y1="12" y2="12" stroke="{p["P"]}" stroke-width="3"/><text x="{l+28}" y="15" font-size="9" fill="{p["INK"]}">Avance real</text>')
    o.append(f'<line x1="{l+110}" x2="{l+132}" y1="12" y2="12" stroke="{p["ACC"]}" stroke-width="2.2" stroke-dasharray="6 4"/><text x="{l+138}" y="15" font-size="9" fill="{p["INK"]}">Avance proyectado (plan)</text>')
    o.append('</svg>')
    return ''.join(o)


def chart2(p, obra, st):
    esp = obra['especialidades']; plan_p = obra.get('personal_planeado_por_dia')
    W, H = 640, 262; l, r, t, b = 42, 18, 26, 34; pw, ph = W - l - r, H - t - b
    mx = max(st['tot'] + (plan_p or [0])) + 2
    ymax = max(8, int(math.ceil(mx / 4) * 4)); paso = 4 if ymax <= 20 else 8
    Y = lambda v: t + (1 - v / ymax) * ph
    slot = pw / 6; bw = 54
    o = [f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica, Arial, sans-serif">']
    for v in range(0, ymax + 1, paso):
        o.append(f'<line x1="{l}" x2="{W-r}" y1="{Y(v)}" y2="{Y(v)}" stroke="{p["GRID"]}"/><text x="{l-8}" y="{Y(v)+3}" font-size="9" fill="{p["MUT"]}" text-anchor="end">{v}</text>')
    o.append(f'<text x="10" y="{t+ph/2}" font-size="9" fill="{p["MUT"]}" transform="rotate(-90 10 {t+ph/2})" text-anchor="middle">Personas en obra</text>')
    for i, dn in enumerate(DIAS):
        cx = l + slot * i + slot / 2; base = 0
        for k, e in enumerate(esp):
            v = st['mat'][e['nombre']][i]
            if not v:
                continue
            y1 = Y(base + v); h = Y(base) - y1
            o.append(f'<rect x="{cx-bw/2}" y="{y1:.1f}" width="{bw}" height="{h-1:.1f}" rx="2" fill="{p["spec"][k % len(p["spec"])]}"/>')
            if h > 13:
                o.append(f'<text x="{cx}" y="{y1+h/2+3:.1f}" font-size="8.5" fill="#fff" text-anchor="middle" font-weight="700">{v}</text>')
            base += v
        if base:
            o.append(f'<text x="{cx}" y="{Y(base)-6:.1f}" font-size="10" fill="{p["INK"]}" text-anchor="middle" font-weight="700">{base}</text>')
        o.append(f'<text x="{cx}" y="{H-b+16}" font-size="9.5" fill="{p["MUT"]}" text-anchor="middle">{dn}</text>')
    if plan_p:
        pts = [(l + slot * i + slot / 2, Y(v)) for i, v in enumerate(plan_p)]
        o.append('<path d="M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + '" fill="none" stroke="#c0392b" stroke-width="1.6" stroke-dasharray="4 3"/>')
        for x, y in pts:
            o.append(f'<path d="M{x},{y-4.5} L{x+4.5},{y} L{x},{y+4.5} L{x-4.5},{y} Z" fill="#fff" stroke="#c0392b" stroke-width="1.6"/>')
        o.append(f'<line x1="{W-r-150}" x2="{W-r-128}" y1="10" y2="10" stroke="#c0392b" stroke-width="1.6" stroke-dasharray="4 3"/><text x="{W-r-122}" y="13" font-size="9" fill="{p["INK"]}">Personal planeado</text>')
    o.append('</svg>')
    return ''.join(o)


# ---------------------------------------------------------------- HTML
TPL = Template('''<!doctype html><html lang="es"><head><meta charset="utf-8"><style>
@page { size: Letter; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; color: $INK; font-size: 9.6pt; line-height: 1.45; }
.page { width: 216mm; height: 279mm; position: relative; page-break-after: always; overflow: hidden; background: #fff; }
.cover { background: $P; color: #fff; padding: 15mm 18mm 12mm; height: 84mm; position: relative; }
.cover .top { display: flex; justify-content: space-between; font-size: 7.5pt; letter-spacing: .2em; text-transform: uppercase; opacity: .8; }
.cover h1 { font-family: Georgia, serif; font-weight: 400; font-size: 27pt; margin: 14px 0 2px; }
.cover .sub { opacity: .85; font-size: 9.5pt; }
.ring { position: absolute; right: 18mm; top: 25mm; width: 36mm; height: 36mm; }
.ring span { position: absolute; inset: 0; display: grid; place-items: center; text-align: center; font-family: Georgia, serif; font-size: 18pt; line-height: 1; }
.ring small { display: block; font-family: Helvetica, Arial, sans-serif; font-size: 5.8pt; letter-spacing: .12em; text-transform: uppercase; opacity: .85; margin-top: 3px; line-height: 1.3; }
.chips { position: absolute; left: 18mm; bottom: 9mm; display: flex; gap: 7px; }
.chip { border: .6pt solid rgba(255,255,255,.38); border-radius: 6px; padding: 5px 10px; font-size: 7.4pt; white-space: nowrap; }
.chip b { display: block; font-size: 10pt; font-weight: 600; }
.accent { background: $ACC; height: 3px; }
.body { padding: 9mm 18mm 0; }
h2 { font-family: Georgia, serif; font-weight: 400; font-size: 14pt; margin: 0 0 6px; }
.eyebrow { font-size: 7pt; letter-spacing: .2em; text-transform: uppercase; color: $ACC; font-weight: 700; margin-bottom: 2px; }
.lights { display: flex; gap: 10px; margin-bottom: 16px; }
.light { flex: 1; border: .6pt solid $BRD; border-radius: 8px; padding: 10px 12px; display: flex; gap: 9px; }
.dot { flex: none; width: 11px; height: 11px; border-radius: 50%; margin-top: 3px; }
.g { background: #3f9a6b; } .a { background: #e0a526; } .r { background: #c0392b; }
.light b { display: block; font-size: 9.5pt; } .light span { color: $MUT; font-size: 8.4pt; line-height: 1.35; display: block; }
.chartbox { border: .6pt solid $BRD; border-radius: 10px; padding: 12px 14px 8px; margin-bottom: 10px; }
.legend { display: flex; flex-wrap: wrap; gap: 4px 14px; margin: 2px 0 2px 42px; font-size: 8pt; color: $INK; }
.legend i { display: inline-block; width: 9px; height: 9px; border-radius: 2px; margin-right: 5px; vertical-align: -1px; }
table { width: 100%; border-collapse: collapse; font-size: 8.6pt; }
th { font-size: 7pt; letter-spacing: .12em; text-transform: uppercase; color: $MUT; text-align: left; font-weight: 600; padding: 0 6px 5px; border-bottom: .8pt solid $INK; }
td { padding: 6px 6px; border-bottom: .5pt solid $ROWL; vertical-align: middle; }
.c { text-align: center; width: 9mm; } .t { font-weight: 700; width: 14mm; }
td small { display: block; color: $MUT; font-size: 7.4pt; margin-left: 15px; }
.sw { display: inline-block; width: 9px; height: 9px; border-radius: 2px; margin-right: 6px; }
tr.sum td { border-top: .8pt solid $INK; border-bottom: 0; background: $SOFT; font-weight: 700; }
.kpis { display: flex; gap: 8px; margin: 8px 0 14px; }
.kpi { flex: 1; background: $SOFT; border-radius: 8px; padding: 10px 12px; }
.kpi b { font-family: Georgia, serif; font-weight: 400; font-size: 20pt; color: $P; display: block; line-height: 1; }
.kpi small { display: block; font-size: 7.8pt; font-weight: 600; margin: 5px 0 1px; }
.kpi span { font-size: 7.8pt; color: $MUT; line-height: 1.3; display: block; }
.tl { position: relative; margin: 8px 0 16px; } .tl .row { display: flex; height: 22px; gap: 2px; }
.tl .row div { display: grid; place-items: center; font-size: 6.8pt; color: #fff; border-radius: 3px; text-align: center; line-height: 1.1; padding: 0 2px; }
.d { background: $P; } .n { background: $ACC; } .p { background: $PEND; color: $MUT !important; }
.today { position: absolute; top: -6px; bottom: -4px; border-left: 1.5px dashed #c0392b; }
.today::after { content: "Hoy"; position: absolute; top: -9px; left: -8px; font-size: 6.5pt; color: #c0392b; background: #fff; padding: 0 2px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.area { border: .6pt solid $BRD; border-radius: 8px; padding: 8px 11px; }
.area .tt { display: flex; justify-content: space-between; align-items: baseline; } .area .tt b { font-size: 9.2pt; } .area .tt em { font-style: normal; font-size: 7.4pt; color: $MUT; }
.bar { height: 4px; background: $BARBG; border-radius: 2px; margin: 5px 0 4px; overflow: hidden; } .bar i { display: block; height: 100%; background: $P; }
.area p { margin: 0; color: $MUT; font-size: 7.8pt; line-height: 1.3; }
.pics { display: flex; gap: 8px; } .pics figure { flex: 1; margin: 0; } .pics img { width: 100%; height: 50mm; object-fit: cover; border-radius: 8px; display: block; }
figcaption { font-size: 7.2pt; color: $MUT; margin-top: 3px; }
ul.cols { margin: 0; padding-left: 15px; columns: 2; column-gap: 24px; } li { margin-bottom: 4px; font-size: 8.8pt; }
.pgfoot { position: absolute; left: 18mm; right: 18mm; bottom: 8mm; display: flex; justify-content: space-between; font-size: 6.8pt; color: #8a978f; border-top: .5pt solid $BRD; padding-top: 6px; letter-spacing: .1em; text-transform: uppercase; }
.hd { display:flex; justify-content: space-between; align-items: baseline; padding: 11mm 18mm 0; font-size: 7pt; letter-spacing: .2em; text-transform: uppercase; color: $MUT; }
.hd b { color: $P; font-family: Georgia, serif; letter-spacing: 0; font-size: 12pt; text-transform: none; }
</style></head><body>

<div class="page">
  <div class="cover">
    <div class="top"><span>$NOMBRE</span><span>Reporte Nº $SEMANA$ETIQ</span></div>
    <h1>Avance de obra</h1>
    <div class="sub">Semana $SEMANA · $RANGO</div>
    <div class="ring"><svg viewBox="0 0 100 100" width="100%" height="100%"><circle cx="50" cy="50" r="40" fill="none" stroke="$TRACK" stroke-width="8"/><circle cx="50" cy="50" r="40" fill="none" stroke="$ACC" stroke-width="8" stroke-linecap="round" stroke-dasharray="$ARC 251.3" transform="rotate(-90 50 50)"/></svg><span><div>$REAL%<small>Avance<br>de obra</small></div></span></div>
    <div class="chips">
      <div class="chip"><b>$SEMANA de $NSEM</b>semanas</div>
      <div class="chip"><b>$PACTADA</b>fecha pactada</div>
      <div class="chip"><b>$ESTIMADA</b>entrega estimada</div>
      <div class="chip"><b>$RESTAN</b>restantes</div>
    </div>
  </div><div class="accent"></div>
  <div class="body">
    <h2>¿Cómo vamos?</h2>
    <div class="lights">
      <div class="light"><i class="dot $CUMPCLS"></i><div><b>Cumplimiento de fecha: $CUMPTXT</b><span>$CUMPDET</span></div></div>
      <div class="light"><i class="dot $ATCLS"></i><div><b>Atención</b><span>$ATENCION</span></div></div>
    </div>
    <div class="eyebrow">Gráfica 1</div>
    <h2>Avance real contra avance proyectado</h2>
    <div class="chartbox">$CH1</div>
  </div>
  <div class="pgfoot"><span>palmascorinto.xyz</span><span>$PIE · 1 / 3</span></div>
</div>

<div class="page">
  <div class="hd"><span>$NOMBRE · Semana $SEMANA</span><b>Personal en obra</b></div>
  <div class="body" style="padding-top:6mm">
    <div class="eyebrow">Gráfica 2</div>
    <h2>Fuerza de trabajo por día</h2>
    <div class="chartbox">$CH2<div class="legend">$LEGEND</div></div>
    <div class="kpis">
      <div class="kpi"><b>$PICO</b><small>Pico de personal</small><span>El $DIAPICO fue el día con más gente en obra.</span></div>
      <div class="kpi"><b>$PROM</b><small>Promedio por día</small><span>Personas trabajando en obra, según los días registrados.</span></div>
    </div>
    <div class="eyebrow">Detalle</div>
    <h2>¿Quién trabajó cada día, y en qué?</h2>
    <table>
      <tr><th>Especialidad / partida</th>$HDR<th class="c t">Jornales</th></tr>
      $ROWS
    </table>
  </div>
  <div class="pgfoot"><span>palmascorinto.xyz</span><span>$PIE · 2 / 3</span></div>
</div>

<div class="page">
  <div class="hd"><span>$NOMBRE · Semana $SEMANA</span><b>Detalle de la obra</b></div>
  <div class="body" style="padding-top:6mm">
    <h2>Fases de la obra</h2>
    <div class="tl"><div class="row">$FASES</div><div class="today" style="left:$HOY%"></div></div>
    <h2>Avance por área</h2>
    <div class="grid">$AREAS</div>
    $FOTOS
    <h2 style="margin-top:16px">Próxima semana</h2>
    <ul class="cols">$PROXIMA</ul>
  </div>
  <div class="pgfoot"><span>palmascorinto.xyz</span><span>$PIE · 3 / 3</span></div>
</div>
</body></html>''')


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def foto_path(dia, archivo, root):
    for base in (dia['_dir'], root):
        f = (base / archivo).resolve()
        if f.exists():
            return f
    sys.exit(f'ERROR: no encuentro la foto "{archivo}" del día {dia["fecha"]}.')


def construir_html(obra, inicio, st, root, ejemplo):
    p = PAL; esp = obra['especialidades']; semana = st['semana']
    pactada = date.fromisoformat(obra['fecha_pactada']); est = date.fromisoformat(obra['entrega_estimada'])
    restan = (pactada - st['ref']).days
    dif = st['real'] - st['plan_ahora']
    if dif >= -2:
        ctxt, ccls = 'dentro de fecha', 'g'
        cdet = f'Vamos en tiempo, con un real de {round(st["real"])}% frente al {round(st["plan_ahora"])}% planeado.'
    elif dif >= -8:
        ctxt, ccls = 'ligero retraso', 'a'
        cdet = f'Vamos con un ligero retraso: {round(st["real"])}% real frente al {round(st["plan_ahora"])}% planeado.'
    else:
        ctxt, ccls = 'con retraso', 'r'
        cdet = f'Hay retraso frente al plan: {round(st["real"])}% real contra {round(st["plan_ahora"])}% planeado.'
    at = (st['ultimo'].get('atencion') or '').strip()
    legend = ''.join(f'<span><i style="background:{p["spec"][i % len(p["spec"])]}"></i>{esc(e["nombre"])}</span>' for i, e in enumerate(esp))
    hdr = ''.join(f'<th class="c">{d}</th>' for d in DIAS)
    rows = ''
    for i, e in enumerate(esp):
        v = st['mat'][e['nombre']]
        rows += f'<tr><td><i class="sw" style="background:{p["spec"][i % len(p["spec"])]}"></i><b>{esc(e["nombre"])}</b><small>{esc(e.get("descripcion", ""))}</small></td>' \
                + ''.join(f'<td class="c">{x if x else "·"}</td>' for x in v) + f'<td class="c t">{sum(v)}</td></tr>'
    rows += '<tr class="sum"><td><b>Total del día</b></td>' + ''.join(f'<td class="c">{x}</td>' for x in st['tot']) + f'<td class="c t">{sum(st["tot"])}</td></tr>'
    # fases
    n = obra['semanas']; fases = ''
    for f in obra['fases']:
        cls = 'd' if f['semana_fin'] < semana else ('n' if f['semana_inicio'] <= semana <= f['semana_fin'] else 'p')
        fases += f'<div class="{cls}" style="flex:{f["semana_fin"]-f["semana_inicio"]+1}">{esc(f["nombre"])}</div>'
    hoy = min(100, ((semana - 1) + st['frac']) / n * 100)
    # áreas
    areas = ''
    for a in obra['areas']:
        pc = st['pcts'][a['nombre']]
        areas += f'<div class="area"><div class="tt"><b>{esc(a["nombre"])}</b><em>{round(pc)}%</em></div><div class="bar"><i style="width:{pc}%"></i></div><p>{esc(st["notas"][a["nombre"]])}</p></div>'
    # fotos: hasta 2, de áreas distintas si se puede
    elegidas, vistas = [], set()
    for d, x in st['fotos']:
        if x.get('area') not in vistas or len(elegidas) < 1:
            elegidas.append((d, x)); vistas.add(x.get('area'))
        if len(elegidas) == 2:
            break
    if len(elegidas) < 2:
        elegidas = st['fotos'][:2]
    fotos = ''
    if elegidas:
        figs = ''.join(f'<figure><img src="{foto_path(d, x["archivo"], root).as_uri()}"><figcaption>{esc(x["pie"])}</figcaption></figure>' for d, x in elegidas)
        fotos = f'<h2 style="margin-top:16px">Así se ve la obra</h2><div class="pics">{figs}</div>'
    prox = ''.join(f'<li>{esc(x)}</li>' for x in st['ultimo'].get('proxima', [])) or '<li>Por definir.</li>'
    vals = dict(p, NOMBRE=esc(obra['nombre']), SEMANA=semana, ETIQ=' · Ejemplo' if ejemplo else '', RANGO=rango_semana(st['lun']),
                ARC=f'{251.3 * st["real"] / 100:.1f}', REAL=round(st['real']), NSEM=n, PACTADA=d_corta(pactada), ESTIMADA=d_corta(est),
                RESTAN=f'{restan} días' if restan >= 0 else f'{-restan} días de atraso',
                CUMPCLS=ccls, CUMPTXT=ctxt, CUMPDET=cdet,
                ATCLS='a' if at else 'g', ATENCION=esc(at) if at else 'Sin asuntos que requieran una decisión esta semana.',
                CH1=chart1(p, obra, st), CH2=chart2(p, obra, st), LEGEND=legend, HDR=hdr, ROWS=rows,
                PICO=st['pico'], DIAPICO=st['dia_pico'], PROM=f'{st["promedio"]:.1f}'.rstrip('0').rstrip('.'),
                FASES=fases, HOY=f'{hoy:.1f}', AREAS=areas, FOTOS=fotos, PROXIMA=prox,
                PIE='Documento de ejemplo' if ejemplo else f'Reporte semana {semana}')
    return TPL.substitute(vals)


def a_pdf(html, destino):
    from playwright.sync_api import sync_playwright
    tmp = destino.with_suffix('.html'); tmp.write_text(html, encoding='utf-8')
    with sync_playwright() as pw:
        try:
            b = pw.chromium.launch()
        except Exception:
            b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium')
        pg = b.new_page(); pg.goto(tmp.as_uri()); pg.wait_for_timeout(700)
        pg.pdf(path=str(destino), format='Letter', print_background=True, prefer_css_page_size=True)
        b.close()
    tmp.unlink()


def optimizar_fotos(root):
    try:
        from PIL import Image, ImageOps
    except ImportError:
        print('Aviso: instala Pillow (pip install pillow) para comprimir fotos.'); return
    for f in sorted((root / 'diario').glob('*/*')):
        if f.suffix.lower() not in ('.jpg', '.jpeg', '.png') or f.stat().st_size < 600_000:
            continue
        im = ImageOps.exif_transpose(Image.open(f)); im.thumbnail((1600, 1600))
        if f.suffix.lower() == '.png':
            im = im.convert('RGB'); f = f.with_suffix('.jpg')
        im.convert('RGB').save(f, 'JPEG', quality=82, optimize=True)
    for f in (root / 'diario').glob('*/*'):
        if f.suffix.lower() in ('.heic', '.heif'):
            print(f'Aviso: {f.name} es HEIC; conviértela a JPG (en el iPhone: Ajustes > Cámara > Formatos > Más compatible).')


def datos_sitio(obra, inicio, dias, root):
    """data/entries.json (registros del sitio) y data/site.json (fases, fechas, reportes)."""
    entries = []
    for d in dias:
        f = d['fecha']; rel = d['_dir'].relative_to(root).as_posix()
        for k, v in d.get('areas', {}).items():
            entries.append(dict(id=f'{f}-a-{k}', kind='reporte', date=f, area=k, title='Avance del día', description=v.get('nota', ''), progress_pct=v['pct']))
        for i, x in enumerate(d.get('fotos', [])):
            ph = foto_path(d, x['archivo'], root).relative_to(root).as_posix()
            entries.append(dict(id=f'{f}-f-{i}', kind='evidencia', date=f, area=x.get('area', 'General'), title=x['pie'], description='',
                                files=[dict(path=ph, name=x['pie'], type='image/jpeg')]))
    ult = dias[-1]; sem = semana_de(inicio, ult['_fecha'])
    st = estado(obra, inicio, dias, sem)
    fases = []
    for f in obra['fases']:
        s = 'terminada' if f['semana_fin'] < sem else ('en curso' if f['semana_inicio'] <= sem else 'pendiente')
        fases.append(dict(name=f['nombre'], status=s))
    reps = []
    for pdf in sorted((root / 'media' / 'reportes').glob('Reporte-Palmas441-semana-*.pdf'), reverse=True):
        w = int(re.search(r'semana-(\d+)', pdf.name).group(1))
        fin = inicio + timedelta(days=7 * w - 2)
        reps.append(dict(title=f'Reporte semanal de avance · Semana {w}', date=min(fin, ult['_fecha']).isoformat(),
                         description='Avance real contra proyectado, personal en obra, fases, avance por área y evidencia fotográfica.',
                         file=pdf.relative_to(root).as_posix()))
    site = dict(sample=False, startDate=obra['inicio'], targetDate=obra['entrega_estimada'], phases=fases, areas=[a['nombre'] for a in obra['areas']],
                overall=round(st['real']), reports=reps)
    return entries, site


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.'); ap.add_argument('--semana', type=int)
    ap.add_argument('--solo-sitio', action='store_true'); ap.add_argument('--salida')
    a = ap.parse_args()
    root = (REPO / a.root).resolve(); ejemplo = a.root.rstrip('/') == 'ejemplo'
    obra, inicio, dias = cargar(root)
    if not dias:
        sys.exit('No hay días registrados todavía (diario/AAAA-MM-DD/dia.json).')
    validar(obra, dias)
    optimizar_fotos(root)
    semana = a.semana or semana_de(inicio, dias[-1]['_fecha'])
    out = Path(a.salida).resolve() if a.salida else root / 'media' / 'reportes'
    out.mkdir(parents=True, exist_ok=True)
    if not a.solo_sitio:
        st = estado(obra, inicio, dias, semana)
        nombre = 'reporte-semanal-ejemplo.pdf' if ejemplo else f'Reporte-Palmas441-semana-{semana:02d}.pdf'
        a_pdf(construir_html(obra, inicio, st, root, ejemplo), out / nombre)
        print('Reporte:', out / nombre)
    if not ejemplo:
        entries, site = datos_sitio(obra, inicio, dias, root)
        entries.sort(key=lambda e: (e['date'], e['id']), reverse=True)
        (root / 'data' / 'entries.json').write_text(json.dumps(entries, ensure_ascii=False, indent=1), encoding='utf-8')
        (root / 'data' / 'site.json').write_text(json.dumps(site, ensure_ascii=False, indent=1), encoding='utf-8')
        print('Datos del sitio actualizados (data/entries.json, data/site.json).')


if __name__ == '__main__':
    main()
