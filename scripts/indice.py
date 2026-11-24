"""Crea indice.json, la lista de paquetes que lee la aplicación.

Uso: python3 indice.py CARPETA ETIQUETA
La carpeta contiene <zona>.pmtiles, <zona>-puntos.json.gz y fuentes.zip.
"""

import gzip
import hashlib
import json
import os
import sys


def archivo(carpeta, nombre):
    ruta = os.path.join(carpeta, nombre)
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return {"archivo": nombre, "bytes": os.path.getsize(ruta),
            "sha256": h.hexdigest()}


def main(carpeta, etiqueta):
    with open("zonas.json", encoding="utf-8") as f:
        todas = json.load(f)
    zonas = []
    for z in todas:
        mapa = f'{z["id"]}.pmtiles'
        puntos = f'{z["id"]}-puntos.json.gz'
        rutas = f'{z["id"]}-rutas.tar.gz'
        if not (os.path.exists(os.path.join(carpeta, mapa))
                and os.path.exists(os.path.join(carpeta, puntos))):
            continue
        with gzip.open(os.path.join(carpeta, puntos), "rt") as f:
            datos = json.load(f)
        zonas.append({"id": z["id"], "nombre": z["nombre"],
                      "fecha_datos": datos["fecha"],
                      "limites": datos["limites"],
                      "mapa": archivo(carpeta, mapa),
                      "puntos": {**archivo(carpeta, puntos),
                                 "total": len(datos["puntos"])},
                      # Rutas sin conexión (fase 2), si se han generado.
                      **({"rutas": archivo(carpeta, rutas)}
                         if os.path.exists(os.path.join(carpeta, rutas))
                         else {})})
    if not zonas:
        sys.exit("No se ha generado ninguna zona")
    indice = {"version": 1, "etiqueta": etiqueta,               "fuentes": archivo(carpeta, "fuentes.zip"), "zonas": zonas}
    with open(os.path.join(carpeta, "indice.json"), "w",
              encoding="utf-8") as f:
        json.dump(indice, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:3])
