from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import urllib.parse
import requests 

app = FastAPI(title="Publicador Dinámico La Papaya")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PublicacionRequest(BaseModel):
    user_id: int

def obtener_datos_usuario(user_id):
    try:
        url_puente = f"https://lapapaya.org/mktg/api_bridge.php?user_id={user_id}"
        response = requests.get(url_puente, timeout=10)
        # Si el bridge falla, lanzamos error
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error llamando al puente PHP: {e}")
        return None

@app.get("/")
def home():
    return {"status": "Online", "mensaje": "Motor de Prompts La Papaya listo."}

@app.post("/generar-contenido")
async def generar_contenido(request: PublicacionRequest):
    user_data = obtener_datos_usuario(request.user_id)
    
    if not user_data:
        raise HTTPException(status_code=500, detail="Error al conectar con el Bridge de La Papaya.")

    # Extraer datos del JSON del Bridge
    prompts = user_data.get("prompts", [])
    prompt_base = random.choice(prompts) if prompts else "Moda circular y sostenibilidad."
    user_sueno = user_data.get("sueno", "Emprender en economía circular")

    # 1. Configuración de Post de Texto (ChatGPT)
    hashtags = "#ModaCircular #LaPapaya #Sostenibilidad"
    prompt_final = f"{prompt_base}\n\nUsa estos hashtags: {hashtags}"
    encoded_prompt = urllib.parse.quote_plus(prompt_final)
    
    # 2. Configuración de Imagen (Nano Banana / Gemini)
    prompt_nano = f"Genera una imagen artística usando el modelo Nano Banana sobre el siguiente concepto: {prompt_base}"
    encoded_nano = urllib.parse.quote_plus(prompt_nano)
    
    # 3. Configuración de ODS (Alineación del Sueño)
    # Nota: Aquí quitamos la etiqueta de imagen que causó el error
    prompt_ods = f"""Actúa como un experto en sostenibilidad de la ONU. 
Mi sueño es: "{user_sueno}". 
Analiza este sueño y alinéalo con al menos 3 de los 17 Objetivos de Desarrollo Sostenible (ODS).
Explica cómo este sueño contribuye a la Prosperidad, las Personas o el Planeta.
Genera una hoja de ruta técnica para que este sueño sea una realidad sostenible."""
    
    encoded_ods = urllib.parse.quote_plus(prompt_ods)
    
    return {
        "prompt_generado": prompt_final,
        "links_ayuda": {
            "chatgpt_texto": f"https://chat.openai.com/?model=gpt-4&prompt={encoded_prompt}",
            "chatgpt_imagen": f"https://chat.openai.com/?model=gpt-4&prompt=Haz+una+imagen+cuadrada+para+redes+sociales+basada+en:+{encoded_prompt}",
            "gemini_nano_banana": f"https://gemini.google.com/app?prompt={encoded_nano}",
            "ods_link": f"https://chatgpt.com/?q={encoded_ods}",
            "canva": "https://www.canva.com/design/DAGhSGpcZvk/edit"
        }
    }
