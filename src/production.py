import pandas as pd

from database import get_database


def get_etapas_ativas() -> pd.DataFrame:
    """Etapas em andamento/pausadas com indicador de atraso."""
    db = get_database()
    q = """
    SELECT
        e.id AS etapa_id,
        e.encomenda_id,
        e.tipo_etapa,
        e.responsavel,
        e.status,
        e.tempo_estimado,
        e.tempo_real,
        e.data_inicio,
        e.data_fim,
        CASE
            WHEN e.data_inicio IS NULL THEN NULL
            ELSE ROUND(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - e.data_inicio)) / 60.0)::INTEGER
        END AS minutos_desde_inicio,
        CASE
            WHEN e.data_inicio IS NULL THEN FALSE
            ELSE (EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - e.data_inicio)) / 60.0) > e.tempo_estimado
        END AS em_atraso
    FROM etapas_producao e
    WHERE e.status IN ('em_andamento', 'pausado')
    ORDER BY em_atraso DESC, e.data_inicio ASC NULLS LAST
    """
    return db.execute_query(q)


def get_gargalos() -> pd.DataFrame:
    db = get_database()
    return db.execute_query("SELECT * FROM gargalos_producao")


def get_produtividade_operario() -> pd.DataFrame:
    db = get_database()
    return db.execute_query("SELECT * FROM produtividade_operario")


def get_tempo_medio_real_vs_estimado() -> pd.DataFrame:
    db = get_database()
    return db.execute_query("SELECT * FROM tempo_medio_real_vs_estimado")


def get_gantt_encomenda(encomenda_id: int) -> pd.DataFrame:
    """Dataset para Gantt: usa data_inicio/data_fim; se não tiver fim, usa agora."""
    db = get_database()
    q = """
    SELECT
        id AS etapa_id,
        tipo_etapa,
        responsavel,
        COALESCE(data_inicio, CURRENT_TIMESTAMP) AS start,
        COALESCE(data_fim, CURRENT_TIMESTAMP) AS finish,
        status
    FROM etapas_producao
    WHERE encomenda_id = %s
    ORDER BY id
    """
    return db.execute_query(q, (encomenda_id,))


def create_etapa(
    encomenda_id: int,
    tipo_etapa: str,
    tempo_estimado_min: int,
    responsavel: str | None = None,
) -> bool:
    db = get_database()
    q = """
    INSERT INTO etapas_producao (encomenda_id, tipo_etapa, tempo_estimado, responsavel)
    VALUES (%s, %s, %s, %s)
    """
    return db.execute_update(q, (encomenda_id, tipo_etapa, int(tempo_estimado_min), responsavel))


def _insert_event(etapa_id: int, evento: str, observacoes: str | None = None) -> bool:
    db = get_database()
    q = """
    INSERT INTO registro_tempo (etapa_id, evento, timestamp_evento, observacoes)
    VALUES (%s, %s, CURRENT_TIMESTAMP, %s)
    """
    return db.execute_update(q, (etapa_id, evento, observacoes))


def iniciar_etapa(etapa_id: int) -> bool:
    """Marca hora de início e coloca status em andamento."""
    db = get_database()
    q = """
    UPDATE etapas_producao
    SET
        data_inicio = COALESCE(data_inicio, CURRENT_TIMESTAMP),
        status = 'em_andamento'
    WHERE id = %s
    """
    return db.execute_update(q, (etapa_id,))


def concluir_etapa(etapa_id: int) -> bool:
    """Marca hora de fim, conclui e calcula tempo_real em minutos."""
    db = get_database()
    q = """
    UPDATE etapas_producao
    SET
        data_inicio = COALESCE(data_inicio, CURRENT_TIMESTAMP),
        data_fim = COALESCE(data_fim, CURRENT_TIMESTAMP),
        status = 'concluido',
        tempo_real = GREATEST(
            0,
            ROUND(EXTRACT(EPOCH FROM (COALESCE(data_fim, CURRENT_TIMESTAMP) - COALESCE(data_inicio, CURRENT_TIMESTAMP))) / 60.0)::INTEGER
        )
    WHERE id = %s
    """
    return db.execute_update(q, (etapa_id,))


def start_etapa(etapa_id: int, observacoes: str | None = None) -> bool:
    return _insert_event(etapa_id, "inicio", observacoes)


def pause_etapa(etapa_id: int, observacoes: str | None = None) -> bool:
    return _insert_event(etapa_id, "pausa", observacoes)


def resume_etapa(etapa_id: int, observacoes: str | None = None) -> bool:
    return _insert_event(etapa_id, "retoma", observacoes)


def finish_etapa(etapa_id: int, observacoes: str | None = None) -> bool:
    return _insert_event(etapa_id, "fim", observacoes)


def get_etapas_por_encomenda(encomenda_id: int) -> pd.DataFrame:
    db = get_database()
    q = """
    SELECT
        id AS etapa_id,
        tipo_etapa,
        tempo_estimado,
        tempo_real,
        responsavel,
        status,
        data_inicio,
        data_fim,
        ROUND((tempo_real / NULLIF(tempo_estimado, 0)) * 100, 1) AS eficiencia_pct
    FROM etapas_producao
    WHERE encomenda_id = %s
    ORDER BY id
    """
    return db.execute_query(q, (encomenda_id,))


def get_registo_tempo(etapa_id: int) -> pd.DataFrame:
    db = get_database()
    q = """
    SELECT evento, timestamp_evento, observacoes
    FROM registro_tempo
    WHERE etapa_id = %s
    ORDER BY timestamp_evento
    """
    return db.execute_query(q, (etapa_id,))
