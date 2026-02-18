from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import random
import urllib.parse
import requests 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def obtener_datos_usuario(user_id):
    """Consulta el puente PHP simulando un navegador para evitar bloqueos"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f"https://lapapaya.org/mktg/api_bridge.php?action=python_query&user_id={user_id}"
        # Usamos GET para máxima compatibilidad con tu servidor actual
        response = requests.get(url, headers=headers, timeout=12)
        response.raise_for_status() 
        return response.json()
    except Exception as e:
        print(f"Error en puente PHP: {e}")
        return None

@app.post("/generar-contenido")
async def generar_contenido(user_id: int = Form(...), target_platform: str = Form(...)):
    user_data = obtener_datos_usuario(user_id)
    
    if not user_data or user_data.get("status") != "success":
        # Este error se captura en tu alert de la web
        raise HTTPException(status_code=500, detail="Error de sincronización con La Papaya")

    prompts = user_data.get("prompts", [])
    prompt_base = random.choice(prompts) if prompts else "Sostenibilidad y comunidad"
    user_sueno = user_data.get("sueno", "Emprender con propósito")
    
    # Construcción del prompt que se copiará al portapapeles
    texto_ia = f"Genera un post para {target_platform.upper()}. Tema: {prompt_base}. Sueño: {user_sueno}."
    
    return {
        "status": "success",
        "prompt_generado": texto_ia,
        "links_ayuda": {
            "chatgpt_texto": f"https://chat.openai.com/?q={urllib.parse.quote(texto_ia)}",
            "gemini_nano_banana": f"https://gemini.google.com/app?prompt={urllib.parse.quote(prompt_base)}"
        }
    }
