"""Añade los paquetes de lugares (<zona>-lugares.json.gz) al indice.json de
una versión ya publicada, sin rehacer mapas ni rutas.

Uso: python3 anadir_lugares.py CARPETA
La carpeta contiene indice.json (el publicado) y los paquetes de lugares.
"""

import json
import os
import sys

from indice import archivo


def main(carpeta):
    ruta = os.path.join(carpeta, "indice.json")
    with open(ruta, encoding="utf-8") as f:
        indice = json.load(f)
    n = 0
    for z in indice["zonas"]:
        nombre = f'{z["id"]}-lugares.json.gz'
        if os.path.exists(os.path.join(carpeta, nombre)):
            z["lugares"] = archivo(carpeta, nombre)
            n += 1
    if n == 0:
        sys.exit("No hay paquetes de lugares")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(indice, f, ensure_ascii=False, indent=1)
    print(f"Lugares añadidos a {n} zonas")


if __name__ == "__main__":
    main(sys.argv[1])
