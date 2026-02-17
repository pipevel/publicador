from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import random
import urllib.parse
import requests 

app = FastAPI(title="Publicador La Papaya")

# Configuración de CORS para que tu web pueda hablar con Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def obtener_datos_del_puente(user_id):
    """Consulta el api_bridge.php para traer los sueños y prompts del usuario"""
    try:
        # Usamos GET porque tu puente ya está validado para este método
        url = f"https://lapapaya.org/mktg/api_bridge.php?action=python_query&user_id={user_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error conectando con el puente: {e}")
        return None

@app.post("/generar-contenido")
async def generar_contenido(user_id: int = Form(...), target_platform: str = Form(...)):
    # 1. Obtener los datos reales de tu base de datos a través del puente
    datos = obtener_datos_del_puente(user_id)
    
    if not datos or datos.get("status") != "success":
        raise HTTPException(status_code=500, detail="No se pudo obtener la info del puente PHP")

    # 2. Extraer la info (usando los campos que definimos en api_bridge.php)
    prompts_disponibles = datos.get("prompts", [])
    # Elegimos un prompt al azar de los que el usuario tiene activos
    base_prompt = random.choice(prompts_disponibles) if prompts_disponibles else "Emprendimiento sostenible"
    sueno_usuario = datos.get("sueno", "Un mundo mejor")
    
    # 3. Personalizar según la red social elegida
    plataforma = target_platform.lower()
    estilos = {
        "instagram": "visual, emocional y lleno de energía",
        "facebook": "cercano, comunitario y narrativo",
        "linkedin": "profesional, estratégico y con autoridad",
        "tiktok": "dinámico, divertido y con ritmo de video",
        "whatsapp": "directo, personal y motivador"
    }
    estilo = estilos.get(plataforma, "creativo")

    # 4. Crear el super-prompt para ChatGPT/IA
    texto_ia = (
        f"Actúa como un experto en marketing. Crea un post para {plataforma.upper()} "
        f"con un tono {estilo}. El tema central es: {base_prompt}. "
        f"Incluye la esencia de este sueño: {sueno_usuario}. "
        f"Termina con un llamado a la acción potente."
    )
    
    # 5. Codificar para que los enlaces funcionen con espacios y tildes
    encoded_text = urllib.parse.quote(texto_ia)
    encoded_img = urllib.parse.quote(f"Cinematic photo, {base_prompt}, high resolution, sustainability style")

    # 6. Devolver la respuesta que espera tu mktg.php
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
