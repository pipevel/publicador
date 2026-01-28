from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import urllib.parse
import requests 

app = FastAPI(title="Publicador Dinámico La Papaya")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PublicacionRequest(BaseModel):
    user_id: int

def obtener_datos_usuario(user_id):
    """Obtiene tanto el prompt como el sueño desde el bridge PHP"""
    try:
        url_puente = f"https://lapapaya.org/mktg/api_bridge.php?user_id={user_id}"
        response = requests.get(url_puente, timeout=10)
        data = response.json()
        
        # Retornamos todo el diccionario de datos
        return data
    except Exception as e:
        print(f"Error llamando al puente PHP: {e}")
        return None

@app.post("/generar-contenido")
async def generar_contenido(request: PublicacionRequest):
    user_data = obtener_datos_usuario(request.user_id)
    
    if not user_data:
        raise HTTPException(status_code=500, detail="Error al conectar con la base de datos.")

    # Extraer prompt (si no hay, usamos uno por defecto)
    prompts = user_data.get("prompts", [])
    prompt_base = random.choice(prompts) if prompts else "Moda circular y sostenibilidad."
    
    # Extraer sueño (si no hay, mensaje genérico)
    user_sueno = user_data.get("sueno", "Emprender en economía circular")

    # 1. Configuración de Post de Texto
    hashtags = "#ModaCircular #LaPapaya #Sostenibilidad"
    prompt_final = f"{prompt_base}\n\nUsa estos hashtags: {hashtags}"
    encoded_prompt = urllib.parse.quote_plus(prompt_final)
    
    # 2. Configuración de Imagen (Nano Banana)
    prompt_nano = f"Genera una imagen artística estilo Nano Banana sobre: {prompt_base}"
    encoded_nano = urllib.parse.quote_plus(prompt_nano)
    
    # 3. Configuración de ODS (Sueño)
    

[Image of sustainable development goals UN]

    prompt_ods = f"""Actúa como experto en sostenibilidad ONU. Mi sueño es: "{user_sueno}". 
    Alinéalo con 3 ODS y genera una hoja de ruta técnica para hacerlo realidad."""
    encoded_ods = urllib.parse.quote_plus(prompt_ods)
    
    return {
        "prompt_generado": prompt_final,
        "links_ayuda": {
            "chatgpt_texto": f"https://chat.openai.com/?model=gpt-4&prompt={encoded_prompt}",
            "chatgpt_imagen": f"https://chat.openai.com/?model=gpt-4&prompt=Imagen+para+redes:+{encoded_prompt}",
            "gemini_nano_banana": f"https://gemini.google.com/app?prompt={encoded_nano}",
            "ods_link": f"https://chatgpt.com/?q={encoded_ods}",
            "canva": "https://www.canva.com/design/DAGhSGpcZvk/edit"
        }
    }
