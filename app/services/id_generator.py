# app/services/id_generator.py
from datetime import datetime
from ..models.database import get_db_connection
from ..utils.logger import setup_logger

logger = setup_logger()

def generate_id(table_name, date=None):
    """
    Gera um ID único no formato AAAAMMDDhhmmXXX para a tabela especificada.
    - table_name: Nome da tabela ('fornecedores' ou 'veiculos').
    - date: Objeto datetime para testes (padrão: datetime.now()).
    - Retorna: String no formato AAAAMMDDhhmmXXX.
    """
    if date is None:
        date = datetime.now()
    
    # Formato do prefixo: AAAAMMDDhhmm
    prefix = date.strftime("%Y%m%d%H%M")
    
    # Conectar ao banco
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        
        # Buscar IDs existentes com o mesmo prefixo
        query = f"SELECT id FROM {table_name} WHERE id LIKE %s"
        cursor.execute(query, (f"{prefix}%",))
        existing_ids = {row[0] for row in cursor.fetchall()}
        
        # Tentar números sequenciais de 000 a 999
        for seq in range(1000):
            id_candidate = f"{prefix}{seq:03d}"
            if id_candidate not in existing_ids:
                logger.info(f"ID gerado: {id_candidate} para {table_name}")
                return id_candidate
        
        raise Exception("Não há IDs disponíveis para o período atual.")
    
    except Exception as e:
        logger.error(f"Erro ao gerar ID para {table_name}: {str(e)}")
        raise
    finally:
        cursor.close()
        connection.close()