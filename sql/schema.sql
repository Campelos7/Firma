-- ============================================
-- SCHEMA: Sistema de Gest�o - Ferragens e Serralharia
-- Autor: Data Analyst Portfolio Project
-- Data: 2026
-- ============================================

-- Tabela de Fornecedores
CREATE TABLE IF NOT EXISTS fornecedores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    contacto VARCHAR(50),
    email VARCHAR(100),
    pais VARCHAR(50),
    avaliacao DECIMAL(3,2) CHECK (avaliacao BETWEEN 0 AND 5),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Materiais
CREATE TABLE IF NOT EXISTS materiais (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL, -- 'inox', 'ferro', 'aluminio', 'pintura', etc
    unidade VARCHAR(20) NOT NULL, -- 'metro', 'kg', 'litro', 'unidade'
    preco_por_unidade DECIMAL(10,2) NOT NULL,
    fornecedor_id INTEGER REFERENCES fornecedores(id),
    lead_time_dias INTEGER NOT NULL, -- tempo de entrega do fornecedor
    stock_atual DECIMAL(10,2) NOT NULL DEFAULT 0,
    stock_minimo DECIMAL(10,2) NOT NULL,
    stock_maximo DECIMAL(10,2),
    ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Tipos de Produtos
CREATE TABLE IF NOT EXISTS tipos_produto (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL, -- 'Port�o Simples', 'Port�o com Grade', 'Estrutura Met�lica'
    descricao TEXT,
    categoria VARCHAR(50) -- 'portoes', 'estruturas', 'guardas', 'outros'
);

-- Tabela de Especifica��es de Produtos (BOM - Bill of Materials)
CREATE TABLE IF NOT EXISTS produtos_materiais (
    id SERIAL PRIMARY KEY,
    tipo_produto_id INTEGER REFERENCES tipos_produto(id),
    material_id INTEGER REFERENCES materiais(id),
    quantidade_por_unidade DECIMAL(10,2) NOT NULL, -- ex: 15 metros de inox por port�o
    UNIQUE(tipo_produto_id, material_id)
);

-- Tabela de Produtos/Projetos (configura��es espec�ficas)
CREATE TABLE IF NOT EXISTS produtos (
    id SERIAL PRIMARY KEY,
    tipo_produto_id INTEGER REFERENCES tipos_produto(id),
    codigo VARCHAR(50) UNIQUE,
    descricao TEXT,
    largura_metros DECIMAL(5,2),
    altura_metros DECIMAL(5,2),
    horas_mao_obra DECIMAL(5,2) NOT NULL, -- horas estimadas de trabalho
    complexidade VARCHAR(20) CHECK (complexidade IN ('baixa', 'media', 'alta')),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Clientes
CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    tipo VARCHAR(20) CHECK (tipo IN ('particular', 'empresa')),
    nif VARCHAR(20),
    contacto VARCHAR(50),
    email VARCHAR(100),
    morada TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Or�amentos
CREATE TABLE IF NOT EXISTS orcamentos (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id),
    produto_id INTEGER REFERENCES produtos(id),
    data_orcamento DATE NOT NULL DEFAULT CURRENT_DATE,
    custo_material DECIMAL(10,2) NOT NULL,
    custo_mao_obra DECIMAL(10,2) NOT NULL,
    outros_custos DECIMAL(10,2) DEFAULT 0,
    custo_total DECIMAL(10,2) GENERATED ALWAYS AS (custo_material + custo_mao_obra + outros_custos) STORED,
    margem_percentual DECIMAL(5,2) NOT NULL, -- ex: 35.00 para 35%
    preco_venda DECIMAL(10,2) NOT NULL,
    margem_absoluta DECIMAL(10,2) GENERATED ALWAYS AS (preco_venda - (custo_material + custo_mao_obra + outros_custos)) STORED,
    status VARCHAR(20) DEFAULT 'pendente' CHECK (status IN ('pendente', 'aprovado', 'rejeitado', 'expirado')),
    validade_dias INTEGER DEFAULT 30,
    observacoes TEXT
);

-- Tabela de Encomendas
CREATE TABLE IF NOT EXISTS encomendas (
    id SERIAL PRIMARY KEY,
    orcamento_id INTEGER REFERENCES orcamentos(id),
    cliente_id INTEGER REFERENCES clientes(id),
    produto_id INTEGER REFERENCES produtos(id),
    data_pedido DATE NOT NULL DEFAULT CURRENT_DATE,
    prazo_prometido_dias INTEGER NOT NULL,
    data_entrega_prometida DATE GENERATED ALWAYS AS (data_pedido + prazo_prometido_dias) STORED,
    data_entrega_real DATE,
    status VARCHAR(30) DEFAULT 'pendente' CHECK (status IN 
        ('pendente', 'em_producao', 'aguarda_material', 'concluido', 'entregue', 'cancelado')
    ),
    valor_total DECIMAL(10,2) NOT NULL,
    prioridade VARCHAR(20) DEFAULT 'normal' CHECK (prioridade IN ('baixa', 'normal', 'alta', 'urgente'))
);

-- Tabela de Movimenta��o de Stock
CREATE TABLE IF NOT EXISTS movimentos_stock (
    id SERIAL PRIMARY KEY,
    material_id INTEGER REFERENCES materiais(id),
    tipo_movimento VARCHAR(20) NOT NULL CHECK (tipo_movimento IN ('entrada', 'saida', 'ajuste')),
    quantidade DECIMAL(10,2) NOT NULL,
    motivo VARCHAR(100), -- 'compra', 'producao', 'correcao', 'encomenda_X'
    encomenda_id INTEGER REFERENCES encomendas(id),
    data_movimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario VARCHAR(50)
);

-- ============================================
-- VIEWS ANAL�TICAS
-- ============================================

-- View: Stock Cr�tico
CREATE OR REPLACE VIEW vw_stock_critico AS
SELECT 
    m.id,
    m.nome,
    m.tipo,
    m.stock_atual,
    m.stock_minimo,
    m.lead_time_dias,
    f.nome AS fornecedor,
    ROUND(m.stock_atual / NULLIF(
        (SELECT AVG(ABS(quantidade)) 
         FROM movimentos_stock ms 
         WHERE ms.material_id = m.id 
           AND ms.tipo_movimento = 'saida'
           AND ms.data_movimento >= CURRENT_DATE - INTERVAL '30 days'), 0
    ), 1) AS dias_cobertura,
    CASE 
        WHEN m.stock_atual < m.stock_minimo THEN 'CR�TICO'
        WHEN m.stock_atual < m.stock_minimo * 1.5 THEN 'ALERTA'
        ELSE 'OK'
    END AS status_stock
FROM materiais m
LEFT JOIN fornecedores f ON m.fornecedor_id = f.id
ORDER BY 
    CASE 
        WHEN m.stock_atual < m.stock_minimo THEN 1
        WHEN m.stock_atual < m.stock_minimo * 1.5 THEN 2
        ELSE 3
    END;

-- View: Performance de Or�amentos
CREATE OR REPLACE VIEW vw_performance_orcamentos AS
SELECT 
    tp.nome AS tipo_produto,
    COUNT(o.id) AS total_orcamentos,
    COUNT(CASE WHEN o.status = 'aprovado' THEN 1 END) AS aprovados,
    ROUND(COUNT(CASE WHEN o.status = 'aprovado' THEN 1 END)::NUMERIC / 
          NULLIF(COUNT(o.id), 0) * 100, 2) AS taxa_conversao_pct,
    ROUND(AVG(o.preco_venda), 2) AS preco_medio,
    ROUND(AVG(o.margem_percentual), 2) AS margem_media_pct,
    ROUND(AVG(o.margem_absoluta), 2) AS margem_media_eur
FROM orcamentos o
JOIN produtos p ON o.produto_id = p.id
JOIN tipos_produto tp ON p.tipo_produto_id = tp.id
WHERE o.data_orcamento >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY tp.nome
ORDER BY total_orcamentos DESC;

-- View: An�lise de Prazos
CREATE OR REPLACE VIEW vw_analise_prazos AS
SELECT 
    e.id,
    c.nome AS cliente,
    tp.nome AS produto,
    e.data_pedido,
    e.prazo_prometido_dias,
    e.data_entrega_prometida,
    e.data_entrega_real,
    e.status,
    CASE 
        WHEN e.data_entrega_real IS NOT NULL 
        THEN e.data_entrega_real - e.data_entrega_prometida
        WHEN e.status NOT IN ('entregue', 'cancelado')
        THEN CURRENT_DATE - e.data_entrega_prometida
        ELSE NULL
    END AS dias_atraso,
    CASE
        WHEN e.data_entrega_real <= e.data_entrega_prometida THEN 'No Prazo'
        WHEN e.data_entrega_real > e.data_entrega_prometida THEN 'Atrasado'
        WHEN e.status NOT IN ('entregue', 'cancelado') 
             AND CURRENT_DATE > e.data_entrega_prometida THEN 'Em Atraso'
        ELSE 'Pendente'
    END AS situacao_prazo
FROM encomendas e
JOIN clientes c ON e.cliente_id = c.id
JOIN produtos p ON e.produto_id = p.id
JOIN tipos_produto tp ON p.tipo_produto_id = tp.id
ORDER BY e.data_pedido DESC;

-- View: Custo por Produto
CREATE OR REPLACE VIEW vw_custo_produtos AS
SELECT 
    tp.nome AS tipo_produto,
    p.codigo,
    SUM(pm.quantidade_por_unidade * m.preco_por_unidade) AS custo_material_estimado,
    p.horas_mao_obra,
    p.horas_mao_obra * 15.00 AS custo_mao_obra_estimado, -- �15/hora estimado
    SUM(pm.quantidade_por_unidade * m.preco_por_unidade) + 
        (p.horas_mao_obra * 15.00) AS custo_total_estimado
FROM produtos p
JOIN tipos_produto tp ON p.tipo_produto_id = tp.id
LEFT JOIN produtos_materiais pm ON p.tipo_produto_id = pm.tipo_produto_id
LEFT JOIN materiais m ON pm.material_id = m.id
GROUP BY tp.nome, p.codigo, p.horas_mao_obra, p.id
ORDER BY custo_total_estimado DESC;

-- ============================================
-- �NDICES PARA PERFORMANCE
-- ============================================

CREATE INDEX IF NOT EXISTS idx_materiais_tipo ON materiais(tipo);
CREATE INDEX IF NOT EXISTS idx_orcamentos_status ON orcamentos(status);
CREATE INDEX IF NOT EXISTS idx_orcamentos_data ON orcamentos(data_orcamento);
CREATE INDEX IF NOT EXISTS idx_encomendas_status ON encomendas(status);
CREATE INDEX IF NOT EXISTS idx_encomendas_data ON encomendas(data_pedido);
CREATE INDEX IF NOT EXISTS idx_movimentos_material ON movimentos_stock(material_id);
CREATE INDEX IF NOT EXISTS idx_movimentos_data ON movimentos_stock(data_movimento);

-- ============================================
-- COMENT�RIOS NAS TABELAS
-- ============================================

COMMENT ON TABLE materiais IS 'Cat�logo de materiais utilizados na produ��o';
COMMENT ON TABLE produtos IS 'Especifica��es de produtos e projetos customizados';
COMMENT ON TABLE orcamentos IS 'Or�amentos gerados para clientes';
COMMENT ON TABLE encomendas IS 'Encomendas confirmadas em produ��o/entrega';
COMMENT ON COLUMN materiais.lead_time_dias IS 'Tempo de entrega do fornecedor em dias';
COMMENT ON COLUMN orcamentos.margem_percentual IS 'Margem de lucro em percentual';
COMMENT ON COLUMN encomendas.prazo_prometido_dias IS 'Prazo prometido ao cliente em dias';

-- ============================================
-- EXPANSÃO 2026: Produção, Consumos, Faturação, Encomendas (Wizard/Detalhe)
-- ============================================

-- Campos adicionais em encomendas (wizard / documentação / pagamento)
ALTER TABLE encomendas
    ADD COLUMN IF NOT EXISTS observacoes TEXT,
    ADD COLUMN IF NOT EXISTS metodo_pagamento VARCHAR(30);

-- --------------------------------------------
-- 1) TEMPO POR ETAPA DE PRODUÇÃO
-- --------------------------------------------

CREATE TABLE IF NOT EXISTS etapas_producao (
    id SERIAL PRIMARY KEY,
    encomenda_id INTEGER NOT NULL REFERENCES encomendas(id) ON DELETE CASCADE,
    tipo_etapa VARCHAR(80) NOT NULL,
    tempo_estimado INTEGER NOT NULL CHECK (tempo_estimado >= 0), -- minutos
    tempo_real INTEGER CHECK (tempo_real >= 0), -- minutos
    responsavel VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'pendente' CHECK (status IN ('pendente', 'em_andamento', 'pausado', 'concluido', 'cancelado')),
    data_inicio TIMESTAMP,
    data_fim TIMESTAMP,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_etapas_producao_encomenda ON etapas_producao(encomenda_id);
CREATE INDEX IF NOT EXISTS idx_etapas_producao_status ON etapas_producao(status);

CREATE TABLE IF NOT EXISTS registro_tempo (
    id SERIAL PRIMARY KEY,
    etapa_id INTEGER NOT NULL REFERENCES etapas_producao(id) ON DELETE CASCADE,
    evento VARCHAR(10) NOT NULL CHECK (evento IN ('inicio', 'pausa', 'retoma', 'fim')),
    timestamp_evento TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    observacoes TEXT,
    eficiencia NUMERIC(6,2)
);

CREATE INDEX IF NOT EXISTS idx_registro_tempo_etapa ON registro_tempo(etapa_id);
CREATE INDEX IF NOT EXISTS idx_registro_tempo_ts ON registro_tempo(timestamp_evento);

-- Recalcular tempo_real (minutos) a partir de eventos inicio/pausa/retoma/fim
CREATE OR REPLACE FUNCTION fn_recalc_tempo_etapa(p_etapa_id INTEGER)
RETURNS VOID AS $$
DECLARE
    ts_inicio TIMESTAMP;
    ts_fim TIMESTAMP;
    paused_seconds NUMERIC := 0;
BEGIN
    SELECT MIN(timestamp_evento) FILTER (WHERE evento = 'inicio') INTO ts_inicio
    FROM registro_tempo
    WHERE etapa_id = p_etapa_id;

    SELECT MAX(timestamp_evento) FILTER (WHERE evento = 'fim') INTO ts_fim
    FROM registro_tempo
    WHERE etapa_id = p_etapa_id;

    IF ts_inicio IS NULL THEN
        RETURN;
    END IF;

    -- Somar tempos em pausa: cada 'pausa' até à próxima 'retoma' (ou 'fim')
    WITH eventos AS (
        SELECT
            timestamp_evento,
            evento,
            LEAD(timestamp_evento) OVER (ORDER BY timestamp_evento) AS next_ts,
            LEAD(evento) OVER (ORDER BY timestamp_evento) AS next_event
        FROM registro_tempo
        WHERE etapa_id = p_etapa_id
        ORDER BY timestamp_evento
    )
    SELECT COALESCE(SUM(EXTRACT(EPOCH FROM (COALESCE(next_ts, ts_fim) - timestamp_evento))), 0)
    INTO paused_seconds
    FROM eventos
    WHERE evento = 'pausa'
      AND (next_event IN ('retoma', 'fim') OR next_event IS NULL)
      AND COALESCE(next_ts, ts_fim) IS NOT NULL;

    UPDATE etapas_producao
    SET
        data_inicio = COALESCE(data_inicio, ts_inicio),
        data_fim = COALESCE(data_fim, ts_fim),
        tempo_real = CASE
            WHEN ts_fim IS NULL THEN tempo_real
            ELSE GREATEST(0, ROUND(((EXTRACT(EPOCH FROM (ts_fim - ts_inicio)) - paused_seconds) / 60.0))::INTEGER)
        END
    WHERE id = p_etapa_id;
END;
$$ LANGUAGE plpgsql;

-- Trigger: atualizar status/data_inicio/data_fim e recalcular tempo_real
CREATE OR REPLACE FUNCTION trg_registro_tempo_apply()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.evento = 'inicio' THEN
        UPDATE etapas_producao
        SET status = 'em_andamento',
            data_inicio = COALESCE(data_inicio, NEW.timestamp_evento)
        WHERE id = NEW.etapa_id;
    ELSIF NEW.evento = 'pausa' THEN
        UPDATE etapas_producao SET status = 'pausado' WHERE id = NEW.etapa_id;
    ELSIF NEW.evento = 'retoma' THEN
        UPDATE etapas_producao SET status = 'em_andamento' WHERE id = NEW.etapa_id;
    ELSIF NEW.evento = 'fim' THEN
        UPDATE etapas_producao
        SET status = 'concluido',
            data_fim = COALESCE(data_fim, NEW.timestamp_evento)
        WHERE id = NEW.etapa_id;
        PERFORM fn_recalc_tempo_etapa(NEW.etapa_id);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_registro_tempo_apply ON registro_tempo;
CREATE TRIGGER tr_registro_tempo_apply
AFTER INSERT ON registro_tempo
FOR EACH ROW
EXECUTE FUNCTION trg_registro_tempo_apply();

-- Views: produção
CREATE OR REPLACE VIEW tempo_medio_real_vs_estimado AS
SELECT
    tipo_etapa,
    COUNT(*) AS total_etapas,
    ROUND(AVG(tempo_estimado)::NUMERIC, 1) AS tempo_estimado_medio_min,
    ROUND(AVG(tempo_real)::NUMERIC, 1) AS tempo_real_medio_min,
    ROUND(AVG((tempo_real - tempo_estimado))::NUMERIC, 1) AS desvio_medio_min,
    ROUND(AVG((tempo_real / NULLIF(tempo_estimado, 0)) * 100)::NUMERIC, 1) AS eficiencia_media_pct
FROM etapas_producao
WHERE status = 'concluido'
  AND tempo_real IS NOT NULL
GROUP BY tipo_etapa
ORDER BY desvio_medio_min DESC;

CREATE OR REPLACE VIEW gargalos_producao AS
SELECT
    e.id AS etapa_id,
    e.encomenda_id,
    e.tipo_etapa,
    e.responsavel,
    e.status,
    e.tempo_estimado,
    COALESCE(e.tempo_real,
        ROUND(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - e.data_inicio)) / 60.0)::INTEGER
    ) AS tempo_atual_min,
    CASE
        WHEN e.data_inicio IS NULL THEN NULL
        ELSE ROUND((EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - e.data_inicio)) / 60.0) - e.tempo_estimado)::INTEGER
    END AS atraso_estimado_min
FROM etapas_producao e
WHERE e.status IN ('em_andamento', 'pausado')
  AND e.data_inicio IS NOT NULL
  AND (EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - e.data_inicio)) / 60.0) > e.tempo_estimado
ORDER BY atraso_estimado_min DESC;

CREATE OR REPLACE VIEW produtividade_operario AS
SELECT
    COALESCE(responsavel, 'N/A') AS responsavel,
    COUNT(*) AS total_etapas,
    ROUND(AVG(tempo_estimado)::NUMERIC, 1) AS tempo_estimado_medio_min,
    ROUND(AVG(tempo_real)::NUMERIC, 1) AS tempo_real_medio_min,
    ROUND(AVG((tempo_estimado / NULLIF(tempo_real, 0)) * 100)::NUMERIC, 1) AS eficiencia_media_pct
FROM etapas_producao
WHERE status = 'concluido'
  AND tempo_real IS NOT NULL
GROUP BY COALESCE(responsavel, 'N/A')
ORDER BY eficiencia_media_pct DESC;

-- --------------------------------------------
-- 2) RASTREAMENTO DE CONSUMO DE MATERIAIS
-- --------------------------------------------

CREATE TABLE IF NOT EXISTS consumo_materiais (
    id SERIAL PRIMARY KEY,
    encomenda_id INTEGER NOT NULL REFERENCES encomendas(id) ON DELETE CASCADE,
    material_id INTEGER NOT NULL REFERENCES materiais(id),
    qtd_planeada NUMERIC(10,2) NOT NULL DEFAULT 0,
    qtd_real NUMERIC(10,2) NOT NULL DEFAULT 0,
    data_consumo DATE NOT NULL DEFAULT CURRENT_DATE,
    motivo_variacao TEXT,
    custo_real NUMERIC(12,2)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_consumo_encomenda_material ON consumo_materiais(encomenda_id, material_id);
CREATE INDEX IF NOT EXISTS idx_consumo_materiais_data ON consumo_materiais(data_consumo);

CREATE OR REPLACE FUNCTION fn_consumo_materiais_apply()
RETURNS TRIGGER AS $$
DECLARE
    delta NUMERIC(10,2);
    preco NUMERIC(10,2);
    movimento_tipo VARCHAR(20);
BEGIN
    SELECT preco_por_unidade INTO preco FROM materiais WHERE id = NEW.material_id;
    NEW.custo_real := COALESCE(NEW.custo_real, ROUND((NEW.qtd_real * COALESCE(preco, 0))::NUMERIC, 2));

    IF TG_OP = 'INSERT' THEN
        delta := NEW.qtd_real;
    ELSE
        delta := NEW.qtd_real - OLD.qtd_real;
    END IF;

    IF delta <> 0 THEN
        IF delta > 0 THEN
            movimento_tipo := 'saida';
        ELSE
            movimento_tipo := 'entrada';
        END IF;

        INSERT INTO movimentos_stock (material_id, tipo_movimento, quantidade, motivo, encomenda_id, data_movimento)
        VALUES (NEW.material_id, movimento_tipo, ABS(delta), 'Consumo materiais (auto)', NEW.encomenda_id, CURRENT_TIMESTAMP);

        IF delta > 0 THEN
            UPDATE materiais SET stock_atual = stock_atual - ABS(delta), ultima_atualizacao = CURRENT_TIMESTAMP WHERE id = NEW.material_id;
        ELSE
            UPDATE materiais SET stock_atual = stock_atual + ABS(delta), ultima_atualizacao = CURRENT_TIMESTAMP WHERE id = NEW.material_id;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_consumo_materiais_apply ON consumo_materiais;
CREATE TRIGGER tr_consumo_materiais_apply
BEFORE INSERT OR UPDATE ON consumo_materiais
FOR EACH ROW
EXECUTE FUNCTION fn_consumo_materiais_apply();

-- Views: consumos / desperdício
CREATE OR REPLACE VIEW vw_consumo_vs_planeado AS
SELECT
    cm.encomenda_id,
    cm.material_id,
    m.nome AS material,
    m.tipo,
    m.unidade,
    ROUND(cm.qtd_planeada, 2) AS qtd_planeada,
    ROUND(cm.qtd_real, 2) AS qtd_real,
    ROUND((cm.qtd_real - cm.qtd_planeada), 2) AS variacao,
    ROUND((cm.qtd_real - cm.qtd_planeada) / NULLIF(cm.qtd_planeada, 0) * 100, 2) AS variacao_pct,
    ROUND(COALESCE(cm.custo_real, cm.qtd_real * m.preco_por_unidade), 2) AS custo_real
FROM consumo_materiais cm
JOIN materiais m ON cm.material_id = m.id;

CREATE OR REPLACE VIEW vw_desperdicio_mensal AS
SELECT
    TO_CHAR(DATE_TRUNC('month', cm.data_consumo), 'YYYY-MM') AS mes,
    m.tipo,
    m.nome AS material,
    ROUND(SUM(GREATEST(cm.qtd_real - cm.qtd_planeada, 0)), 2) AS desperdicio_qtd,
    ROUND(SUM(GREATEST(cm.qtd_real - cm.qtd_planeada, 0) * m.preco_por_unidade), 2) AS desperdicio_valor
FROM consumo_materiais cm
JOIN materiais m ON cm.material_id = m.id
GROUP BY DATE_TRUNC('month', cm.data_consumo), m.tipo, m.nome
ORDER BY mes DESC, desperdicio_valor DESC;

CREATE OR REPLACE VIEW vw_eficiencia_material AS
SELECT
    m.id AS material_id,
    m.nome AS material,
    m.tipo,
    ROUND(SUM(cm.qtd_planeada), 2) AS planeado_total,
    ROUND(SUM(cm.qtd_real), 2) AS real_total,
    ROUND((SUM(cm.qtd_planeada) / NULLIF(SUM(cm.qtd_real), 0)) * 100, 2) AS eficiencia_pct,
    ROUND(SUM(GREATEST(cm.qtd_real - cm.qtd_planeada, 0) * m.preco_por_unidade), 2) AS custo_desperdicio
FROM consumo_materiais cm
JOIN materiais m ON cm.material_id = m.id
GROUP BY m.id, m.nome, m.tipo
ORDER BY custo_desperdicio DESC;

-- --------------------------------------------
-- 3) SISTEMA FATURAÇÃO COMPLETO
-- --------------------------------------------

CREATE TABLE IF NOT EXISTS numeracao_faturas (
    ano INTEGER PRIMARY KEY,
    ultimo_num INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS faturas (
    id SERIAL PRIMARY KEY,
    num_fatura VARCHAR(20) UNIQUE,
    encomenda_id INTEGER REFERENCES encomendas(id) ON DELETE SET NULL,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    data_emissao DATE NOT NULL DEFAULT CURRENT_DATE,
    vencimento DATE,
    valor_base NUMERIC(12,2) NOT NULL DEFAULT 0,
    taxa_iva NUMERIC(5,2) NOT NULL DEFAULT 23.00,
    valor_iva NUMERIC(12,2) NOT NULL DEFAULT 0,
    valor_total NUMERIC(12,2) NOT NULL DEFAULT 0,
    valor_pago NUMERIC(12,2) NOT NULL DEFAULT 0,
    saldo NUMERIC(12,2) GENERATED ALWAYS AS (valor_total - valor_pago) STORED,
    metodo_pagamento VARCHAR(30),
    status VARCHAR(20) NOT NULL DEFAULT 'rascunho' CHECK (status IN ('rascunho', 'emitida', 'parcial', 'paga', 'vencida', 'cancelada')),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_faturas_cliente ON faturas(cliente_id);
CREATE INDEX IF NOT EXISTS idx_faturas_status ON faturas(status);
CREATE INDEX IF NOT EXISTS idx_faturas_vencimento ON faturas(vencimento);

CREATE TABLE IF NOT EXISTS itens_fatura (
    id SERIAL PRIMARY KEY,
    fatura_id INTEGER NOT NULL REFERENCES faturas(id) ON DELETE CASCADE,
    descricao TEXT NOT NULL,
    quantidade NUMERIC(12,2) NOT NULL DEFAULT 1,
    preco_unitario NUMERIC(12,2) NOT NULL DEFAULT 0,
    taxa_iva NUMERIC(5,2) NOT NULL DEFAULT 23.00,
    valor_linha_base NUMERIC(12,2) GENERATED ALWAYS AS (quantidade * preco_unitario) STORED,
    valor_linha_iva NUMERIC(12,2) GENERATED ALWAYS AS ((quantidade * preco_unitario) * (taxa_iva / 100.0)) STORED,
    valor_linha_total NUMERIC(12,2) GENERATED ALWAYS AS ((quantidade * preco_unitario) + ((quantidade * preco_unitario) * (taxa_iva / 100.0))) STORED
);

CREATE INDEX IF NOT EXISTS idx_itens_fatura_fatura ON itens_fatura(fatura_id);

CREATE TABLE IF NOT EXISTS pagamentos (
    id SERIAL PRIMARY KEY,
    fatura_id INTEGER NOT NULL REFERENCES faturas(id) ON DELETE CASCADE,
    data_pagamento DATE NOT NULL DEFAULT CURRENT_DATE,
    valor_pago NUMERIC(12,2) NOT NULL CHECK (valor_pago >= 0),
    metodo VARCHAR(30),
    referencia VARCHAR(80)
);

CREATE INDEX IF NOT EXISTS idx_pagamentos_fatura ON pagamentos(fatura_id);
CREATE INDEX IF NOT EXISTS idx_pagamentos_data ON pagamentos(data_pagamento);

-- Gerar num_fatura (AAAA/0001) e atualizar numeracao_faturas
CREATE OR REPLACE FUNCTION fn_set_num_fatura()
RETURNS TRIGGER AS $$
DECLARE
    v_ano INTEGER;
    v_novo_num INTEGER;
BEGIN
    IF NEW.num_fatura IS NOT NULL AND NEW.num_fatura <> '' THEN
        RETURN NEW;
    END IF;

    v_ano := EXTRACT(YEAR FROM COALESCE(NEW.data_emissao, CURRENT_DATE))::INTEGER;

    INSERT INTO numeracao_faturas (ano, ultimo_num)
    VALUES (v_ano, 0)
    ON CONFLICT (ano) DO NOTHING;

    UPDATE numeracao_faturas nf
    SET ultimo_num = nf.ultimo_num + 1
    WHERE nf.ano = v_ano
    RETURNING nf.ultimo_num INTO v_novo_num;

    NEW.num_fatura := v_ano::TEXT || '/' || LPAD(v_novo_num::TEXT, 4, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_set_num_fatura ON faturas;
CREATE TRIGGER tr_set_num_fatura
BEFORE INSERT ON faturas
FOR EACH ROW
EXECUTE FUNCTION fn_set_num_fatura();

-- Recalcular totais da fatura quando itens mudam
CREATE OR REPLACE FUNCTION fn_recalc_totais_fatura(p_fatura_id INTEGER)
RETURNS VOID AS $$
BEGIN
    UPDATE faturas f
    SET
        valor_base = COALESCE((SELECT SUM(valor_linha_base) FROM itens_fatura WHERE fatura_id = p_fatura_id), 0),
        valor_iva = COALESCE((SELECT SUM(valor_linha_iva) FROM itens_fatura WHERE fatura_id = p_fatura_id), 0),
        valor_total = COALESCE((SELECT SUM(valor_linha_total) FROM itens_fatura WHERE fatura_id = p_fatura_id), 0)
    WHERE f.id = p_fatura_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION trg_itens_fatura_recalc()
RETURNS TRIGGER AS $$
DECLARE
    fid INTEGER;
BEGIN
    fid := COALESCE(NEW.fatura_id, OLD.fatura_id);
    IF fid IS NOT NULL THEN
        PERFORM fn_recalc_totais_fatura(fid);
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_itens_fatura_recalc_ins ON itens_fatura;
DROP TRIGGER IF EXISTS tr_itens_fatura_recalc_upd ON itens_fatura;
DROP TRIGGER IF EXISTS tr_itens_fatura_recalc_del ON itens_fatura;
CREATE TRIGGER tr_itens_fatura_recalc_ins AFTER INSERT ON itens_fatura FOR EACH ROW EXECUTE FUNCTION trg_itens_fatura_recalc();
CREATE TRIGGER tr_itens_fatura_recalc_upd AFTER UPDATE ON itens_fatura FOR EACH ROW EXECUTE FUNCTION trg_itens_fatura_recalc();
CREATE TRIGGER tr_itens_fatura_recalc_del AFTER DELETE ON itens_fatura FOR EACH ROW EXECUTE FUNCTION trg_itens_fatura_recalc();

-- Atualizar valor_pago e status conforme pagamentos
CREATE OR REPLACE FUNCTION fn_recalc_pagamentos_fatura(p_fatura_id INTEGER)
RETURNS VOID AS $$
DECLARE
    total_pago NUMERIC(12,2);
    total_fatura NUMERIC(12,2);
    venc DATE;
BEGIN
    SELECT COALESCE(SUM(valor_pago), 0) INTO total_pago FROM pagamentos WHERE fatura_id = p_fatura_id;
    SELECT valor_total, vencimento INTO total_fatura, venc FROM faturas WHERE id = p_fatura_id;

    UPDATE faturas
    SET valor_pago = total_pago,
        status = CASE
            WHEN status = 'cancelada' THEN 'cancelada'
            WHEN total_pago >= total_fatura AND total_fatura > 0 THEN 'paga'
            WHEN total_pago > 0 AND total_pago < total_fatura THEN 'parcial'
            WHEN venc IS NOT NULL AND venc < CURRENT_DATE AND COALESCE(total_pago, 0) < COALESCE(total_fatura, 0) THEN 'vencida'
            WHEN status = 'rascunho' THEN status
            ELSE 'emitida'
        END
    WHERE id = p_fatura_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION trg_pagamentos_recalc()
RETURNS TRIGGER AS $$
DECLARE
    fid INTEGER;
BEGIN
    fid := COALESCE(NEW.fatura_id, OLD.fatura_id);
    IF fid IS NOT NULL THEN
        PERFORM fn_recalc_pagamentos_fatura(fid);
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_pagamentos_recalc_ins ON pagamentos;
DROP TRIGGER IF EXISTS tr_pagamentos_recalc_upd ON pagamentos;
DROP TRIGGER IF EXISTS tr_pagamentos_recalc_del ON pagamentos;
CREATE TRIGGER tr_pagamentos_recalc_ins AFTER INSERT ON pagamentos FOR EACH ROW EXECUTE FUNCTION trg_pagamentos_recalc();
CREATE TRIGGER tr_pagamentos_recalc_upd AFTER UPDATE ON pagamentos FOR EACH ROW EXECUTE FUNCTION trg_pagamentos_recalc();
CREATE TRIGGER tr_pagamentos_recalc_del AFTER DELETE ON pagamentos FOR EACH ROW EXECUTE FUNCTION trg_pagamentos_recalc();

-- Views: faturação
CREATE OR REPLACE VIEW vw_aging_report AS
SELECT
    f.id AS fatura_id,
    f.num_fatura,
    f.cliente_id,
    c.nome AS cliente,
    f.data_emissao,
    f.vencimento,
    f.valor_total,
    f.valor_pago,
    f.saldo,
    GREATEST(0, CURRENT_DATE - COALESCE(f.vencimento, f.data_emissao)) AS dias_em_divida,
    CASE
        WHEN COALESCE(f.vencimento, f.data_emissao) >= CURRENT_DATE THEN '0-30'
        WHEN CURRENT_DATE - COALESCE(f.vencimento, f.data_emissao) BETWEEN 1 AND 30 THEN '0-30'
        WHEN CURRENT_DATE - COALESCE(f.vencimento, f.data_emissao) BETWEEN 31 AND 60 THEN '31-60'
        WHEN CURRENT_DATE - COALESCE(f.vencimento, f.data_emissao) BETWEEN 61 AND 90 THEN '61-90'
        ELSE '>90'
    END AS aging_bucket
FROM faturas f
JOIN clientes c ON f.cliente_id = c.id
WHERE f.status IN ('emitida', 'parcial', 'vencida')
  AND f.saldo > 0
ORDER BY dias_em_divida DESC;

CREATE OR REPLACE VIEW vw_receita_faturada_vs_recebida AS
SELECT
    TO_CHAR(DATE_TRUNC('month', f.data_emissao), 'YYYY-MM') AS mes,
    ROUND(SUM(f.valor_total), 2) AS receita_faturada,
    ROUND(SUM(f.valor_pago), 2) AS receita_recebida,
    ROUND(SUM(f.saldo), 2) AS saldo_aberto
FROM faturas f
WHERE f.status <> 'cancelada'
GROUP BY DATE_TRUNC('month', f.data_emissao)
ORDER BY mes DESC;

CREATE OR REPLACE VIEW vw_cash_flow AS
SELECT
    TO_CHAR(DATE_TRUNC('month', p.data_pagamento), 'YYYY-MM') AS mes,
    ROUND(SUM(p.valor_pago), 2) AS cash_in
FROM pagamentos p
GROUP BY DATE_TRUNC('month', p.data_pagamento)
ORDER BY mes DESC;

-- --------------------------------------------
-- 5) PÁGINA DETALHADA ENCOMENDAS: documentos + histórico
-- --------------------------------------------

CREATE TABLE IF NOT EXISTS encomenda_documentos (
    id SERIAL PRIMARY KEY,
    encomenda_id INTEGER NOT NULL REFERENCES encomendas(id) ON DELETE CASCADE,
    tipo VARCHAR(30) NOT NULL DEFAULT 'outro',
    nome_arquivo VARCHAR(255) NOT NULL,
    caminho_arquivo TEXT NOT NULL,
    mime_type VARCHAR(80),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_encomenda_documentos_encomenda ON encomenda_documentos(encomenda_id);

CREATE TABLE IF NOT EXISTS encomenda_eventos (
    id SERIAL PRIMARY KEY,
    encomenda_id INTEGER NOT NULL REFERENCES encomendas(id) ON DELETE CASCADE,
    tipo_evento VARCHAR(30) NOT NULL,
    descricao TEXT,
    usuario VARCHAR(80),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_encomenda_eventos_encomenda ON encomenda_eventos(encomenda_id);

CREATE OR REPLACE FUNCTION trg_encomendas_log_status()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND NEW.status IS DISTINCT FROM OLD.status THEN
        INSERT INTO encomenda_eventos (encomenda_id, tipo_evento, descricao, usuario)
        VALUES (NEW.id, 'status', 'Status alterado: ' || OLD.status || ' → ' || NEW.status, NULL);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_encomendas_log_status ON encomendas;
CREATE TRIGGER tr_encomendas_log_status
AFTER UPDATE ON encomendas
FOR EACH ROW
EXECUTE FUNCTION trg_encomendas_log_status();
