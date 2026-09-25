"""
Manejo del archivo de estado (estado_publicaciones.json), que guarda
la fecha de Chile y los horarios ya publicados HOY, para no repetirlos
y para detectar correctamente el cambio de dia (evita el riesgo de que
un reinicio a medianoche en horario de Chile confunda al pipeline con
el reloj UTC del servidor de GitHub Actions).
"""
import json
import os
from datetime import datetime

import pytz

import config


def _fecha_hoy_chile():
    tz = pytz.timezone(config.ZONA_HORARIA)
    return datetime.now(tz).strftime("%Y-%m-%d")


def cargar_estado():
    if not os.path.exists(config.ARCHIVO_ESTADO):
        return {"fecha_chile": _fecha_hoy_chile(), "horarios_publicados": []}

    with open(config.ARCHIVO_ESTADO, "r", encoding="utf-8") as f:
        estado = json.load(f)

    # Si el archivo es de un dia distinto (hora de Chile), se reinicia.
    if estado.get("fecha_chile") != _fecha_hoy_chile():
        estado = {"fecha_chile": _fecha_hoy_chile(), "horarios_publicados": []}

    return estado


def guardar_estado(estado):
    with open(config.ARCHIVO_ESTADO, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)


def marcar_horario_publicado(hora):
    estado = cargar_estado()
    if hora not in estado["horarios_publicados"]:
        estado["horarios_publicados"].append(hora)
    guardar_estado(estado)
