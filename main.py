import os
import logging
import json
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
from pyairtable import Api as AirtableApi

# --- 1. CONFIGURACIÓN ---
load_dotenv()
# ... (El resto de la carga de credenciales es igual) ...
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
ADMIN_PHONE_NUMBER = os.getenv("ADMIN_PHONE_NUMBER")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")

if not all([GEMINI_API_KEY, ADMIN_PHONE_NUMBER, AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME]):
    raise ValueError("Faltan credenciales críticas en el .env.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') 
airtable_api = AirtableApi(AIRTABLE_API_KEY)
airtable_table = airtable_api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 2. MAPA DE SINÓNIMOS LOCAL (EL FILTRO INTELIGENTE) ---
MAPA_SINONIMOS = {
    "internet": "wifi",
    "clave": "wifi",
    "contraseña": "wifi",
    "red": "wifi",
    "comida": "desayuno",
    "buffet": "desayuno",
    "alberca": "pileta",
    "piscina": "pileta"
}

# --- 3. MODELOS DE DATOS ---
class WhatsAppMessage(BaseModel):
    sender_id: str
    message_content: str

# --- 4. FUNCIONES DE AIRTABLE ---
def buscar_en_airtable(termino: str) -> dict | None:
    # ... (Sin cambios aquí)
    logger.info(f"🔎 Buscando en Airtable el término clave: '{termino}'")
    try:
        formula = f"OR(LOWER('{termino}') = LOWER({{Pregunta}}), FIND(LOWER('{termino}'), LOWER({{Sinonimos}})))"
        records = airtable_table.all(formula=formula, max_records=1)
        if records:
            return records[0]
        return None
    except Exception as e:
        logger.error(f"🔴 Error al buscar en Airtable: {e}")
        return None

# --- 5. APLICACIÓN FASTAPI ---
app = FastAPI(title="Motor de Conocimiento v1.7 - Filtro Inteligente", version="1.7.0")

@app.post("/webhook")
def recibir_mensaje_whatsapp(mensaje: WhatsAppMessage):
    logger.info(f"🟢 Mensaje recibido de {mensaje.sender_id}: '{mensaje.message_content}'")
    
    if mensaje.sender_id == ADMIN_PHONE_NUMBER:
        return {"status": "ok", "reply": "Modo Admin reconocido. Funcionalidad pendiente."}
    else:
        # --- MODO HUÉSPED CON LÓGICA HÍBRIDA ---
        logger.info(f"👤 Mensaje en Modo Huésped.")
        
        temas_encontrados = []
        # PASO 1: Búsqueda Local Rápida
        for palabra in mensaje.message_content.lower().split():
            if palabra in MAPA_SINONIMOS:
                tema = MAPA_SINONIMOS[palabra]
                if tema not in temas_encontrados:
                    temas_encontrados.append(tema)
        
        if temas_encontrados:
            logger.info(f"✅ Temas identificados por BÚSQUEDA LOCAL: {temas_encontrados}")
        else:
            # PASO 2: Fallback a IA si la búsqueda local no encuentra nada
            logger.warning("⚠️ Búsqueda local no encontró temas, usando fallback de IA...")
            prompt_identificador = f"Analiza la pregunta: '{mensaje.message_content}'. Devuelve una lista JSON con temas clave de esta lista: ['wifi', 'desayuno', 'pileta']."
            response_temas = model.generate_content(prompt_identificador)
            try:
                json_puro = response_temas.text[response_temas.text.find('['):response_temas.text.rfind(']') + 1]
                temas_encontrados = json.loads(json_puro)
                logger.info(f"🧠 Temas identificados por IA: {temas_encontrados}")
            except Exception as e:
                logger.error(f"🔴 Error al parsear temas JSON de la IA: {e}")
                temas_encontrados = []

        # El resto del flujo es el mismo
        conocimiento_db = ""
        if temas_encontrados:
            for tema in temas_encontrados:
                entrada_encontrada = buscar_en_airtable(tema)
                if entrada_encontrada:
                    conocimiento_db += f"- Sobre '{tema}': {entrada_encontrada.get('fields', {}).get('Respuesta', '')}\n"
        
        prompt_final = f"Eres Alex, conserje. Responde amablemente usando esta información: \n{conocimiento_db if conocimiento_db else 'No se encontró información.'}\n\nPregunta: '{mensaje.message_content}'\n\nSi no tienes info, di que consultarás con recepción."
        response_final = model.generate_content(prompt_final)
        respuesta_ia = response_final.text.strip()
        logger.info(f"🤖 Respuesta final generada: '{respuesta_ia}'")
        return {"status": "ok", "reply": respuesta_ia}