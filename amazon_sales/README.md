# 📊 Amazon Sales & Revenue Performance Analytics Pipeline

A self-directed data engineering and portfolio framework modeling high-scale transactional payloads based on global Amazon Seller Central streams. This project executes a robust Python and SQL pipeline over a large-scale e-commerce dataset containing **128,975 transactional records**, systematically uncovering **₹8.1 Million in hidden losses** due to cancellations and product returns.

## 🚀 Interactive Dashboard Preview
![Amazon Sales Dashboard](dashboard_preview.gif)

---

## 🏗️ Architecture Design: Enterprise Observability & Self-Healing Layout
To meet the rigorous data quality, error boundaries, and monitoring standards required in production-grade e-commerce infrastructure, the framework deploys a strict multi-layered verification and monitoring architecture:
1. **Enterprise Logging Framework (`logging`):** Completely replaced legacy, unmonitored standard stdout text prints with a formal Python logging machine. Events, environment shifts, and connection faults are systematically tracked across precise execution states (`INFO`, `WARNING`, `CRITICAL`) to allow direct parsing by automated cloud orchestrators.
2. **First-Class Rejection Metrics & Quarantine:** Malformed textual data corruptions or alphanumeric anomalies are proactively intercepted row-by-row. Instead of masking failures using silent zero conversions that skew corporate averages downstream, corrupt fields are cast to explicit `NULL` maps and actively tracked as a first-class operational quality metric.
3. **Automated Alerting Thresholds (Fail-Fast):** Incorporates an active runtime processing limit constraint. If the e-commerce data ingestion pipeline encounters a critical row rejection rate greater than **5.0%** of the batch payload volume, the entire framework halts execution immediately and throws a hard termination state (`sys.exit(1)`) to trigger scheduler alerts.
4. **Self-Healing Pre-Load Layer:** Coerces incoming data structure alignments (e.g., preventing schema drift by casting Order IDs to clean strings) and strips alphanumeric grouping formatting or currency markers before numeric conversion.
5. **Decoupled Unit Testing (`pytest`):** Core transformation math and financial logic are fully decoupled into an independent logic module (`amazon_parser.py`) to eliminate environmental connection dependencies, allowing rapid parameterized testing execution.
6. **Declarative Schema Validation (`pandera`):** Screens the fully aligned, cleaned, and healed dataframe for structural attributes, duplicate keys, and range constraints before allowing downstream relational loading.

---

## 🔗 Dataset Provenance & Disclosure (Clone & Run Standard)
* **Data Source:** Publicly verified [Amazon Sale Report dataset via Kaggle](https://kaggle.com).
* **Scale:** 128,975 raw rows capturing transactions from Amazon India.
* **Testing Vibe:** This repository contains a lightweight **`Amazon_sales_sample.csv`** to ensure full reproducibility and execution checks for reviewers and target clients without requiring heavy local system storage or processing overhead.

---

## 🎯 Engineered Financial Insights
By deploying high-precision numeric types and strict data quality boundaries, this project systematically isolates transactional anomalies to calculate true commercial performance metrics across the Amazon India network:

1. **The Revenue Leakage:** Total Gross Revenue was calculated at **₹78,592,678.30**. By building strict status-filtering layers, the actual **Net Revenue (Clean)** was isolated at **₹70,403,750.00**, proving that **₹8,188,928.30 (10.4% of gross volume)** was tied up in logistics failures (cancellations and returns).
2. **The Product Leader:** The **"Set"** product category stands as the core revenue driver, registering **50,284 successful orders** and yielding **₹35,100,949** in sanitized net revenue.
3. **Inventory Sweet Spot:** Size **"M"** systematically dominates order velocity across all main product lines, establishing the highest high-volume transaction metrics.
4. **Commercial Peak:** Time-series sorting identifies **April 2022 (Month 04)** as the highest historical revenue spike.

---

## 🛠️ Tech Stack & Pipeline Configurations
- **Data Engineering:** Python (Pandas) executing an inline self-healing text cleanup matrix, robust `logging` stream handlers, and strict type formatting via `pandera.pandas`. High-precision accounting aggregates utilize `decimal.Decimal` logic to completely eliminate binary float drifting. Loose zero-interpolations (`.fillna(0)`) are entirely deprecated.
- **Testing Suite:** `pytest` executing parametrized, table-driven unit tests to simulate and intercept raw input anomalies.
- **Database Architecture:** PostgreSQL (SQLAlchemy + `psycopg2-binary`) deploying optimized bulk block write configurations (`chunksize=10000`) and secure Connection Pooler layers (Port `6543`), featuring automated local file backup routing.
- **BI Visualization:** Power BI Desktop configured with custom localization schemas for the Indian Rupee (`₹`) financial system, optimized for flawless metric aggregations (`SUM()` and `AVERAGE()`).

---

## 📁 Repository Directory Structure

```text
amazon-sales-analytics/
└── amazon_sales/
    ├── Amazon_sales_sample.csv            # Custom Ingestion Sample Dataset
    ├── amazon_parser.py                   # Pure Decoupled Parsing & Business Logic (100% Testable)
    ├── amazon_analytics.py                # Main Core Analytics Engine & Production Logging Handlers
    ├── amazon_ingestion.py                # Relational Storage Ingestion Stream with Logging Blueprint
    ├── test_amazon.py                     # Parametrized Pytest Suite & Code Crash Simulator
    ├── requirements.txt                   # Locked Software Dependency Layout Matrix
    └── README.md                          # Enterprise Systems Documentation
```

---

## 🚀 Quick Start (Clone & Run Standard)

### 1. Replicate Local Dependencies
Deploy the isolated software version scheme inside your local execution environment:
```powershell
pip install -r requirements.txt
```

### 2. Execute Automated Code Testing
Run the complete unit testing suite using the built-in crash-test vectors to verify validation stability:
```powershell
pytest test_amazon.py -v
```

### 3. Run the Local Financial Validation Audit
To verify the analytical layer using the pre-packaged sample data pool, execute:
```powershell
python amazon_analytics.py
```

### 4. Inspect the Ingestion Architecture Blueprint
Test the dual-mode framework pipeline to inspect database ingestion scalability configurations:
```powershell
python amazon_ingestion.py
```

---
*Engineered under the UpDataLogic Performance Framework for transparent, honest, and reproducible analytics pipelines.*
