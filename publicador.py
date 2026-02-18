from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import random
import urllib.parse
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generar-contenido")
async def generar_contenido(
    user_id: int = Form(...),
    target_platform: str = Form(...),
    sueno: str = Form("Emprender con propósito"),
    prompts: str = Form("[]")
):
    prompts_list = json.loads(prompts)
    prompt_base = random.choice(prompts_list) if prompts_list else "Sostenibilidad y comunidad"

    texto_ia = (
        f"Genera un post optimizado para {target_platform.upper()}. "
        f"Tema: {prompt_base}. "
        f"Inspiración: {sueno}."
    )
    return {
    "status": "success",
    "prompt_generado": texto_ia,
    "links": {
        "chatgpt": f"https://chat.openai.com/?q={urllib.parse.quote(texto_ia)}",
        "gemini": f"https://gemini.google.com/app?prompt={urllib.parse.quote(prompt_base)}",
        "dalle": f"https://chat.openai.com/?q={urllib.parse.quote('Genera una imagen para: ' + texto_ia)}"
    }
}
```

---

## El nuevo flujo
```
mktg.php → consulta MySQL local → pasa datos al JS → JS llama Render → Render genera contenido
