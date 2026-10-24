"""Lee el feed público de un diario de Letterboxd y escribe continuar.json al lado de este archivo.

Lo corre GitHub cada hora (.github/workflows/letterboxd.yml). Solo usa la biblioteca estándar.
Uso: python3 letterboxd.py [usuario] [cantidad]
"""
import json
import os
import re
import sys
import time
import urllib.request

USUARIO = sys.argv[1] if len(sys.argv) > 1 else 'RandomReviewer1'
CANTIDAD = int(sys.argv[2]) if len(sys.argv) > 2 else 8
DESTINO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'continuar.json')
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
         'septiembre', 'octubre', 'noviembre', 'diciembre']


def campo(bloque, etiqueta):
    m = re.search(rf'<{etiqueta}>([\s\S]*?)</{etiqueta}>', bloque)
    if not m:
        return ''
    texto = m.group(1).strip()
    for a, b in (('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'), ('&quot;', '"'), ('&#39;', "'"), ('&#x27;', "'")):
        texto = texto.replace(a, b)
    return texto


def color(texto):
    """Un tono oscuro y estable por película, para el resplandor de fondo."""
    h = 0
    for c in texto:
        h = (h * 31 + ord(c)) % 360
    return f'hsl({h}, 55%, 30%)'


def main():
    pedido = urllib.request.Request(f'https://letterboxd.com/{USUARIO}/rss/',
                                    headers={'User-Agent': 'Mozilla/5.0 (pantalla-inicio personal)'})
    with urllib.request.urlopen(pedido, timeout=30) as r:
        xml = r.read().decode('utf-8')
    anio_actual = time.gmtime(time.time() - 3 * 3600).tm_year      # hora de Argentina
    vistas, items = set(), []
    for bloque in re.findall(r'<item>([\s\S]*?)</item>', xml):
        titulo, anio = campo(bloque, 'letterboxd:filmTitle'), campo(bloque, 'letterboxd:filmYear')
        if not titulo or (titulo, anio) in vistas:      # si la viste dos veces, solo la más reciente
            continue
        vistas.add((titulo, anio))
        fecha = campo(bloque, 'letterboxd:watchedDate').split('-')
        visto = ''
        if len(fecha) == 3:
            visto = f'visto el {int(fecha[2])} de {MESES[int(fecha[1]) - 1]}'
            if int(fecha[0]) != anio_actual:
                visto += f' de {fecha[0]}'
        otra_vez = (campo(bloque, 'letterboxd:rewatch') == 'Yes'
                    or re.search(r'/film/[^/]+/\d+/?$', campo(bloque, 'link')))
        estrellas = re.search(r' - ([★½]+)\s*$', campo(bloque, 'title'))
        poster = re.search(r'<img src="([^"]+)"', campo(bloque, 'description'))
        items.append({
            'etiqueta': 'Visto recientemente', 'fuente': 'Letterboxd', 'titulo': titulo,
            'subtitulo': ' · '.join(x for x in (anio, visto, 'otra vez' if otra_vez else '') if x),
            'restante': estrellas.group(1) if estrellas else '',
            'poster': poster.group(1) if poster else '', 'color': color(titulo),
        })
        if len(items) >= CANTIDAD:
            break
    if not items:
        sys.exit('El feed no trae entradas de diario')
    with open(DESTINO, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'{len(items)} películas de {USUARIO} -> continuar.json')


if __name__ == '__main__':
    main()
