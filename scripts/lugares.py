"""Convierte los lugares con nombre exportados por osmium (GeoJSON por
líneas) en el paquete de lugares de PreppBase, para buscar sitios por su
nombre sin internet (sección 72.1 del Documento Maestro).

Uso: python3 lugares.py entrada.geojsonseq salida.json.gz FECHA
"""

import gzip
import json
import sys

# Orden de importancia: sirve para ordenar los resultados.
TIPOS = ["ciudad", "pueblo", "aldea", "barrio", "paraje", "pico", "puerto"]

PLACE = {
    "city": "ciudad",
    "town": "pueblo",
    "village": "pueblo",
    "hamlet": "aldea",
    "isolated_dwelling": "aldea",
    "suburb": "barrio",
    "quarter": "barrio",
    "neighbourhood": "barrio",
    "locality": "paraje",
}


def tipo(t):
    if t.get("place") in PLACE:
        return PLACE[t["place"]]
    if t.get("natural") == "peak":
        return "pico"
    if t.get("mountain_pass") == "yes" or t.get("natural") == "saddle":
        return "puerto"
    return None


def centro(geom):
    if geom["type"] == "Point":
        return geom["coordinates"]
    anillo = (geom["coordinates"][0] if geom["type"] == "Polygon"
              else geom["coordinates"][0][0])
    pts = anillo[:-1] or anillo
    return [sum(p[0] for p in pts) / len(pts),
            sum(p[1] for p in pts) / len(pts)]


def main(entrada, salida, fecha):
    lugares, vistos = [], set()
    with open(entrada, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip().lstrip("\x1e")
            if not linea:
                continue
            o = json.loads(linea)
            t = o.get("properties") or {}
            nombre = (t.get("name") or "").strip()
            tp = tipo(t)
            if not nombre or tp is None or not o.get("geometry"):
                continue
            lon, lat = centro(o["geometry"])
            clave = (nombre, tp, round(lat, 3), round(lon, 3))
            if clave in vistos:
                continue
            vistos.add(clave)
            # Nombre en la otra lengua oficial (por ejemplo, «Donostia /
            # San Sebastián»), para encontrarlo de las dos formas.
            otros = sorted({v.strip() for k, v in t.items()
                            if k in ("name:es", "name:eu", "name:ca",
                                     "name:gl", "alt_name", "official_name")
                            and v and v.strip() not in nombre})
            fila = [TIPOS.index(tp), round(lat, 6), round(lon, 6), nombre]
            if otros:
                fila.append(" / ".join(otros))
            lugares.append(fila)
    if not lugares:
        sys.exit("Sin lugares: algo ha fallado")
    datos = {"version": 1, "fecha": fecha, "tipos": TIPOS,
             "lugares": lugares}
    with gzip.open(salida, "wt", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(lugares)} lugares")


if __name__ == "__main__":
    main(*sys.argv[1:4])
