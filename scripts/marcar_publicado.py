"""
Marca un horario como publicado hoy en el archivo de estado.
Uso: python scripts/marcar_publicado.py "HH:MM"
"""
import sys

from estado import marcar_horario_publicado

if __name__ == "__main__":
    if len(sys.argv) < 2 or not sys.argv[1]:
        print("Falta indicar la hora a marcar como publicada. Uso: marcar_publicado.py HH:MM")
        sys.exit(1)
    marcar_horario_publicado(sys.argv[1])
    print(f"Horario {sys.argv[1]} marcado como publicado.")
