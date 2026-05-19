import os
from dotenv import load_dotenv
from app import create_app
 
# Cargar variables de entorno antes de arrancar
load_dotenv()
 
app = create_app()
 
if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 3002))
    app.run(host="0.0.0.0", port=port, debug=app.config["DEBUG"])
 