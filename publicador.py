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

def obtener_datos_usuario(user_id):
    """Consulta el puente PHP usando un GET simple para evitar el error 415"""
    try:
        # Simulamos un navegador para que el servidor PHP no bloquee la petición
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        url = f"https://lapapaya.org/mktg/api_bridge.php?action=python_query&user_id={user_id}"
        
        # Petición GET limpia y directa
        response = requests.get(url, headers=headers, timeout=15)
        
        # Si el servidor responde con error (como el 415 anterior), esto lo capturará
        response.raise_for_status() 
        return response.json()
    except Exception as e:
        print(f"Error detallado en la conexión con PHP: {e}")
        return None

@app.post("/generar-contenido")
async def generar_contenido(
    user_id: int = Form(...), 
    target_platform: str = Form(...)
):
    # 1. Obtener datos desde PHP (Puente validado para ID 2)
    user_data = obtener_datos_usuario(user_id)
    
    if not user_data or user_data.get("status") != "success":
        # Este es el error 500 que viste en tus logs
        raise HTTPException(status_code=500, detail="El puente PHP rechazó la conexión o el ID no es válido.")

    # 2. Extraer información (Sueños y Prompts)
    prompts = user_data.get("prompts", [])
    prompt_base = random.choice(prompts) if prompts else "Sostenibilidad y comunidad urbana"
    user_sueno = user_data.get("sueno", "Emprender con propósito")
    platform = target_platform.lower()

    # 3. Construcción de los textos para la IA
    instruccion_ia = f"Genera un post para {platform.upper()}. Tema: {prompt_base}. Sueño: {user_sueno}."
    encoded_text = urllib.parse.quote(instruccion_ia)
    encoded_img = urllib.parse.quote(f"Professional photography, {prompt_base}, 4k resolution")

    # 4. Respuesta para el JavaScript de mktg.php
    return {
        "status": "success",
        "prompt_generado": instruccion_ia,
        "links_ayuda": {
            "chatgpt_texto": f"https://chat.openai.com/?q={encoded_text}",
            "chatgpt_imagen": f"https://chat.openai.com/?q=Genera+imagen+para:+{encoded_img}",
            "gemini_nano_banana": f"https://gemini.google.com/app?prompt={encoded_img}"
        }
    }
