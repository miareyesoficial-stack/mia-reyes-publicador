"""
Publica una imagen o Reel en Instagram via la Graph API de Meta.

Instagram exige una URL publica para el media (image_url / video_url), y
como este proyecto no tiene servidor propio, se usa el mismo truco que el
pipeline de referencia (Curiosidades de IA): subir el archivo como asset
de un Release temporal de GitHub para conseguirle una URL publica, y
borrar ese Release apenas termina de publicarse.
"""
import os
import time

import requests

import config

API_BASE = "https://graph.facebook.com/v20.0"


def publicar_en_instagram(ruta_media, caption, es_video):
    url_publica, tag_release = _subir_a_release_temporal(ruta_media)
    try:
        contenedor_id = _crear_contenedor(url_publica, caption, es_video)
        _esperar_contenedor_listo(contenedor_id)
        return _publicar_contenedor(contenedor_id)
    finally:
        _borrar_release_temporal(tag_release)


def _crear_contenedor(url_publica, caption, es_video):
    endpoint = f"{API_BASE}/{config.INSTAGRAM_BUSINESS_ID}/media"
    datos = {
        "caption": caption,
        "access_token": config.FACEBOOK_ACCESS_TOKEN,
    }
    if es_video:
        datos["media_type"] = "REELS"
        datos["video_url"] = url_publica
    else:
        datos["image_url"] = url_publica

    resp = requests.post(endpoint, data=datos, timeout=60)
    resp.raise_for_status()
    return resp.json()["id"]


def _esperar_contenedor_listo(contenedor_id, intentos=30, espera_segundos=10):
    endpoint = f"{API_BASE}/{contenedor_id}"
    for _ in range(intentos):
        resp = requests.get(
            endpoint,
            params={"fields": "status_code", "access_token": config.FACEBOOK_ACCESS_TOKEN},
            timeout=30,
        )
        resp.raise_for_status()
        estado = resp.json().get("status_code")
        if estado == "FINISHED":
            return
        if estado == "ERROR":
            raise RuntimeError("Meta reporto un error procesando el contenedor de Instagram")
        time.sleep(espera_segundos)
    raise TimeoutError("El contenedor de Instagram no termino de procesarse a tiempo")


def _publicar_contenedor(contenedor_id):
    endpoint = f"{API_BASE}/{config.INSTAGRAM_BUSINESS_ID}/media_publish"
    resp = requests.post(
        endpoint,
        data={"creation_id": contenedor_id, "access_token": config.FACEBOOK_ACCESS_TOKEN},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def _subir_a_release_temporal(ruta_media):
    repo = config.GITHUB_REPOSITORY
    token = config.GITHUB_TOKEN
    tag = f"temp-media-{int(time.time())}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }

    resp = requests.post(
        f"https://api.github.com/repos/{repo}/releases",
        headers=headers,
        json={"tag_name": tag, "name": tag, "draft": False, "prerelease": True},
        timeout=30,
    )
    resp.raise_for_status()
    release = resp.json()
    upload_url = release["upload_url"].split("{")[0]

    nombre_archivo = os.path.basename(ruta_media)
    with open(ruta_media, "rb") as f:
        contenido = f.read()

    mime = "video/mp4" if ruta_media.lower().endswith((".mp4", ".mov", ".m4v")) else "image/jpeg"
    resp_asset = requests.post(
        upload_url,
        headers={**headers, "Content-Type": mime},
        params={"name": nombre_archivo},
        data=contenido,
        timeout=120,
    )
    resp_asset.raise_for_status()
    asset = resp_asset.json()
    return asset["browser_download_url"], tag


def _borrar_release_temporal(tag):
    repo = config.GITHUB_REPOSITORY
    token = config.GITHUB_TOKEN
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    resp = requests.get(
        f"https://api.github.com/repos/{repo}/releases/tags/{tag}",
        headers=headers,
        timeout=30,
    )
    if resp.status_code != 200:
        return
    release_id = resp.json()["id"]
    requests.delete(
        f"https://api.github.com/repos/{repo}/releases/{release_id}",
        headers=headers,
        timeout=30,
    )
    requests.delete(
        f"https://api.github.com/repos/{repo}/git/refs/tags/{tag}",
        headers=headers,
        timeout=30,
    )
