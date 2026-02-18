from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import requests
import random
import urllib.parse

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
    target_platform: str = Form(...)
):

    try:
        response = requests.post(
    "https://lapapaya.org/mktg/api_bridge.php",
    json={"user_id": user_id},
    timeout=10
)




        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"PHP error {response.status_code}: {response.text}"
            )

        try:
            user_data = response.json()
        except Exception:
            raise HTTPException(
                status_code=500,
                detail=f"Respuesta no es JSON válido: {response.text}"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en conexión con puente PHP: {str(e)}"
        )

    # Validación de respuesta del PHP
    if user_data.get("status") != "success":
        error_msg = user_data.get("error", "Usuario no encontrado")
        raise HTTPException(
            status_code=500,
            detail=f"Error de base de datos: {error_msg}"
        )

    # Generar contenido
    prompts = user_data.get("prompts") or []
    prompt_base = random.choice(prompts) if prompts else "Sostenibilidad y comunidad"
    sueno = user_data.get("sueno", "Emprender con propósito")

    texto_ia = (
        f"Genera un post optimizado para {target_platform.upper()}. "
        f"Tema: {prompt_base}. "
        f"Inspiración: {sueno}."
    )

    return {
        "status": "success",
        "prompt_generado": texto_ia,
        "links": {
            "chatgpt": f"https://chat.openai.com/?q={urllib.parse.quote(texto_ia)}",
            "gemini": f"https://gemini.google.com/app?prompt={urllib.parse.quote(prompt_base)}"
        }
    }
