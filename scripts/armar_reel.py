"""
Arma un Reel de REEL_DURACION_SEGUNDOS a partir de UNA sola foto fija
(sin efectos, sin zoom, sin Ken Burns) con musica de fondo elegida al azar
entre las pistas libres de derechos configuradas.
"""
import os
import random
import tempfile
import urllib.request

from moviepy.editor import AudioFileClip, ImageClip

import config


def _descargar_audio(url):
    fd, ruta = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    urllib.request.urlretrieve(url, ruta)
    return ruta


def construir_reel_desde_foto(ruta_foto):
    pista_url = random.choice(config.PISTAS_MUSICA)
    ruta_audio = _descargar_audio(pista_url)

    clip_imagen = (
        ImageClip(ruta_foto)
        .set_duration(config.REEL_DURACION_SEGUNDOS)
        .resize(height=config.REEL_ALTO)
    )

    # Si el ancho no calza exactamente con REEL_ANCHO, se centra sobre un
    # fondo negro de 1080x1920 (sin recortar ni deformar la foto).
    clip_imagen = clip_imagen.on_color(
        size=(config.REEL_ANCHO, config.REEL_ALTO),
        color=(0, 0, 0),
        pos="center",
    )

    audio = AudioFileClip(ruta_audio).subclip(0, config.REEL_DURACION_SEGUNDOS)
    clip_final = clip_imagen.set_audio(audio)

    os.makedirs("output", exist_ok=True)
    ruta_salida = os.path.join("output", "reel.mp4")
    clip_final.write_videofile(
        ruta_salida,
        fps=config.REEL_FPS,
        codec="libx264",
        audio_codec="aac",
    )
    return ruta_salida
