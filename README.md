# FinSight – FinTech Data Engineering & Analytics Portfolio

## Problem Statement & Business Context
Financial institutions need robust data pipelines to ingest transaction streams, ensure data quality, and provide analytical insights for fraud detection, credit‑risk assessment, and customer behavior. This project demonstrates an end‑to‑end data‑engineering workflow built with Python, PostgreSQL, and an interactive Streamlit web dashboard.

## Datasets
| Dataset | Description | Source URL | Used For |
|---|---|---|---|
| **PaySim** | Synthetic mobile‑money transaction data (includes fraud label) | https://raw.githubusercontent.com/ntumg/paysim/master/paysim.csv | Transaction, fraud‑risk analysis |
| **UCI Credit Card Default** | Credit‑card client data with default flag | https://archive.ics.uci.edu/ml/machine-learning-databases/00350/default%20of%20credit%20card%20clients.xls | Credit‑risk analysis |

Both files are automatically downloaded by the ingestion script into `data/raw/`.

## Architecture Overview
```mermaid
graph TD
    A[Download Datasets] --> B[Ingestion (src/ingestion)]
    B --> C[Staging Tables (SQL)]
    C --> D[Validation (src/validation)]
    D --> E[Transformation (src/transformation)]
    E --> F[Warehouse Load (src/warehouse)]
    F --> G[Fact‑Dimension Model (SQL)]
    G --> H[Analytical Marts (SQL Views)]
    H --> I[Streamlit Dashboard]
```

1. **Ingestion** – Reads CSVs, validates schema, writes raw rows to staging tables `stg_paysim_raw` and `stg_credit_raw`.
2. **Validation** – Executes data‑quality rules (missing values, duplicates, invalid amounts, etc.) and stores a log in `validation_log`.
3. **Transformation** – Cleans data, derives date keys, normalises categorical fields, and writes to `transformed_*` tables.
4. **Warehouse** – Dimensions (`dim_customer`, `dim_date`, `dim_transaction_type`) and fact (`fact_transactions`).
5. **Marts** – Views such as `vw_transaction_summary`, `vw_fraud_summary`, `vw_credit_default_summary`, `vw_customer_transactions`.
6. **Streamlit Dashboard** – Interactive web UI connecting directly to PostgreSQL analytical views, with six dashboard pages accessible at `http://localhost:8501`.

## Project Structure
```
FinSight/
│
├── data/
│   ├── raw/                # auto‑downloaded CSVs
│   └── processed/          # optional parquet/CSV after transformation
│
├── src/
│   ├── ingestion/          # loader.py, __main__.py
│   ├── validation/         # rules.py, runner.py
│   ├── transformation/     # clean_paysim.py, clean_credit.py
│   └── warehouse/          # load_fact.py
│
├── sql/
│   ├── staging/            # create_staging_tables.sql
│   ├── warehouse/          # dimensions & fact DDL
│   └── marts/              # analytical view DDLs
│
├── dashboards/
│   └── app.py              # Streamlit dashboard (6 interactive pages)
│
├── tests/                  # pytest suite
├── config/                 # db.yaml, logging.yaml
├── docker-compose.yml
├── app.py                  # Root shortcut – runs the Streamlit dashboard
├── run_pipeline.py         # One‑command end‑to‑end pipeline runner
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Clone the repository
```bash
git clone <repo-url>
cd FinSight
```

### 2. Install dependencies
```bash
python -m venv .venv
.\.venv\Scripts\activate       # Windows
# source .venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
```

### 3. Start PostgreSQL via Docker
```bash
docker-compose up -d
```
The container runs PostgreSQL 15 with default credentials (`postgres/postgres`).

### 4. Run the full ETL pipeline
You can run each step individually or use the one‑command pipeline runner:

**Option A – One command (recommended)**
```bash
python run_pipeline.py
```

**Option B – Step by step**
```bash
python -m src.ingestion         # Download & stage raw data
python -m src.validation.runner # Data quality checks
python -m src.transformation    # Clean & transform data
python -m src.warehouse.load_fact  # Build fact-dimension model & marts
```

### 5. Launch the Interactive Streamlit Dashboard
```bash
streamlit run app.py
```
Opens at **http://localhost:8501** and provides six interactive pages:

| Page | What You'll See |
|---|---|
| 📊 **Executive Overview** | KPIs – Total Volume, Transactions, Customers, Fraud Rate, Default Rate |
| 💳 **Transaction Analytics** | Volume by channel, average ticket size, hourly velocity |
| 🛡️ **Fraud Risk** | Fraud loss exposure, fraud rates by type, high-risk transaction inspector |
| 📉 **Credit Risk** | Default rates by age bracket, education level & marital status |
| 👥 **Customer Insights** | Top spenders and customer spending distribution |
| 📋 **Data Quality Logs** | Live audit trail of `validation_log` and `ingestion_log` |

## Testing
Run the full test suite:
```bash
pytest -q
```
All core validation, transformation, and ingestion utilities are covered.

## Verification Table (Mapping Resume Claims)
| Resume Claim | Implemented In | File / Table / Component |
|---|---|---|
| Built an end‑to‑end ETL pipeline | Ingestion + Validation + Transformation + Warehouse Load | `src/ingestion/loader.py`, `src/validation/runner.py`, `src/transformation/clean_*.py`, `src/warehouse/load_fact.py` |
| Python + SQL | Entire codebase | `.py` files & `.sql` scripts |
| PostgreSQL | Database backend | `docker-compose.yml`, all SQL DDL/DML |
| Data validation | Validation rules | `src/validation/rules.py` |
| Data‑quality checks | Validation runner logs | `validation_log` table |
| Fact‑dimension warehouse | Dimension & fact tables | `sql/warehouse/create_dimensions.sql`, `sql/warehouse/create_fact.sql` |
| Transformation layers | Python cleaning scripts | `src/transformation/*.py` |
| Transaction analysis | Analytical view | `sql/marts/transaction_analysis.sql` |
| Fraud‑risk analysis | Analytical view | `sql/marts/fraud_analysis.sql` |
| Credit‑risk analysis | Analytical view | `sql/marts/credit_risk_analysis.sql` |
| Customer analysis | Analytical view | `sql/marts/customer_analysis.sql` |
| Interactive Dashboard | Streamlit web app | `app.py`, `dashboards/app.py` |

## Limitations & Assumptions
* Datasets are synthetic/public; they do not contain real customer data.
* The pipeline runs in batch mode, not real‑time streaming.
* Fraud‑risk analysis is descriptive only – no predictive modeling is performed.
* Docker is used only for PostgreSQL (and optional pgAdmin).
