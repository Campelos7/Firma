import streamlit as st
import sys
import os

# Adicionar diretórios ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from database import get_database

from config import APP_TITLE, APP_ICON
from src import pricing, inventory, delivery, visualizations, forms
from src import production, material_tracking, invoicing
from datetime import date, timedelta

# Configuração da página
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title(f"{APP_ICON} {APP_TITLE}")

# Sidebar com navegação
st.sidebar.title("📈 Navegação")

st.sidebar.markdown("### 📄 Relatórios")
page = st.sidebar.radio(
    "Visualização:",
    [
        "🏠 Dashboard",
        "💰 Análise de Preços",
        "📦 Gestão de Stock",
        "🚚 Entregas",
        "⏱️ Controlo Produção",
        "💶 Faturação",
        "📋 Encomendas",
    ],
    key="reports"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ➕ Inserir Dados")
insert_page = st.sidebar.radio(
    "Gestão:",
    [
        "Nenhuma",
        "👥 Novo Cliente",
        "📝 Novo Orçamento",
        "➕ Nova Encomenda",
        "📦 Movimento Stock",
        "📧 Novo Material",
    ],
    key="insert"
)

# ====================
# PÁGINA: DASHBOARD
# ====================
if page == "🏠 Dashboard":
    st.header("🏠 Dashboard Geral")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        # Rentabilidade
        df_rent = pricing.get_rentabilidade_produtos()
        if not df_rent.empty:
            total_receita = df_rent['receita_total'].sum()
            col1.metric("Receita Total", f"€{total_receita:,.2f}")
        
        # Stock crítico
        df_stock = inventory.get_stock_critico()
        if not df_stock.empty:
            num_criticos = len(df_stock)
            col2.metric("Materiais Críticos", num_criticos)
        
        # Entregas pendentes
        df_entregas = delivery.get_entregas_pendentes()
        if not df_entregas.empty:
            num_pendentes = len(df_entregas)
            col3.metric("Entregas Pendentes", num_pendentes)
        
        # Margem média
        if not df_rent.empty:
            margem_media = df_rent['margem_media_pct'].mean()
            col4.metric("Margem Média", f"{margem_media:.1f}%")
        
        st.markdown("---")
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Receita por Produto")
            if not df_rent.empty:
                fig = visualizations.create_bar_chart(
                    df_rent.head(10), 
                    'produto', 
                    'receita_total',
                    'Top 10 Produtos por Receita'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🔴 Stock Crítico")
            if not df_stock.empty:
                fig = visualizations.create_bar_chart(
                    df_stock.head(10),
                    'nome',
                    'custo_reposicao',
                    'Top 10 Materiais a Repor'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Entregas próximas
        st.subheader("📅 Entregas Próximas (30 dias)")
        df_timeline = delivery.get_timeline_entregas(30)
        if not df_timeline.empty:
            st.dataframe(df_timeline, use_container_width=True)
        else:
            st.info("Sem entregas nos próximos 30 dias")
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        st.info("🔌 Verifique se a base de dados está configurada e acessível.")

# ====================
# PÁGINA: ANÁLISE DE PREÇOS
# ====================
elif page == "💰 Análise de Preços":
    st.header("💰 Análise de Preços e Rentabilidade")
    
    try:
        # Rentabilidade por produto
        st.subheader("📈 Rentabilidade por Produto")
        df_rent = pricing.get_rentabilidade_produtos()
        if not df_rent.empty:
            st.dataframe(df_rent, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = visualizations.create_bar_chart(
                    df_rent,
                    'produto',
                    'margem_media_pct',
                    'Margem % por Produto',
                    color='margem_media_pct'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = visualizations.create_scatter_chart(
                    df_rent,
                    'preco_medio',
                    'margem_media_eur',
                    'Preço vs Margem',
                    size='receita_total'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Preços vs Mercado
        st.subheader("🔄 Comparação com Mercado")
        df_mercado = pricing.get_precos_vs_mercado()
        if not df_mercado.empty:
            st.dataframe(df_mercado, use_container_width=True)
            
            fig = visualizations.create_bar_chart(
                df_mercado,
                'tipo_produto',
                'diferenca_percentual',
                'Diferença % vs Mercado'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Top Clientes
        st.subheader("👥 Top Clientes")
        df_clientes = pricing.get_top_clientes(10)
        if not df_clientes.empty:
            st.dataframe(df_clientes, use_container_width=True)
            
            fig = visualizations.create_bar_chart(
                df_clientes,
                'cliente',
                'valor_total',
                'Top 10 Clientes por Valor'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Margem por Categoria
        st.subheader("🏷️ Margem por Categoria")
        df_cat = pricing.get_margem_por_categoria()
        if not df_cat.empty:
            st.dataframe(df_cat, use_container_width=True)
            
            fig = visualizations.create_pie_chart(
                df_cat,
                'categoria',
                'receita_total',
                'Distribuição de Receita por Categoria'
            )
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")

# ====================
# PÁGINA: GESTÃO DE STOCK
# ====================
elif page == "📦 Gestão de Stock":
    st.header("📦 Gestão de Stock e Inventário")
    
    try:
        # Stock Crítico
        st.subheader("⚠️ Stock Crítico - Ação Necessária")
        df_critico = inventory.get_stock_critico()
        if not df_critico.empty:
            st.error(f"🔴 {len(df_critico)} materiais precisam de reposição!")
            st.dataframe(df_critico, use_container_width=True)
            
            fig = visualizations.create_bar_chart(
                df_critico.head(10),
                'nome',
                'quantidade_repor',
                'Top 10 Materiais a Repor (Quantidade)'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ Todos os materiais com stock adequado!")
        
        st.markdown("---")
        
        # Valor do Stock
        st.subheader("💵 Valor do Stock")
        df_valor = inventory.get_valor_stock()
        if not df_valor.empty:
            st.dataframe(df_valor, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = visualizations.create_pie_chart(
                    df_valor,
                    'tipo',
                    'valor_stock',
                    'Distribuição do Valor de Stock'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = visualizations.create_bar_chart(
                    df_valor,
                    'tipo',
                    'taxa_ocupacao_pct',
                    'Taxa de Ocupação do Stock (%)'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Rotatividade
        st.subheader("🔄 Rotatividade de Materiais (3 meses)")
        df_rot = inventory.get_rotatividade_materiais()
        if not df_rot.empty:
            st.dataframe(df_rot, use_container_width=True)
        
        st.markdown("---")
        
        # Previsão de Necessidades
        st.subheader("🔮 Previsão de Necessidades (30 dias)")
        df_prev = inventory.get_previsao_necessidades(30)
        if not df_prev.empty:
            st.dataframe(df_prev, use_container_width=True)
            
            # Materiais que precisam reposição
            df_repor = df_prev[df_prev['status'] == 'REPOR']
            if not df_repor.empty:
                st.warning(f"⚠️ {len(df_repor)} materiais precisarão de reposição nos próximos 30 dias!")
        
        st.markdown("---")
        
        # Performance Fornecedores
        st.subheader("🚢 Performance dos Fornecedores")
        df_forn = inventory.get_fornecedores_performance()
        if not df_forn.empty:
            st.dataframe(df_forn, use_container_width=True)
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")

# ====================
# PÁGINA: ENTREGAS
# ====================
elif page == "🚚 Entregas":
    st.header("🚚 Gestão de Entregas")
    
    try:
        # Entregas Pendentes
        st.subheader("📦 Entregas Pendentes")
        df_pend = delivery.get_entregas_pendentes()
        if not df_pend.empty:
            # Contar por prioridade
            atrasadas = len(df_pend[df_pend['prioridade'] == 'ATRASADO'])
            urgentes = len(df_pend[df_pend['prioridade'] == 'URGENTE'])
            hoje = len(df_pend[df_pend['prioridade'] == 'HOJE'])
            
            col1, col2, col3 = st.columns(3)
            col1.metric("🔴 Atrasadas", atrasadas)
            col2.metric("🟡 Urgentes (3 dias)", urgentes)
            col3.metric("🟢 Hoje", hoje)
            
            st.dataframe(df_pend, use_container_width=True)
        else:
            st.success("✅ Sem entregas pendentes!")
        
        st.markdown("---")
        
        # Performance de Entregas
        st.subheader("📊 Performance de Entregas")
        df_perf = delivery.get_performance_entregas()
        if not df_perf.empty:
            st.dataframe(df_perf, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = visualizations.create_bar_chart(
                    df_perf,
                    'produto',
                    'taxa_pontualidade',
                    'Taxa de Pontualidade por Produto (%)'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = visualizations.create_bar_chart(
                    df_perf,
                    'produto',
                    'atraso_medio_dias',
                    'Atraso Médio (dias)'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Entregas por Cidade
        st.subheader("🏙️ Entregas por Cidade")

        if hasattr(delivery, "get_entregas_por_cidade"):
            df_cid = delivery.get_entregas_por_cidade()
        else:
            # Fallback para quando o Streamlit ainda está com um módulo antigo em cache.
            df_reg = delivery.get_entregas_por_regiao()
            if not df_reg.empty and "regiao" in df_reg.columns:
                s = df_reg["regiao"].fillna("").astype(str)
                s = s.str.replace("\n", ",", regex=False)
                cidade = s.str.split(",").str[-1].str.strip()
                cidade = cidade.str.replace(r"^\s*\d{4}-\d{3}\s*", "", regex=True).str.strip()
                cidade = cidade.where(cidade.ne(""), "Sem cidade")

                df_cid = df_reg.copy()
                df_cid["cidade"] = cidade
                df_cid = (
                    df_cid.groupby("cidade", as_index=False)
                    .agg(
                        num_entregas=("num_entregas", "sum"),
                        concluidas=("concluidas", "sum"),
                        atraso_medio_dias=("atraso_medio_dias", "mean"),
                        custo_medio_entrega=("custo_medio_entrega", "mean"),
                    )
                    .sort_values("num_entregas", ascending=False)
                )
            else:
                df_cid = df_reg

        if not df_cid.empty:
            st.dataframe(df_cid, use_container_width=True)

            fig = visualizations.create_pie_chart(
                df_cid,
                'cidade',
                'num_entregas',
                'Distribuição de Entregas por Cidade'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Custos de Logística
        st.subheader("💰 Custos de Logística")
        df_custos = delivery.get_custos_logistica()
        if not df_custos.empty:
            st.dataframe(df_custos, use_container_width=True)
            
            fig = visualizations.create_bar_chart(
                df_custos,
                'categoria',
                'custo_total',
                'Custo Total de Entregas por Categoria'
            )
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")

# ====================
# PÁGINA: CONTROLO PRODUÇÃO
# ====================
elif page == "⏱️ Controlo Produção":
    st.header("⏱️ Controlo Produção")

    try:
        df_ativas = production.get_etapas_ativas()

        col1, col2, col3 = st.columns(3)
        col1.metric("Etapas ativas", int(len(df_ativas)))
        col2.metric("Em atraso", int((df_ativas["em_atraso"] == True).sum()) if not df_ativas.empty else 0)
        col3.metric("Operários ativos", int(df_ativas["responsavel"].nunique()) if not df_ativas.empty else 0)

        st.markdown("---")
        st.subheader("🟢 Etapas ativas")
        if not df_ativas.empty:
            st.dataframe(df_ativas, use_container_width=True)
        else:
            st.info("Sem etapas ativas neste momento")

        st.markdown("---")
        st.subheader("🕒 Acompanhar hora início/fim (sem cronómetro)")
        etapa_id = st.number_input("Etapa ID", min_value=0, step=1, value=0)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🟢 Marcar início", use_container_width=True, disabled=(etapa_id <= 0)):
                ok = production.iniciar_etapa(int(etapa_id))
                st.success("Início marcado" if ok else "Falha")
        with c2:
            if st.button("✅ Marcar fim", use_container_width=True, disabled=(etapa_id <= 0)):
                ok = production.concluir_etapa(int(etapa_id))
                st.success("Fim marcado" if ok else "Falha")

        st.markdown("---")
        st.subheader("🚨 Alertas de atraso")
        df_gargalos = production.get_gargalos()
        if not df_gargalos.empty:
            st.warning(f"{len(df_gargalos)} etapas em atraso")
            st.dataframe(df_gargalos, use_container_width=True)
        else:
            st.success("Sem gargalos detectados")

        st.markdown("---")
        st.subheader("🗓️ Gantt por encomenda")
        encomenda_id = st.number_input("Encomenda ID", min_value=0, step=1, value=0, key="prod_gantt_encomenda")
        if encomenda_id > 0:
            df_gantt = production.get_gantt_encomenda(int(encomenda_id))
            if not df_gantt.empty:
                fig = visualizations.create_timeline(
                    df_gantt,
                    x_start="start",
                    x_end="finish",
                    y="tipo_etapa",
                    title=f"Gantt - Encomenda #{int(encomenda_id)}",
                    color="status",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem etapas registadas para esta encomenda")

        st.markdown("---")
        st.subheader("📈 Relatório eficiência")
        col1, col2 = st.columns(2)
        with col1:
            df_eff_etapas = production.get_tempo_medio_real_vs_estimado()
            if not df_eff_etapas.empty:
                st.dataframe(df_eff_etapas, use_container_width=True)
        with col2:
            df_eff_op = production.get_produtividade_operario()
            if not df_eff_op.empty:
                st.dataframe(df_eff_op, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Erro na produção: {e}")

# ====================
# PÁGINA: FATURAÇÃO
# ====================
elif page == "💶 Faturação":
    st.header("💶 Faturação")

    try:
        invoicing.refresh_vencidas()
        tab1, tab2, tab3 = st.tabs(["➕ Criar/Emitir", "📄 Lista", "📊 Contas a receber"])

        with tab1:
            st.subheader("Gerar fatura a partir de encomenda")
            encomenda_id = st.number_input("ID Encomenda", min_value=0, step=1, value=0, key="fat_encomenda")
            venc = st.date_input("Vencimento", value=date.today() + timedelta(days=30))
            metodo = st.selectbox("Método pagamento", ["transferencia", "mb", "dinheiro", "outro"], index=0)
            if st.button("Gerar fatura", disabled=(encomenda_id <= 0)):
                fatura_id = invoicing.gerar_fatura_de_encomenda(int(encomenda_id), vencimento=venc, metodo_pagamento=metodo)
                st.success(f"Fatura criada (ID={fatura_id})")

                try:
                    from src import pdf_generator  # lazy import

                    pdf_path = pdf_generator.generate_invoice_pdf(fatura_id)
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            "⬇️ Download PDF",
                            data=f.read(),
                            file_name=os.path.basename(pdf_path),
                            mime="application/pdf",
                        )
                except ModuleNotFoundError as e:
                    st.error(
                        f"Dependências de PDF em falta ({e}). Instala com: pip install -r requirements.txt"
                    )
                except Exception as e:
                    st.error(f"Falha ao gerar PDF: {e}")

        with tab2:
            df = invoicing.list_faturas()
            if df.empty:
                st.info("Sem faturas")
            else:
                st.dataframe(df, use_container_width=True)
                st.markdown("---")
                st.subheader("Registar pagamento")
                fatura_id = st.number_input("Fatura ID", min_value=0, step=1, value=0, key="fat_pag_fatura")
                valor_pago = st.number_input("Valor pago", min_value=0.0, step=10.0, value=0.0)
                metodo_p = st.text_input("Método", "transferencia")
                referencia = st.text_input("Referência", "")
                if st.button("Registar pagamento", disabled=(fatura_id <= 0 or valor_pago <= 0)):
                    try:
                        ok = invoicing.registar_pagamento(
                            int(fatura_id),
                            float(valor_pago),
                            metodo=metodo_p,
                            referencia=referencia or None,
                        )
                        st.success("Pagamento registado" if ok else "Falha ao registar")
                    except ValueError as e:
                        st.error(str(e))

                st.markdown("---")
                st.subheader("Gerar PDF")
                fatura_pdf_id = st.number_input("Fatura ID (PDF)", min_value=0, step=1, value=0, key="fat_pdf_id")
                if st.button("Gerar PDF", disabled=(fatura_pdf_id <= 0)):
                    try:
                        from src import pdf_generator  # lazy import

                        pdf_path = pdf_generator.generate_invoice_pdf(int(fatura_pdf_id))
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                "⬇️ Download PDF",
                                data=f.read(),
                                file_name=os.path.basename(pdf_path),
                                mime="application/pdf",
                            )
                    except ModuleNotFoundError as e:
                        st.error(
                            f"Dependências de PDF em falta ({e}). Instala com: pip install -r requirements.txt"
                        )
                    except Exception as e:
                        st.error(f"Falha ao gerar PDF: {e}")

        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Aging report")
                df_aging = invoicing.get_aging_report()
                if not df_aging.empty:
                    st.dataframe(df_aging, use_container_width=True)
                else:
                    st.success("Sem faturas em aberto")
            with col2:
                st.subheader("Receita faturada vs recebida")
                df_rev = invoicing.get_receita_faturada_vs_recebida()
                if not df_rev.empty:
                    st.dataframe(df_rev, use_container_width=True)

            st.markdown("---")
            st.subheader("Cash flow (recebimentos)")
            df_cf = invoicing.get_cash_flow()
            if not df_cf.empty:
                st.dataframe(df_cf, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Erro na faturação: {e}")
        st.info(
            "Se for a primeira vez, aplica o schema. Em Windows, o `psql` pode não estar no PATH. "
            "Opções: (1) `python scripts\\apply_schema.py` ou (2) `psql -U postgres -d firma -f sql\\schema.sql` (com o PostgreSQL bin no PATH)."
        )

# ====================
# PÁGINA: ENCOMENDAS (LISTA + DETALHE)
# ====================
elif page == "📋 Encomendas":
    st.header("📋 Encomendas")

    try:
        db = get_database()
        tab_lista, tab_cal, tab_kanban = st.tabs(["Lista", "Calendário", "Kanban"])

        base_q = """
        SELECT
            e.id,
            c.nome AS cliente,
            tp.nome AS produto,
            e.data_pedido,
            e.data_entrega_prometida,
            e.status,
            e.prioridade,
            e.valor_total
        FROM encomendas e
        JOIN clientes c ON e.cliente_id = c.id
        JOIN produtos p ON e.produto_id = p.id
        JOIN tipos_produto tp ON p.tipo_produto_id = tp.id
        WHERE 1=1
        """

        with tab_lista:
            st.subheader("Lista")
            col1, col2, col3 = st.columns(3)
            with col1:
                status_f = st.multiselect(
                    "Status",
                    ['pendente', 'em_producao', 'aguarda_material', 'concluido', 'entregue', 'cancelado'],
                    default=['pendente', 'em_producao', 'aguarda_material'],
                )
            with col2:
                periodo = st.date_input("Período (pedido)", value=(date.today() - timedelta(days=180), date.today()))
            with col3:
                busca = st.text_input("Busca (cliente/produto)", "")

            q = base_q
            params = []

            if status_f:
                q += " AND e.status = ANY(%s)"
                params.append(status_f)

            if isinstance(periodo, tuple) and len(periodo) == 2:
                q += " AND e.data_pedido BETWEEN %s AND %s"
                params.extend([periodo[0], periodo[1]])

            if busca:
                q += " AND (c.nome ILIKE %s OR tp.nome ILIKE %s)"
                params.extend([f"%{busca}%", f"%{busca}%"])

            q += " ORDER BY e.data_pedido DESC, e.id DESC"

            df = db.execute_query(q, tuple(params) if params else None)
            if df.empty:
                st.info("Sem encomendas com estes filtros")
            else:
                st.dataframe(df, use_container_width=True)

            st.markdown("---")
            st.subheader("Detalhe")
            encomenda_id = st.number_input("Selecionar Encomenda ID", min_value=0, step=1, value=0)
            if encomenda_id > 0:
                enc = db.execute_query(
                    """
                    SELECT
                        e.*, c.nome AS cliente_nome, c.email AS cliente_email, c.contacto AS cliente_contacto,
                        tp.nome AS produto_tipo, p.codigo AS produto_codigo
                    FROM encomendas e
                    JOIN clientes c ON e.cliente_id = c.id
                    JOIN produtos p ON e.produto_id = p.id
                    JOIN tipos_produto tp ON p.tipo_produto_id = tp.id
                    WHERE e.id = %s
                    """,
                    (int(encomenda_id),),
                )
                if enc.empty:
                    st.error("Encomenda não encontrada")
                else:
                    r = enc.iloc[0]

                    # Sec 1: info geral
                    st.markdown("### Sec 1: Info geral")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Cliente", r["cliente_nome"])
                    col2.metric("Produto", f"{r['produto_tipo']} ({r['produto_codigo']})")
                    col3.metric("Valor", f"€{float(r['valor_total']):,.2f}")
                    col4.metric("Status", r["status"])

                    novo_status = st.selectbox(
                        "Alterar status",
                        ['pendente', 'em_producao', 'aguarda_material', 'concluido', 'entregue', 'cancelado'],
                        index=['pendente', 'em_producao', 'aguarda_material', 'concluido', 'entregue', 'cancelado'].index(r['status']),
                        key="enc_status",
                    )
                    if st.button("Guardar status"):
                        ok = db.execute_update("UPDATE encomendas SET status=%s WHERE id=%s", (novo_status, int(encomenda_id)))
                        st.success("Atualizado" if ok else "Falha")

                    st.markdown("---")

                    # Sec 2: materiais
                    st.markdown("### Sec 2: Materiais usados")
                    df_mat = material_tracking.get_desperdicio_por_encomenda(int(encomenda_id))
                    if not df_mat.empty:
                        st.dataframe(df_mat, use_container_width=True)
                        fig = visualizations.create_bar_chart(df_mat, "material", "custo_real", "Custo real por material")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Sem consumos registados ainda")

                    st.markdown("#### Registar consumo real")
                    df_materiais = forms.get_lista_materiais()
                    mat_opts = {f"{row['id']} - {row['nome']} ({row['unidade']})": int(row["id"]) for _, row in df_materiais.iterrows()} if not df_materiais.empty else {}
                    if mat_opts:
                        mat_label = st.selectbox("Material", list(mat_opts.keys()))
                        qtd_real = st.number_input("Qtd real", min_value=0.0, step=0.1, value=0.0)
                        motivo = st.text_input("Motivo variação (opcional)", "")
                        if st.button("Guardar consumo", disabled=(qtd_real <= 0)):
                            ok = material_tracking.registar_consumo_real(int(encomenda_id), mat_opts[mat_label], float(qtd_real), motivo or None)
                            st.success("Consumo registado" if ok else "Falha")

                    st.markdown("---")

                    # Sec 3: produção
                    st.markdown("### Sec 3: Etapas produção")
                    df_etapas = production.get_etapas_por_encomenda(int(encomenda_id))
                    if not df_etapas.empty:
                        st.dataframe(df_etapas, use_container_width=True)
                        df_gantt = production.get_gantt_encomenda(int(encomenda_id))
                        if not df_gantt.empty:
                            fig = visualizations.create_timeline(
                                df_gantt,
                                x_start="start",
                                x_end="finish",
                                y="tipo_etapa",
                                title="Gantt - Etapas",
                                color="status",
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Sem etapas registadas")

                    st.markdown("#### Controlo rápido")
                    etapa_id = st.number_input("Etapa ID (controlar)", min_value=0, step=1, value=0, key="enc_etapa_ctrl")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("🟢 Marcar início", disabled=(etapa_id <= 0), key="enc_etapa_start"):
                            st.success("OK" if production.iniciar_etapa(int(etapa_id)) else "Falha")
                    with c2:
                        if st.button("✅ Marcar fim", disabled=(etapa_id <= 0), key="enc_etapa_finish"):
                            st.success("OK" if production.concluir_etapa(int(etapa_id)) else "Falha")

                    st.markdown("---")

                    # Sec 4: faturação
                    st.markdown("### Sec 4: Faturação")
                    df_fat = db.execute_query("SELECT id, num_fatura, status, valor_total, valor_pago, saldo FROM faturas WHERE encomenda_id=%s ORDER BY id DESC", (int(encomenda_id),))
                    if not df_fat.empty:
                        st.dataframe(df_fat, use_container_width=True)
                    else:
                        st.info("Sem fatura associada")
                        if st.button("Gerar fatura", key="enc_gera_fatura"):
                            fatura_id = invoicing.gerar_fatura_de_encomenda(int(encomenda_id), vencimento=date.today() + timedelta(days=30))
                            st.success(f"Fatura criada (ID={fatura_id})")

                    st.markdown("---")

                    # Sec 5: documentos
                    st.markdown("### Sec 5: Documentos")
                    upload = st.file_uploader("Upload (PDF/imagem)", type=["pdf", "png", "jpg", "jpeg"], key="enc_upload")
                    if upload is not None:
                        base_dir = os.path.join("data", "uploads", f"encomenda_{int(encomenda_id)}")
                        os.makedirs(base_dir, exist_ok=True)
                        out_path = os.path.join(base_dir, upload.name)
                        with open(out_path, "wb") as f:
                            f.write(upload.getbuffer())
                        db.execute_update(
                            """
                            INSERT INTO encomenda_documentos (encomenda_id, tipo, nome_arquivo, caminho_arquivo, mime_type)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (int(encomenda_id), "upload", upload.name, out_path.replace('\\\\', '/'), upload.type),
                        )
                        st.success("Documento guardado")

                    df_docs = db.execute_query(
                        "SELECT id, tipo, nome_arquivo, caminho_arquivo, criado_em FROM encomenda_documentos WHERE encomenda_id=%s ORDER BY criado_em DESC",
                        (int(encomenda_id),),
                    )
                    if not df_docs.empty:
                        st.dataframe(df_docs, use_container_width=True)

                    st.markdown("---")

                    # Sec 6: histórico
                    st.markdown("### Sec 6: Histórico")
                    df_hist = db.execute_query(
                        "SELECT criado_em, tipo_evento, descricao, usuario FROM encomenda_eventos WHERE encomenda_id=%s ORDER BY criado_em DESC",
                        (int(encomenda_id),),
                    )
                    if not df_hist.empty:
                        st.dataframe(df_hist, use_container_width=True)
                    nota = st.text_area("Nota interna", "", key="enc_nota")
                    if st.button("Adicionar nota", disabled=(not nota.strip())):
                        ok = db.execute_update(
                            "INSERT INTO encomenda_eventos (encomenda_id, tipo_evento, descricao, usuario) VALUES (%s, 'nota', %s, %s)",
                            (int(encomenda_id), nota.strip(), "admin"),
                        )
                        st.success("Nota adicionada" if ok else "Falha")

        with tab_cal:
            st.subheader("Calendário (entregas prometidas)")
            df = db.execute_query(
                """
                SELECT
                    e.id,
                    c.nome AS cliente,
                    tp.nome AS produto,
                    e.data_pedido,
                    e.data_entrega_prometida,
                    e.data_entrega_real,
                    e.status,
                    e.prioridade,
                    e.valor_total
                FROM encomendas e
                JOIN clientes c ON e.cliente_id = c.id
                JOIN produtos p ON e.produto_id = p.id
                JOIN tipos_produto tp ON p.tipo_produto_id = tp.id
                WHERE e.status <> 'cancelado'
                ORDER BY e.data_entrega_prometida ASC
                """,
                None,
            )

            if df.empty:
                st.info("Sem encomendas")
            else:
                df_cal = df.copy()
                df_cal["start"] = df_cal["data_pedido"].astype(str)
                df_cal["finish"] = df_cal["data_entrega_real"].fillna(df_cal["data_entrega_prometida"]).astype(str)
                df_cal["item"] = df_cal.apply(
                    lambda r: f"#{int(r['id'])} {r['cliente']} ({r['produto']})",
                    axis=1,
                )

                fig = visualizations.create_timeline(
                    df_cal,
                    x_start="start",
                    x_end="finish",
                    y="item",
                    title="Linha temporal das encomendas (pedido → entrega)",
                    color="status",
                )
                st.plotly_chart(fig, use_container_width=True)

        with tab_kanban:
            st.subheader("Kanban")
            df = db.execute_query(base_q, None)
            if df.empty:
                st.info("Sem encomendas")
            else:
                cols = st.columns(5)
                estados = ["pendente", "aguarda_material", "em_producao", "concluido", "entregue"]
                for i, estado in enumerate(estados):
                    with cols[i]:
                        st.markdown(f"#### {estado}")
                        sub = df[df["status"] == estado]
                        for _, row in sub.head(25).iterrows():
                            st.caption(f"#{int(row['id'])} • {row['cliente']} • €{float(row['valor_total']):,.0f}")

    except Exception as e:
        st.error(f"❌ Erro nas encomendas: {e}")

# ====================
# SECÇÃO: INSERÇÃO DE DADOS
# ====================

if insert_page != "Nenhuma":
    st.markdown("---")
    st.subheader("➕ Inserção de Dados")

    # --------------------
    # Novo Cliente
    # --------------------
    if insert_page == "👥 Novo Cliente":
        st.markdown("#### 👥 Registar Novo Cliente")
        with st.form("form_novo_cliente"):
            nome = st.text_input("Nome do cliente")
            contacto = st.text_input("Contacto")
            email = st.text_input("Email")
            morada = st.text_area("Morada / Localização")
            tipo = st.selectbox("Tipo de cliente", ["particular", "empresa"])
            submitted_cliente = st.form_submit_button("Guardar cliente")

        if submitted_cliente:
            if not nome:
                st.error("O nome do cliente é obrigatório.")
            else:
                ok = forms.inserir_cliente(nome, contacto, email, morada, tipo)
                if ok:
                    st.success("Cliente inserido com sucesso.")
                else:
                    st.error("Erro ao inserir cliente. Verifique a ligação à base de dados.")

    # --------------------
    # Novo Orçamento
    # --------------------
    elif insert_page == "📝 Novo Orçamento":
        st.markdown("#### 📝 Registar Novo Orçamento")

        df_clientes = forms.get_lista_clientes()
        df_produtos = forms.get_lista_produtos()

        if df_clientes.empty or df_produtos.empty:
            st.warning("É necessário ter clientes e produtos registados para criar orçamentos.")
        else:
            clientes_options = {
                f"{row['id']} - {row['nome']}": int(row["id"]) for _, row in df_clientes.iterrows()
            }
            produtos_options = {
                f"{row['id']} - {row['nome']}": int(row["id"]) for _, row in df_produtos.iterrows()
            }

            with st.form("form_novo_orcamento"):
                cliente_label = st.selectbox("Cliente", list(clientes_options.keys()))
                produto_label = st.selectbox("Produto", list(produtos_options.keys()))

                custo_material = st.number_input("Custo de material (€)", min_value=0.0, step=1.0)
                custo_mao_obra = st.number_input("Custo de mão de obra (€)", min_value=0.0, step=1.0)
                outros_custos = st.number_input("Outros custos (€)", min_value=0.0, step=1.0, value=0.0)
                margem_percentual = st.number_input("Margem (%)", min_value=0.0, step=0.5, value=35.0)
                preco_venda = st.number_input("Preço de venda (€)", min_value=0.0, step=1.0)
                validade_dias = st.number_input(
                    "Validade do orçamento (dias)", min_value=1, step=1, value=30
                )
                observacoes = st.text_area("Observações", "")
                submitted_orcamento = st.form_submit_button("Guardar orçamento")

            if submitted_orcamento:
                cliente_id = clientes_options[cliente_label]
                produto_id = produtos_options[produto_label]
                ok = forms.inserir_orcamento(
                    cliente_id,
                    produto_id,
                    custo_material,
                    custo_mao_obra,
                    outros_custos,
                    margem_percentual,
                    preco_venda,
                    int(validade_dias),
                    observacoes or None,
                )
                if ok:
                    st.success("Orçamento inserido com sucesso.")
                else:
                    st.error("Erro ao inserir orçamento. Verifique a ligação à base de dados.")

    # --------------------
    # Movimento de Stock
    # --------------------
    elif insert_page == "📦 Movimento Stock":
        st.markdown("#### 📦 Registar Movimento de Stock")

        df_materiais = forms.get_lista_materiais()
        if df_materiais.empty:
            st.warning("Não existem materiais registados na base de dados.")
        else:
            materiais_options = {
                f"{row['id']} - {row['nome']} ({row['unidade']})": int(row["id"])
                for _, row in df_materiais.iterrows()
            }

            with st.form("form_movimento_stock"):
                material_label = st.selectbox("Material", list(materiais_options.keys()))
                tipo_movimento = st.selectbox("Tipo de movimento", ["entrada", "saida", "ajuste"])
                quantidade = st.number_input("Quantidade", min_value=0.0, step=1.0)
                motivo = st.text_input("Motivo", "")
                encomenda_id_val = st.number_input(
                    "ID da encomenda (opcional)", min_value=0, step=1, value=0
                )
                usuario = st.text_input("Utilizador", "")
                submitted_movimento = st.form_submit_button("Registar movimento")

            if submitted_movimento:
                material_id = materiais_options[material_label]
                encomenda_id = int(encomenda_id_val) if encomenda_id_val > 0 else None
                ok = forms.registar_movimento_stock(
                    material_id,
                    tipo_movimento,
                    quantidade,
                    motivo or None,
                    encomenda_id,
                    usuario or None,
                )
                if ok:
                    st.success("Movimento de stock registado com sucesso.")
                else:
                    st.error("Erro ao registar movimento de stock. Verifique a ligação à base de dados.")

    # --------------------
    # Novo Material
    # --------------------
    elif insert_page == "📧 Novo Material":
        st.markdown("#### 📧 Registar Novo Material")

        df_fornecedores = forms.get_lista_fornecedores()
        if df_fornecedores.empty:
            st.warning("Não existem fornecedores registados na base de dados.")
        else:
            fornecedores_options = {
                f"{row['id']} - {row['nome']}": int(row["id"]) for _, row in df_fornecedores.iterrows()
            }

            with st.form("form_novo_material"):
                nome = st.text_input("Nome do material")
                tipo = st.text_input("Tipo de material (ex: inox, ferro, alumínio)")
                unidade = st.text_input("Unidade (ex: metro, kg, unidade)")
                preco_por_unidade = st.number_input(
                    "Preço por unidade (€)", min_value=0.0, step=0.1
                )
                fornecedor_label = st.selectbox("Fornecedor", list(fornecedores_options.keys()))
                lead_time_dias = st.number_input(
                    "Lead time (dias)", min_value=0, step=1, value=0
                )
                stock_atual = st.number_input(
                    "Stock atual", min_value=0.0, step=1.0, value=0.0
                )
                stock_minimo = st.number_input(
                    "Stock mínimo", min_value=0.0, step=1.0, value=0.0
                )
                stock_maximo = st.number_input(
                    "Stock máximo (opcional)", min_value=0.0, step=1.0, value=0.0
                )
                submitted_material = st.form_submit_button("Guardar material")

            if submitted_material:
                if not nome:
                    st.error("O nome do material é obrigatório.")
                else:
                    fornecedor_id = fornecedores_options[fornecedor_label]
                    stock_maximo_val = stock_maximo if stock_maximo > 0 else None
                    ok = forms.inserir_material(
                        nome,
                        tipo,
                        unidade,
                        preco_por_unidade,
                        fornecedor_id,
                        int(lead_time_dias),
                        stock_atual,
                        stock_minimo,
                        stock_maximo_val,
                    )
                    if ok:
                        st.success("Material inserido com sucesso.")
                    else:
                        st.error("Erro ao inserir material. Verifique a ligação à base de dados.")

    # --------------------
    # Nova Encomenda (Wizard)
    # --------------------
    elif insert_page == "➕ Nova Encomenda":
        st.markdown("#### ➕ Nova Encomenda (Wizard)")

        try:
            if "wizard_step" not in st.session_state:
                st.session_state.wizard_step = 1

            step = int(st.session_state.wizard_step)
            st.progress(step / 5.0)

            # Step 1: Cliente
            if step == 1:
                st.subheader("Step 1: Dados cliente")
                df_clientes = forms.get_lista_clientes()
                clientes_options = {
                    f"{row['id']} - {row['nome']}": int(row["id"]) for _, row in df_clientes.iterrows()
                } if not df_clientes.empty else {}

                modo = st.radio("Cliente", ["Existente", "Novo"], horizontal=True)

                if modo == "Existente":
                    if not clientes_options:
                        st.warning("Sem clientes registados")
                    else:
                        cliente_label = st.selectbox("Selecionar cliente", list(clientes_options.keys()))
                        st.session_state.wizard_cliente_id = clientes_options[cliente_label]
                else:
                    nome = st.text_input("Nome")
                    nif = st.text_input("NIF (opcional)")
                    contacto = st.text_input("Contacto")
                    email = st.text_input("Email")
                    morada = st.text_area("Morada")
                    tipo = st.selectbox("Tipo", ["particular", "empresa"], index=0)
                    if st.button("Criar cliente"):
                        if not nome:
                            st.error("Nome é obrigatório")
                        else:
                            cid = forms.inserir_cliente_returning_id(nome, contacto, email, morada, tipo, nif or None)
                            if cid:
                                st.session_state.wizard_cliente_id = int(cid)
                                st.success(f"Cliente criado (ID={cid})")
                            else:
                                st.error("Falha ao criar cliente")

                if st.button("Próximo ▶️", disabled=("wizard_cliente_id" not in st.session_state)):
                    st.session_state.wizard_step = 2
                    st.experimental_rerun()

            # Step 2: Produto
            elif step == 2:
                st.subheader("Step 2: Especificações produto")
                df_tipos = forms.get_lista_tipos_produto()
                if df_tipos.empty:
                    st.error("Sem tipos de produto registados")
                else:
                    tipos_options = {f"{r['id']} - {r['nome']}": int(r["id"]) for _, r in df_tipos.iterrows()}
                    tipo_label = st.selectbox("Tipo produto", list(tipos_options.keys()))
                    tipo_id = tipos_options[tipo_label]
                    st.session_state.wizard_tipo_produto_id = tipo_id

                    codigo_default = f"WZ-{date.today().strftime('%Y%m%d')}-{st.session_state.wizard_cliente_id}"
                    codigo = st.text_input("Código", value=codigo_default)
                    descricao = st.text_area("Descrição")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        largura = st.number_input("Largura (m)", min_value=0.0, step=0.1, value=3.0)
                    with col2:
                        altura = st.number_input("Altura (m)", min_value=0.0, step=0.1, value=2.0)
                    with col3:
                        horas = st.number_input("Horas mão-de-obra (estimado)", min_value=0.0, step=1.0, value=16.0)
                    complexidade = st.selectbox("Complexidade", ["baixa", "media", "alta"], index=1)

                    foto = st.file_uploader("Upload foto (opcional)", type=["png", "jpg", "jpeg"])
                    st.session_state.wizard_foto = foto

                    if st.button("Próximo ▶️"):
                        pid = forms.inserir_produto(
                            tipo_id,
                            codigo,
                            descricao or None,
                            largura if largura > 0 else None,
                            altura if altura > 0 else None,
                            float(horas),
                            complexidade,
                        )
                        if pid:
                            st.session_state.wizard_produto_id = int(pid)
                            st.session_state.wizard_horas = float(horas)
                            st.session_state.wizard_step = 3
                            st.experimental_rerun()
                        else:
                            st.error("Falha ao criar produto")

                if st.button("◀️ Voltar"):
                    st.session_state.wizard_step = 1
                    st.experimental_rerun()

            # Step 3: Cálculo automático
            elif step == 3:
                st.subheader("Step 3: Cálculo automático")
                db = get_database()
                df_bom = db.execute_query(
                    """
                    SELECT m.id AS material_id, m.nome, m.tipo, m.unidade,
                           pm.quantidade_por_unidade AS qtd_planeada,
                           m.preco_por_unidade,
                           (pm.quantidade_por_unidade * m.preco_por_unidade) AS custo
                    FROM produtos p
                    JOIN produtos_materiais pm ON p.tipo_produto_id = pm.tipo_produto_id
                    JOIN materiais m ON pm.material_id = m.id
                    WHERE p.id = %s
                    ORDER BY custo DESC
                    """,
                    (st.session_state.wizard_produto_id,),
                )

                if df_bom.empty:
                    st.warning("Este tipo de produto não tem BOM (produtos_materiais) configurado")
                    custo_material = 0.0
                else:
                    st.dataframe(df_bom, use_container_width=True)
                    custo_material = float(df_bom["custo"].sum())

                taxa_hora = float(os.getenv("HOURLY_RATE_EUR", "15"))
                custo_mao_obra = float(st.session_state.get("wizard_horas", 0.0)) * taxa_hora
                outros = st.number_input("Outros custos (€)", min_value=0.0, step=10.0, value=0.0)
                margem = st.number_input("Margem (%)", min_value=0.0, step=0.5, value=35.0)

                custo_total = custo_material + custo_mao_obra + float(outros)
                preco_sugerido = custo_total * (1.0 + (float(margem) / 100.0))

                col1, col2, col3 = st.columns(3)
                col1.metric("Custo material", f"€{custo_material:,.2f}")
                col2.metric("Custo mão-de-obra", f"€{custo_mao_obra:,.2f}")
                col3.metric("Preço sugerido", f"€{preco_sugerido:,.2f}")

                st.session_state.wizard_custo_material = custo_material
                st.session_state.wizard_custo_mao_obra = custo_mao_obra
                st.session_state.wizard_outros = float(outros)
                st.session_state.wizard_margem = float(margem)
                st.session_state.wizard_preco = float(preco_sugerido)

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("◀️ Voltar"):
                        st.session_state.wizard_step = 2
                        st.experimental_rerun()
                with c2:
                    if st.button("Próximo ▶️"):
                        st.session_state.wizard_step = 4
                        st.experimental_rerun()

            # Step 4: Prazos
            elif step == 4:
                st.subheader("Step 4: Prazos")
                prazo = st.number_input("Prazo prometido (dias)", min_value=1, step=1, value=21)
                prioridade = st.selectbox("Prioridade", ["baixa", "normal", "alta", "urgente"], index=1)
                metodo_pagamento = st.selectbox("Pagamento", ["transferencia", "mb", "dinheiro", "outro"], index=0)
                obs = st.text_area("Observações", "")

                st.session_state.wizard_prazo = int(prazo)
                st.session_state.wizard_prioridade = prioridade
                st.session_state.wizard_metodo_pagamento = metodo_pagamento
                st.session_state.wizard_obs = obs

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("◀️ Voltar"):
                        st.session_state.wizard_step = 3
                        st.experimental_rerun()
                with c2:
                    if st.button("Próximo ▶️"):
                        st.session_state.wizard_step = 5
                        st.experimental_rerun()

            # Step 5: Confirmação
            elif step == 5:
                st.subheader("Step 5: Confirmação")
                st.write("Cliente ID:", st.session_state.wizard_cliente_id)
                st.write("Produto ID:", st.session_state.wizard_produto_id)
                st.write("Preço:", f"€{st.session_state.wizard_preco:,.2f}")
                st.write("Prazo (dias):", st.session_state.wizard_prazo)

                gerar_pdf = st.checkbox("Gerar PDF orçamento", value=True)

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("◀️ Voltar"):
                        st.session_state.wizard_step = 4
                        st.experimental_rerun()
                with c2:
                    if st.button("✅ Criar encomenda"):
                        orc_id = forms.inserir_orcamento_returning_id(
                            st.session_state.wizard_cliente_id,
                            st.session_state.wizard_produto_id,
                            st.session_state.wizard_custo_material,
                            st.session_state.wizard_custo_mao_obra,
                            st.session_state.wizard_outros,
                            st.session_state.wizard_margem,
                            st.session_state.wizard_preco,
                            observacoes=st.session_state.wizard_obs or None,
                        )
                        if not orc_id:
                            st.error("Falha ao criar orçamento")
                        else:
                            enc_id = forms.inserir_encomenda_returning_id(
                                int(orc_id),
                                st.session_state.wizard_cliente_id,
                                st.session_state.wizard_produto_id,
                                st.session_state.wizard_prazo,
                                st.session_state.wizard_preco,
                                prioridade=st.session_state.wizard_prioridade,
                                status="pendente",
                                metodo_pagamento=st.session_state.wizard_metodo_pagamento,
                                observacoes=st.session_state.wizard_obs or None,
                            )
                            if not enc_id:
                                st.error("Falha ao criar encomenda")
                            else:
                                material_tracking.initialize_planeado_for_encomenda(int(enc_id))

                                total_min = int(round(float(st.session_state.wizard_horas) * 60.0))
                                etapas_default = [
                                    ("Corte & Preparação", int(total_min * 0.25)),
                                    ("Soldadura", int(total_min * 0.35)),
                                    ("Acabamentos", int(total_min * 0.25)),
                                    ("Montagem", max(0, total_min - int(total_min * 0.25) - int(total_min * 0.35) - int(total_min * 0.25))),
                                ]
                                for nome_etapa, mins in etapas_default:
                                    production.create_etapa(int(enc_id), nome_etapa, max(0, int(mins)), None)

                                st.success(f"Encomenda criada (ID={enc_id})")

                                if gerar_pdf:
                                    try:
                                        from src import pdf_generator  # lazy import

                                        pdf_path = pdf_generator.generate_orcamento_pdf(int(orc_id))
                                        with open(pdf_path, "rb") as f:
                                            st.download_button(
                                                "⬇️ Download Orçamento PDF",
                                                data=f.read(),
                                                file_name=os.path.basename(pdf_path),
                                                mime="application/pdf",
                                            )
                                    except ModuleNotFoundError as e:
                                        st.error(
                                            f"Dependências de PDF em falta ({e}). Instala com: pip install -r requirements.txt"
                                        )

                                st.session_state.wizard_step = 1

        except Exception as e:
            st.error(f"❌ Erro no wizard: {e}")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("📊 Dashboard de Business Intelligence\n\nSistema de gestão para ferragens e serralharia")
