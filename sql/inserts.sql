-- ============================================
-- DADOS DE EXEMPLO - Sistema Ferragens
-- ============================================

-- Fornecedores
INSERT INTO fornecedores (nome, contacto, email, pais, avaliacao) VALUES
('MetalPro Portugal', '+351 253 123 456', 'comercial@metalpro.pt', 'Portugal', 4.5),
('Inox Solutions Lda', '+351 22 987 6543', 'vendas@inoxsol.pt', 'Portugal', 4.8),
('Ferros do Norte', '+351 253 456 789', 'info@ferrosnorte.pt', 'Portugal', 4.2),
('Tintas Industriais SA', '+351 21 345 6789', 'comercial@tintasind.pt', 'Portugal', 4.6),
('Global Steel EU', '+34 912 345 678', 'sales@globalsteel.eu', 'Espanha', 4.3);

-- Materiais
INSERT INTO materiais (nome, tipo, unidade, preco_por_unidade, fornecedor_id, lead_time_dias, stock_atual, stock_minimo, stock_maximo) VALUES
-- Metais
('Tubo Inox 304 40x40x2mm', 'inox', 'metro', 8.50, 2, 7, 150.00, 50.00, 300.00),
('Tubo Inox 304 50x50x2mm', 'inox', 'metro', 12.30, 2, 7, 80.00, 40.00, 200.00),
('Chapa Inox 304 2mm', 'inox', 'metro2', 45.00, 2, 10, 25.00, 15.00, 60.00),
('Tubo Ferro 40x40x2mm', 'ferro', 'metro', 4.20, 1, 5, 200.00, 80.00, 400.00),
('Tubo Ferro 50x50x3mm', 'ferro', 'metro', 6.80, 1, 5, 180.00, 70.00, 350.00),
('Perfil L Ferro 50x50x5mm', 'ferro', 'metro', 5.50, 3, 7, 120.00, 50.00, 250.00),
('Chapa Ferro 3mm', 'ferro', 'metro2', 22.00, 3, 5, 40.00, 20.00, 80.00),
('Var�o Inox 12mm', 'inox', 'metro', 3.80, 2, 7, 90.00, 30.00, 150.00),
-- Consum�veis
('El�ctrodos Rutilo 2.5mm', 'consumivel', 'kg', 4.50, 1, 3, 45.00, 20.00, 100.00),
('Disco Corte Inox 125mm', 'consumivel', 'unidade', 1.80, 1, 3, 150.00, 50.00, 300.00),
('Disco Corte Ferro 125mm', 'consumivel', 'unidade', 1.20, 1, 3, 180.00, 60.00, 350.00),
-- Acabamentos
('Tinta Primer Cinza', 'pintura', 'litro', 12.50, 4, 5, 35.00, 15.00, 80.00),
('Tinta Ep�xi Preta', 'pintura', 'litro', 18.00, 4, 5, 28.00, 12.00, 60.00),
('Tinta Ep�xi Branca', 'pintura', 'litro', 18.00, 4, 5, 22.00, 12.00, 60.00),
('Verniz Prote��o UV', 'pintura', 'litro', 22.00, 4, 7, 15.00, 8.00, 40.00),
-- Acess�rios
('Dobradi�as Pesadas Inox', 'acessorio', 'unidade', 8.50, 2, 10, 40.00, 20.00, 80.00),
('Fechaduras Seguran�a', 'acessorio', 'unidade', 35.00, 2, 10, 15.00, 8.00, 40.00),
('Motor Port�o Autom�tico', 'acessorio', 'unidade', 280.00, 5, 14, 5.00, 3.00, 12.00);

-- Tipos de Produto
INSERT INTO tipos_produto (nome, descricao, categoria) VALUES
('Port�o Simples', 'Port�o b�sico em estrutura de tubo com chapas', 'portoes'),
('Port�o com Grade Decorativa', 'Port�o com grade trabalhada e detalhes', 'portoes'),
('Port�o Autom�tico', 'Port�o motorizado com automa��o', 'portoes'),
('Guarda Escadas Inox', 'Guarda-corpo para escadas em inox polido', 'guardas'),
('Estrutura Met�lica Cobertura', 'Estrutura para telhado ou cobertura', 'estruturas'),
('Port�o Industrial', 'Port�o refor�ado para uso industrial', 'portoes');

-- BOM - Bill of Materials (quanto de cada material por tipo de produto)
INSERT INTO produtos_materiais (tipo_produto_id, material_id, quantidade_por_unidade) VALUES
-- Port�o Simples (tipo_produto_id = 1)
(1, 5, 12.00),  -- 12m Tubo Ferro 50x50x3mm
(1, 7, 3.50),   -- 3.5m� Chapa Ferro 3mm
(1, 12, 2.00),  -- 2L Tinta Primer
(1, 13, 1.50),  -- 1.5L Tinta Ep�xi Preta
(1, 16, 4.00),  -- 4 Dobradi�as
(1, 17, 1.00),  -- 1 Fechadura
-- Port�o com Grade (tipo_produto_id = 2)
(2, 5, 14.00),  -- 14m Tubo Ferro 50x50x3mm
(2, 8, 25.00),  -- 25m Var�o Inox (grade decorativa)
(2, 12, 2.50),  -- 2.5L Primer
(2, 14, 2.00),  -- 2L Tinta Branca
(2, 16, 4.00),
(2, 17, 1.00),
-- Port�o Autom�tico (tipo_produto_id = 3)
(3, 2, 15.00),  -- 15m Tubo Inox 50x50
(3, 3, 4.00),   -- 4m� Chapa Inox
(3, 16, 6.00),
(3, 17, 1.00),
(3, 18, 1.00),  -- 1 Motor
-- Guarda Escadas (tipo_produto_id = 4)
(4, 1, 8.00),   -- 8m Tubo Inox 40x40
(4, 8, 12.00),  -- 12m Var�o Inox
(4, 15, 0.50),  -- 0.5L Verniz
-- Estrutura Met�lica (tipo_produto_id = 5)
(5, 6, 45.00),  -- 45m Perfil L
(5, 5, 30.00),  -- 30m Tubo Ferro 50x50
(5, 12, 5.00),  -- 5L Primer
(5, 13, 4.00);  -- 4L Tinta Preta

-- Produtos espec�ficos
INSERT INTO produtos (tipo_produto_id, codigo, descricao, largura_metros, altura_metros, horas_mao_obra, complexidade) VALUES
(1, 'PORT-SMP-001', 'Port�o simples 3x2m ferro preto', 3.00, 2.00, 12.0, 'baixa'),
(1, 'PORT-SMP-002', 'Port�o simples 4x2.5m ferro preto', 4.00, 2.50, 16.0, 'baixa'),
(2, 'PORT-GRD-001', 'Port�o grade decorativa 3.5x2.2m', 3.50, 2.20, 20.0, 'media'),
(2, 'PORT-GRD-002', 'Port�o grade decorativa 4x2.5m', 4.00, 2.50, 24.0, 'media'),
(3, 'PORT-AUT-001', 'Port�o autom�tico inox 4x2.5m', 4.00, 2.50, 28.0, 'alta'),
(3, 'PORT-AUT-002', 'Port�o autom�tico inox 5x2.5m', 5.00, 2.50, 32.0, 'alta'),
(4, 'GRD-ESC-001', 'Guarda escadas inox 5m linear', 5.00, 1.10, 10.0, 'media'),
(4, 'GRD-ESC-002', 'Guarda escadas inox 8m linear', 8.00, 1.10, 14.0, 'media'),
(5, 'EST-COB-001', 'Estrutura cobertura 6x4m', 6.00, 3.50, 40.0, 'alta'),
(6, 'PORT-IND-001', 'Port�o industrial 6x3m refor�ado', 6.00, 3.00, 35.0, 'alta');

-- Clientes
INSERT INTO clientes (nome, tipo, nif, contacto, email, morada) VALUES
('Jo�o Silva Constru��es Lda', 'empresa', '501234567', '+351 253 111 222', 'joao@silvaconstrucoes.pt', 'Rua das Flores 45, Guimar�es'),
('Maria Santos', 'particular', '123456789', '+351 912 345 678', 'maria.santos@email.pt', 'Av. Principal 123, Braga'),
('TechBuild SA', 'empresa', '502345678', '+351 253 222 333', 'comercial@techbuild.pt', 'Zona Industrial Lote 7, Famalic�o'),
('Ant�nio Costa', 'particular', '234567890', '+351 933 456 789', 'antonio.costa@email.pt', 'Rua do Com�rcio 78, Guimar�es'),
('Imobili�ria Norte Lda', 'empresa', '503456789', '+351 22 876 5432', 'info@imobiliarianorte.pt', 'Av. da Liberdade 250, Porto'),
('Carlos Mendes', 'particular', '345678901', '+351 965 432 109', 'carlosm@email.pt', 'Trav. S�o Jo�o 12, Braga'),
('Construtora Moderna SA', 'empresa', '504567890', '+351 253 444 555', 'obras@construtoramoderna.pt', 'Rua Industrial 88, Guimar�es'),
('Ana Pereira', 'particular', '456789012', '+351 917 654 321', 'anap@email.pt', 'Largo Central 5, Vizela');

-- Or�amentos (�ltimos 6 meses)
INSERT INTO orcamentos (cliente_id, produto_id, data_orcamento, custo_material, custo_mao_obra, outros_custos, margem_percentual, preco_venda, status, observacoes) VALUES
(1, 1, '2025-08-15', 185.00, 180.00, 20.00, 35.00, 520.00, 'aprovado', 'Instala��o inclu�da'),
(2, 3, '2025-08-20', 420.00, 300.00, 35.00, 40.00, 1057.00, 'aprovado', 'Cliente preferencial'),
(3, 5, '2025-09-05', 680.00, 420.00, 50.00, 38.00, 1587.00, 'aprovado', 'Projeto especial com automa��o'),
(4, 2, '2025-09-12', 225.00, 240.00, 25.00, 35.00, 662.00, 'pendente', 'Aguarda aprova��o cliente'),
(5, 9, '2025-09-20', 1250.00, 600.00, 80.00, 32.00, 2547.00, 'aprovado', 'Estrutura para condom�nio'),
(2, 7, '2025-10-03', 320.00, 150.00, 18.00, 36.00, 664.00, 'aprovado', NULL),
(6, 1, '2025-10-15', 185.00, 180.00, 20.00, 35.00, 520.00, 'rejeitado', 'Cliente achou caro'),
(7, 10, '2025-10-22', 980.00, 525.00, 65.00, 35.00, 2120.00, 'aprovado', 'Port�o para f�brica'),
(8, 4, '2025-11-05', 380.00, 360.00, 30.00, 37.00, 1055.00, 'aprovado', NULL),
(1, 6, '2025-11-18', 720.00, 480.00, 55.00, 38.00, 1731.00, 'aprovado', 'Segunda encomenda do cliente'),
(3, 8, '2025-11-28', 385.00, 210.00, 22.00, 36.00, 839.00, 'pendente', 'Aguarda visita t�cnica'),
(4, 2, '2025-12-10', 225.00, 240.00, 25.00, 35.00, 662.00, 'aprovado', 'Aprovado ap�s negocia��o'),
(5, 5, '2025-12-20', 680.00, 420.00, 50.00, 35.00, 1554.00, 'aprovado', 'Condom�nio fase 2'),
(6, 3, '2026-01-08', 420.00, 300.00, 35.00, 38.00, 1042.00, 'pendente', 'Or�amento recente');

-- Encomendas (aprovadas e em execu��o)
INSERT INTO encomendas (orcamento_id, cliente_id, produto_id, data_pedido, prazo_prometido_dias, data_entrega_real, status, valor_total, prioridade) VALUES
(1, 1, 1, '2025-08-20', 15, '2025-09-02', 'entregue', 520.00, 'normal'),
(2, 2, 3, '2025-08-25', 21, '2025-09-18', 'entregue', 1057.00, 'alta'),
(3, 3, 5, '2025-09-10', 25, '2025-10-08', 'entregue', 1587.00, 'alta'),
(5, 5, 9, '2025-09-25', 30, '2025-10-28', 'entregue', 2547.00, 'normal'),
(6, 2, 7, '2025-10-08', 18, '2025-10-30', 'entregue', 664.00, 'normal'),
(8, 7, 10, '2025-10-28', 28, '2025-11-28', 'entregue', 2120.00, 'alta'),
(9, 8, 4, '2025-11-10', 20, '2025-12-05', 'entregue', 1055.00, 'normal'),
(10, 1, 6, '2025-11-22', 22, NULL, 'em_producao', 1731.00, 'alta'),
(12, 4, 2, '2025-12-15', 18, NULL, 'em_producao', 662.00, 'normal'),
(13, 5, 5, '2025-12-28', 24, NULL, 'aguarda_material', 1554.00, 'urgente');

-- Movimentos de Stock (�ltimos 2 meses - entradas e sa�das)
INSERT INTO movimentos_stock (material_id, tipo_movimento, quantidade, motivo, encomenda_id, data_movimento) VALUES
-- Entradas (compras)
(1, 'entrada', 100.00, 'Reposi��o stock', NULL, '2025-11-05'),
(2, 'entrada', 50.00, 'Reposi��o stock', NULL, '2025-11-05'),
(5, 'entrada', 120.00, 'Reposi��o stock', NULL, '2025-11-10'),
(13, 'entrada', 20.00, 'Reposi��o stock', NULL, '2025-11-15'),
-- Sa�das (produ��o)
(1, 'saida', 8.00, 'Produ��o guarda escadas', 7, '2025-11-12'),
(8, 'saida', 12.00, 'Produ��o guarda escadas', 7, '2025-11-12'),
(5, 'saida', 14.00, 'Produ��o port�o', 9, '2025-12-16'),
(12, 'saida', 2.50, 'Produ��o port�o', 9, '2025-12-16'),
(13, 'saida', 1.50, 'Produ��o port�o', 9, '2025-12-16'),
(2, 'saida', 15.00, 'Produ��o port�o autom�tico', 10, '2025-12-29'),
(3, 'saida', 4.00, 'Produ��o port�o autom�tico', 10, '2025-12-29'),
(18, 'saida', 1.00, 'Instala��o motor', 10, '2025-12-30'),
-- Ajustes
(10, 'ajuste', -5.00, 'Correc��o invent�rio', NULL, '2025-12-01'),
(9, 'ajuste', 3.00, 'Correc��o invent�rio', NULL, '2025-12-01');

-- Atualizar stocks ap�s movimentos
UPDATE materiais SET stock_atual = stock_atual - 8.00 WHERE id = 1;
UPDATE materiais SET stock_atual = stock_atual - 12.00 WHERE id = 8;
UPDATE materiais SET stock_atual = stock_atual - 14.00 WHERE id = 5;
UPDATE materiais SET stock_atual = stock_atual - 2.50 WHERE id = 12;
UPDATE materiais SET stock_atual = stock_atual - 1.50 WHERE id = 13;
UPDATE materiais SET stock_atual = stock_atual - 15.00 WHERE id = 2;
UPDATE materiais SET stock_atual = stock_atual - 4.00 WHERE id = 3;
UPDATE materiais SET stock_atual = stock_atual - 1.00 WHERE id = 18;

-- ============================================
-- DADOS EXEMPLO (2026): Produção / Consumos / Faturação
-- ============================================

-- Etapas de produção para encomendas em produção/aguarda material
INSERT INTO etapas_producao (encomenda_id, tipo_etapa, tempo_estimado, responsavel, status, data_inicio)
VALUES
(8, 'Corte & Preparação', 240, 'Rui', 'em_andamento', CURRENT_TIMESTAMP - INTERVAL '5 hours'),
(8, 'Soldadura', 360, 'Rui', 'pendente', NULL),
(9, 'Corte & Preparação', 180, 'Ana', 'em_andamento', CURRENT_TIMESTAMP - INTERVAL '3 hours'),
(9, 'Pintura', 120, 'Ana', 'pendente', NULL),
(10, 'Montagem', 300, 'Carlos', 'pausado', CURRENT_TIMESTAMP - INTERVAL '8 hours');

-- Registo de tempo (eventos) para simular pauses e conclusão
INSERT INTO registro_tempo (etapa_id, evento, timestamp_evento, observacoes)
SELECT id, 'inicio', data_inicio, 'Início automático (seed)'
FROM etapas_producao
WHERE status IN ('em_andamento', 'pausado') AND data_inicio IS NOT NULL;

INSERT INTO registro_tempo (etapa_id, evento, timestamp_evento, observacoes)
SELECT id, 'pausa', CURRENT_TIMESTAMP - INTERVAL '6 hours', 'Paragem para aguardar consumíveis'
FROM etapas_producao
WHERE encomenda_id = 10 AND tipo_etapa = 'Montagem';

-- Consumos planeados vs reais (exemplo)
INSERT INTO consumo_materiais (encomenda_id, material_id, qtd_planeada, qtd_real, data_consumo, motivo_variacao)
VALUES
(8, 2, 15.00, 16.20, CURRENT_DATE - 2, 'Cortes adicionais por ajuste em obra'),
(8, 3, 4.00, 4.50, CURRENT_DATE - 2, 'Desperdício por defeito na chapa'),
(9, 5, 14.00, 13.20, CURRENT_DATE - 1, 'Otimização de corte'),
(9, 12, 2.50, 2.80, CURRENT_DATE - 1, 'Primário extra em segunda demão');

-- Faturas + itens + pagamentos (numeração e totais são calculados por triggers)
INSERT INTO faturas (encomenda_id, cliente_id, data_emissao, vencimento, metodo_pagamento, status)
VALUES
(1, 1, '2025-09-02', '2025-10-02', 'transferencia', 'emitida'),
(2, 2, '2025-09-18', '2025-10-18', 'mb', 'emitida'),
(8, 1, CURRENT_DATE - 20, CURRENT_DATE - 5, 'transferencia', 'emitida');

-- Itens (uma linha simples por fatura)
INSERT INTO itens_fatura (fatura_id, descricao, quantidade, preco_unitario, taxa_iva)
SELECT f.id, 'Serviço / Produto (Encomenda #' || COALESCE(f.encomenda_id::TEXT, '-') || ')', 1, e.valor_total / 1.23, 23.00
FROM faturas f
LEFT JOIN encomendas e ON e.id = f.encomenda_id
WHERE f.encomenda_id IS NOT NULL;

-- Pagamentos (exemplo parcial e em atraso)
INSERT INTO pagamentos (fatura_id, data_pagamento, valor_pago, metodo, referencia)
SELECT id, CURRENT_DATE - 10, 200.00, 'transferencia', 'TRF-EXEMPLO-001'
FROM faturas
WHERE encomenda_id = 8;

-- Documentos (paths são exemplos; a app guarda ficheiros em data/uploads)
INSERT INTO encomenda_documentos (encomenda_id, tipo, nome_arquivo, caminho_arquivo, mime_type)
VALUES
(8, 'foto', 'medidas_portao.jpg', 'data/uploads/encomenda_8/medidas_portao.jpg', 'image/jpeg');

-- Histórico
INSERT INTO encomenda_eventos (encomenda_id, tipo_evento, descricao, usuario)
VALUES
(8, 'nota', 'Cliente pediu alteração de cor para preto mate.', 'admin'),
(9, 'nota', 'Confirmar entrega de materiais na próxima semana.', 'admin');
