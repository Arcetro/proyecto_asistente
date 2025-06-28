import google.generativeai as genai
from config import settings # Importamos la configuración
import logging
import json

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def identificar_temas(texto_pregunta: str) -> list:
    logger.info("🧠 IA identificando temas...")
    prompt = f"Analiza la pregunta: '{texto_pregunta}'. Devuelve una lista JSON con temas clave de esta lista: ['wifi', 'desayuno', 'pileta']. Si preguntan por internet o clave, el tema es 'wifi'."
    try:
        response = await model.generate_content_async(prompt)
        json_puro = response.text[response.text.find('['):response.text.rfind(']') + 1]
        temas = json.loads(json_puro)
        logger.info(f"✅ Temas identificados por IA: {temas}")
        return temas
    except Exception as e:
        logger.error(f"🔴 Error al identificar temas con IA: {e}")
        return []

async def formular_respuesta_final(pregunta: str, conocimiento: str) -> str:
    logger.info("🤖 IA formulando respuesta final...")
    prompt = f"Eres Alex, conserje. Responde amablemente la pregunta del huésped usando esta información: \n{conocimiento if conocimiento else 'No se encontró información.'}\n\nPregunta: '{pregunta}'\n\nSi no tienes info, di que consultarás con recepción."
    try:
        response = await model.generate_content_async(prompt)
        logger.info("✅ Respuesta final formulada.")
        return response.text.strip()
    except Exception as e:
        logger.error(f"🔴 Error al formular respuesta con IA: {e}")
        return "Disculpe, estoy teniendo un problema técnico para formular la respuesta."