import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

# Crear directorio de logs si no existe
logs_dir = Path(__file__).parent.parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Configurar logger
logger = logging.getLogger("card-service")
logger.setLevel(logging.DEBUG)

# Formato de logs
formatter = logging.Formatter(
    fmt='[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Handler para archivo combinado
combined_handler = RotatingFileHandler(
    logs_dir / "combined.log",
    maxBytes=5 * 1024 * 1024,  # 5MB
    backupCount=10
)
combined_handler.setLevel(logging.DEBUG)
combined_handler.setFormatter(formatter)

# Handler para errores
error_handler = RotatingFileHandler(
    logs_dir / "error.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=5
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

# Handler para transacciones
transaction_handler = RotatingFileHandler(
    logs_dir / "transactions.log",
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=20
)
transaction_handler.setLevel(logging.INFO)
transaction_formatter = logging.Formatter(
    fmt='%(asctime)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
transaction_handler.setFormatter(transaction_formatter)

# Console handler (solo en desarrollo)
if os.getenv("FLASK_DEBUG", "false").lower() == "true":
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

logger.addHandler(combined_handler)
logger.addHandler(error_handler)

# Logger específico para transacciones
transaction_logger = logging.getLogger("card-service.transactions")
transaction_logger.addHandler(transaction_handler)
transaction_logger.setLevel(logging.INFO)
