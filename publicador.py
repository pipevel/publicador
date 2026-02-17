from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import random
import urllib.parse
import requests 

app = FastAPI(title="Publicador Estratégico La Papaya")

# Configuración de CORS para permitir la conexión desde lapapaya.org
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def obtener_datos_usuario(user_id):
    """Consulta el api_bridge.php para obtener sueños y prompts"""
    try:
        # Usamos la URL que ya verificamos manualmente
        url_puente = f"https://lapapaya.org/mktg/api_bridge.php?action=python_query&user_id={user_id}"
        response = requests.get(url_puente, timeout=12)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error en comunicación con el puente PHP: {e}")
        return None

@app.post("/generar-contenido")
async def generar_contenido(
    user_id: int = Form(...), 
    target_platform: str = Form(...)
):
    # 1. Obtener datos reales de la base de datos
    user_data = obtener_datos_usuario(user_id)
    
    if not user_data or user_data.get("status") != "success":
        raise HTTPException(status_code=500, detail="No se pudo sincronizar con la base de datos de La Papaya")

    # 2. Extraer información (Sueños y Prompts)
    prompts = user_data.get("prompts", [])
    prompt_base = random.choice(prompts) if prompts else "Sostenibilidad y comunidad urbana."
    user_sueno = user_data.get("sueno", "Emprender con propósito")
    platform = target_platform.lower()

    # 3. Personalización por plataforma
    config = {
        "instagram": "visual, inspirador y con mucha energía",
        "facebook": "cercano, comunitario y narrativo",
        "linkedin": "profesional, estratégico y corporativo",
        "tiktok": "dinámico, entretenido y con guion rápido",
        "twitter": "directo, ingenioso y conciso",
        "whatsapp": "personal, motivador y breve"
    }
    estilo = config.get(platform, "creativo")

    # 4. Construcción del Prompt para la IA
    instruccion_ia = (
        f"Actúa como un experto en Marketing Digital. Crea un post para {platform.upper()} "
        f"con un tono {estilo}. El tema es: {prompt_base}. "
        f"Conéctalo con este sueño: {user_sueno}. Incluye 3 hashtags y un CTA."
    )
    
    # 5. Codificación para enlaces externos
    encoded_text = urllib.parse.quote(instruccion_ia)
    prompt_visual = f"Cinematic photography, {prompt_base}, high quality, La Papaya style"
    encoded_img = urllib.parse.quote(prompt_visual)
    
    # 6. Respuesta final al navegador
    return {
        "status": "success",
        "prompt_generado": instruccion_ia,
        "links_ayuda": {
            "chatgpt_texto": f"https://chat.openai.com/?q={encoded_text}",
            "chatgpt_imagen": f"https://chat.openai.com/?q=Genera+una+imagen+para:+{encoded_img}",
            "gemini_nano_banana": f"https://gemini.google.com/app?prompt={encoded_img}"
        }
    }
