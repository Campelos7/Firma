# 🔧 Sistema de Gestão — Ferragens e Serralharia

Aplicação em **Python + Streamlit** com **PostgreSQL** para apoiar a gestão operacional e analítica de uma empresa de ferragens/serralharia: **stock**, **produção**, **encomendas**, **entregas**, **preços/rentabilidade** e **faturação** (inclui **PDF + QR**).

Documentação rápida:
- [INICIO_RAPIDO.md](INICIO_RAPIDO.md) (setup rápido)
- [SETUP_GUIDE.md](SETUP_GUIDE.md) (setup detalhado)

## 📋 Funcionalidades

- 📊 **Dashboard Geral** - Visão geral do negócio com métricas principais
- 💰 **Análise de Preços** - Rentabilidade, comparação com mercado, top clientes
- 📦 **Gestão de Stock** - Stock crítico, valor de inventário, previsão de necessidades
- 🚚 **Entregas** - Entregas pendentes, performance, custos de logística

### Novidades (2026)

- ⏱️ **Controlo Produção** - Etapas, cronómetro start/pausa/retoma/fim, gargalos, Gantt e eficiência
- 📉 **Consumo de Materiais** - Consumo planeado vs real, desperdício e impacto monetário (integrado em Encomendas)
- 💶 **Faturação** - Numeração sequencial AAAA/0001, itens, pagamentos, PDF + QR, aging report e cash flow
- ➕ **Nova Encomenda (Wizard)** - Multi-step com criação de cliente/produto, cálculo de custos, criação de orçamento/encomenda
- 📋 **Encomendas (Detalhe)** - Lista/Calendário/Kanban + detalhe (materiais, produção, faturação, documentos, histórico)

## 🛠️ Tecnologias

**App & UI**
- Python (3.9+; recomendado 3.11+)
- Streamlit

**Base de Dados**
- PostgreSQL
- psycopg2 (driver)

**Dados & Visualização**
- pandas
- Plotly

**Documentos**
- fpdf2 (PDF)
- qrcode + Pillow (QR/imagens)

**Config**
- python-dotenv (.env)

## 📦 Estrutura do Projeto

```
Firma/
├── dashboard/
│   └── app.py              # Dashboard Streamlit principal
├── src/
│   ├── database.py         # Gestão de conexões à BD
│   ├── pricing.py          # Análises de preços e rentabilidade
│   ├── inventory.py        # Gestão de stock e inventário
│   ├── delivery.py         # Análise de entregas
│   └── visualizations.py   # Funções para gráficos
│   ├── production.py        # Produção (etapas + tempos)
│   ├── material_tracking.py # Consumos e desperdício
│   ├── invoicing.py         # Faturação (faturas/itens/pagamentos)
│   └── pdf_generator.py     # PDFs (fatura/orçamento) + QR
├── sql/
│   ├── schema.sql          # Schema da base de dados
│   ├── inserts.sql         # Dados de exemplo
│   └── queries.sql         # Queries analíticas
├── scripts/
│   └── apply_schema.py      # Aplica schema.sql (+ inserts opcional)
├── config.py               # Configurações
├── requirements.txt        # Dependências Python
├── .env                    # Configurações locais (criar manualmente)
└── README.md              # Este ficheiro
```

## 🚀 Getting Started (Windows / PowerShell)

### 1) Pré-requisitos

#### Instalar PostgreSQL
1. Descarregar e instalar PostgreSQL: https://www.postgresql.org/download/windows/
2. Durante a instalação, definir password para o utilizador `postgres`
3. Verificar instalação:
```powershell
psql --version
```

#### Instalar Python
1. Verificar se tens Python instalado:
```powershell
python --version
```
2. Se não tiveres, descarregar de: https://www.python.org/downloads/

> Nota: devido às dependências (ex.: `pandas`), recomenda-se **Python 3.11+**.

### 2) Configurar Base de Dados

#### Criar base de dados e carregar schema/dados

```powershell
# Navegar para a pasta do projeto
cd <CAMINHO_PARA_O_PROJETO>\Firma

# Criar base de dados
psql -U postgres -c "CREATE DATABASE firma;"

# Carregar schema (estrutura das tabelas)
psql -U postgres -d firma -f sql\schema.sql

# Carregar dados de exemplo
psql -U postgres -d firma -f sql\inserts.sql
```

**NOTA**: Quando executares os comandos `psql`, vai pedir a password do PostgreSQL que definiste na instalação.

### 3) Configurar Ambiente Python

#### Instalar dependências:

Opcional (recomendado): criar ambiente virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```powershell
# Navegar para a pasta do projeto (se ainda não estiveres)
cd <CAMINHO_PARA_O_PROJETO>\Firma

# Instalar pacotes Python necessários
python -m pip install -r requirements.txt
```

### 4) Configurar Credenciais (.env)

Criar ficheiro `.env` na raiz do projeto com as tuas credenciais:

```powershell
# Copiar exemplo
copy .env.example .env

# Editar .env com as tuas credenciais
notepad .env
```

Conteúdo do `.env`:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=firma
DB_USER=postgres
DB_PASSWORD=<A_TUA_PASSWORD_POSTGRESQL>
```

> Dica: o repositório inclui `.env.example` com opções extra (dados da empresa para PDFs e SMTP). O `.env` está no `.gitignore`.

### 5) Executar Dashboard

```powershell
# A partir da pasta do projeto
streamlit run dashboard\app.py
```

O dashboard vai abrir automaticamente no teu browser em: **http://localhost:8501**

## 📱 Como usar o Dashboard

1. **🏠 Dashboard** - Página inicial com visão geral
2. **💰 Análise de Preços** - Clica na sidebar para ver análises de rentabilidade
3. **📦 Gestão de Stock** - Ver materiais críticos e valor de inventário
4. **🚚 Entregas** - Gerir entregas pendentes e analisar performance

## 🧰 Scripts úteis

- Aplicar `schema.sql` e (opcionalmente) `inserts.sql` via Python: 
	- `python scripts\apply_schema.py`

## 🔧 Resolução de Problemas

### Erro: "connection refused" ou "database does not exist"
- Verificar se PostgreSQL está a correr
- Confirmar que a base de dados `firma` foi criada
- Verificar credenciais no ficheiro `.env`

### Erro: "No module named 'psycopg2'"
```powershell
python -m pip install psycopg2-binary
```

### Erro: "No module named 'streamlit'"
```powershell
python -m pip install streamlit
```

### Para reiniciar a base de dados (apagar tudo e começar de novo):
```powershell
psql -U postgres -c "DROP DATABASE firma;"
psql -U postgres -c "CREATE DATABASE firma;"
psql -U postgres -d firma -f sql\schema.sql
psql -U postgres -d firma -f sql\inserts.sql
```

### Alternativa (sem `psql` no PATH)

Se não tiveres o `psql` disponível no terminal, podes aplicar o schema via Python (a BD precisa de existir):

```powershell
python scripts\apply_schema.py
```

## 📊 Dados de Exemplo

O projeto inclui dados de exemplo em `sql/inserts.sql` com:
- Fornecedores de vários países
- Materiais (inox, ferro, alumínio, etc.)
- Tipos de produtos (portões, estruturas, etc.)
- Orçamentos e vendas
- Entregas e movimentos de stock

## 🎯 Roadmap

- [ ] Adicionar autenticação de utilizadores
- [ ] Exportar relatórios em PDF
- [ ] Notificações automáticas de stock crítico
- [ ] Dashboard mobile-friendly
- [ ] Integração com APIs de fornecedores

## 📘 Documentação

- Setup rápido: [INICIO_RAPIDO.md](INICIO_RAPIDO.md)
- Setup detalhado: [SETUP_GUIDE.md](SETUP_GUIDE.md)

## 📝 Notas

- A aplicação usa dados de exemplo. Podes modificar `sql/inserts.sql` com os teus dados reais.
- Para fazer backup da base de dados: `pg_dump -U postgres firma > backup.sql`
- Para ambiente de produção, alterar credenciais e usar variáveis de ambiente seguras.

## 👤 Autor

Data Analyst Portfolio Project - 2026

---

**🚀 Boa sorte com a tua aplicação!**
