# app/config.py
from os import path
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, "../.env"))

class Config:
    """Configurações da aplicação Flask."""
    SECRET_KEY = os.getenv("SECRET_KEY")
    DATABASE_PATH = os.path.join(basedir, "../app.sqlite3")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
    SAFRA = os.getenv("SAFRA")

    # Verificar se OUTPUT_FOLDER está definido
    OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER")
    if not OUTPUT_FOLDER:
        raise ValueError("A variável de ambiente OUTPUT_FOLDER não está definida no .env")

    VEICULO_IMAGE_DIR = path.join(os.getenv("OUTPUT_FOLDER"), "veiculos")