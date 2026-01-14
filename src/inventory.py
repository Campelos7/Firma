import pandas as pd
from database import get_database


def get_stock_critico() -> pd.DataFrame:
    """Retorna materiais com stock crítico que precisam de reposição"""
    db = get_database()
    
    query = """
    SELECT 
        m.nome,
        m.tipo,
        m.unidade,
        ROUND(m.stock_atual, 2) AS stock_atual,
        ROUND(m.stock_minimo, 2) AS stock_minimo,
        ROUND(m.stock_minimo - m.stock_atual, 2) AS quantidade_repor,
        ROUND(m.preco_por_unidade, 2) AS preco_unidade,
        ROUND((m.stock_minimo - m.stock_atual) * m.preco_por_unidade, 2) AS custo_reposicao,
        f.nome AS fornecedor,
        m.lead_time_dias
    FROM materiais m
    LEFT JOIN fornecedores f ON m.fornecedor_id = f.id
    WHERE m.stock_atual < m.stock_minimo
    ORDER BY custo_reposicao DESC
    """
    
    return db.execute_query(query)


def get_valor_stock() -> pd.DataFrame:
    """Calcula valor total de stock por tipo de material"""
    db = get_database()
    
    query = """
    SELECT 
        m.tipo,
        COUNT(*) AS num_materiais,
        ROUND(SUM(m.stock_atual), 2) AS quantidade_total,
        ROUND(SUM(m.stock_atual * m.preco_por_unidade), 2) AS valor_stock,
        ROUND(AVG(m.stock_atual / NULLIF(m.stock_minimo, 0) * 100), 2) AS taxa_ocupacao_pct
    FROM materiais m
    GROUP BY m.tipo
    ORDER BY valor_stock DESC
    """
    
    return db.execute_query(query)


def get_rotatividade_materiais() -> pd.DataFrame:
    """Análise de rotatividade de materiais"""
    db = get_database()
    
    query = """
    SELECT 
        m.nome,
        m.tipo,
        COUNT(ms.id) AS num_movimentos,
        ROUND(SUM(CASE WHEN ms.tipo_movimento = 'saida' THEN ms.quantidade ELSE 0 END), 2) AS total_saidas,
        ROUND(SUM(CASE WHEN ms.tipo_movimento = 'entrada' THEN ms.quantidade ELSE 0 END), 2) AS total_entradas,
        ROUND(m.stock_atual, 2) AS stock_atual,
        ROUND(m.stock_atual * m.preco_por_unidade, 2) AS valor_stock
    FROM materiais m
    LEFT JOIN movimentos_stock ms ON m.id = ms.material_id
        AND ms.data_movimento >= CURRENT_DATE - INTERVAL '3 months'
    GROUP BY m.id, m.nome, m.tipo, m.stock_atual, m.preco_por_unidade
    ORDER BY total_saidas DESC
    """
    
    return db.execute_query(query)


def get_previsao_necessidades(dias: int = 30) -> pd.DataFrame:
    """Previsão de necessidades de materiais baseado em projetos futuros"""
    db = get_database()
    
    query = f"""
    SELECT 
        m.nome AS material,
        m.tipo,
        ROUND(m.stock_atual, 2) AS stock_atual,
        ROUND(SUM(pm.quantidade_por_unidade), 2) AS necessidade_estimada,
        ROUND(m.stock_atual - SUM(pm.quantidade_por_unidade), 2) AS saldo_previsto,
        CASE 
            WHEN m.stock_atual - SUM(pm.quantidade_por_unidade) < m.stock_minimo 
            THEN 'REPOR'
            ELSE 'OK'
        END AS status
    FROM materiais m
    JOIN produtos_materiais pm ON m.id = pm.material_id
    JOIN produtos p ON pm.tipo_produto_id = p.tipo_produto_id
    JOIN orcamentos o ON p.id = o.produto_id
    WHERE o.status IN ('pendente', 'aprovado')
        AND o.data_orcamento <= CURRENT_DATE + INTERVAL '{dias} days'
    GROUP BY m.id, m.nome, m.tipo, m.stock_atual, m.stock_minimo
    ORDER BY saldo_previsto
    """
    
    return db.execute_query(query)


def get_fornecedores_performance() -> pd.DataFrame:
    """Performance dos fornecedores"""
    db = get_database()
    
    query = """
    SELECT 
        f.nome AS fornecedor,
        f.pais,
        f.avaliacao,
        COUNT(DISTINCT m.id) AS num_materiais,
        ROUND(AVG(m.lead_time_dias), 1) AS lead_time_medio,
        ROUND(SUM(m.stock_atual * m.preco_por_unidade), 2) AS valor_stock_fornecido
    FROM fornecedores f
    LEFT JOIN materiais m ON f.id = m.fornecedor_id
    GROUP BY f.id, f.nome, f.pais, f.avaliacao
    ORDER BY valor_stock_fornecido DESC
    """
    
    return db.execute_query(query)