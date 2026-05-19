import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "service-mastercard"))

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3002, debug=app.config["DEBUG"])
