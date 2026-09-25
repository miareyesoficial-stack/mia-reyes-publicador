"""
Configuracion central del pipeline de publicacion de Mia Reyes.
"""
import os

# ---- Credenciales / secretos (vienen de GitHub Secrets) ----
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GOOGLE_SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
GOOGLE_DRIVE_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")  # carpeta IMAGENES
FACEBOOK_ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ID = os.environ.get("INSTAGRAM_BUSINESS_ID")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")

# ---- Video del Reel ----
# La carpeta IMAGENES puede tener tanto fotos como videos ya grabados:
# - Si el archivo tomado es un VIDEO: se publica tal cual, sin modificarlo.
# - Si el archivo tomado es una FOTO: se arma un video fijo (sin efectos)
#   de REEL_DURACION_SEGUNDOS con musica de fondo (ver PISTAS_MUSICA).
EXTENSIONES_VIDEO = [".mp4", ".mov", ".m4v"]
EXTENSIONES_IMAGEN = [".jpg", ".jpeg", ".png", ".webp"]

REEL_DURACION_SEGUNDOS = 30
REEL_ANCHO = 1080
REEL_ALTO = 1920
REEL_FPS = 24

# Pistas de musica "movida" / energetica, libres de derechos (Pixabay Audio, CC0).
# Se elige una al azar en cada Reel.
PISTAS_MUSICA = [
    "https://cdn.pixabay.com/download/audio/2022/10/25/audio_946bc45f2c.mp3?filename=energetic-rock-124008.mp3",
    "https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8dd02cc27.mp3?filename=funky-groove-118929.mp3",
    "https://cdn.pixabay.com/download/audio/2023/09/03/audio_ac1bb4b6b6.mp3?filename=energetic-drive-173404.mp3",
    "https://cdn.pixabay.com/download/audio/2021/11/25/audio_00fa5f0c39.mp3?filename=powerful-beat-118656.mp3",
]

# ---- Estilos / "angulos" para variar el tono del caption ----
ANGULOS_CAPTION = [
    "Misteriosa y provocadora, dejando algo a la imaginacion, sin dar todo.",
    "Coqueta y juguetona, como una invitacion directa.",
    "Segura de si misma, dueña de su cuerpo, tono empoderado.",
    "Intima, como si le estuviera hablando solo a una persona.",
    "Divertida y espontanea, como un detras de camaras.",
    "Nostalgica, como el recuerdo de una sesion de fotos o un viaje.",
    "Curiosa, hace una pregunta directa a quien ve la publicacion.",
    "Presumida, se muestra orgullosa de como se ve hoy.",
]

# ---- Hashtags base (se combinan con los que sugiera Gemini) ----
# Minimo 8 hashtags por publicacion: estos fijos + los que Gemini agregue
# segun la foto, hasta completar al menos 8 en total.
HASHTAGS_BASE = [
    "#miareyes",
    "#contenidoexclusivo",
    "#fanvue",
    "#modelo",
    "#influencer",
    "#contenidopremium",
    "#sigueme",
    "#exclusivo",
]
MINIMO_HASHTAGS = 8

# ---- Archivos de estado ----
ARCHIVO_ESTADO = "estado_publicaciones.json"

# ---- Carpetas Drive (subcarpetas dentro de GOOGLE_DRIVE_FOLDER_ID / IMAGENES) ----
# Ciclo para nunca quedarse sin contenido (igual que reels-automatizados):
#   1. Se busca primero en IMAGENES (archivos nuevos, sin usar).
#      Al usarse, se mueven a "Usadas".
#   2. Si IMAGENES esta vacia, se reutiliza el mas antiguo de "Usadas".
#      Al reutilizarse, se mueve a "Reutilizadas".
#   3. Si tambien "Usadas" esta vacia, se reutiliza el mas antiguo de
#      "Reutilizadas" (se deja ahi mismo, sigue rotando en ese ciclo).
# Asi el pipeline nunca deja de publicar mientras haya al menos un archivo
# en cualquiera de las tres carpetas.
NOMBRE_SUBCARPETA_USADAS = "Usadas"
NOMBRE_SUBCARPETA_REUTILIZADAS = "Reutilizadas"

# ---- Zona horaria ----
ZONA_HORARIA = "America/Santiago"

# ---- Horarios fijos de publicacion ----
HORARIOS_POR_DIA = {
    0: [
        {"hora": "09:14", "tipo": "imagen"},
        {"hora": "15:47", "tipo": "imagen"},
        {"hora": "21:03", "tipo": "imagen"},
    ],
    1: [
        {"hora": "10:38", "tipo": "imagen"},
        {"hora": "16:22", "tipo": "imagen"},
        {"hora": "20:51", "tipo": "imagen"},
    ],
    2: [
        {"hora": "08:57", "tipo": "imagen"},
        {"hora": "14:19", "tipo": "imagen"},
        {"hora": "22:08", "tipo": "imagen"},
    ],
    3: [
        {"hora": "11:26", "tipo": "imagen"},
        {"hora": "17:44", "tipo": "imagen"},
        {"hora": "19:33", "tipo": "imagen"},
    ],
    4: [
        {"hora": "09:41", "tipo": "imagen"},
        {"hora": "13:12", "tipo": "imagen"},
        {"hora": "16:58", "tipo": "imagen"},
        {"hora": "19:27", "tipo": "video"},
        {"hora": "22:15", "tipo": "imagen"},
    ],
    5: [
        {"hora": "08:33", "tipo": "imagen"},
        {"hora": "10:47", "tipo": "imagen"},
        {"hora": "12:21", "tipo": "imagen"},
        {"hora": "14:58", "tipo": "imagen"},
        {"hora": "17:36", "tipo": "imagen"},
        {"hora": "19:14", "tipo": "video"},
        {"hora": "21:52", "tipo": "imagen"},
    ],
    6: [
        {"hora": "09:07", "tipo": "imagen"},
        {"hora": "11:39", "tipo": "imagen"},
        {"hora": "13:24", "tipo": "imagen"},
        {"hora": "15:51", "tipo": "imagen"},
        {"hora": "17:18", "tipo": "video"},
        {"hora": "19:46", "tipo": "imagen"},
        {"hora": "21:29", "tipo": "imagen"},
    ],
}
