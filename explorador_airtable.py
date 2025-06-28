import os
from dotenv import load_dotenv
from pyairtable import Api

# --- CONFIGURACIÓN ---
# Carga las credenciales del mismo archivo .env
load_dotenv()
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")

# --- SCRIPT DE EXPLORACIÓN ---
if not AIRTABLE_API_KEY:
    print("🔴 ERROR: No se encontró la variable AIRTABLE_API_KEY en tu archivo .env.")
    print("   Asegúrate de que el archivo .env exista en la misma carpeta y contenga la línea:")
    print("   AIRTABLE_API_KEY=tu_llave_que_empieza_con_pat...")
else:
    print("🩺 Iniciando explorador de Airtable...")
    print(f"Usando API Key que empieza con: {AIRTABLE_API_KEY[:8]}...")
    print("-" * 50)

    try:
        api = Api(AIRTABLE_API_KEY)
        # Obtenemos la lista de todas las bases a las que la llave tiene acceso
        bases = api.bases()
        
        if not bases:
            print("⚠️ No se encontró ninguna 'Base' de Airtable accesible por esta API Key.")
            print("   Posible Causa: La API Key es incorrecta o no le diste acceso a ninguna 'Base' cuando la creaste en el Developer Hub de Airtable.")
        else:
            print("✅ ¡Éxito! Tu API Key tiene acceso a lo siguiente:")
            for base in bases:
                print(f"\n🏢 Base: '{base.name}'")
                print(f"   ╚═ BASE ID: {base.id}")
                print(f"     Tablas dentro de esta base:")
                for table in base.tables():
                    print(f"       ├── 📄 Tabla: '{table.name}'")
                    print(f"       │    ╚═ TABLE ID: {table.id}")
                print("-" * 20)

    except Exception as e:
        print(f"🔴 Ocurrió un error inesperado al conectar con Airtable: {e}")

print("\n--- EXPLORACIÓN FINALIZADA ---")