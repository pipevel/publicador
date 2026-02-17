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
    """Consulta el bridge PHP para traer sueños y prompts del usuario"""
    try:
        url = f"https://lapapaya.org/mktg/api_bridge.php?action=python_query&user_id={user_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error en comunicación con PHP: {e}")
        return None

@app.post("/generar-contenido")
async def generar_contenido(
    user_id: int = Form(...), 
    target_platform: str = Form(...)
):
    # 1. Obtener datos reales de la DB
    user_data = obtener_datos_usuario(user_id)
    
    if not user_data or user_data.get("status") != "success":
        raise HTTPException(status_code=500, detail="No se pudo obtener la información de La Papaya.")

    # 2. Extraer info (Sueños y Prompts activos)
    prompts = user_data.get("prompts", [])
    prompt_base = random.choice(prompts) if prompts else "Comunidad y sostenibilidad."
    user_sueno = user_data.get("sueno", "Emprender con propósito")
    platform = target_platform.lower()

    # 3. Personalización por plataforma
    config = {
        "instagram": "visual y emocional",
        "facebook": "cercano y comunitario",
        "linkedin": "profesional y estratégico",
        "tiktok": "dinámico y divertido",
        "twitter": "conciso y directo",
        "whatsapp": "personal y breve"
    }
    estilo = config.get(platform, "creativo")

    # 4. Construcción del Prompt para la IA
    instruccion_ia = (
        f"Actúa como experto en marketing. Crea un post para {platform.upper()} "
        f"con tono {estilo}. Tema: {prompt_base}. "
        f"Conéctalo con este sueño: {user_sueno}. Incluye CTA y hashtags."
    )
    
    # 5. Codificación para enlaces
    encoded_text = urllib.parse.quote(instruccion_ia)
    encoded_img = urllib.parse.quote(f"Professional photography, {prompt_base}, high quality")
    
    # 6. Respuesta final
    return {
        "status": "success",
        "prompt_generado": instruccion_ia,
        "links_ayuda": {
            "chatgpt_texto": f"https://chat.openai.com/?q={encoded_text}",
            "chatgpt_imagen": f"https://chat.openai.com/?q=Genera+imagen+para:+{encoded_img}",
            "gemini_nano_banana": f"https://gemini.google.com/app?prompt={encoded_img}"
        }
    }
