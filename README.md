# PreppBase · mapas

Paquetes de mapas sin conexión para la aplicación PreppBase, uno por
comunidad autónoma. Se generan solos cada mes con GitHub Actions
(`.github/workflows/mapas.yml`) y se publican en *Releases*.

Cada versión contiene:

- `<zona>.pmtiles`: mapa vectorial (esquema OpenMapTiles), generado con
  Planetiler.
- `<zona>-puntos.json.gz`: puntos de interés (refugios, agua potable,
  puntos de captación, gasolineras, farmacias y centros sanitarios).
- `fuentes.zip`: tipografía para los nombres del mapa.
- `indice.json`: lista de paquetes con tamaño y huella SHA-256, que la
  aplicación comprueba tras descargar.

## Licencias de los datos

- Mapa y puntos: © colaboradores de OpenStreetMap, licencia ODbL.
  Extractos de Geofabrik.
- Esquema de teselas: © OpenMapTiles.
- Costa y mar: osmdata.openstreetmap.de (ODbL). Natural Earth (dominio
  público).
- Tipografía Noto Sans: SIL Open Font License.
