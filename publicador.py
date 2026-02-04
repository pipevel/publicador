from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import urllib.parse
import requests 

app = FastAPI(title="Publicador Dinámico Multi-Red La Papaya")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PublicacionRequest(BaseModel):
    user_id: int
    target_platform: str = "instagram"

def obtener_datos_usuario(user_id):
    try:
        url_puente = f"https://lapapaya.org/mktg/api_bridge.php?user_id={user_id}"
        response = requests.get(url_puente, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error llamando al puente PHP: {e}")
        return None

@app.post("/generar-contenido")
async def generar_contenido(request: PublicacionRequest):
    user_data = obtener_datos_usuario(request.user_id)
    
    if not user_data:
        raise HTTPException(status_code=500, detail="Error al conectar con el Bridge.")

    prompts = user_data.get("prompts", [])
    prompt_base = random.choice(prompts) if prompts else "Economía circular y colaboración social."
    user_sueno = user_data.get("sueno", "Emprender con propósito")
    platform = request.target_platform.lower()

    # --- Lógica de Personalización Expandida ---
    config_plataformas = {
        "instagram": {
            "estilo": "Visual, inspirador y cercano. Usa emojis.",
            "formato": "Post cuadrado o Reel.",
            "hashtags": "#LaPapaya #Sostenibilidad #CaliCo",
            "img_style": "Estética limpia, colores vibrantes, luz natural."
        },
        "facebook": {
            "estilo": "Informativo y comunitario. Ideal para grupos.",
            "formato": "Post con imagen horizontal.",
            "hashtags": "#Comunidad #Cali #ProyectosSociales",
            "img_style": "Personas colaborando, ambiente real."
        },
        "linkedin": {
            "estilo": "Profesional, estratégico y orientado a impacto ESG.",
            "formato": "Post de opinión profesional.",
            "hashtags": "#Liderazgo #ImpactoSocial #ESG #Networking",
            "img_style": "Minimalista, profesional, alta calidad."
        },
        "tiktok": {
            "estilo": "Dinámico, con hook fuerte y lenguaje de tendencia.",
            "formato": "Guion para video vertical 9:16.",
            "hashtags": "#Trend #EcoTips #Cali #StoryTime",
            "img_style": "Estilo POV, dinámico, urbano."
        },
        "twitter": {
            "estilo": "Conciso, directo y provocador de debate. Máximo 280 caracteres.",
            "formato": "Tweet o inicio de hilo.",
            "hashtags": "#LaPapaya #Cali #Sostenible",
            "img_style": "Infografía simple, fotografía de alto contraste."
        },
        "whatsapp": {
            "estilo": "Personal, urgente y muy directo. Formato de 'Estado'.",
            "formato": "Texto corto con invitación a chatear.",
            "hashtags": "",
            "img_style": "Cercano, tipo selfie o foto de proceso real."
        }
    }

    conf = config_plataformas.get(platform, config_plataformas["instagram"])

    # 1. Prompt de Texto
    instruccion_ia = f"""Actúa como experto en marketing digital. Genera contenido para {platform.upper()}.
Estilo: {conf['estilo']}
Formato: {conf['formato']}
Concepto: {prompt_base}
Conecta con este sueño: "{user_sueno}".
Incluye un Call to Action claro.
Hashtags: {conf['hashtags']}"""

    encoded_prompt = urllib.parse.quote_plus(instruccion_ia)
    
    # 2. Prompt de Imagen
    prompt_img_final = f"{conf['img_style']} concepto: {prompt_base}. Professional photography."
    encoded_img = urllib.parse.quote_plus(prompt_img_final)
    
    # 3. Prompt de ODS
    prompt_ods = f"Analiza este sueño: '{user_sueno}' bajo el marco de los ODS de la ONU."
    encoded_ods = urllib.parse.quote_plus(prompt_ods)
    
    return {
        "platform_selected": platform,
        "prompt_generado": instruccion_ia,
        "links_ayuda": {
            "chatgpt_texto": f"https://chat.openai.com/?model=gpt-4&prompt={encoded_prompt}",
            "chatgpt_imagen": f"https://chat.openai.com/?model=gpt-4&prompt=Genera+una+imagen+para+{platform}+estilo+{encoded_img}",
            "gemini_nano_banana": f"https://gemini.google.com/app?prompt={encoded_img}",
            "ods_link": f"https://chatgpt.com/?q={encoded_ods}",
            "canva": "https://www.canva.com/design/DAGhSGpcZvk/edit"
        }
    }
