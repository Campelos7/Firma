import pandas as pd

from database import get_database


def get_consumo_vs_planeado(encomenda_id: int | None = None) -> pd.DataFrame:
    db = get_database()
    if encomenda_id is None:
        return db.execute_query("SELECT * FROM vw_consumo_vs_planeado ORDER BY encomenda_id, material")

    q = """
    SELECT *
    FROM vw_consumo_vs_planeado
    WHERE encomenda_id = %s
    ORDER BY custo_real DESC
    """
    return db.execute_query(q, (encomenda_id,))


def get_desperdicio_mensal() -> pd.DataFrame:
    db = get_database()
    return db.execute_query("SELECT * FROM vw_desperdicio_mensal")


def get_eficiencia_material() -> pd.DataFrame:
    db = get_database()
    return db.execute_query("SELECT * FROM vw_eficiencia_material")


def initialize_planeado_for_encomenda(encomenda_id: int) -> bool:
    """Cria/atualiza consumos planeados baseados no BOM do tipo de produto da encomenda."""
    db = get_database()

    q = """
    INSERT INTO consumo_materiais (encomenda_id, material_id, qtd_planeada, qtd_real, data_consumo)
    SELECT
        e.id AS encomenda_id,
        pm.material_id,
        pm.quantidade_por_unidade AS qtd_planeada,
        0 AS qtd_real,
        CURRENT_DATE
    FROM encomendas e
    JOIN produtos p ON e.produto_id = p.id
    JOIN produtos_materiais pm ON p.tipo_produto_id = pm.tipo_produto_id
    WHERE e.id = %s
    ON CONFLICT (encomenda_id, material_id)
    DO UPDATE SET qtd_planeada = EXCLUDED.qtd_planeada
    """

    return db.execute_update(q, (encomenda_id,))


def registar_consumo_real(
    encomenda_id: int,
    material_id: int,
    qtd_real: float,
    motivo_variacao: str | None = None,
) -> bool:
    """Regista (upsert) o consumo real; triggers tratam de custo e stock."""
    db = get_database()
    q = """
    INSERT INTO consumo_materiais (encomenda_id, material_id, qtd_planeada, qtd_real, data_consumo, motivo_variacao)
    VALUES (%s, %s, 0, %s, CURRENT_DATE, %s)
    ON CONFLICT (encomenda_id, material_id)
    DO UPDATE SET
        qtd_real = EXCLUDED.qtd_real,
        data_consumo = EXCLUDED.data_consumo,
        motivo_variacao = EXCLUDED.motivo_variacao
    """
    return db.execute_update(q, (encomenda_id, material_id, float(qtd_real), motivo_variacao))


def get_desperdicio_por_encomenda(encomenda_id: int) -> pd.DataFrame:
    db = get_database()
    q = """
    SELECT
        encomenda_id,
        material,
        tipo,
        unidade,
        qtd_planeada,
        qtd_real,
        variacao,
        variacao_pct,
        custo_real
    FROM vw_consumo_vs_planeado
    WHERE encomenda_id = %s
    ORDER BY custo_real DESC
    """
    return db.execute_query(q, (encomenda_id,))
