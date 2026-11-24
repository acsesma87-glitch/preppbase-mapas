"""Reparte las teselas de rutas de Valhalla (hechas para toda España de una
vez) en un paquete por zona. Como todas salen de la misma construcción,
encajan entre sí: en el teléfono se juntan y las rutas pueden pasar de una
comunidad a otra.

Cada paquete lleva las teselas que tocan el rectángulo de la zona (con un
margen), con su ruta relativa (por ejemplo, 2/000/751/234.gph).

Uso: python3 repartir_rutas.py CARPETA_TESELAS ZONA.poly SALIDA.tar.gz
"""

import os
import sys
import tarfile

# Tamaño en grados de las teselas de cada nivel de Valhalla.
TAMANO = {0: 4.0, 1: 1.0, 2: 0.25}
MARGEN = 0.25


def limites_poly(ruta):
    lons, lats = [], []
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            partes = linea.split()
            if len(partes) == 2:
                try:
                    lon, lat = float(partes[0]), float(partes[1])
                except ValueError:
                    continue
                lons.append(lon)
                lats.append(lat)
    if not lons:
        sys.exit(f"Contorno vacío: {ruta}")
    return (min(lons) - MARGEN, min(lats) - MARGEN,
            max(lons) + MARGEN, max(lats) + MARGEN)


def caja_tesela(nivel, ident):
    t = TAMANO[nivel]
    columnas = int(360 / t)
    fila, col = divmod(ident, columnas)
    oeste, sur = -180 + col * t, -90 + fila * t
    return oeste, sur, oeste + t, sur + t


def main(carpeta, poly, salida):
    o, s, e, n = limites_poly(poly)
    elegidas = []
    for raiz, _, archivos in os.walk(carpeta):
        for a in archivos:
            if not a.endswith(".gph"):
                continue
            relativa = os.path.relpath(os.path.join(raiz, a), carpeta)
            partes = relativa[:-4].split(os.sep)
            nivel = int(partes[0])
            if nivel not in TAMANO:
                continue
            ident = int("".join(partes[1:]))
            to, ts, te, tn = caja_tesela(nivel, ident)
            if to <= e and te >= o and ts <= n and tn >= s:
                elegidas.append(relativa)
    if not elegidas:
        sys.exit(f"Ninguna tesela para {poly}")
    with tarfile.open(salida, "w:gz", compresslevel=9) as tar:
        for r in sorted(elegidas):
            tar.add(os.path.join(carpeta, r), arcname=r.replace(os.sep, "/"))
    print(f"{len(elegidas)} teselas en {salida}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
