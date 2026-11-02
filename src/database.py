import os
import sqlite3
import pandas as pd
from glob import glob

DB_PATH = "emporio.db"
DATA_DIR = "data"

def init_db():
    """Lê todos os arquivos CSV na pasta data/ e cria tabelas no SQLite."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    
    csv_files = glob(os.path.join(DATA_DIR, "*.csv"))
    
    if not csv_files:
        print(f"[Aviso] Nenhum arquivo CSV encontrado na pasta '{DATA_DIR}'.")
        return None

    for file in csv_files:
        table_name = os.path.splitext(os.path.basename(file))[0]
        df = pd.read_csv(file)
        
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"[DB] Tabela '{table_name}' criada com {len(df)} registros.")
        
    conn.close()
    return DB_PATH

def query_db(query: str) -> str:
    """Executa uma query SQL e retorna os resultados formatados para o LLM."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return "A consulta não retornou resultados."
            
        return df.to_markdown(index=False)
    except Exception as e:
        return f"Erro na consulta SQL: {e}"

if __name__ == "__main__":
    init_db()