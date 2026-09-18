from pathlib import Path
import json
from urllib import request
from urllib.error import URLError

import pandas as pd


PROJECT = Path(__file__).parent
OUTPUT_FOLDER = PROJECT / "outputs"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"


def load_project_results():
    """Load the finance results created by the pipeline."""
    departments = pd.read_csv(
        OUTPUT_FOLDER / "department_summary.csv"
    )

    anomalies = pd.read_csv(
        OUTPUT_FOLDER / "anomalies.csv"
    )

    forecast = pd.read_csv(
        OUTPUT_FOLDER / "forecast.csv"
    )

    return departments, anomalies, forecast


def build_prompt(departments, anomalies, forecast):
    """Create a prompt using verified Python results."""
    total_budget = departments["budget"].sum()
    total_actual = departments["actual"].sum()
    total_variance = total_budget - total_actual

    department_results = departments.copy()

    department_results["overrun"] = (
        department_results["actual"]
        - department_results["budget"]
    )

    worst_department = (
        department_results
        .sort_values(
            "overrun",
            ascending=False,
        )
        .iloc[0]
    )

    return f"""
You are assisting a financial analyst.

Python has already calculated and verified these facts:

Total budget: ${total_budget:,.2f}
Total actual: ${total_actual:,.2f}
Total variance: ${total_variance:,.2f}
Largest departmental overrun:
{worst_department["department"]}
Number of transactions flagged for review:
{len(anomalies)}

Your only task is to provide exactly three short
recommended actions.

Do not calculate, repeat, change, or invent any numbers.
Do not write an executive summary.
Do not restate the financial results.
"""


def ask_ollama(prompt):
    """Send the finance results to the local Ollama model."""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }

    encoded_payload = json.dumps(
        payload
    ).encode("utf-8")

    web_request = request.Request(
        OLLAMA_URL,
        data=encoded_payload,
        headers={
            "Content-Type": "application/json"
        },
        method="POST",
    )

    try:
        with request.urlopen(
            web_request,
            timeout=180,
        ) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

            return result["response"]

    except URLError as error:
        raise RuntimeError(
            "Ollama is not available. "
            "Make sure the Ollama application is open."
        ) from error


def main():
    departments, anomalies, forecast = (
        load_project_results()
    )

    prompt = build_prompt(
        departments,
        anomalies,
        forecast,
    )

    print(
        "Asking the local AI to analyze "
        "SmartBudget..."
    )

    summary = ask_ollama(prompt)

    output_file = (
        OUTPUT_FOLDER
        / "ai_finance_summary.txt"
    )

    output_file.write_text(
        summary,
        encoding="utf-8",
    )

    print("\nLOCAL AI FINANCE REPORT\n")
    print(summary)

    print(
        f"\nReport saved to: {output_file}"
    )


if __name__ == "__main__":
    main()