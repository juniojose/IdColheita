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
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB = os.getenv("MYSQL_DB")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
    OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER")
    SAFRA = os.getenv("SAFRA")
    VEICULO_IMAGE_DIR = path.join(os.getenv("OUTPUT_FOLDER"), "veiculos")