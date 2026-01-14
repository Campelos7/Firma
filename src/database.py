import psycopg2
import pandas as pd
from typing import Optional, List, Tuple
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG


class Database:
    """Classe para gestão da conexão à base de dados PostgreSQL"""
    
    def __init__(self):
        self.config = DB_CONFIG
        self.conn = None
        self.last_error: Optional[str] = None
        
    def connect(self):
        """Estabelece conexão com a base de dados"""
        try:
            self.conn = psycopg2.connect(**self.config)
            self.last_error = None
            return True
        except Exception as e:
            self.last_error = str(e)
            print(f"Erro ao conectar à base de dados: {e}")
            return False
    
    def disconnect(self):
        """Fecha conexão com a base de dados"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """Executa query e retorna DataFrame"""
        if not self.conn:
            self.connect()
        
        try:
            df = pd.read_sql_query(query, self.conn, params=params)
            self.last_error = None
            return df
        except Exception as e:
            self.last_error = str(e)
            print(f"Erro ao executar query: {e}")
            return pd.DataFrame()
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> bool:
        """Executa query de atualização (INSERT, UPDATE, DELETE)"""
        if not self.conn:
            self.connect()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            cursor.close()
            self.last_error = None
            return True
        except Exception as e:
            self.last_error = str(e)
            print(f"Erro ao executar atualização: {e}")
            self.conn.rollback()
            return False

    def execute_returning(self, query: str, params: Optional[tuple] = None):
        """Executa INSERT/UPDATE ... RETURNING e devolve o valor retornado (primeira coluna da primeira linha)."""
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            self.conn.commit()
            cursor.close()
            self.last_error = None
            if not row:
                return None
            return row[0]
        except Exception as e:
            self.last_error = str(e)
            print(f"Erro ao executar returning: {e}")
            self.conn.rollback()
            return None

    def execute_many(self, statements: List[Tuple[str, Optional[tuple]]]) -> bool:
        """Executa múltiplas queries numa transação."""
        if not self.conn:
            self.connect()

        try:
            cursor = self.conn.cursor()
            for query, params in statements:
                cursor.execute(query, params)
            self.conn.commit()
            cursor.close()
            self.last_error = None
            return True
        except Exception as e:
            self.last_error = str(e)
            print(f"Erro ao executar transação: {e}")
            self.conn.rollback()
            return False

    def execute_sql_file(self, file_path: str) -> bool:
        """Executa um ficheiro .sql inteiro na BD.

        Útil em Windows quando `psql` não está no PATH.
        """
        if not self.conn:
            self.connect()

        def _read_text(path: str) -> str:
            for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
                try:
                    with open(path, "r", encoding=enc) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()

        try:
            sql = _read_text(file_path)
            cursor = self.conn.cursor()
            cursor.execute(sql)
            self.conn.commit()
            cursor.close()
            self.last_error = None
            return True
        except Exception as e:
            self.last_error = str(e)
            print(f"Erro ao executar ficheiro SQL ({file_path}): {e}")
            self.conn.rollback()
            return False


def get_database() -> Database:
    """Retorna instância de Database"""
    return Database()