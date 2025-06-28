from pyairtable import Api
from config import settings # Importamos la configuración
import logging

logger = logging.getLogger(__name__)

# Inicializamos el cliente de Airtable una sola vez
api = Api(settings.AIRTABLE_API_KEY)
table = api.table(settings.AIRTABLE_BASE_ID, settings.AIRTABLE_TABLE_NAME)

# La función ahora es asíncrona, aunque la librería subyacente no lo sea.
# FastAPI lo manejará de forma eficiente en un thread separado.
async def buscar_en_airtable(termino: str) -> dict | None:
    logger.info(f"🔎 Buscando en Airtable el término clave: '{termino}'")
    try:
        formula = f"OR(LOWER('{termino}') = LOWER({{Pregunta}}), FIND(LOWER('{termino}'), LOWER({{Sinonimos}})))"
        records = table.all(formula=formula, max_records=1)
        if records:
            record = records[0]
            logger.info(f"✅ Entrada encontrada en Airtable (ID: {record['id']})")
            return record
        logger.warning(f"⚠️ No se encontró el término '{termino}' en Airtable.")
        return None
    except Exception as e:
        logger.error(f"🔴 Error al buscar en Airtable: {e}")
        return None