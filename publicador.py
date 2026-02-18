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
    # 1. Conexión con el Puente PHP
    try:
        url = f"https://lapapaya.org/mktg/api_bridge.php?user_id={user_id}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            raise HTTPException(
                status_code=500, 
                detail=f"PHP error {response.status_code}: {response.text}"
            )
        
        user_data = response.json()
        
    except Exception as e:
        # Esto captura el error "line 1 column 1" y te muestra la respuesta real del PHP
        raise HTTPException(
            status_code=500, 
            detail=f"Error en puente PHP o JSON inválido: {str(e)}"
        )

    # 2. Validar que el PHP encontró al usuario
    if user_data.get("status") != "success":
        error_msg = user_data.get("error", "Usuario no encontrado")
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {error_msg}")

    # 3. Generar el contenido
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
