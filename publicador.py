from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import random
import urllib.parse
import requests 

app = FastAPI(title="Publicador La Papaya")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def obtener_datos_usuario(user_id):
    """Consulta el puente PHP usando un GET simple para evitar el error 415"""
    try:
        # Forzamos los headers para que parezca una navegación normal y evitar bloqueos
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f"https://lapapaya.org/mktg/api_bridge.php?action=python_query&user_id={user_id}"
        
        # Hacemos la petición GET limpia
        response = requests.get(url, headers=headers, timeout=15)
        
        # Si el servidor responde algo que no es JSON, esto fallará y lo veremos en el log
        return response.json()
    except Exception as e:
        print(f"Error detallado en el puente: {e}")
        return None

@app.post("/generar-contenido")
async def generar_contenido(
    user_id: int = Form(...), 
    target_platform: str = Form(...)
):
    # 1. Obtener datos desde PHP
    user_data = obtener_datos_usuario(user_id)
    
    if not user_data or user_data.get("status") != "success":
        # Este es el error 500 que viste en el log
        raise HTTPException(status_code=500, detail="El puente PHP rechazó la conexión o devolvió un error.")

    # 2. Extraer información del JSON exitoso
    prompts = user_data.get("prompts", [])
    prompt_base = random.choice(prompts) if prompts else "Sostenibilidad y comunidad"
    user_sueno = user_data.get("sueno", "Emprender con propósito")
    platform = target_platform.lower()

    # 3. Construcción del contenido
    texto_ia = f"Post para {platform.upper()}: {prompt_base}. Inspirado en el sueño: {user_sueno}."
    encoded_text = urllib.parse.quote(texto_ia)
    encoded_img = urllib.parse.quote(f"Professional photography, {prompt_base}")

    return {
        "status": "success",
        "prompt_generado": texto_ia,
        "links_ayuda": {
            "chatgpt_texto": f"https://chat.openai.com/?q={encoded_text}",
            "chatgpt_imagen": f"https://chat.openai.com/?q=Genera+imagen+para:+{encoded_img}",
            "gemini_nano_banana": f"https://gemini.google.com/app?prompt={encoded_img}"
        }
    }
