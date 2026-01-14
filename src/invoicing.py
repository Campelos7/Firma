from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from typing import Optional

import pandas as pd

try:
    from src.database import get_database
except ModuleNotFoundError:
    from database import get_database


DEFAULT_IVA = 23.00


def _has_table(table_name: str) -> bool:
    db = get_database()
    df = db.execute_query("SELECT to_regclass(%s) AS reg", (f"public.{table_name}",))
    if df.empty:
        return False
    return df.iloc[0]["reg"] is not None


def list_faturas(limit: int = 200) -> pd.DataFrame:
    db = get_database()
    q = f"""
    SELECT
        f.id,
        f.num_fatura,
        c.nome AS cliente,
        f.data_emissao,
        f.vencimento,
        f.valor_total,
        f.valor_pago,
        f.saldo,
        f.status,
        f.metodo_pagamento,
        f.encomenda_id
    FROM faturas f
    JOIN clientes c ON f.cliente_id = c.id
    ORDER BY f.data_emissao DESC, f.id DESC
    LIMIT {int(limit)}
    """
    return db.execute_query(q)


def get_aging_report() -> pd.DataFrame:
    db = get_database()
    return db.execute_query("SELECT * FROM vw_aging_report")


def get_receita_faturada_vs_recebida() -> pd.DataFrame:
    db = get_database()
    return db.execute_query("SELECT * FROM vw_receita_faturada_vs_recebida")


def get_cash_flow() -> pd.DataFrame:
    db = get_database()
    return db.execute_query("SELECT * FROM vw_cash_flow")


def refresh_vencidas() -> bool:
    """Atualiza status para 'vencida' quando vencimento passou e ainda há saldo em aberto."""
    db = get_database()
    q = """
    UPDATE faturas
    SET status = 'vencida'
    WHERE status IN ('emitida', 'parcial')
        AND vencimento IS NOT NULL
        AND vencimento < CURRENT_DATE
        AND saldo > 0
    """
    return db.execute_update(q)


def create_fatura(
    cliente_id: int,
    encomenda_id: Optional[int] = None,
    data_emissao: Optional[date] = None,
    vencimento: Optional[date] = None,
    metodo_pagamento: Optional[str] = None,
    status: str = "rascunho",
) -> int:
    db = get_database()
    q = """
    INSERT INTO faturas (cliente_id, encomenda_id, data_emissao, vencimento, metodo_pagamento, status)
    VALUES (%s, %s, COALESCE(%s, CURRENT_DATE), %s, %s, %s)
    RETURNING id
    """
    fatura_id = db.execute_returning(q, (cliente_id, encomenda_id, data_emissao, vencimento, metodo_pagamento, status))
    if fatura_id is None:
        if not _has_table("faturas"):
            raise RuntimeError(
                "A tabela 'faturas' não existe na BD. Aplica o schema: python scripts\\apply_schema.py"
            )
        raise RuntimeError(db.last_error or "Falha ao criar fatura")
    return int(fatura_id)


def add_item(
    fatura_id: int,
    descricao: str,
    quantidade: float,
    preco_unitario: float,
    taxa_iva: float = DEFAULT_IVA,
) -> bool:
    db = get_database()
    q = """
    INSERT INTO itens_fatura (fatura_id, descricao, quantidade, preco_unitario, taxa_iva)
    VALUES (%s, %s, %s, %s, %s)
    """
    return db.execute_update(q, (fatura_id, descricao, quantidade, preco_unitario, taxa_iva))


def get_fatura_detail(fatura_id: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    db = get_database()
    header = db.execute_query(
        """
        SELECT
            f.*,
            c.nome AS cliente_nome,
            c.nif AS cliente_nif,
            c.email AS cliente_email,
            c.contacto AS cliente_contacto,
            c.morada AS cliente_morada
        FROM faturas f
        JOIN clientes c ON f.cliente_id = c.id
        WHERE f.id = %s
        """,
        (fatura_id,),
    )
    itens = db.execute_query(
        """
        SELECT descricao, quantidade, preco_unitario, taxa_iva, valor_linha_base, valor_linha_iva, valor_linha_total
        FROM itens_fatura
        WHERE fatura_id = %s
        ORDER BY id
        """,
        (fatura_id,),
    )
    pagamentos = db.execute_query(
        """
        SELECT data_pagamento, valor_pago, metodo, referencia
        FROM pagamentos
        WHERE fatura_id = %s
        ORDER BY data_pagamento DESC, id DESC
        """,
        (fatura_id,),
    )
    return header, itens, pagamentos


def registar_pagamento(
    fatura_id: int,
    valor_pago: float,
    metodo: Optional[str] = None,
    referencia: Optional[str] = None,
    data_pagamento: Optional[date] = None,
) -> bool:
    db = get_database()

    valor = Decimal(str(valor_pago)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if valor <= Decimal("0.00"):
        raise ValueError("O valor pago tem de ser maior que 0.")

    # Validação robusta para múltiplos pagamentos: calcula o saldo pela soma real dos pagamentos.
    # Fazemos INSERT condicional e com lock da fatura para evitar race conditions.
    insert_q = """
    WITH f AS (
        SELECT
            id,
            valor_total,
            COALESCE((SELECT SUM(p.valor_pago) FROM pagamentos p WHERE p.fatura_id = faturas.id), 0) AS total_pago
        FROM faturas
        WHERE id = %s
        FOR UPDATE
    ),
    calc AS (
        SELECT
            id,
            GREATEST(valor_total - total_pago, 0) AS saldo_calc
        FROM f
    ),
    ins AS (
        INSERT INTO pagamentos (fatura_id, data_pagamento, valor_pago, metodo, referencia)
        SELECT
            id,
            COALESCE(%s, CURRENT_DATE),
            %s,
            %s,
            %s
        FROM calc
        WHERE %s <= saldo_calc + 0.01
        RETURNING id
    )
    SELECT id FROM ins
    """

    inserted_id = db.execute_returning(
        insert_q,
        (int(fatura_id), data_pagamento, valor, metodo, referencia, valor),
    )

    if inserted_id is not None:
        return True

    # Se não inseriu, distinguir entre "fatura não existe" e "excedeu saldo".
    saldo_q = """
    SELECT
        GREATEST(
            f.valor_total - COALESCE((SELECT SUM(p.valor_pago) FROM pagamentos p WHERE p.fatura_id = f.id), 0),
            0
        ) AS saldo_calc
    FROM faturas f
    WHERE f.id = %s
    """
    df = db.execute_query(saldo_q, (int(fatura_id),))
    if df.empty:
        raise ValueError("Fatura não encontrada.")

    saldo_calc = Decimal(str(df.iloc[0]["saldo_calc"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if saldo_calc <= Decimal("0.00"):
        raise ValueError("Esta fatura já não tem saldo em aberto.")

    raise ValueError(f"Valor pago (€{valor}) excede o saldo em aberto (€{saldo_calc}).")


def gerar_fatura_de_encomenda(
    encomenda_id: int,
    vencimento: Optional[date] = None,
    metodo_pagamento: Optional[str] = None,
    taxa_iva: float = DEFAULT_IVA,
    status: str = "emitida",
) -> int:
    """Cria fatura (1 linha) baseada na encomenda, com IVA automático."""
    db = get_database()

    encomenda = db.execute_query(
        """
        SELECT
            e.id AS encomenda_id,
            e.valor_total,
            e.cliente_id,
            tp.nome AS tipo_produto,
            p.codigo
        FROM encomendas e
        JOIN produtos p ON e.produto_id = p.id
        JOIN tipos_produto tp ON p.tipo_produto_id = tp.id
        WHERE e.id = %s
        """,
        (encomenda_id,),
    )

    if encomenda.empty:
        raise ValueError("Encomenda não encontrada")

    row = encomenda.iloc[0]
    cliente_id = int(row["cliente_id"])
    valor_total = float(row["valor_total"])

    fatura_id = create_fatura(
        cliente_id=cliente_id,
        encomenda_id=int(row["encomenda_id"]),
        vencimento=vencimento,
        metodo_pagamento=metodo_pagamento,
        status=status,
    )

    preco_base = valor_total / (1.0 + (taxa_iva / 100.0))
    descricao = f"{row['tipo_produto']} ({row['codigo']}) - Encomenda #{encomenda_id}"

    ok = add_item(
        fatura_id=fatura_id,
        descricao=descricao,
        quantidade=1,
        preco_unitario=round(preco_base, 2),
        taxa_iva=taxa_iva,
    )

    if not ok:
        raise RuntimeError("Falha ao inserir itens da fatura")

    return fatura_id
