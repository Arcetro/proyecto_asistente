import logging
from fastapi import FastAPI
from pydantic import BaseModel
from config import settings # Importamos nuestra configuración centralizada
import airtable_manager     # Importamos nuestros módulos de servicio
import gemini_manager       # Importamos nuestros módulos de servicio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Motor de Conocimiento v2.0 - Refactorizado", version="2.0.0")

class WhatsAppMessage(BaseModel):
    sender_id: str
    message_content: str

@app.post("/webhook")
async def recibir_mensaje_whatsapp(mensaje: WhatsAppMessage): # ¡Ahora es async def!
    logger.info(f"🟢 Mensaje recibido de {mensaje.sender_id}: '{mensaje.message_content}'")
    
    if mensaje.sender_id == settings.ADMIN_PHONE_NUMBER:
        return {"status": "ok", "reply": "Modo Admin reconocido. Lógica pendiente de refactorización."}
    else:
        # --- MODO HUÉSPED ASÍNCRONO Y MODULAR ---
        logger.info(f"👤 Mensaje en Modo Huésped.")
        
        temas = await gemini_manager.identificar_temas(mensaje.message_content)
        
        conocimiento_db = ""
        if temas:
            for tema in temas:
                entrada_encontrada = await airtable_manager.buscar_en_airtable(tema)
                if entrada_encontrada:
                    conocimiento_db += f"- Sobre '{tema}': {entrada_encontrada.get('fields', {}).get('Respuesta', '')}\n"
        
        respuesta_ia = await gemini_manager.formular_respuesta_final(mensaje.message_content, conocimiento_db)
        
        logger.info(f"🤖 Respuesta final enviada: '{respuesta_ia}'")
        return {"status": "ok", "reply": respuesta_ia}