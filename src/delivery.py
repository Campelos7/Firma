import pandas as pd
from database import get_database


def get_entregas_pendentes() -> pd.DataFrame:
    """Retorna entregas pendentes"""
    db = get_database()
    
    query = """
    SELECT 
        e.id,
        c.nome AS cliente,
        tp.nome AS produto,
        e.data_entrega_prometida AS data_prevista,
        e.status,
        CURRENT_DATE - e.data_entrega_prometida AS dias_atraso,
        CASE 
            WHEN e.data_entrega_prometida < CURRENT_DATE THEN 'ATRASADO'
            WHEN e.data_entrega_prometida = CURRENT_DATE THEN 'HOJE'
            WHEN e.data_entrega_prometida <= CURRENT_DATE + 3 THEN 'URGENTE'
            ELSE 'OK'
        END AS prioridade
    FROM encomendas e
    JOIN orcamentos o ON e.orcamento_id = o.id
    JOIN clientes c ON o.cliente_id = c.id
    JOIN produtos p ON o.produto_id = p.id
    JOIN tipos_produto tp ON p.tipo_produto_id = tp.id
    WHERE e.status IN ('pendente', 'em_producao')
    ORDER BY e.data_entrega_prometida
    """
    
    return db.execute_query(query)


def get_performance_entregas() -> pd.DataFrame:
    """Análise de performance de entregas"""
    db = get_database()
    
    query = """
    SELECT 
        tp.nome AS produto,
        COUNT(*) AS total_entregas,
        COUNT(CASE WHEN e.status = 'concluido' THEN 1 END) AS concluidas,
        COUNT(CASE WHEN e.data_entrega_real <= e.data_entrega_prometida THEN 1 END) AS no_prazo,
        ROUND(COUNT(CASE WHEN e.data_entrega_real <= e.data_entrega_prometida THEN 1 END)::numeric / 
              NULLIF(COUNT(CASE WHEN e.status = 'concluido' THEN 1 END), 0) * 100, 2) AS taxa_pontualidade,
        ROUND(AVG(CASE WHEN e.data_entrega_real IS NOT NULL 
                       THEN e.data_entrega_real - e.data_entrega_prometida END), 1) AS atraso_medio_dias
    FROM encomendas e
    JOIN orcamentos o ON e.orcamento_id = o.id
    JOIN produtos p ON o.produto_id = p.id
    JOIN tipos_produto tp ON p.tipo_produto_id = tp.id
    WHERE e.data_entrega_prometida >= CURRENT_DATE - INTERVAL '6 months'
    GROUP BY tp.nome
    ORDER BY total_entregas DESC
    """
    
    return db.execute_query(query)


def get_entregas_por_regiao() -> pd.DataFrame:
    """(Legacy) Entregas por região.

    Nota: historicamente esta função usava `c.morada` inteira como 'regiao'.
    Mantemos por compatibilidade, mas o recomendado é usar `get_entregas_por_cidade()`.
    """
    df = get_entregas_por_cidade()
    if not df.empty and "cidade" in df.columns:
        df = df.rename(columns={"cidade": "regiao"})
    return df


def get_entregas_por_cidade() -> pd.DataFrame:
    """Entregas agrupadas por cidade (extraída da morada do cliente).

    Heurística: usa o último segmento da morada (separado por vírgula/linha) e remove
    um possível código postal no início (ex: '4800-000 Guimarães' -> 'Guimarães').
    """
    db = get_database()

    query = """
    WITH base AS (
        SELECT
            e.id AS encomenda_id,
            e.status,
            e.data_entrega_prometida,
            e.data_entrega_real,
            e.valor_total,
            c.morada,
            regexp_split_to_array(COALESCE(c.morada, ''), E'[,\\n]+') AS parts
        FROM encomendas e
        JOIN orcamentos o ON e.orcamento_id = o.id
        JOIN clientes c ON o.cliente_id = c.id
    ), norm AS (
        SELECT
            encomenda_id,
            status,
            data_entrega_prometida,
            data_entrega_real,
            valor_total,
            COALESCE(
                NULLIF(
                    btrim(
                        regexp_replace(
                            parts[array_length(parts, 1)],
                            '^[0-9]{4}-[0-9]{3}\\s*',
                            ''
                        )
                    ),
                    ''
                ),
                'Sem cidade'
            ) AS cidade
        FROM base
    )
    SELECT
        cidade,
        COUNT(*) AS num_entregas,
        COUNT(CASE WHEN status = 'concluido' THEN 1 END) AS concluidas,
        ROUND(AVG(CASE WHEN data_entrega_real IS NOT NULL
                       THEN data_entrega_real - data_entrega_prometida END), 1) AS atraso_medio_dias,
        ROUND(AVG(valor_total), 2) AS custo_medio_entrega
    FROM norm
    GROUP BY cidade
    ORDER BY num_entregas DESC
    """

    return db.execute_query(query)


def get_timeline_entregas(dias: int = 30) -> pd.DataFrame:
    """Timeline de entregas próximas"""
    db = get_database()
    
    query = f"""
    SELECT 
        e.data_entrega_prometida AS data_prevista,
        c.nome AS cliente,
        tp.nome AS produto,
        e.status,
        o.preco_venda AS valor,
        CURRENT_DATE - e.data_entrega_prometida AS dias_ate_entrega
    FROM encomendas e
    JOIN orcamentos o ON e.orcamento_id = o.id
    JOIN clientes c ON o.cliente_id = c.id
    JOIN produtos p ON o.produto_id = p.id
    JOIN tipos_produto tp ON p.tipo_produto_id = tp.id
    WHERE e.data_entrega_prometida BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '{dias} days'
        AND e.status != 'concluido'
    ORDER BY e.data_entrega_prometida
    """
    
    return db.execute_query(query)


def get_custos_logistica() -> pd.DataFrame:
    """Análise de custos de logística"""
    db = get_database()
    
    query = """
    SELECT 
        tp.categoria,
        COUNT(*) AS num_entregas,
        ROUND(AVG(e.valor_total), 2) AS custo_medio,
        ROUND(SUM(e.valor_total), 2) AS custo_total,
        ROUND(AVG(e.valor_total / NULLIF(o.preco_venda, 0) * 100), 2) AS pct_sobre_venda
    FROM encomendas e
    JOIN orcamentos o ON e.orcamento_id = o.id
    JOIN produtos p ON o.produto_id = p.id
    JOIN tipos_produto tp ON p.tipo_produto_id = tp.id
    WHERE e.valor_total > 0
    GROUP BY tp.categoria
    ORDER BY custo_total DESC
    """
    
    return db.execute_query(query)
