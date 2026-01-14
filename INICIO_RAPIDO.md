# 🚀 INÍCIO RÁPIDO - Como dar RUN

## Passo a Passo Simples

> Pré-requisito: **Python 3.9+** (recomendado 3.11+) e PostgreSQL.

### 1. Instalar PostgreSQL (se ainda não tiveres)
- Download: https://www.postgresql.org/download/windows/
- Ao instalar, define uma password (ex: "postgres")

### 2. Criar a Base de Dados
Abre PowerShell e executa:

```powershell
cd C:\Users\tomas\source\repos\Firma

# Criar BD
psql -U postgres -c "CREATE DATABASE firma;"

# Carregar estrutura
psql -U postgres -d firma -f sql\schema.sql

# Carregar dados
psql -U postgres -d firma -f sql\inserts.sql
```

### 3. Instalar Bibliotecas Python

```powershell
python -m pip install -r requirements.txt
```

### 4. Configurar Password

Cria ficheiro `.env` na pasta do projeto:

```powershell
copy .env.example .env
notepad .env
```

Muda a linha com a password:
```
DB_PASSWORD=<coloca_aqui_a_tua_password_do_postgres>
```

### 5. RUN! 🎉

```powershell
streamlit run dashboard\app.py
```

Abre automaticamente no browser: http://localhost:8501

---

## Alternativa (sem `psql` no PATH)

Se não tiveres `psql` disponível no terminal, podes aplicar o schema via Python (a BD `firma` tem de existir):

```powershell
python scripts\apply_schema.py
```

---

## ⚡ Comandos Rápidos (copiar e colar)

Se já tens PostgreSQL instalado:

```powershell
# 1. Navegar para a pasta
cd C:\Users\tomas\source\repos\Firma

# 2. Setup BD (vai pedir password)
psql -U postgres -c "CREATE DATABASE firma;"
psql -U postgres -d firma -f sql\schema.sql
psql -U postgres -d firma -f sql\inserts.sql

# 3. Instalar Python packages
pip install -r requirements.txt

# 4. Criar .env
copy .env.example .env

# 5. Editar .env com tua password
notepad .env

# 6. RUN!
streamlit run dashboard\app.py
```

---

## ❌ Problemas?

**PostgreSQL não está instalado?**
```powershell
psql --version
```
Se der erro, instala: https://www.postgresql.org/download/windows/

**Python não está instalado?**
```powershell
python --version
```
Se der erro, instala: https://www.python.org/downloads/

**Erro "database already exists"?**
Tudo bem! Continua para os próximos passos.

**Erro ao conectar à BD?**
- Verifica se a password no `.env` está correta
- Verifica se PostgreSQL está a correr

---

## 📊 O que vais ver

Dashboard com 4 páginas:
- 🏠 **Dashboard** - Visão geral
- 💰 **Preços** - Análise de rentabilidade
- 📦 **Stock** - Gestão de inventário
- 🚚 **Entregas** - Logística

Diverte-te! 🎉
