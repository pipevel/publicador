from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import random
import urllib.parse
import requests 

app = FastAPI(title="Publicador La Papaya")

# Permitir que tu web lapapaya.org hable con este servidor
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def obtener_datos_usuario(user_id):
    """Consulta el bridge PHP para traer los datos reales de la DB"""
    try:
        url = f"https://lapapaya.org/mktg/api_bridge.php?action=python_query&user_id={user_id}"
        response = requests.get(url, timeout=12) # Tiempo de espera prudente
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error conectando con el puente: {e}")
        return None

@app.post("/generar-contenido")
async def generar_contenido(
    user_id: int = Form(...), 
    target_platform: str = Form(...)
):
    # 1. Obtener la info del usuario (sueños y prompts)
    datos = obtener_datos_usuario(user_id)
    
    if not datos or datos.get("status") != "success":
        raise HTTPException(status_code=500, detail="No se pudo sincronizar con la base de datos de La Papaya")

    # 2. Extraer los datos que vimos en el bridge
    prompts_disponibles = datos.get("prompts", [])
    prompt_base = random.choice(prompts_disponibles) if prompts_disponibles else "Sostenibilidad y comunidad urbana"
    sueno_usuario = datos.get("sueno", "Un futuro mejor para todos")
    
    # 3. Personalización según la red social
    plataforma = target_platform.lower()
    estilos = {
        "instagram": "visual e inspirador",
        "facebook": "comunitario y conversacional",
        "linkedin": "profesional y estratégico",
        "tiktok": "dinámico y divertido",
        "twitter": "directo y conciso",
        "whatsapp": "personal y motivador"
    }
    estilo = estilos.get(plataforma, "creativo")

    # 4. Crear el Prompt Maestro
    texto_ia = (
        f"Actúa como experto en marketing digital. Crea un post para {plataforma.upper()} "
        f"con tono {estilo}. Tema: {prompt_base}. "
        f"Conecta con este sueño: {sueno_usuario}. Incluye hashtags y CTA."
    )
    
    # 5. Codificar para los botones de ayuda
    encoded_text = urllib.parse.quote(texto_ia)
    encoded_img = urllib.parse.quote(f"Professional photography, {prompt_base}, high resolution")

    # 6. Respuesta final para el JavaScript
    return {
        "status": "success",
        "prompt_generado": texto_ia,
        "links_ayuda": {
            "chatgpt_texto": f"https://chat.openai.com/?q={encoded_text}",
            "chatgpt_imagen": f"https://chat.openai.com/?q=Genera+imagen+para:+{encoded_img}",
            "gemini_nano_banana": f"https://gemini.google.com/app?prompt={encoded_img}"
        }
    }
