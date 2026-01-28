from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import urllib.parse
import os
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

def obtener_prompt_desde_db(user_id):
    try:
        url_puente = f"https://lapapaya.org/mktg/api_bridge.php?user_id={user_id}"
        response = requests.get(url_puente, timeout=10)
        data = response.json()
        
        if "prompts" in data and len(data["prompts"]) > 0:
            return random.choice(data["prompts"])
        return None
        
    except Exception as e:
        print(f"Error llamando al puente PHP: {e}")
        return "error_bridge"

@app.get("/")
def home():
    return {"status": "Online", "mensaje": "Motor de Prompts La Papaya listo."}

@app.post("/generar-contenido")
async def generar_contenido(request: PublicacionRequest):
    prompt_base = obtener_prompt_desde_db(request.user_id)
    
    if prompt_base == "error_bridge":
        raise HTTPException(status_code=500, detail="Error al conectar con la base de datos de La Papaya.")
    
    if not prompt_base:
        raise HTTPException(status_code=404, detail="No se encontraron prompts para este usuario.")

    hashtags = "#ModaCircular #LaPapaya #Sostenibilidad"
    prompt_final = f"{prompt_base}\n\nUsa estos hashtags: {hashtags}"
    
    # Codificamos los prompts para las URLs
    encoded_prompt = urllib.parse.quote_plus(prompt_final)
    
    # Prompt específico para imagen con Nano Banana
    prompt_nano = f"Genera una imagen artística usando el modelo Nano Banana sobre el siguiente concepto: {prompt_base}"
    encoded_nano = urllib.parse.quote_plus(prompt_nano)
    
    return {
        "prompt_generado": prompt_final,
        "links_ayuda": {
            "chatgpt_texto": f"https://chat.openai.com/?model=gpt-4&prompt={encoded_prompt}",
            "chatgpt_imagen": f"https://chat.openai.com/?model=gpt-4&prompt=Haz+una+imagen+cuadrada+para+redes+sociales+basada+en:+{encoded_prompt}",
            "gemini_nano_banana": f"https://gemini.google.com/app?prompt={encoded_nano}",
            "canva": "https://www.canva.com/design/DAGhSGpcZvk/edit"
        }
    }
