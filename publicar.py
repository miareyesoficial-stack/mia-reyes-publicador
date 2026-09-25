"""
Script principal del pipeline de Mia Reyes.

Uso: python publicar.py --tipo imagen o video

Flujo:
  1. Toma el siguiente archivo de Drive segun el ciclo de rotacion.
     - tipo "imagen": toma el siguiente archivo de imagen disponible.
     - tipo "video": prioriza un video real subido por Jose; si no hay
       ningun video disponible, toma una foto y arma un Reel de 30s con
       musica de fondo (sin efectos).
     - Si no hay NADA disponible en ninguna de las tres carpetas de Drive,
       se omite la publicacion (no se inventa contenido).
  2. Genera el caption con Gemini, mirando la foto/imagen real.
  3. Publica en Instagram (imagen normal o Reel) via la Graph API.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))

import config  # noqa: E402
from drive_utils import obtener_siguiente_archivo  # noqa: E402
from caption_gemini import generar_caption  # noqa: E402
from armar_reel import construir_reel_desde_foto  # noqa: E402
from publicar_instagram import publicar_en_instagram  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tipo", choices=["imagen", "video"], required=True)
    args = parser.parse_args()

    if args.tipo == "video":
        archivo = obtener_siguiente_archivo(config.EXTENSIONES_VIDEO)
        if archivo:
            ruta_publicar = archivo["ruta_local"]
            es_video = True
        else:
            archivo = obtener_siguiente_archivo(config.EXTENSIONES_IMAGEN)
            if not archivo:
                print("No hay contenido disponible en Drive (ni video ni foto). Se omite esta publicacion.")
                return
            print("No habia video disponible: se arma un Reel de 30s a partir de una foto.")
            ruta_publicar = construir_reel_desde_foto(archivo["ruta_local"])
            es_video = True
    else:
        archivo = obtener_siguiente_archivo(config.EXTENSIONES_IMAGEN)
        if not archivo:
            print("No hay fotos disponibles en Drive. Se omite esta publicacion.")
            return
        ruta_publicar = archivo["ruta_local"]
        es_video = False

    print(f"Generando caption a partir de: {archivo['name']}")
    caption = generar_caption(archivo["ruta_local"])
    print("Caption generado:\n" + caption)

    print("Publicando en Instagram...")
    publicar_en_instagram(ruta_publicar, caption, es_video)
    print("Publicado con exito.")


if __name__ == "__main__":
    main()
