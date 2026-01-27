from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import urllib.parse

app = FastAPI(title="Publicador La Papaya x ZAREY API")

# IMPORTANTE: Esto permite que tu sitio web lea la API sin errores de bloqueo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción puedes cambiar esto por ["https://lapapaya.org"]
    allow_methods=["*"],
    allow_headers=["*"],
)

class PublicacionRequest(BaseModel):
    categoria: str
    incluir_hashtags: bool = True

# Lista completa de los 30 prompts de Moda Circular (ZAREY x La Papaya)
PROMPTS_MODA = [
    "Crea un post sobre la 'Seda de Plástico': explica cómo el PET recuperado por ZAREY se transforma en fibra textil suave.",
    "Diseña un carrusel educativo: 'El ciclo de vida de una prenda ZAREY', desde el residuo industrial hasta la pasarela.",
    "Haz un reel explicativo mostrando cómo el aprovechamiento de textiles de ZAREY impacta en los ODS 9, 12 y 13.",
    "Publica un post comparativo entre 'Moda Rápida vs Moda Circular', destacando la materia prima de ZAREY.",
    "Crea un carrusel con la frase: 'Tu ropa ya no es solo tela, es trazabilidad y datos' con apoyo de ZAREY.",
    "Haz un post donde expliques cómo la moda circular reduce la huella de carbono y costos para diseñadores locales.",
    "Crea un reel tipo storytelling sobre el viaje de una botella del Papayogging convertida en prenda exclusiva.",
    "Diseña un carrusel con ejemplos de cómo un residuo textil genera impacto social en Cali y rentabilidad.",
    "Publica un post sobre la 'Estética de la Recuperación': cómo los materiales de ZAREY elevan las marcas aliadas.",
    "Crea un carrusel con indicadores clave de moda circular (kg recuperados, agua ahorrada) medidos por ZAREY.",
    "Haz un post comparativo: 'Prenda tradicional vs Prenda circular certificada por ZAREY'.",
    "Crea un reel reflexivo sobre la moda consciente en la descontaminación de los ríos de nuestra región.",
    "Publica un post conectando la limpieza de fibras en Buenaventura con el evento Papayogging.",
    "Diseña un carrusel: '¿Por qué la moda circular atrae más inversión verde?', desde la logística de ZAREY.",
    "Crea un post educativo: 'Blockchain y Moda', explicando cómo el certificado de ZAREY garantiza la verdad ambiental.",
    "Haz un reel mostrando la trazabilidad de una fibra desde el centro de acopio de ZAREY hasta el diseño final.",
    "Diseña un carrusel explicando la 'Tokenización de Retales' para financiar la moda circular en La Papaya.",
    "Publica un post con un caso de una colección de moda tokenizada donde el comprador es socio del impacto.",
    "Crea un carrusel educativo sobre bonos de impacto textil y certificados de aprovechamiento de ZAREY.",
    "Haz un post conectando la preventa de una colección de moda circular con el Papayogging del 16 de junio.",
    "Crea un post de opinión: 'La moda sin trazabilidad es Greenwashing', resaltando los informes de ZAREY.",
    "Diseña un carrusel para marcas de ropa sobre qué buscan los inversionistas ESG en la cadena textil.",
    "Publica un post educativo: 'Del residuo al lujo', mostrando cómo la gestión de ZAREY aumenta el valor de marca.",
    "Crea un reel reflexivo sobre el diseñador como 'curador de materiales recuperados' en alianza con ZAREY.",
    "Diseña un carrusel con métricas de aprovechamiento para empresas que donan dotaciones viejas a ZAREY.",
    "Publica un post invitando al Papayogging: ven a recolectar la materia prima de la moda del futuro.",
    "Crea un post respondiendo a: 'La moda circular es impagable', con argumentos de ahorro y valor futuro.",
    "Diseña un reel compartiendo la visión de Cali como 'Capital de la Moda Circular' gracias a esta alianza.",
    "Publica un post invitando a marcas a certificar su aprovechamiento de residuos con La Papaya y ZAREY.",
    "Video-manifiesto: 'Vestir el Cambio', conectando gestión de ZAREY, tecnología de La Papaya y Papayogging."
]

@app.get("/")
def home():
    return {"status": "Online", "mensaje": "API de La Papaya x ZAREY funcionando correctamente."}

@app.post("/generar-contenido")
async def generar_contenido(request: PublicacionRequest):
    try:
        prompt_base = random.choice(PROMPTS_MODA)
        hashtags = "#ModaCircular #ZAREY #LaPapaya #CaliSostenible #EconomiaCircular #Papayogging"
        
        prompt_final = f"{prompt_base}\n\nUsa estos hashtags: {hashtags}"
        encoded_prompt = urllib.parse.quote_plus(prompt_final)
        
        return {
            "prompt_generado": prompt_final,
            "links_ayuda": {
                "chatgpt_texto": f"https://chat.openai.com/?model=gpt-4&prompt={encoded_prompt}",
                "chatgpt_imagen": f"https://chat.openai.com/?model=gpt-4&prompt=Haz+una+imagen+cuadrada+para+redes+sociales+basada+en:+{encoded_prompt}",
                "canva": "https://www.canva.com/design/DAGhSGpcZvk/edit"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
