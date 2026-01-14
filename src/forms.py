import pandas as pd
from database import get_database
from datetime import date, datetime


def inserir_cliente(nome: str, contacto: str, email: str, morada: str, tipo: str = 'particular') -> bool:
    """Insere novo cliente na base de dados"""
    db = get_database()
    
    query = """
    INSERT INTO clientes (nome, contacto, email, morada, tipo)
    VALUES (%s, %s, %s, %s, %s)
    """
    
    return db.execute_update(query, (nome, contacto, email, morada, tipo))


def inserir_cliente_returning_id(
    nome: str,
    contacto: str,
    email: str,
    morada: str,
    tipo: str = "particular",
    nif: str | None = None,
) -> int | None:
    """Insere cliente e devolve o ID."""
    db = get_database()
    query = """
    INSERT INTO clientes (nome, contacto, email, morada, tipo, nif)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    return db.execute_returning(query, (nome, contacto, email, morada, tipo, nif))


def inserir_material(nome: str, tipo: str, unidade: str, preco_por_unidade: float,
                     fornecedor_id: int, lead_time_dias: int, stock_atual: float,
                     stock_minimo: float, stock_maximo: float = None) -> bool:
    """Insere novo material na base de dados"""
    db = get_database()
    
    query = """
    INSERT INTO materiais (nome, tipo, unidade, preco_por_unidade, fornecedor_id, 
                          lead_time_dias, stock_atual, stock_minimo, stock_maximo)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    return db.execute_update(query, (nome, tipo, unidade, preco_por_unidade, fornecedor_id,
                                     lead_time_dias, stock_atual, stock_minimo, stock_maximo))


def inserir_orcamento(cliente_id: int, produto_id: int,
                      custo_material: float, custo_mao_obra: float,
                      outros_custos: float, margem_percentual: float,
                      preco_venda: float, validade_dias: int = 30,
                      observacoes: str = None) -> bool:
    """Insere novo orçamento de acordo com a estrutura da tabela orcamentos"""
    db = get_database()
    
    query = """
    INSERT INTO orcamentos (
        cliente_id, produto_id, data_orcamento,
        custo_material, custo_mao_obra, outros_custos,
        margem_percentual, preco_venda,
        status, validade_dias, observacoes
    )
    VALUES (%s, %s, CURRENT_DATE,
            %s, %s, %s,
            %s, %s,
            'pendente', %s, %s)
    """
    
    return db.execute_update(
        query,
        (
            cliente_id,
            produto_id,
            custo_material,
            custo_mao_obra,
            outros_custos,
            margem_percentual,
            preco_venda,
            validade_dias,
            observacoes,
        ),
    )


def registar_movimento_stock(
    material_id: int,
    tipo_movimento: str,
    quantidade: float,
    motivo: str | None = None,
    encomenda_id: int | None = None,
    usuario: str | None = None,
) -> bool:
    """Regista movimento de stock (entrada/saída)"""
    db = get_database()
    
    query = """
    INSERT INTO movimentos_stock (
        material_id,
        tipo_movimento,
        quantidade,
        motivo,
        encomenda_id,
        data_movimento,
        usuario
    )
    VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s)
    """
    
    success = db.execute_update(
        query,
        (material_id, tipo_movimento, quantidade, motivo, encomenda_id, usuario),
    )
    
    if success:
        # Atualizar stock atual do material
        if tipo_movimento == 'entrada':
            update_query = "UPDATE materiais SET stock_atual = stock_atual + %s WHERE id = %s"
        else:  # saída
            update_query = "UPDATE materiais SET stock_atual = stock_atual - %s WHERE id = %s"
        
        db.execute_update(update_query, (quantidade, material_id))
    
    return success


def get_lista_clientes() -> pd.DataFrame:
    """Retorna lista de clientes para dropdown"""
    db = get_database()
    query = "SELECT id, nome FROM clientes ORDER BY nome"
    return db.execute_query(query)


def get_lista_produtos() -> pd.DataFrame:
    """Retorna lista de produtos para dropdown"""
    db = get_database()
    query = """
    SELECT p.id, tp.nome || ' - ' || p.codigo AS nome 
    FROM produtos p 
    JOIN tipos_produto tp ON p.tipo_produto_id = tp.id 
    ORDER BY tp.nome
    """
    return db.execute_query(query)


def get_lista_tipos_produto() -> pd.DataFrame:
    """Retorna lista de tipos de produto para wizard."""
    db = get_database()
    query = "SELECT id, nome, categoria FROM tipos_produto ORDER BY nome"
    return db.execute_query(query)


def inserir_produto(
    tipo_produto_id: int,
    codigo: str,
    descricao: str | None,
    largura_metros: float | None,
    altura_metros: float | None,
    horas_mao_obra: float,
    complexidade: str,
) -> int | None:
    """Cria um produto/configuração e devolve o ID."""
    db = get_database()
    q = """
    INSERT INTO produtos (
        tipo_produto_id, codigo, descricao, largura_metros, altura_metros, horas_mao_obra, complexidade
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    return db.execute_returning(
        q,
        (
            int(tipo_produto_id),
            codigo,
            descricao,
            largura_metros,
            altura_metros,
            float(horas_mao_obra),
            complexidade,
        ),
    )


def inserir_orcamento_returning_id(
    cliente_id: int,
    produto_id: int,
    custo_material: float,
    custo_mao_obra: float,
    outros_custos: float,
    margem_percentual: float,
    preco_venda: float,
    validade_dias: int = 30,
    observacoes: str | None = None,
) -> int | None:
    """Insere orçamento e devolve o ID."""
    db = get_database()
    q = """
    INSERT INTO orcamentos (
        cliente_id, produto_id, data_orcamento,
        custo_material, custo_mao_obra, outros_custos,
        margem_percentual, preco_venda,
        status, validade_dias, observacoes
    )
    VALUES (%s, %s, CURRENT_DATE,
            %s, %s, %s,
            %s, %s,
            'pendente', %s, %s)
    RETURNING id
    """
    return db.execute_returning(
        q,
        (
            int(cliente_id),
            int(produto_id),
            float(custo_material),
            float(custo_mao_obra),
            float(outros_custos),
            float(margem_percentual),
            float(preco_venda),
            int(validade_dias),
            observacoes,
        ),
    )


def inserir_encomenda_returning_id(
    orcamento_id: int,
    cliente_id: int,
    produto_id: int,
    prazo_prometido_dias: int,
    valor_total: float,
    prioridade: str = "normal",
    status: str = "pendente",
    metodo_pagamento: str | None = None,
    observacoes: str | None = None,
) -> int | None:
    """Cria encomenda e devolve o ID."""
    db = get_database()
    q = """
    INSERT INTO encomendas (
        orcamento_id, cliente_id, produto_id,
        data_pedido, prazo_prometido_dias,
        status, valor_total, prioridade,
        metodo_pagamento, observacoes
    )
    VALUES (%s, %s, %s,
            CURRENT_DATE, %s,
            %s, %s, %s,
            %s, %s)
    RETURNING id
    """
    return db.execute_returning(
        q,
        (
            int(orcamento_id),
            int(cliente_id),
            int(produto_id),
            int(prazo_prometido_dias),
            status,
            float(valor_total),
            prioridade,
            metodo_pagamento,
            observacoes,
        ),
    )


def get_lista_fornecedores() -> pd.DataFrame:
    """Retorna lista de fornecedores para dropdown"""
    db = get_database()
    query = "SELECT id, nome FROM fornecedores ORDER BY nome"
    return db.execute_query(query)


def get_lista_materiais() -> pd.DataFrame:
    """Retorna lista de materiais para dropdown"""
    db = get_database()
    query = "SELECT id, nome, unidade FROM materiais ORDER BY nome"
    return db.execute_query(query)


def atualizar_status_orcamento(orcamento_id: int, novo_status: str) -> bool:
    """Atualiza status de um orçamento"""
    db = get_database()
    query = "UPDATE orcamentos SET status = %s WHERE id = %s"
    return db.execute_update(query, (novo_status, orcamento_id))
