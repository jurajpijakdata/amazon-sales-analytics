# Amazon Sales & Revenue Performance Analytics Pipeline

[![tests](https://github.com/jurajpijakdata/amazon-sales-analytics/actions/workflows/tests.yml/badge.svg)](https://github.com/jurajpijakdata/amazon-sales-analytics/actions/workflows/tests.yml)

A Python and SQL data pipeline built over a real-scale Amazon India sales dataset (128,975 transactional records), built to surface exactly how much revenue is lost to cancellations and returns rather than just reporting gross sales.

## Dashboard preview

![Amazon Sales Dashboard](amazon_sales/dashboard_preview.gif)

## How it's built

**Self-healing currency parsing.** Raw price strings come in with inconsistent formatting (currency symbols, mixed comma/dot grouping). `amazon_parser.py` normalizes them into high-precision `Decimal` values, isolated in its own tested module so the parsing logic never depends on a database connection.

**Quarantine over silent failure.** Rows with unparseable amounts get `NULL` and a `data_quality_status = 'UNKNOWN'` flag instead of being defaulted to zero, which would quietly understate revenue. If more than 5% of a run's rows fail validation, the pipeline stops rather than loading a bad batch.

**Schema validation.** `pandera` checks structure, ranges, and required columns before anything is written downstream.

**Idempotent loads.** The ingestion script uses `INSERT ... ON CONFLICT DO UPDATE` keyed on each row's own line-item ID (an Amazon order can span several rows when it contains multiple SKUs, so `Order ID` alone isn't a unique key -- the dataset's own row index is), so it can be re-run safely without creating duplicates.

**Tested at two levels.** `test_amazon.py` covers the currency parsing logic directly. `test_amazon_pipeline.py` is an integration test that actually runs both `amazon_analytics.py` and `amazon_ingestion.py` end to end with no configuration present, the same situation a fresh clone of this repo is in. Both run automatically in CI on every push (see the badge above).

## Dataset

- **Source:** [Amazon Sale Report dataset via Kaggle](https://kaggle.com).
- **Scale:** 128,975 raw rows of Amazon India transactions.
- **Sample included:** This repo ships a lightweight `Amazon_sales_sample.csv` so the pipeline is fully runnable end to end without needing the full dataset or a database connection.

## What the numbers show

- **Revenue leakage:** Gross revenue across the full dataset was ₹78,592,678.30. After filtering out cancellations and returns, clean net revenue was ₹70,403,750.00 -- meaning ₹8,188,928.30 (10.4% of gross volume) was tied up in logistics failures.
- **Top category:** "Set" is the leading product category by volume, with 42,181 successful orders and ₹35,100,949 in clean net revenue.
- **Size distribution:** Size "M" has the highest order volume across the main product lines.
- **Seasonality:** April 2022 was the highest-revenue month in the dataset.

## Tech stack

- **Data engineering:** Python (pandas) with a self-healing text cleanup layer, `logging` for structured output, and `pandera` for schema validation. Monetary values use `decimal.Decimal` throughout to avoid floating-point rounding drift.
- **Testing:** `pytest`, parametrized unit tests plus a full-pipeline integration test.
- **Database:** PostgreSQL via SQLAlchemy + `psycopg2-binary`, with a chunked bulk-upsert load step and an automatic local SQLite fallback when no cloud database is configured.
- **BI:** Power BI, formatted for Indian Rupee (₹) currency display.

## Repository structure

```text
amazon-sales-analytics/
├── amazon_sales/
│   ├── amazon_parser.py          # Currency parsing & Decimal conversion logic (unit tested)
│   ├── amazon_analytics.py       # Reads the CSV, cleans it, prints revenue metrics
│   ├── amazon_ingestion.py       # Loads cleaned data into Postgres (or SQLite fallback)
│   ├── test_amazon.py            # Unit tests for amazon_parser.py
│   ├── test_amazon_pipeline.py   # Integration tests: run both scripts end to end
│   ├── Amazon_sales_sample.csv   # Sample dataset for reproducible runs
│   ├── requirements.txt          # Pinned dependencies
│   ├── .env.example              # Template for real database credentials
│   └── dashboard_preview.gif
├── .github/workflows/tests.yml   # CI: runs the test suite on every push/PR
├── LICENSE
└── README.md
```

## Quick start

All commands below are run from inside the `amazon_sales/` folder.

```bash
cd amazon_sales
```

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the test suite

```bash
pytest -v
```

### 3. Run the analytics script

Computes and prints the revenue metrics from the sample dataset:

```bash
python amazon_analytics.py
```

### 4. Run the ingestion pipeline

Loads the cleaned data into a database. With no `.env` file configured, it automatically falls back to a local SQLite database, so this runs with zero setup:

```bash
python amazon_ingestion.py
```

To connect it to a real Postgres/Supabase database instead, copy `.env.example` to `.env` (both inside `amazon_sales/`) and fill in your real credentials.

---
*Built under the UpDataLogic Performance Framework for transparent, honest, and reproducible analytics pipelines.*
