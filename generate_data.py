
import pandas as pd
import numpy as np
from pathlib import Path

# Make the data reproducible
np.random.seed(42)

# Create the data directory if it doesn't exist
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# ------------------------------------------
# 1. GENERATE SALES AND FINANCIAL DATA
# ------------------------------------------

num_records = 500

dates = pd.date_range(
    start="2025-01-01",
    end="2025-12-31",
    periods=num_records
)

departments = ["Sales", "Marketing", "Operations", "Technology"]
products = ["Laptop", "Monitor", "Keyboard", "Mouse", "Printer"]
regions = ["North", "South", "East", "West"]

sales_data = pd.DataFrame({
    "Date": dates,
    "Department": np.random.choice(
        departments, num_records
    ),
    "Product": np.random.choice(
        products, num_records
    ),
    "Region": np.random.choice(
        regions, num_records
    ),
    "Units_Sold": np.random.randint(
        1, 21, num_records
    ),
    "Unit_Price": np.random.randint(
        500, 50001, num_records
    ),
    "Unit_Cost": np.random.randint(
        200, 35001, num_records
    )
})

# Ensure the unit cost is lower than the unit price
sales_data["Unit_Cost"] = (
    sales_data["Unit_Cost"]
    .clip(upper=sales_data["Unit_Price"] - 1)
)

# Calculate financial values
sales_data["Revenue"] = (
    sales_data["Units_Sold"] *
    sales_data["Unit_Price"]
)

sales_data["Expenses"] = (
    sales_data["Units_Sold"] *
    sales_data["Unit_Cost"]
)

sales_data["Profit"] = (
    sales_data["Revenue"] -
    sales_data["Expenses"]
)

# Save sales dataset
sales_data.to_csv(
    DATA_DIR / "sales_data.csv",
    index=False
)

# ------------------------------------------
# 2. GENERATE EMPLOYEE DATA
# ------------------------------------------

num_employees = 120

employee_departments = np.random.choice(
    departments,
    num_employees,
    p=[0.35, 0.20, 0.25, 0.20]
)

employee_data = pd.DataFrame({
    "Employee_ID": [
        f"EMP{i:03d}"
        for i in range(1, num_employees + 1)
    ],
    "Department": employee_departments,
    "Age": np.random.randint(
        22, 61, num_employees
    ),
    "Experience_Years": np.random.randint(
        0, 31, num_employees
    ),
    "Monthly_Salary": np.random.randint(
        20000, 100001, num_employees
    ),
    "Performance_Score": np.random.randint(
        1, 6, num_employees
    )
})

# Save employee dataset
employee_data.to_csv(
    DATA_DIR / "employee_data.csv",
    index=False
)

# ------------------------------------------
# 3. DISPLAY DATASET SUMMARY
# ------------------------------------------

print("Sample datasets generated successfully!")
print()

print("SALES DATA")
print(f"Total records: {len(sales_data)}")
print(sales_data.head())
print()

print("EMPLOYEE DATA")
print(f"Total employees: {len(employee_data)}")
print(employee_data.head())

print()
print("Files saved in the data/ folder.")
