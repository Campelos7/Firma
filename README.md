# 🔧 Management System — Hardware & Metalworking

Application built with **Python + Streamlit** and **PostgreSQL** to support the operational and analytical management of a hardware / metalworking company: **stock**, **production**, **orders**, **deliveries**, **pricing & profitability**, and **invoicing** (includes **PDF + QR**).

Quick documentation:
- [INICIO_RAPIDO.md](INICIO_RAPIDO.md) (quick setup)
- [SETUP_GUIDE.md](SETUP_GUIDE.md) (detailed setup)

---

## 📋 Features

- 📊 **General Dashboard** – Business overview with key metrics  
- 💰 **Pricing Analysis** – Profitability, market comparison, top customers  
- 📦 **Stock Management** – Critical stock, inventory value, demand forecasting  
- 🚚 **Deliveries** – Pending deliveries, performance, logistics costs  

### New (2026)

- ⏱️ **Production Control** – Stages, start/pause/resume/finish timer, bottlenecks, Gantt charts and efficiency  
- 📉 **Material Consumption** – Planned vs actual consumption, waste and monetary impact (integrated into Orders)  
- 💶 **Invoicing** – Sequential numbering YYYY/0001, items, payments, PDF + QR, aging report and cash flow  
- ➕ **New Order (Wizard)** – Multi-step flow with client/product creation, cost calculation, quote/order creation  
- 📋 **Orders (Detail)** – List/Calendar/Kanban + detailed view (materials, production, invoicing, documents, history)  

---

## 🛠️ Technologies

### App & UI
- Python (3.9+; recommended 3.11+)
- Streamlit

### Database
- PostgreSQL
- psycopg2 (driver)

### Data & Visualization
- pandas
- Plotly

### Documents
- fpdf2 (PDF)
- qrcode + Pillow (QR/images)

### Configuration
- python-dotenv (.env)

---

## 📦 Project Structure

```
Firma/
├── dashboard/
│   └── app.py
├── src/
│   ├── database.py
│   ├── pricing.py
│   ├── inventory.py
│   ├── delivery.py
│   ├── visualizations.py
│   ├── production.py
│   ├── material_tracking.py
│   ├── invoicing.py
│   └── pdf_generator.py
├── sql/
│   ├── schema.sql
│   ├── inserts.sql
│   └── queries.sql
├── scripts/
│   └── apply_schema.py
├── config.py
├── requirements.txt
├── .env
└── README.md
```

---

## 🚀 Getting Started (Windows / PowerShell)

### 1) Prerequisites

#### Install PostgreSQL
1. Download and install PostgreSQL: https://www.postgresql.org/download/windows/
2. Set a password for the `postgres` user
3. Verify installation:
```powershell
psql --version
```

#### Install Python
```powershell
python --version
```

> Python **3.11+** recommended.

---

### 2) Database Setup

```powershell
psql -U postgres -c "CREATE DATABASE firma;"
psql -U postgres -d firma -f sql\schema.sql
psql -U postgres -d firma -f sql\inserts.sql
```

---

### 3) Python Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

---

### 4) Environment Variables

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=firma
DB_USER=postgres
DB_PASSWORD=your_password
```

---

### 5) Run the App

```powershell
streamlit run dashboard\app.py
```

---

## 📊 Sample Data

Includes suppliers, materials, products, quotes, sales, deliveries and stock movements.

---

## 🎯 Roadmap

- [ ] User authentication
- [ ] PDF report exports
- [ ] Stock alerts
- [ ] Mobile dashboard
- [ ] Supplier API integrations

---

## 👤 Author

Data Analyst Portfolio Project – 2026
