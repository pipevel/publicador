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
async def generar_contenido(user_id: int = Form(...), target_platform: str = Form(...)):
    # 1. Intentar conectar con la base de datos de La Papaya
    try:
        url = f"https://lapapaya.org/mktg/api_bridge.php?action=python_query&user_id={user_id}"
        # Añadimos un User-Agent para que el servidor PHP no rechace la petición
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        user_data = response.json()
    except Exception as e:
        print(f"Error de conexión: {e}")
        raise HTTPException(status_code=500, detail="El puente PHP no responde")

    if user_data.get("status") != "success":
        raise HTTPException(status_code=500, detail="Usuario no encontrado en la base de datos")

    # 2. Generar el prompt basado en los datos reales del usuario
    prompts = user_data.get("prompts", [])
    prompt_base = random.choice(prompts) if prompts else "Sostenibilidad y comunidad"
    sueno = user_data.get("sueno", "Emprender con propósito")
    
    texto_ia = f"Genera un post para {target_platform.upper()}. Tema: {prompt_base}. Inspiración: {sueno}."
    
    return {
        "status": "success",
        "prompt_generado": texto_ia,
        "links": {
            "chatgpt": f"https://chat.openai.com/?q={urllib.parse.quote(texto_ia)}",
            "gemini": f"https://gemini.google.com/app?prompt={urllib.parse.quote(prompt_base)}"
        }
    }
