import os
import sys
from dotenv import load_dotenv
from notion_client import Client, APIResponseError

print("--- INICIANDO SCRIPT DE DIAGNÓSTICO DE NOTION ---")

# 1. Cargar configuración
load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

if not NOTION_API_KEY or not NOTION_DATABASE_ID:
    print("🔴 ERROR: Asegúrate de que NOTION_API_KEY y NOTION_DATABASE_ID estén en tu archivo .env.")
    sys.exit()

print(f"Usando Database ID: {NOTION_DATABASE_ID}")
print(f"Usando API Key que empieza con: {NOTION_API_KEY[:8]}...")
print("-" * 50)

# 2. Inicializar cliente
notion = Client(auth=NOTION_API_KEY)

# 3. Prueba N°1: ¿Puedo OBTENER la información de la base de datos?
print("\nPASO 1: Intentando obtener metadatos de la base de datos (retrieve)...")
try:
    db_metadata = notion.databases.retrieve(database_id=NOTION_DATABASE_ID)
    print("✅ ¡ÉXITO! La integración PUEDE ver la base de datos.")
    print("   Nombre detectado:", "".join(part["plain_text"] for part in db_metadata["title"]))
    print("   Propiedades detectadas (Columnas):")
    for prop in db_metadata["properties"]:
        print(f"     - {prop}")
except APIResponseError as e:
    print(f"🔴 ¡FALLO en el Paso 1!")
    print(f"   Error de Notion: {e}")
    print("   Esto confirma que el problema es de raíz: el ID es incorrecto o la integración no tiene el permiso MÁS BÁSICO de acceso.")
    sys.exit()

print("-" * 50)

# 4. Prueba N°2: ¿Puedo BUSCAR (query) en la base de datos?
print("\nPASO 2: Intentando buscar (query) la entrada 'wifi'...")
try:
    query_response = notion.databases.query(
        database_id=NOTION_DATABASE_ID,
        filter={"property": "Pregunta", "title": {"contains": "wifi"}}
    )
    print("✅ ¡ÉXITO! La integración PUEDE realizar búsquedas en la base de datos.")
    if query_response["results"]:
        print("   ¡Se encontraron resultados! La búsqueda funciona.")
    else:
        print("   ⚠️ La búsqueda se ejecutó pero no encontró la fila 'wifi'. Revisa que la entrada exista y esté escrita correctamente.")
        
except APIResponseError as e:
    print(f"🔴 ¡FALLO en el Paso 2!")
    print(f"   Error de Notion: {e}")
    print("   Esto significa que la integración puede 'ver' la base de datos, pero NO tiene permisos para buscar en ella, o que la estructura del filtro es incorrecta (ej: la columna 'Pregunta' no existe o no es de tipo 'Título').")

print("\n--- DIAGNÓSTICO FINALIZADO ---")