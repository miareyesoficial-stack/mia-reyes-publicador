"""
Utilidades de Google Drive: obtiene el siguiente archivo a publicar
siguiendo el ciclo de rotacion de contenido (IMAGENES -> Usadas -> Reutilizadas)
para que el pipeline nunca se quede sin contenido.
"""
import os
import io
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import config

SCOPES = ["https://www.googleapis.com/auth/drive"]


def get_drive_service():
    info = json.loads(config.GOOGLE_SERVICE_ACCOUNT_JSON)
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def _listar_archivos(service, folder_id, extensiones=None):
    query = f"'{folder_id}' in parents and trashed = false"
    resp = service.files().list(
        q=query,
        fields="files(id, name, mimeType, createdTime)",
        orderBy="createdTime",
        pageSize=1000,
    ).execute()
    archivos = resp.get("files", [])
    if extensiones:
        archivos = [
            a for a in archivos
            if os.path.splitext(a["name"])[1].lower() in extensiones
        ]
    return archivos


def _obtener_o_crear_subcarpeta(service, nombre, padre_id):
    query = (
        f"'{padre_id}' in parents and name = '{nombre}' "
        "and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    )
    resp = service.files().list(q=query, fields="files(id, name)").execute()
    archivos = resp.get("files", [])
    if archivos:
        return archivos[0]["id"]
    metadata = {
        "name": nombre,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [padre_id],
    }
    carpeta = service.files().create(body=metadata, fields="id").execute()
    return carpeta["id"]


def _mover_archivo(service, archivo_id, origen_id, destino_id):
    service.files().update(
        fileId=archivo_id,
        addParents=destino_id,
        removeParents=origen_id,
        fields="id, parents",
    ).execute()


def _descargar_archivo(service, archivo):
    os.makedirs("descargas", exist_ok=True)
    ruta = os.path.join("descargas", archivo["name"])
    request = service.files().get_media(fileId=archivo["id"])
    with io.FileIO(ruta, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    return ruta


def obtener_siguiente_archivo(extensiones=None):
    service = get_drive_service()
    raiz_id = config.GOOGLE_DRIVE_FOLDER_ID
    usadas_id = _obtener_o_crear_subcarpeta(service, config.NOMBRE_SUBCARPETA_USADAS, raiz_id)
    reutilizadas_id = _obtener_o_crear_subcarpeta(service, config.NOMBRE_SUBCARPETA_REUTILIZADAS, raiz_id)

    nuevos = _listar_archivos(service, raiz_id, extensiones)
    if nuevos:
        archivo = nuevos[0]
        ruta = _descargar_archivo(service, archivo)
        _mover_archivo(service, archivo["id"], raiz_id, usadas_id)
        return {"id": archivo["id"], "name": archivo["name"], "ruta_local": ruta}

    usadas = _listar_archivos(service, usadas_id, extensiones)
    if usadas:
        archivo = usadas[0]
        ruta = _descargar_archivo(service, archivo)
        _mover_archivo(service, archivo["id"], usadas_id, reutilizadas_id)
        return {"id": archivo["id"], "name": archivo["name"], "ruta_local": ruta}

    reutilizadas = _listar_archivos(service, reutilizadas_id, extensiones)
    if reutilizadas:
        archivo = reutilizadas[0]
        ruta = _descargar_archivo(service, archivo)
        return {"id": archivo["id"], "name": archivo["name"], "ruta_local": ruta}

    return None
