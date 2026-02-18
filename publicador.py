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
        # Usamos GET simple para máxima compatibilidad
        response = requests.get(url, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

@app.post("/generar-contenido")
async def generar_contenido(user_id: int = Form(...), target_platform: str = Form(...)):
    user_data = obtener_datos_usuario(user_id)
    
    if not user_data or user_data.get("status") != "success":
        # Este error es el que ves en el alert de la web
        raise HTTPException(status_code=500, detail="Error de sincronización con La Papaya")

    prompts = user_data.get("prompts", [])
    prompt_base = random.choice(prompts) if prompts else "Sostenibilidad"
    user_sueno = user_data.get("sueno", "Emprender")
    
    texto_final = f"Post para {target_platform.upper()}: {prompt_base}. Inspirado en: {user_sueno}."
    
    return {
        "status": "success",
        "prompt_generado": texto_final,
        "links_ayuda": {
            "chatgpt": f"https://chat.openai.com/?q={urllib.parse.quote(texto_final)}",
            "gemini": f"https://gemini.google.com/app?prompt={urllib.parse.quote(prompt_base)}"
        }
    }
