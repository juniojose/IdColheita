# app/models/database.py
import mysql.connector
from mysql.connector import Error
from flask import current_app
from ..utils.logger import setup_logger  # Alterado de .utils.logger para ..utils.logger

logger = setup_logger()

def get_db_connection():
    """Estabelece conexão com o banco de dados MySQL."""
    try:
        connection = mysql.connector.connect(
            host=current_app.config["MYSQL_HOST"],
            user=current_app.config["MYSQL_USER"],
            password=current_app.config["MYSQL_PASSWORD"],
            database=current_app.config["MYSQL_DB"]
        )
        if connection.is_connected():
            logger.info("Conexão com o banco de dados estabelecida.")
            return connection
    except Error as e:
        logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
        raise

def init_db(app):
    """Inicializa o banco de dados e cria as tabelas necessárias."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Criação da tabela fornecedores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fornecedores (
                id VARCHAR(15) PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                pessoa_de_contato VARCHAR(255),
                whatsapp VARCHAR(20)
            )
        """)

        # Criação da tabela veiculos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS veiculos (
                id VARCHAR(15) PRIMARY KEY,
                id_fornecedor VARCHAR(15) NOT NULL,
                placa VARCHAR(7) NOT NULL,
                ativo VARCHAR(6) NOT NULL,
                status ENUM('ok', 'bloqueado', 'desligado') NOT NULL,
                sequencial INT NOT NULL,
                foto1 VARCHAR(255),
                foto2 VARCHAR(255),
                FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id)
            )
        """)

        connection.commit()
        logger.info("Tabelas do banco de dados criadas com sucesso.")
    except Error as e:
        logger.error(f"Erro ao inicializar o banco de dados: {str(e)}")
        raise
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("Conexão com o banco de dados fechada.")