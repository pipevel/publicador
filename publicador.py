from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import random
import urllib.parse
import requests 

app = FastAPI(title="Publicador La Papaya")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta raíz para que Render confirme que la app está "viva"
@app.get("/")
async def root():
    return {"status": "online", "message": "Publicador La Papaya Funcionando"}

def obtener_datos_usuario(user_id):
    """Consulta el puente PHP usando un GET simple para evitar el error 415"""
    try:
        # Usamos headers de navegador para que el servidor PHP no bloquee la petición
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'application/json'
        }
        url = f"https://lapapaya.org/mktg/api_bridge.php?action=python_query&user_id={user_id}"
        
        # Petición GET limpia
        response = requests.get(url, headers=headers, timeout=12)
        response.raise_for_status() 
        return response.json()
    except Exception as e:
        print(f"Error detallado en el puente: {e}")
        return None

@app.post("/generar-contenido")
async def generar_contenido(
    user_id: int = Form(...), 
    target_platform: str = Form(...)
):
    # 1. Obtener datos desde PHP (Sueño y Prompts del usuario)
    user_data = obtener_datos_usuario(user_id)
    
    if not user_data or user_data.get("status") != "success":
        # Este error es el que salía en tu alert
        raise HTTPException(status_code=500, detail="No se pudo sincronizar con la base de datos de La Papaya")

    # 2. Extraer información real de la DB
    prompts = user_data.get("prompts", [])
    prompt_base = random.choice(prompts) if prompts else "Sostenibilidad y comunidad"
    user_sueno = user_data.get("sueno", "Emprender con propósito")
    platform = target_platform.lower()

    # 3. Construcción del Prompt Maestro
    texto_ia = f"Genera un post para {platform.upper()}. Tema: {prompt_base}. Sueño: {user_sueno}."
    encoded_text = urllib.parse.quote(texto_ia)
    encoded_img = urllib.parse.quote(f"Professional photography, {prompt_base}, high quality")

    # 4. Respuesta para el mktg.php
    return {
        "status": "success",
        "prompt_generado": texto_ia,
        "links_ayuda": {
            "chatgpt_texto": f"https://chat.openai.com/?q={encoded_text}",
            "chatgpt_imagen": f"https://chat.openai.com/?q=Genera+imagen+para:+{encoded_img}",
            "gemini_nano_banana": f"https://gemini.google.com/app?prompt={encoded_img}"
        }
    }
