from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import random
import urllib.parse
import requests 

app = FastAPI(title="Publicador La Papaya")

# Configuración de CORS para permitir la conexión desde lapapaya.org
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "online", "message": "Servidor de La Papaya listo"}

def obtener_datos_usuario(user_id):
    """Consulta el puente PHP usando un GET simple con headers de navegador"""
    try:
        # Headers para evitar el error 415 y bloqueos del servidor
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        url = f"https://lapapaya.org/mktg/api_bridge.php?action=python_query&user_id={user_id}"
        
        # Petición GET limpia
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() 
        return response.json()
    except Exception as e:
        print(f"Error detallado en el puente PHP: {e}")
        return None

@app.post("/generar-contenido")
async def generar_contenido(
    user_id: int = Form(...), 
    target_platform: str = Form(...)
):
    # 1. Obtener datos desde el puente PHP
    user_data = obtener_datos_usuario(user_id)
    
    if not user_data or user_data.get("status") != "success":
        # Este es el error 500 que se captura en el script JS
        raise HTTPException(status_code=500, detail="El puente PHP rechazó la conexión o devolvió un error.")

    # 2. Procesar información real de la base de datos
    prompts = user_data.get("prompts", [])
    prompt_base = random.choice(prompts) if prompts else "Sostenibilidad y comunidad urbana"
    user_sueno = user_data.get("sueno", "Emprender con propósito")
    platform = target_platform.lower()

    # 3. Personalización y construcción del prompt
    texto_ia = f"Actúa como experto en marketing. Crea un post para {platform.upper()}. Tema: {prompt_base}. Conéctalo con este sueño: {user_sueno}. Incluye CTA y hashtags."
    
    # Codificación para los botones de ayuda
    encoded_text = urllib.parse.quote(texto_ia)
    encoded_img = urllib.parse.quote(f"Professional photography, {prompt_base}, high quality")

    return {
        "status": "success",
        "prompt_generado": texto_ia,
        "links_ayuda": {
            "chatgpt_texto": f"https://chat.openai.com/?q={encoded_text}",
            "chatgpt_imagen": f"https://chat.openai.com/?q=Genera+una+imagen+para:+{encoded_img}",
            "gemini_nano_banana": f"https://gemini.google.com/app?prompt={encoded_img}"
        }
    }
