# FinSight – FinTech Data Engineering & Analytics Portfolio

## Problem Statement & Business Context
Financial institutions need robust data pipelines to ingest transaction streams, ensure data quality, and provide analytical insights for fraud detection, credit risk assessment, and customer behavior. This project showcases a complete end‑to‑end data‑engineering workflow built with Python, PostgreSQL, and Power BI, exactly as described on the resume.

## Datasets
| Dataset | Description | Source URL | Used For |
|---|---|---|---|
| **PaySim** | Synthetic mobile money transaction data (including fraud label) | https://raw.githubusercontent.com/ntumg/paysim/master/paysim.csv | Transaction, fraud‑risk analysis |
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
    H --> I[Power BI Dashboard]
```
1. **Ingestion** – Reads CSVs, validates schema, writes raw rows to staging tables `stg_paysim_raw` and `stg_credit_raw`.
2. **Validation** – Executes data‑quality rules (missing values, duplicates, invalid amounts, etc.) and stores a log in `validation_log`.
3. **Transformation** – Cleans data, derives date keys, normalises categorical fields, and writes to `transformed_*` tables.
4. **Warehouse** – Dimensions (`dim_customer`, `dim_date`, `dim_transaction_type`) and fact (`fact_transactions`).
5. **Marts** – Views such as `vw_transaction_summary`, `vw_fraud_summary`, `vw_credit_default_summary`, `vw_customer_transactions`.
6. **Power BI** – Connects to the PostgreSQL views; the supplied `FinSight.pbix` contains five pages (Executive Overview, Transaction Analytics, Fraud‑Risk Analytics, Customer Analytics, Credit‑Risk Analytics).

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
├── tests/                  # pytest suite
├── dashboards/             # FinSight.pbix (Power BI dashboard)
├── config/                 # db.yaml, logging.yaml
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Setup Instructions
1. **Clone the repository** (or unzip the project folder).
2. **Install dependencies**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Start PostgreSQL** via Docker
   ```bash
   docker-compose up -d
   ```
   The container runs PostgreSQL 15 with default credentials (`postgres/postgres`).
4. **Run the ingestion pipeline** – it will download the datasets and load them into the staging tables:
   ```bash
   python -m src.ingestion
   ```
5. **Validate data**
   ```bash
   python -m src.validation.runner
   ```
   Validation results are stored in the `validation_log` table.
6. **Transform data**
   ```bash
   python -m src.transformation
   ```
7. **Load the warehouse**
   ```bash
   python -m src.warehouse.load_fact
   ```
8. **Create analytical views** (run once after the fact table is populated):
   ```bash
   psql -U postgres -d finsight -f sql/marts/transaction_analysis.sql
   psql -U postgres -d finsight -f sql/marts/fraud_analysis.sql
   psql -U postgres -d finsight -f sql/marts/credit_risk_analysis.sql
   psql -U postgres -d finsight -f sql/marts/customer_analysis.sql
   ```
9. **Open Power BI** – open `dashboards/FinSight.pbix` and connect to the PostgreSQL database using the same credentials. The report will pull data from the analytical views.

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
| Power BI | Dashboard file | `dashboards/FinSight.pbix` |

## Limitations & Assumptions
* Datasets are synthetic/public; they do not contain real HSBC customer data.
* The pipeline runs in batch mode, not real‑time streaming.
* Fraud‑risk analysis is descriptive only – no predictive modeling is performed.
* The Power BI file is a static template; users can further customise visuals.
* Docker is used only for PostgreSQL (and optional pgAdmin).

---
*Generated on 2026‑09‑12.*
