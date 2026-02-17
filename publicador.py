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
    allow_headers=["*"],
    allow_methods=["*"],
)

# --- NUEVA RUTA RAÍZ ---
@app.get("/")
async def root():
    return {
        "mensaje": "Servidor de Publicación La Papaya activo",
        "estado": "Online",
        "endpoints_disponibles": ["/generar-contenido (POST)", "/docs (Swagger)"]
    }

class PublicacionRequest(BaseModel):
    user_id: int
    target_platform: str = "instagram"

def obtener_datos_usuario(user_id):
    try:
        # Forzamos la acción en la URL para evitar ambigüedades
        url_puente = f"https://lapapaya.org/mktg/api_bridge.php?action=python_query&user_id={user_id}"
        
        # Realizamos un GET explícito sin cuerpo de mensaje (body)
        # Esto elimina el error 415 de "Unsupported Media Type"
        response = requests.get(url_puente, timeout=15)
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error crítico llamando al puente PHP: {e}")
        return None

@app.post("/generar-contenido")
async def generar_contenido(request: PublicacionRequest):
    user_data = obtener_datos_usuario(request.user_id)
    
    if not user_data:
        raise HTTPException(status_code=500, detail="Error al conectar con el Bridge.")

    prompts = user_data.get("prompts", [])
    prompt_base = random.choice(prompts) if prompts else "Sostenibilidad y comunidad urbana."
    user_sueno = user_data.get("sueno", "Emprender con propósito social")
    platform = request.target_platform.lower()

    # --- Configuración de Estilos por Plataforma ---
    config_plataformas = {
        "instagram": {"estilo": "Visual e inspirador", "hashtags": "#LaPapaya #Sostenibilidad #CaliCo"},
        "facebook": {"estilo": "Comunitario y conversacional", "hashtags": "#Comunidad #Cali #Proyectos"},
        "linkedin": {"estilo": "Profesional y estratégico", "hashtags": "#ImpactoSocial #ESG #Networking"},
        "tiktok": {"estilo": "Dinámico con guion de video", "hashtags": "#Trend #EcoTips #Cali"},
        "twitter": {"estilo": "Directo y conciso (280 caracteres)", "hashtags": "#LaPapaya #Cali"},
        "whatsapp": {"estilo": "Personal y directo para Estados", "hashtags": ""}
    }

    conf = config_plataformas.get(platform, config_plataformas["instagram"])

    # 1. Prompt de Texto (Copywriting)
    instruccion_ia = f"Actúa como experto en marketing. Genera contenido para {platform.upper()}. Estilo: {conf['estilo']}. Concepto: {prompt_base}. Conecta con el sueño: '{user_sueno}'. Hashtags: {conf['hashtags']}"
    encoded_text_prompt = urllib.parse.quote_plus(instruccion_ia)
    
    # 2. Estilo Visual Editorial
    estilo_editorial = "Editorial photography, soft daylight, muted colors, realistic textures, minimal composition, documentary style"
    prompt_imagen_completo = f"{estilo_editorial} based on: {prompt_base}"
    encoded_img_prompt = urllib.parse.quote_plus(prompt_imagen_completo)
    
    # 3. Prompt de ODS
    prompt_ods = f"Analiza este sueño: '{user_sueno}' bajo los ODS de la ONU."
    encoded_ods = urllib.parse.quote_plus(prompt_ods)
    
    return {
        "platform_selected": platform,
        "prompt_generado": instruccion_ia,
        "links_ayuda": {
            "chatgpt_texto": f"https://chat.openai.com/?model=gpt-4&prompt={encoded_text_prompt}",
            "chatgpt_imagen": f"https://chat.openai.com/?model=gpt-4&prompt=Generate+a+square+social+media+image+with:+{encoded_img_prompt}",
            "gemini_nano_banana": f"https://gemini.google.com/app?prompt={encoded_img_prompt}",
            "ods_link": f"https://chatgpt.com/?q={encoded_ods}",
            "canva": "https://www.canva.com/design/DAGhSGpcZvk/edit"
        }
    }
