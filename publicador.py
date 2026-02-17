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

def obtener_datos_del_puente(user_id):
    """Consulta el api_bridge.php de La Papaya"""
    try:
        # Usamos la URL que ya probamos que funciona con user_id=2
        url = f"https://lapapaya.org/mktg/api_bridge.php?action=python_query&user_id={user_id}"
        response = requests.get(url, timeout=10)
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
    # 1. Obtener datos de la DB a través del puente
    datos = obtener_datos_del_puente(user_id)
    
    if not datos or datos.get("status") != "success":
        raise HTTPException(status_code=500, detail="Error al conectar con la base de datos de La Papaya")

    # 2. Extraer información del usuario
    prompts_disponibles = datos.get("prompts", [])
    base_prompt = random.choice(prompts_disponibles) if prompts_disponibles else "Emprendimiento y sostenibilidad"
    sueno_usuario = datos.get("sueno", "Un futuro mejor")
    
    # 3. Personalización por plataforma
    plataforma = target_platform.lower()
    estilos = {
        "instagram": "visual y emocional",
        "facebook": "comunitario y cercano",
        "linkedin": "profesional y estratégico",
        "tiktok": "dinámico y divertido",
        "twitter": "conciso y directo",
        "whatsapp": "personal y motivador"
    }
    estilo = estilos.get(plataforma, "creativo")

    # 4. Construcción del Prompt Maestro
    texto_ia = (
        f"Actúa como experto en marketing. Crea un post para {plataforma.upper()} "
        f"con tono {estilo}. Tema: {base_prompt}. "
        f"Incluye la esencia de: {sueno_usuario}. "
        f"Agrega 3 hashtags relevantes y un llamado a la acción."
    )
    
    # 5. Codificación para URLs
    encoded_text = urllib.parse.quote(texto_ia)
    encoded_img = urllib.parse.quote(f"Professional photography, {base_prompt}, sustainability style, 4k")

    # 6. Respuesta para el mktg.php
    return {
        "status": "success",
        "platform_selected": plataforma,
        "prompt_generado": texto_ia,
        "links_ayuda": {
            "chatgpt_texto": f"https://chat.openai.com/?q={encoded_text}",
            "chatgpt_imagen": f"https://chat.openai.com/?q=Genera+una+imagen+para:+{encoded_img}",
            "gemini_nano_banana": f"https://gemini.google.com/app?prompt={encoded_img}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
