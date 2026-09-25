"""
Genera el caption (texto + hashtags) para una publicacion usando Gemini,
mirando la foto real y variando el tono segun ANGULOS_CAPTION.
"""
import random

import google.generativeai as genai

import config


def generar_caption(ruta_imagen):
    genai.configure(api_key=config.GEMINI_API_KEY)
    modelo = genai.GenerativeModel("gemini-1.5-flash")

    angulo = random.choice(config.ANGULOS_CAPTION)

    prompt = f"""
Eres Mia Reyes, una creadora de contenido para adultos en Instagram (@miareyes.oficial).
Mira la imagen adjunta y escribe un caption para esa publicacion, en espanol de Chile,
con este tono/angulo: "{angulo}"

Reglas:
- Maximo 3 a 4 lineas de texto (sin contar los hashtags).
- Habla en primera persona, como si fueras Mia.
- No repitas literalmente el angulo indicado, usalo solo como guia de tono.
- Al final, en una linea aparte, agrega entre 3 y 6 hashtags relevantes a la
  foto (ademas de los que ya usamos siempre, no los repitas):
  {', '.join(config.HASHTAGS_BASE)}
- Maximo 2 a 3 emojis en todo el texto.
- Manten un tono sugerente pero dentro de las normas de contenido de Instagram
  (nada explicito en el texto).

Responde SOLO con el texto final del caption, sin explicaciones adicionales.
"""

    with open(ruta_imagen, "rb") as f:
        datos_imagen = f.read()

    mime = "image/png" if ruta_imagen.lower().endswith(".png") else "image/jpeg"

    respuesta = modelo.generate_content([
        prompt,
        {"mime_type": mime, "data": datos_imagen},
    ])

    texto = respuesta.text.strip()

    hashtags_extra = [palabra for palabra in texto.split() if palabra.startswith("#")]
    hashtags_finales = list(dict.fromkeys(config.HASHTAGS_BASE + hashtags_extra))

    if len(hashtags_finales) < config.MINIMO_HASHTAGS:
        genericos = ["#modelochilena", "#contenidoexclusivo18", "#fotografia", "#lifestyle", "#viral"]
        for g in genericos:
            if len(hashtags_finales) >= config.MINIMO_HASHTAGS:
                break
            if g not in hashtags_finales:
                hashtags_finales.append(g)

    texto_sin_hashtags = " ".join(
        palabra for palabra in texto.split() if not palabra.startswith("#")
    ).strip()

    return f"{texto_sin_hashtags}\n\n{' '.join(hashtags_finales)}"
