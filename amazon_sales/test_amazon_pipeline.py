import shutil
import subprocess
import sys
from pathlib import Path


def _run_script(script_name, tmp_path):
    repo_root = Path(__file__).resolve().parent
    for filename in (script_name, "amazon_parser.py", "Amazon_sales_sample.csv"):
        shutil.copy(repo_root / filename, tmp_path / filename)

    return subprocess.run(
        [sys.executable, script_name],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )


def test_amazon_analytics_runs_end_to_end(tmp_path):
    """
    Runs the analytics script for real against the sample dataset and
    checks it completes successfully. This is the scenario the README's
    quick start walks a reviewer through.
    """
    result = _run_script("amazon_analytics.py", tmp_path)

    assert result.returncode == 0, (
        f"amazon_analytics.py exited with code {result.returncode}.\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    assert "DATA VALIDATION & CLEANSING COMPLETED SUCCESSFULLY" in result.stdout


def test_amazon_ingestion_runs_end_to_end_with_no_configuration(tmp_path):
    """
    Integration test for the ingestion pipeline, not just the currency
    logic covered by test_amazon.py.

    With no .env file present -- the exact situation a fresh clone of this
    repo is in -- the pipeline must fall back to a local SQLite database
    and complete successfully (extract, transform, validate, load) rather
    than crashing.
    """
    result = _run_script("amazon_ingestion.py", tmp_path)

    assert result.returncode == 0, (
        f"amazon_ingestion.py exited with code {result.returncode}.\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    assert "PIPELINE RUN COMPLETION: STATUS 0 [SUCCESS]" in result.stdout
