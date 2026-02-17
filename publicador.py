from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import random
import urllib.parse
import requests 

app = FastAPI(title="Publicador Dinámico La Papaya")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"estado": "Online", "mensaje": "Servidor de La Papaya listo"}

def obtener_datos_usuario(user_id):
    try:
        # Llamamos al puente usando GET que es lo más estable
        url_puente = f"https://lapapaya.org/mktg/api_bridge.php?action=python_query&user_id={user_id}"
        response = requests.get(url_puente, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error en el puente PHP: {e}")
        return None

@app.post("/generar-contenido")
async def generar_contenido(user_id: int = Form(...), target_platform: str = Form(...)):
    # 1. Obtener datos desde el Bridge PHP
    user_data = obtener_datos_usuario(user_id)
    
    if not user_data or user_data.get("status") != "success":
        raise HTTPException(status_code=500, detail="No se pudo obtener información del usuario.")

    # 2. Extraer información
    prompts = user_data.get("prompts", [])
    prompt_base = random.choice(prompts) if prompts else "Sostenibilidad y comunidad urbana."
    user_sueno = user_data.get("sueno", "Emprender con propósito social")
    platform = target_platform.lower()

    # 3. Configuración por plataforma
    config_plataformas = {
        "instagram": {"estilo": "Visual e inspirador", "hashtags": "#LaPapaya #Sostenibilidad"},
        "facebook": {"estilo": "Comunitario y conversacional", "hashtags": "#Comunidad #Cali"},
        "linkedin": {"estilo": "Profesional y estratégico", "hashtags": "#ImpactoSocial #Networking"},
        "tiktok": {"estilo": "Dinámico con guion de video", "hashtags": "#EcoTips #Trend"},
        "twitter": {"estilo": "Directo y conciso", "hashtags": "#LaPapaya #Cali"},
        "whatsapp": {"estilo": "Personal para estados", "hashtags": ""}
    }

    conf = config_plataformas.get(platform, config_plataformas["instagram"])

    # 4. Construcción de Prompts para la IA
    instruccion_ia = f"Genera un post para {platform.upper()}. Estilo: {conf['estilo']}. Concepto: {prompt_base}. Sueño: '{user_sueno}'. Hashtags: {conf['hashtags']}"
    encoded_text = urllib.parse.quote_plus(instruccion_ia)
    
    prompt_img = f"Editorial photography, realistic style, based on: {prompt_base}"
    encoded_img = urllib.parse.quote_plus(prompt_img)
    
    # 5. Respuesta final
    return {
        "platform_selected": platform,
        "prompt_generado": instruccion_ia,
        "links_ayuda": {
            "chatgpt_texto": f"https://chat.openai.com/?model=gpt-4&prompt={encoded_text}",
            "chatgpt_imagen": f"https://chat.openai.com/?model=gpt-4&prompt=Generate+image:+{encoded_img}",
            "gemini_nano_banana": f"https://gemini.google.com/app?prompt={encoded_img}"
        }
    }
