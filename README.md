# SmartBudget Finance Dashboard

An end-to-end finance analytics project that analyzes spending, compares budgets with actual costs, forecasts future expenses, detects unusual transactions, extracts invoice data using OCR, and generates financial recommendations with a locally hosted AI model.

## Project Results

- Analyzed 240 fictional financial transactions
- Compared $1,191,560 in budgeted costs with $1,196,140 in actual costs
- Identified a total unfavorable variance of $4,580
- Flagged 12 unusual transactions using machine learning
- Produced a three-month expense forecast
- Extracted invoice information with Tesseract OCR
- Generated recommendations locally using Ollama

## Technologies

- Python
- pandas and NumPy
- scikit-learn
- SQL and SQLite
- Tesseract OCR and PyPDF
- Ollama and Llama 3.2
- HTML and CSS
- Git and GitHub

## Main Features

### Financial Analytics

The Python analysis calculates total spending, budget variance, department performance, category summaries, and monthly trends.

### Machine Learning

An Isolation Forest model identifies transactions that may require additional review.

### Forecasting

A linear regression model forecasts expenses for the next three months.

### Invoice OCR

Tesseract reads invoice images and extracts fields such as vendor, invoice number, date, department, amount, and payment method.

### Local AI Reporting

Ollama runs a local Llama model that reviews verified analytics results and recommends financial actions without sending financial data to an external AI service.

### Automated Pipeline

Run the entire workflow with:

```bash
python run_pipeline.py
```

## Project Structure

```text
smartbudget-finance-dashboard/
├── data/
├── invoices/
├── outputs/
├── index.html
├── smartbudget.sql
├── smartbudget_analysis.py
├── invoice_ocr.py
├── local_ai_summary.py
├── run_pipeline.py
└── requirements.txt
```

## Installation

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Download the local Ollama model:

```bash
ollama pull llama3.2:3b
```

Run the complete project:

```bash
python run_pipeline.py
```

## Skills Demonstrated

This project demonstrates financial analytics, data cleaning, SQL, machine learning, forecasting, OCR, workflow automation, local AI deployment, dashboard development, Git, and GitHub.

## Disclaimer

All transactions and invoices in this project are fictional and were created for educational and portfolio purposes.
