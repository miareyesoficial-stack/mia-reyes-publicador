"""
Publica una imagen o Reel en Instagram via la Graph API de Meta.

Instagram exige una URL publica para el media (image_url / video_url), y
como este proyecto no tiene servidor propio, se usa el mismo truco que el
pipeline de referencia (Curiosidades de IA): subir el archivo como asset
de un Release temporal de GitHub para conseguirle una URL publica, y
borrar ese Release apenas termina de publicarse.
"""
import os
import base64
import time

import requests

import config

API_BASE = "https://graph.facebook.com/v20.0"


def publicar_en_instagram(ruta_media, caption, es_video):
    url_publica, ruta_repo, sha = _subir_a_repo_temporal(ruta_media)
    try:
        contenedor_id = _crear_contenedor(url_publica, caption, es_video)
        _esperar_contenedor_listo(contenedor_id)
        return _publicar_contenedor(contenedor_id)
    finally:
        _borrar_de_repo_temporal(ruta_repo, sha)

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
    print("META RESPONSE:", resp.status_code, resp.text)
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


def _subir_a_repo_temporal(ruta_media):
    repo = config.GITHUB_REPOSITORY
    token = config.GITHUB_TOKEN
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }

    nombre_archivo = os.path.basename(ruta_media)
    ruta_repo = f"tmp_media/{int(time.time())}_{nombre_archivo}"
    with open(ruta_media, "rb") as f:
        contenido_b64 = base64.b64encode(f.read()).decode("utf-8")

    resp = requests.put(
        f"https://api.github.com/repos/{repo}/contents/{ruta_repo}",
        headers=headers,
        json={
            "message": f"Media temporal para publicar: {nombre_archivo}",
            "content": contenido_b64,
            "branch": "main",
        },
        timeout=60,
    )
    resp.raise_for_status()
    sha = resp.json()["content"]["sha"]
    url_publica = f"https://raw.githubusercontent.com/{repo}/main/{ruta_repo}"
    return url_publica, ruta_repo, sha
def _borrar_de_repo_temporal(ruta_repo, sha):
    repo = config.GITHUB_REPOSITORY
    token = config.GITHUB_TOKEN
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    requests.delete(
        f"https://api.github.com/repos/{repo}/contents/{ruta_repo}",
        headers=headers,
        json={
            "message": f"Eliminar media temporal: {ruta_repo}",
            "sha": sha,
            "branch": "main",
        },
        timeout=30,
    )
    
