-- ============================================
-- QUERIES ANALÍTICAS - Business Intelligence
-- ============================================

-- 1. ANÁLISE DE RENTABILIDADE POR PRODUTO
-- Identifica produtos mais rentáveis
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
WHERE o.data_orcamento >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY tp.nome
ORDER BY receita_total DESC;

-- 2. STOCK CRÍTICO E NECESSIDADE DE REPOSIÇÃO
-- Materiais que precisam ser comprados urgentemente
SELECT 
    m.nome,
    m.tipo,
    m.stock_atual,
    m.stock_minimo,
    m.stock_minimo - m.stock_atual AS quantidade_repor,
    (m.stock_minimo - m.stock_atual) * m.preco_por_unidade AS valor_reposicao,
    m.lead_time_dias,
    f.nome AS fornecedor,
    CURRENT_DATE + m.lead_time_dias AS data_entrega_estimada
FROM materiais m
JOIN fornecedores f ON m.fornecedor_id = f.id
WHERE m.stock_atual < m.stock_minimo
ORDER BY (m.stock_minimo - m.stock_atual) * m.preco_por_unidade DESC;

-- 3. CONSUMO MÉDIO DE MATERIAIS (últimos 60 dias)
-- Calcula consumo diário para previsão
SELECT 
    m.nome,
    m.tipo,
    COUNT(ms.id) AS num_movimentos,
    ROUND(SUM(ms.quantidade), 2) AS total_consumido,
    ROUND(AVG(ms.quantidade), 2) AS media_por_movimento,
    ROUND(SUM(ms.quantidade) / 60.0, 2) AS consumo_medio_diario,
    m.stock_atual,
    ROUND(m.stock_atual / NULLIF(SUM(ms.quantidade) / 60.0, 0), 1) AS dias_cobertura
FROM materiais m
LEFT JOIN movimentos_stock ms ON m.material_id = ms.id
WHERE ms.tipo_movimento = 'saida'
  AND ms.data_movimento >= CURRENT_DATE - INTERVAL '60 days'
GROUP BY m.id, m.nome, m.tipo, m.stock_atual
HAVING SUM(ms.quantidade) > 0
ORDER BY dias_cobertura ASC;

-- 4. PERFORMANCE DE ENTREGA
-- Análise de cumprimento de prazos
SELECT 
    DATE_TRUNC('month', e.data_pedido) AS mes,
    COUNT(e.id) AS total_encomendas,
    COUNT(CASE WHEN e.data_entrega_real <= e.data_entrega_prometida THEN 1 END) AS entregues_no_prazo,
    COUNT(CASE WHEN e.data_entrega_real > e.data_entrega_prometida THEN 1 END) AS entregues_atrasadas,
    ROUND(
        COUNT(CASE WHEN e.data_entrega_real <= e.data_entrega_prometida THEN 1 END)::NUMERIC / 
        NULLIF(COUNT(CASE WHEN e.status = 'entregue' THEN 1 END), 0) * 100, 
        1
    ) AS taxa_pontualidade_pct,
    ROUND(AVG(e.data_entrega_real - e.data_entrega_prometida), 1) AS media_atraso_dias
FROM encomendas e
WHERE e.status = 'entregue'
  AND e.data_pedido >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY DATE_TRUNC('month', e.data_pedido)
ORDER BY mes DESC;

-- 5. PREVISÃO DE NECESSIDADE DE MATERIAIS
-- Para encomendas em produção e pendentes
WITH encomendas_ativas AS (
    SELECT e.id, e.produto_id
    FROM encomendas e
    WHERE e.status IN ('pendente', 'em_producao', 'aguarda_material')
),
necessidade_materiais AS (
    SELECT 
        m.id AS material_id,
        m.nome,
        m.tipo,
        SUM(pm.quantidade_por_unidade) AS quantidade_necessaria,
        m.stock_atual,
        GREATEST(SUM(pm.quantidade_por_unidade) - m.stock_atual, 0) AS deficit,
        m.preco_por_unidade,
        GREATEST(SUM(pm.quantidade_por_unidade) - m.stock_atual, 0) * m.preco_por_unidade AS valor_compra_necessaria
    FROM encomendas_ativas ea
    JOIN produtos p ON ea.produto_id = p.id
    JOIN produtos_materiais pm ON p.tipo_produto_id = pm.tipo_produto_id
    JOIN materiais m ON pm.material_id = m.id
    GROUP BY m.id, m.nome, m.tipo, m.stock_atual, m.preco_por_unidade
)
SELECT 
    nome,
    tipo,
    ROUND(quantidade_necessaria, 2) AS qtd_necessaria,
    ROUND(stock_atual, 2) AS stock_atual,
    ROUND(deficit, 2) AS deficit,
    ROUND(valor_compra_necessaria, 2) AS valor_compra_eur
FROM necessidade_materiais
WHERE deficit > 0
ORDER BY valor_compra_necessaria DESC;

-- 6. ANÁLISE DE MARGEM POR FAIXA DE PREÇO
-- Identifica sweet spot de preço
SELECT 
    CASE 
        WHEN o.preco_venda < 500 THEN '< €500'
        WHEN o.preco_venda < 1000 THEN '€500-1000'
        WHEN o.preco_venda < 1500 THEN '€1000-1500'
        WHEN o.preco_venda < 2000 THEN '€1500-2000'
        ELSE '> €2000'
    END AS faixa_preco,
    COUNT(o.id) AS num_orcamentos,
    COUNT(CASE WHEN o.status = 'aprovado' THEN 1 END) AS aprovados,
    ROUND(
        COUNT(CASE WHEN o.status = 'aprovado' THEN 1 END)::NUMERIC / 
        NULLIF(COUNT(o.id), 0) * 100, 
        1
    ) AS taxa_conversao_pct,
    ROUND(AVG(o.margem_percentual), 2) AS margem_media_pct,
    ROUND(SUM(CASE WHEN o.status = 'aprovado' THEN o.preco_venda ELSE 0 END), 2) AS receita_total
FROM orcamentos o
WHERE o.data_orcamento >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY faixa_preco
ORDER BY 
    CASE faixa_preco
        WHEN '< €500' THEN 1
        WHEN '€500-1000' THEN 2
        WHEN '€1000-1500' THEN 3
        WHEN '€1500-2000' THEN 4
        ELSE 5
    END;

-- 7. TOP CLIENTES POR RECEITA
SELECT 
    c.nome,
    c.tipo,
    COUNT(DISTINCT e.id) AS num_encomendas,
    ROUND(SUM(e.valor_total), 2) AS receita_total,
    ROUND(AVG(e.valor_total), 2) AS ticket_medio,
    MAX(e.data_pedido) AS ultima_encomenda,
    CURRENT_DATE - MAX(e.data_pedido) AS dias_desde_ultima
FROM clientes c
JOIN encomendas e ON c.id = e.cliente_id
WHERE e.status != 'cancelado'
GROUP BY c.id, c.nome, c.tipo
ORDER BY receita_total DESC
LIMIT 10;

-- 8. SIMULAÇÃO DE IMPACTO DE AUMENTO DE PREÇO DO INOX
-- Simula +15% no preço do inox
WITH materiais_inox AS (
    SELECT id, nome, preco_por_unidade,
           preco_por_unidade * 1.15 AS novo_preco
    FROM materiais
    WHERE tipo = 'inox'
),
impacto_produtos AS (
    SELECT 
        tp.nome AS produto,
        p.codigo,
        SUM(pm.quantidade_por_unidade * mi.preco_por_unidade) AS custo_material_atual,
        SUM(pm.quantidade_por_unidade * mi.novo_preco) AS custo_material_novo,
        SUM(pm.quantidade_por_unidade * mi.novo_preco) - 
            SUM(pm.quantidade_por_unidade * mi.preco_por_unidade) AS aumento_custo
    FROM produtos p
    JOIN tipos_produto tp ON p.tipo_produto_id = tp.id
    JOIN produtos_materiais pm ON p.tipo_produto_id = pm.tipo_produto_id
    JOIN materiais_inox mi ON pm.material_id = mi.id
    GROUP BY tp.nome, p.codigo
)
SELECT 
    produto,
    codigo,
    ROUND(custo_material_atual, 2) AS custo_atual_eur,
    ROUND(custo_material_novo, 2) AS custo_novo_eur,
    ROUND(aumento_custo, 2) AS aumento_eur,
    ROUND((aumento_custo / NULLIF(custo_material_atual, 0)) * 100, 1) AS aumento_percentual
FROM impacto_produtos
ORDER BY aumento_eur DESC;

-- 9. ENCOMENDAS EM RISCO DE ATRASO
-- Encomendas que podem não cumprir prazo
SELECT 
    e.id,
    c.nome AS cliente,
    tp.nome AS produto,
    e.data_pedido,
    e.prazo_prometido_dias,
    e.data_entrega_prometida,
    CURRENT_DATE - e.data_entrega_prometida AS dias_atraso_atual,
    e.status,
    e.prioridade,
    CASE
        WHEN e.status = 'aguarda_material' THEN 'BLOQUEADO - Falta Material'
        WHEN CURRENT_DATE > e.data_entrega_prometida THEN 'ATRASADO'
        WHEN CURRENT_DATE > e.data_entrega_prometida - 3 THEN 'RISCO ALTO'
        ELSE 'EM DIA'
    END AS alerta
FROM encomendas e
JOIN clientes c ON e.cliente_id = c.id
JOIN produtos p ON e.produto_id = p.id
JOIN tipos_produto tp ON p.tipo_produto_id = tp.id
WHERE e.status IN ('pendente', 'em_producao', 'aguarda_material')
ORDER BY 
    CASE 
        WHEN e.status = 'aguarda_material' THEN 1
        WHEN CURRENT_DATE > e.data_entrega_prometida THEN 2
        ELSE 3
    END,
    e.data_entrega_prometida;

-- 10. EVOLUÇÃO MENSAL DE RECEITA E MARGEM
SELECT 
    TO_CHAR(e.data_pedido, 'YYYY-MM') AS mes,
    COUNT(e.id) AS num_encomendas,
    ROUND(SUM(e.valor_total), 2) AS receita_total,
    ROUND(AVG(e.valor_total), 2) AS ticket_medio,
    ROUND(AVG(o.margem_percentual), 2) AS margem_media_pct,
    ROUND(SUM(o.margem_absoluta), 2) AS lucro_total_estimado
FROM encomendas e
JOIN orcamentos o ON e.orcamento_id = o.id
WHERE e.status != 'cancelado'
  AND e.data_pedido >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY TO_CHAR(e.data_pedido, 'YYYY-MM')
ORDER BY mes DESC;

-- 11. EFICIÊNCIA DE PRODUÇÃO (Horas vs Prazo)
SELECT 
    tp.nome AS tipo_produto,
    ROUND(AVG(p.horas_mao_obra), 1) AS horas_estimadas,
    ROUND(AVG(e.prazo_prometido_dias), 1) AS prazo_medio_dias,
    COUNT(e.id) AS num_encomendas,
    COUNT(CASE WHEN e.data_entrega_real <= e.data_entrega_prometida THEN 1 END) AS entregues_prazo,
    ROUND(
        COUNT(CASE WHEN e.data_entrega_real <= e.data_entrega_prometida THEN 1 END)::NUMERIC /
        NULLIF(COUNT(CASE WHEN e.status = 'entregue' THEN 1 END), 0) * 100,
        1
    ) AS taxa_sucesso_pct
FROM encomendas e
JOIN produtos p ON e.produto_id = p.id
JOIN tipos_produto tp ON p.tipo_produto_id = tp.id
WHERE e.data_pedido >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY tp.nome
ORDER BY num_encomendas DESC;