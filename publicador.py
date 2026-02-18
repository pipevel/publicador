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
    try:
        # Forzamos que la URL lleve el ID claramente
        url = f"https://lapapaya.org/mktg/api_bridge.php?user_id={user_id}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        # LOG PARA RENDER: Esto te dirá qué está respondiendo el PHP exactamente
        print(f"DEBUG PHP: {response.text}") 
        
        user_data = response.json()
    except Exception as e:
        # Si el PHP falla, devolvemos el error exacto para saber qué pasa
        raise HTTPException(status_code=500, detail=f"Error en puente PHP: {str(e)}")

    if user_data.get("status") != "success":
        # Aquí es donde te salía "Usuario no encontrado"
        raise HTTPException(status_code=500, detail=f"PHP dice: {user_data.get('error', 'Error desconocido')}")

    # ... resto del código igual ...

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
