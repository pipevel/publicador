from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import random
import urllib.parse
import requests 

app = FastAPI()

# Esto permite que tu web hable con el servidor sin bloqueos de seguridad
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def consultar_datos_papaya(user_id):
    """Obtiene los sueños y prompts reales desde tu PHP"""
    try:
        url = f"https://lapapaya.org/mktg/api_bridge.php?action=python_query&user_id={user_id}"
        # Simulamos un navegador para evitar bloqueos del servidor
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=12)
        return response.json()
    except:
        return None

@app.post("/generar-contenido")
async def generar(user_id: int = Form(...), target_platform: str = Form(...)):
    # 1. Traemos la información de la base de datos
    data = consultar_datos_papaya(user_id)
    
    if not data or data.get("status") != "success":
        # Este es el error que ves actualmente en pantalla
        raise HTTPException(status_code=500, detail="Error de sincronización con La Papaya")

    # 2. Elegimos contenido al azar de lo que el usuario ha escrito
    prompts = data.get("prompts", [])
    base = random.choice(prompts) if prompts else "Sostenibilidad y comunidad"
    sueno = data.get("sueno", "Emprender con propósito")
    
    # 3. Creamos el prompt final
    texto_ia = f"Actúa como experto en marketing. Crea un post para {target_platform.upper()}. Tema: {base}. Basado en este sueño: {sueno}."
    
    return {
        "status": "success",
        "prompt_generado": texto_ia,
        "links_ayuda": {
            "chatgpt": f"https://chat.openai.com/?q={urllib.parse.quote(texto_ia)}",
            "gemini": f"https://gemini.google.com/app?prompt={urllib.parse.quote(base)}"
        }
    }
