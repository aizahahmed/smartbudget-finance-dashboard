from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression


PROJECT = Path(__file__).parent
DATA_FOLDER = PROJECT / "data"
OUTPUT_FOLDER = PROJECT / "outputs"

DATA_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

rng = np.random.default_rng(42)

department_totals = {
    "Operations": {"budget": 317760, "actual": 322530},
    "Technology": {"budget": 278650, "actual": 279530},
    "Sales": {"budget": 299640, "actual": 311230},
    "Human Resources": {"budget": 295510, "actual": 282850},
}

categories = [
    "Payroll",
    "Software",
    "Travel",
    "Office Supplies",
    "Marketing",
    "Professional Services",
    "Utilities",
    "Training",
]

vendors = [
    "PayServe",
    "CloudSuite",
    "Metro Travel",
    "Office Hub",
    "MarketWorks",
    "Advisory Partners",
    "City Power",
    "SkillPath",
]

payment_methods = ["ACH", "Corporate Card", "Wire"]


def allocate_total(total, count):
    """Create random positive values that add up to an exact total."""
    weights = rng.random(count)
    raw = total * weights / weights.sum()
    values = np.floor(raw).astype(int)

    difference = total - values.sum()
    order = np.argsort(raw - values)[::-1]
    values[order[:difference]] += 1

    return values


records = []
transaction_number = 1001

for department, totals in department_totals.items():
    budgets = allocate_total(totals["budget"], 60)
    actuals = allocate_total(totals["actual"], 60)

    for position in range(60):
        month = position // 5 + 1
        day = (position * 5) % 27 + 1
        category_index = (position + len(department)) % len(categories)

        budget = int(budgets[position])
        actual = int(actuals[position])

        records.append(
            {
                "transaction_id": f"TXN-{transaction_number}",
                "transaction_date": f"2026-{month:02d}-{day:02d}",
                "department": department,
                "category": categories[category_index],
                "vendor": vendors[category_index],
                "budget": budget,
                "actual": actual,
                "status": (
                    "Over budget"
                    if actual > budget
                    else "Within budget"
                ),
                "payment_method": rng.choice(payment_methods),
            }
        )

        transaction_number += 1


transactions = pd.DataFrame(records)
transactions["transaction_date"] = pd.to_datetime(
    transactions["transaction_date"]
)

transactions["variance"] = (
    transactions["budget"] - transactions["actual"]
)

transactions["variance_percent"] = np.where(
    transactions["budget"] == 0,
    np.nan,
    (
        transactions["actual"] - transactions["budget"]
    ) / transactions["budget"],
)

# Machine-learning anomaly detection
model = IsolationForest(
    contamination=0.05,
    random_state=42,
)

transactions["anomaly"] = model.fit_predict(
    transactions[
        ["budget", "actual", "variance_percent"]
    ].fillna(0)
)

transactions["anomaly_status"] = np.where(
    transactions["anomaly"] == -1,
    "Review",
    "Normal",
)

# Department summary
department_summary = (
    transactions.groupby("department", as_index=False)
    .agg(
        budget=("budget", "sum"),
        actual=("actual", "sum"),
    )
)

department_summary["variance"] = (
    department_summary["budget"]
    - department_summary["actual"]
)

department_summary["status"] = np.where(
    department_summary["actual"]
    > department_summary["budget"],
    "Over budget",
    "Within budget",
)

# Category summary
category_summary = (
    transactions.groupby("category", as_index=False)
    .agg(
        budget=("budget", "sum"),
        actual=("actual", "sum"),
    )
)

category_summary["variance"] = (
    category_summary["budget"]
    - category_summary["actual"]
)

# Monthly spending and forecasting
transactions["month"] = (
    transactions["transaction_date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_summary = (
    transactions.groupby("month", as_index=False)
    .agg(
        budget=("budget", "sum"),
        actual=("actual", "sum"),
    )
)

x = np.arange(len(monthly_summary)).reshape(-1, 1)
y = monthly_summary["actual"].to_numpy()

forecast_model = LinearRegression()
forecast_model.fit(x, y)

future_x = np.arange(
    len(monthly_summary),
    len(monthly_summary) + 3,
).reshape(-1, 1)

future_months = pd.date_range(
    "2027-01-01",
    periods=3,
    freq="MS",
).strftime("%Y-%m")

forecast = pd.DataFrame(
    {
        "month": future_months,
        "forecast_actual": forecast_model.predict(
            future_x
        ).round(2),
    }
)

# Save CSV outputs
transactions.to_csv(
    DATA_FOLDER / "transactions.csv",
    index=False,
)

department_summary.to_csv(
    OUTPUT_FOLDER / "department_summary.csv",
    index=False,
)

category_summary.to_csv(
    OUTPUT_FOLDER / "category_summary.csv",
    index=False,
)

monthly_summary.to_csv(
    OUTPUT_FOLDER / "monthly_summary.csv",
    index=False,
)

forecast.to_csv(
    OUTPUT_FOLDER / "forecast.csv",
    index=False,
)

transactions[
    transactions["anomaly_status"] == "Review"
].to_csv(
    OUTPUT_FOLDER / "anomalies.csv",
    index=False,
)

# Save data to SQLite
database = sqlite3.connect(
    PROJECT / "smartbudget.db"
)

transactions.to_sql(
    "transactions",
    database,
    if_exists="replace",
    index=False,
)

database.execute(
    "CREATE INDEX IF NOT EXISTS "
    "idx_department ON transactions(department)"
)

database.execute(
    "CREATE INDEX IF NOT EXISTS "
    "idx_category ON transactions(category)"
)

database.commit()
database.close()

total_budget = transactions["budget"].sum()
total_actual = transactions["actual"].sum()

print("SmartBudget analysis completed")
print(f"Transactions: {len(transactions):,}")
print(f"Total budget: ${total_budget:,.0f}")
print(f"Total actual: ${total_actual:,.0f}")
print(
    f"Variance: ${total_budget - total_actual:,.0f}"
)
print(
    f"Anomalies flagged: "
    f"{(transactions['anomaly_status'] == 'Review').sum()}"
)
print("\nDepartment summary:")
print(department_summary.to_string(index=False))
print("\nThree-month forecast:")
print(forecast.to_string(index=False))