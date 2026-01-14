# Setup Guide (Windows)

Este guia cobre a instalação da BD PostgreSQL, carga do schema (inclui Produção, Consumos e Faturação) e execução do dashboard Streamlit.

## 1) Pré-requisitos

- Python (mínimo 3.9; recomendado 3.11+)
- PostgreSQL

## 2) Criar BD e carregar schema

No PowerShell, na raiz do projeto:

- Criar BD:

`psql -U postgres -c "CREATE DATABASE firma;"`

- Carregar schema:

`psql -U postgres -d firma -f sql\schema.sql`

- Carregar dados de exemplo:

`psql -U postgres -d firma -f sql\inserts.sql`

### Alternativa (sem `psql` no PATH)

Se não tiveres o `psql` disponível no terminal, podes aplicar `schema.sql` e (opcionalmente) `inserts.sql` via Python.

1) Cria a base de dados (uma vez) no pgAdmin ou com `psql` noutro terminal/máquina.

2) Depois, na raiz do projeto:

`python scripts\apply_schema.py`

## 3) Ambiente Python

- Instalar dependências:

`python -m pip install -r requirements.txt`

## 4) Variáveis de ambiente

- Copiar o exemplo:

`copy .env.example .env`

- Editar `.env` e preencher:
  - `DB_PASSWORD`
  - (opcional) dados da empresa (`COMPANY_*`) para PDFs
  - (opcional) SMTP para envio de email

## 5) Executar

`streamlit run dashboard\app.py`

## 6) Páginas novas

- ⏱️ Controlo Produção: controlo de etapas (start/pausa/retoma/fim) + Gantt + gargalos
- 💶 Faturação: gerar faturas, PDF, pagamentos, contas a receber
- ➕ Nova Encomenda: wizard multi-step com cálculo + criação de orçamento/encomenda
- 📋 Encomendas: lista + calendário + kanban + detalhe (materiais, etapas, faturação, documentos, histórico)
