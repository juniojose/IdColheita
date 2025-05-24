# app/models/veiculo.py
from .database import get_db_connection
from ..utils.logger import setup_logger

logger = setup_logger()

class Veiculo:
    def __init__(self, id, id_fornecedor, placa, ativo, status, sequencial, foto1=None, foto2=None):
        self.id = id
        self.id_fornecedor = id_fornecedor
        self.placa = placa
        self.ativo = ativo
        self.status = status
        self.sequencial = sequencial
        self.foto1 = foto1
        self.foto2 = foto2

    def salvar(self):
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO veiculos (id, id_fornecedor, placa, ativo, status, sequencial, foto1, foto2)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (self.id, self.id_fornecedor, self.placa, self.ativo, self.status, self.sequencial, self.foto1, self.foto2))
            connection.commit()
            logger.info(f"Veículo {self.id} salvo com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao salvar veículo {self.id}: {str(e)}")
            raise
        finally:
            cursor.close()
            connection.close()

    def atualizar(self):
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            query = """
                UPDATE veiculos
                SET id_fornecedor = %s, placa = %s, ativo = %s, status = %s, sequencial = %s, foto1 = %s, foto2 = %s
                WHERE id = %s
            """
            cursor.execute(query, (self.id_fornecedor, self.placa, self.ativo, self.status, self.sequencial, self.foto1, self.foto2, self.id))
            connection.commit()
            logger.info(f"Veículo {self.id} atualizado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao atualizar veículo {self.id}: {str(e)}")
            raise
        finally:
            cursor.close()
            connection.close()

    def deletar(self):
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            query = "DELETE FROM veiculos WHERE id = %s"
            cursor.execute(query, (self.id,))
            connection.commit()
            logger.info(f"Veículo {self.id} deletado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao deletar veículo {self.id}: {str(e)}")
            raise
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def listar_todos():
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM veiculos")
            veiculos = cursor.fetchall()
            return [Veiculo(**v) for v in veiculos]
        except Exception as e:
            logger.error(f"Erro ao listar veículos: {str(e)}")
            raise
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def buscar_por_id(id):
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM veiculos WHERE id = %s", (id,))
            veiculo = cursor.fetchone()
            if veiculo:
                return Veiculo(**veiculo)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar veículo {id}: {str(e)}")
            raise
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def gerar_sequencial():
        """Gera o próximo número sequencial (1 a 999) com base no maior valor existente."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT MAX(sequencial) FROM veiculos")
            max_sequencial = cursor.fetchone()[0]
            if max_sequencial is None:
                return 1
            return min(max_sequencial + 1, 999)
        except Exception as e:
            logger.error(f"Erro ao gerar sequencial: {str(e)}")
            raise
        finally:
            cursor.close()
            connection.close()