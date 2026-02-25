from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import random
import urllib.parse
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generar-contenido")
async def generar_contenido(
    user_id: int = Form(...),
    target_platform: str = Form(...),
    sueno: str = Form("Emprender con propósito"),
    prompts: str = Form("[]"),
    url_tienda: str = Form(...)  # <--- Nuevo parámetro
):
    prompts_list = json.loads(prompts)
    tema = random.choice(prompts_list) if prompts_list else "Propósito y comunidad"

    # Instrucción de ventas de alto impacto
    texto_ia = (
        f"Actúa como un Copywriter de respuesta directa experto en {target_platform.upper()}. "
        f"Tu objetivo es generar una venta o visita. Tema: {tema}. Propósito: {sueno}. "
        f"Escribe un post que use un gancho emocional y termine OBLIGATORIAMENTE con un "
        f"Call to Action claro que incluya este enlace: {url_tienda}"
    )

    return {
        "status": "success",
        "prompt_generado": texto_ia,
        "links": {
            "chatgpt": f"https://chat.openai.com/?q={urllib.parse.quote(texto_ia)}",
            "gemini": f"https://gemini.google.com/app?prompt={urllib.parse.quote(texto_ia)}",
            "dalle": f"https://chat.openai.com/?q={urllib.parse.quote('Crea una imagen visualmente impactante y profesional sobre: ' + tema)}"
        }
    }}
