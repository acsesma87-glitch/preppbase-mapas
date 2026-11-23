"""Convierte los puntos de interés exportados por osmium (GeoJSON por
líneas) en el paquete de puntos de PreppBase (JSON comprimido con gzip).

Categorías (sección 3.2 del Documento Maestro). Agua potable y puntos de
captación son categorías distintas: solo es potable lo que OpenStreetMap
marca como apto para beber.

Uso: python3 pois.py entrada.geojsonseq salida.json.gz FECHA
"""

import gzip
import json
import sys

CATEGORIAS = ["refugio", "agua_potable", "captacion", "gasolinera",
              "farmacia", "sanitario"]

REFUGIO_NO = {"public_transport", "changing_rooms", "field_shelter",
              "sun_shelter", "smoking_area"}
SANITARIO = {"hospital", "clinic", "doctors"}


def categoria(t):
    amenity = t.get("amenity")
    potable = t.get("drinking_water")
    if amenity == "shelter":
        return None if t.get("shelter_type") in REFUGIO_NO else "refugio"
    if t.get("tourism") in ("alpine_hut", "wilderness_hut"):
        return "refugio"
    if amenity in ("drinking_water", "water_point"):
        return "captacion" if potable == "no" else "agua_potable"
    if (t.get("man_made") in ("water_tap", "water_well")
            or t.get("natural") == "spring"):
        return "agua_potable" if potable == "yes" else "captacion"
    if amenity == "fuel":
        return "gasolinera"
    if amenity == "pharmacy" or t.get("healthcare") == "pharmacy":
        return "farmacia"
    if amenity in SANITARIO or t.get("healthcare") in (
            "hospital", "clinic", "centre"):
        return "sanitario"
    return None


def detalle(t, cat):
    partes = []
    if cat == "sanitario" and t.get("emergency") == "yes":
        partes.append("Urgencias")
    marca = t.get("brand") or t.get("operator")
    if marca and marca != t.get("name"):
        partes.append(marca)
    if t.get("opening_hours"):
        partes.append("Horario: " + t["opening_hours"])
    if t.get("access") in ("private", "no"):
        partes.append("Acceso privado")
    if cat == "captacion":
        partes.append("Agua sin confirmar como potable: tratarla antes de beber")
    return " · ".join(partes)


def centro(geom):
    if geom["type"] == "Point":
        return geom["coordinates"]
    anillo = (geom["coordinates"][0] if geom["type"] == "Polygon"
              else geom["coordinates"][0][0])
    pts = anillo[:-1] or anillo
    return [sum(p[0] for p in pts) / len(pts),
            sum(p[1] for p in pts) / len(pts)]


def main(entrada, salida, fecha):
    puntos, vistos = [], set()
    with open(entrada, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip().lstrip("\x1e")
            if not linea:
                continue
            o = json.loads(linea)
            t = o.get("properties") or {}
            cat = categoria(t)
            if cat is None or not o.get("geometry"):
                continue
            clave = f'{t.get("@type", "")}{t.get("@id", "")}'
            if clave in vistos:
                continue
            vistos.add(clave)
            lon, lat = centro(o["geometry"])
            puntos.append([CATEGORIAS.index(cat), round(lat, 6),
                           round(lon, 6), t.get("name", ""),
                           detalle(t, cat)])
    datos = {"version": 1, "fecha": fecha, "categorias": CATEGORIAS,
             "puntos": puntos}
    with gzip.open(salida, "wt", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(puntos)} puntos")


if __name__ == "__main__":
    main(*sys.argv[1:4])
