# app/utils/logger.py
import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger():
    """Configura o logger para a aplicação."""
    logger = logging.getLogger("IdColheita")
    logger.setLevel(logging.INFO)

    # Evitar múltiplos handlers
    if not logger.handlers:
        # Configurar handler para arquivo com rotação (máximo 5MB, até 5 arquivos)
        log_handler = RotatingFileHandler(
            "idcolheita.log", maxBytes=5 * 1024 * 1024, backupCount=5
        )
        log_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        logger.addHandler(log_handler)

    return logger