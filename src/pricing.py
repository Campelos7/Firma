import pandas as pd
from database import get_database


def get_rentabilidade_produtos(meses: int = 6) -> pd.DataFrame:
    """Retorna análise de rentabilidade por produto"""
    db = get_database()
    
    query = f"""
    SELECT 
        tp.nome AS produto,
        COUNT(o.id) AS num_orcamentos,
        COUNT(CASE WHEN o.status = 'aprovado' THEN 1 END) AS aprovados,
        ROUND(AVG(o.preco_venda), 2) AS preco_medio,
        ROUND(AVG(o.custo_total), 2) AS custo_medio,
        ROUND(AVG(o.margem_absoluta), 2) AS margem_media_eur,
        ROUND(AVG(o.margem_percentual), 2) AS margem_media_pct,
        ROUND(SUM(CASE WHEN o.status = 'aprovado' THEN o.preco_venda ELSE 0 END), 2) AS receita_total
    FROM orcamentos o
    JOIN produtos p ON o.produto_id = p.id
    JOIN tipos_produto tp ON p.tipo_produto_id = tp.id
    WHERE o.data_orcamento >= CURRENT_DATE - INTERVAL '{meses} months'
    GROUP BY tp.nome
    ORDER BY receita_total DESC
    """
    
    return db.execute_query(query)


def get_precos_vs_mercado() -> pd.DataFrame:
    """Compara preços praticados vs custo médio (proxy de mercado)"""
    db = get_database()
    
    query = """
    SELECT 
        tp.nome AS tipo_produto,
        ROUND(AVG(o.preco_venda), 2) AS preco_medio_praticado,
        ROUND(AVG(o.custo_total), 2) AS preco_medio_mercado,
        ROUND(AVG(o.preco_venda - o.custo_total), 2) AS diferenca,
        ROUND(AVG((o.preco_venda - o.custo_total) / NULLIF(o.custo_total, 0) * 100), 2) AS diferenca_percentual,
        COUNT(*) AS num_orcamentos
    FROM orcamentos o
    JOIN produtos p ON o.produto_id = p.id
    JOIN tipos_produto tp ON p.tipo_produto_id = tp.id
    GROUP BY tp.nome
    ORDER BY diferenca_percentual
    """
    
    return db.execute_query(query)


def get_top_clientes(limite: int = 10) -> pd.DataFrame:
    """Retorna top clientes por valor de negócio"""
    db = get_database()
    
    query = f"""
    SELECT 
        c.nome AS cliente,
        c.morada AS localizacao,
        COUNT(o.id) AS num_orcamentos,
        COUNT(CASE WHEN o.status = 'aprovado' THEN 1 END) AS num_aprovados,
        ROUND(AVG(CASE WHEN o.status = 'aprovado' THEN o.preco_venda END), 2) AS valor_medio,
        ROUND(SUM(CASE WHEN o.status = 'aprovado' THEN o.preco_venda ELSE 0 END), 2) AS valor_total
    FROM clientes c
    JOIN orcamentos o ON c.id = o.cliente_id
    GROUP BY c.id, c.nome, c.morada
    ORDER BY valor_total DESC
    LIMIT {limite}
    """
    
    return db.execute_query(query)


def get_margem_por_categoria() -> pd.DataFrame:
    """Análise de margem por categoria de produto"""
    db = get_database()
    
    query = """
    SELECT 
        tp.categoria,
        COUNT(o.id) AS num_orcamentos,
        ROUND(AVG(o.margem_percentual), 2) AS margem_media_pct,
        ROUND(AVG(o.margem_absoluta), 2) AS margem_media_eur,
        ROUND(SUM(CASE WHEN o.status = 'aprovado' THEN o.preco_venda ELSE 0 END), 2) AS receita_total
    FROM orcamentos o
    JOIN produtos p ON o.produto_id = p.id
    JOIN tipos_produto tp ON p.tipo_produto_id = tp.id
    GROUP BY tp.categoria
    ORDER BY receita_total DESC
    """
    
    return db.execute_query(query)