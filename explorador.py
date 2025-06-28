import os
from dotenv import load_dotenv
from notion_client import Client, APIResponseError

# Carga las credenciales del mismo archivo .env
load_dotenv()
notion_token = os.getenv("NOTION_API_KEY")

# Verifica si la llave de Notion existe
if not notion_token:
    print("🔴 ERROR: No se encontró la variable NOTION_API_KEY en el archivo .env.")
    exit()

# Inicializa el cliente
notion = Client(auth=notion_token)

print("🩺 Iniciando explorador de Notion...")
print("-" * 30)

try:
    # El método search() busca todo a lo que la integración tiene acceso
    search_results = notion.search()["results"]
    
    if not search_results:
        print("⚠️ No se encontró ningún contenido.")
        print("Esto confirma que la integración NO TIENE ACCESO a ninguna página o base de datos.")
        print("SOLUCIÓN: Volvé a Notion, andá al menú 'Share' de tu página 'Conocimiento Q&A' e invitá a tu integración ('ConectorMaestro') con permisos 'Can edit'.")
    else:
        print("✅ ¡Éxito! La integración tiene acceso al siguiente contenido:")
        for item in search_results:
            item_type = item.get("object")
            item_id = item.get("id")
            title = "Sin Título"
            
            if item_type == "database":
                # Si es una base de datos, el título está en la propiedad 'title'
                title_list = item.get("title", [])
                if title_list:
                    title = title_list[0].get("plain_text", "Base de datos sin título")
            elif item_type == "page":
                 # Si es una página, el título está dentro de las propiedades
                title_prop = item.get("properties", {}).get("Name", {}) # Notion a veces usa 'Name' o 'title'
                if not title_prop:
                    title_prop = item.get("properties", {}).get("title", {})
                
                title_list = title_prop.get("title", [])
                if title_list:
                    title = title_list[0].get("plain_text", "Página sin título")

            print(f"  - Título: {title}")
            print(f"    Tipo: {item_type}")
            print(f"    ID:   {item_id}")
            print("-" * 20)

except APIResponseError as e:
    print(f"🔴 ERROR DE API NOTION: {e}")
    print("Esto usualmente significa que tu NOTION_API_KEY es inválida o ha sido revocada.")

except Exception as e:
    print(f"🔴 Ocurrió un error inesperado: {e}")