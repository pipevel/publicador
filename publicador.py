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

# Agregamos una ruta raíz para que Render sepa que el servicio está vivo
@app.get("/")
async def root():
    return {"status": "online", "message": "Servidor de La Papaya listo"}

def obtener_datos_usuario(user_id):
    """Consulta el puente PHP de forma segura"""
    try:
        # Simulamos un navegador para evitar el error 415
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        url = f"https://lapapaya.org/mktg/api_bridge.php?action=python_query&user_id={user_id}"
        
        # Realizamos la petición GET simple
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() 
        return response.json()
    except Exception as e:
        print(f"Error en el puente PHP: {e}")
        return None

@app.post("/generar-contenido")
async def generar_contenido(
    user_id: int = Form(...), 
    target_platform: str = Form(...)
):
    # 1. Obtener datos desde PHP
    user_data = obtener_datos_usuario(user_id)
    
    if not user_data or user_data.get("status") != "success":
        # Si esto falla, verás el error en tu web
        raise HTTPException(status_code=500, detail="No se pudo sincronizar con la base de datos de La Papaya")

    # 2. Extraer información
    prompts = user_data.get("prompts", [])
    prompt_base = random.choice(prompts) if prompts else "Sostenibilidad y comunidad"
    user_sueno = user_data.get("sueno", "Emprender con propósito")
    platform = target_platform.lower()

    # 3. Construcción de los textos
    instruccion_ia = f"Genera un post para {platform.upper()}. Tema: {prompt_base}. Sueño: {user_sueno}."
    encoded_text = urllib.parse.quote(instruccion_ia)
    encoded_img = urllib.parse.quote(f"Professional photography, {prompt_base}, 4k")

    # 4. Respuesta para mktg.php
    return {
        "status": "success",
        "prompt_generado": instruccion_ia,
        "links_ayuda": {
            "chatgpt_texto": f"https://chat.openai.com/?q={encoded_text}",
            "chatgpt_imagen": f"https://chat.openai.com/?q=Genera+imagen+para:+{encoded_img}",
            "gemini_nano_banana": f"https://gemini.google.com/app?prompt={encoded_img}"
        }
    }
