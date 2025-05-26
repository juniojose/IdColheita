# app/models/fornecedor.py
from .database import get_db_connection
from ..utils.logger import setup_logger

logger = setup_logger()

class Fornecedor:
    def __init__(self, id, nome, pessoa_de_contato=None, whatsapp=None):
        self.id = id
        self.nome = nome
        self.pessoa_de_contato = pessoa_de_contato
        self.whatsapp = whatsapp

    def salvar(self):
        connection = get_db_connection()
        cursor = None
        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO fornecedores (id, nome, pessoa_de_contato, whatsapp)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(query, (self.id, self.nome, self.pessoa_de_contato, self.whatsapp))
            connection.commit()
            logger.info(f"Fornecedor {self.id} salvo com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao salvar fornecedor {self.id}: {str(e)}")
            raise
        finally:
            cursor.close()
            connection.close()

    def atualizar(self):
        connection = get_db_connection()
        cursor = None
        try:
            cursor = connection.cursor()
            query = """
                UPDATE fornecedores
                SET nome = ?, pessoa_de_contato = ?, whatsapp = ?
                WHERE id = ?
            """
            cursor.execute(query, (self.nome, self.pessoa_de_contato, self.whatsapp, self.id))
            connection.commit()
            logger.info(f"Fornecedor {self.id} atualizado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao atualizar fornecedor {self.id}: {str(e)}")
            raise
        finally:
            cursor.close()
            connection.close()

    def deletar(self):
        connection = get_db_connection()
        cursor = None
        try:
            cursor = connection.cursor()
            query = "DELETE FROM fornecedores WHERE id = ?"
            cursor.execute(query, (self.id,))
            connection.commit()
            logger.info(f"Fornecedor {self.id} deletado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao deletar fornecedor {self.id}: {str(e)}")
            raise
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def listar_todos():
        connection = get_db_connection()
        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM fornecedores")
            fornecedores = cursor.fetchall()
            return [Fornecedor(**f) for f in fornecedores]
        except Exception as e:
            logger.error(f"Erro ao listar fornecedores: {str(e)}")
            raise
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def buscar_por_id(id):
        connection = get_db_connection()
        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM fornecedores WHERE id = ?", (id,))
            fornecedor = cursor.fetchone()
            if fornecedor:
                return Fornecedor(**fornecedor)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar fornecedor {id}: {str(e)}")
            raise
        finally:
            cursor.close()
            connection.close()