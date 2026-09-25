"""
Revisa la hora actual de Chile y los horarios fijos del dia de la semana
para decidir si hay una publicacion pendiente (atrasada y no publicada aun).

Este script corre cada 30 minutos desde GitHub Actions. Como los horarios
programados de Actions no son exactos, en vez de publicar "a la hora exacta"
se compara la hora actual contra la lista de horarios fijos del dia y se
publica el mas atrasado que todavia no se haya marcado como publicado hoy.
"""
import os
from datetime import datetime

import pytz

import config
from estado import cargar_estado


def escribir_salida(clave, valor):
    salida = os.environ.get("GITHUB_OUTPUT")
    if salida:
        with open(salida, "a", encoding="utf-8") as f:
            f.write(f"{clave}={valor}\n")
    print(f"{clave}={valor}")


def main():
    tz = pytz.timezone(config.ZONA_HORARIA)
    ahora = datetime.now(tz)
    dia_semana = ahora.weekday()  # 0 = lunes ... 6 = domingo
    hora_actual = ahora.strftime("%H:%M")

    horarios_hoy = config.HORARIOS_POR_DIA.get(dia_semana, [])
    estado = cargar_estado()
    publicados = estado["horarios_publicados"]

    pendiente = None
    for h in sorted(horarios_hoy, key=lambda x: x["hora"]):
        if h["hora"] <= hora_actual and h["hora"] not in publicados:
            pendiente = h
            break  # el mas atrasado (mas antiguo sin publicar) primero

    if pendiente:
        escribir_salida("hay_pendiente", "true")
        escribir_salida("tipo", pendiente["tipo"])
        escribir_salida("hora", pendiente["hora"])
    else:
        escribir_salida("hay_pendiente", "false")


if __name__ == "__main__":
    main()
