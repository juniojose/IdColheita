# app/models/database.py
import sqlite3
from flask import current_app
from ..utils.logger import setup_logger

logger = setup_logger()

def get_db_connection():
    """Estabelece conexão com o banco de dados SQLite."""
    try:
        db_path = current_app.config["DATABASE_PATH"]
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Retornar como dicionário
        logger.info("Conexão SQLite estabelecida.")
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao SQLite: {str(e)}")
        raise

def init_db(app):
    """Inicializa o banco de dados SQLite e cria as tabelas necessárias."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fornecedores (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                pessoa_de_contato TEXT,
                whatsapp TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS veiculos (
                id TEXT PRIMARY KEY,
                id_fornecedor TEXT NOT NULL,
                placa TEXT NOT NULL,
                ativo TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('ok', 'bloqueado', 'desligado')),
                sequencial INTEGER NOT NULL,
                foto1 TEXT,
                foto2 TEXT,
                FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id)
            )
        """)

        connection.commit()
        logger.info("Tabelas criadas no SQLite com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao inicializar SQLite: {str(e)}")
        raise
    finally:
        connection.close()
        logger.info("Conexão SQLite encerrada.")
