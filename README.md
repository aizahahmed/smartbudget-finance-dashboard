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

The complete workflow can be run with one command:

```bash
python run_pipeline.py


