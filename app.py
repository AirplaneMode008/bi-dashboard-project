
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Business Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# 2. LOAD DATA
# ==========================================

DATA_DIR = Path(__file__).parent / "data"


# ==========================================
# 2. LOAD DATA AND HANDLE CSV UPLOADS
# ==========================================

DATA_DIR = Path(__file__).parent / "data"

sales_file = DATA_DIR / "sales_data.csv"
employee_file = DATA_DIR / "employee_data.csv"

# Load default datasets
default_sales_df = pd.read_csv(
    sales_file,
    parse_dates=["Date"]
)

default_employee_df = pd.read_csv(
    employee_file
)

# Initialize session state
if "sales_data" not in st.session_state:
    st.session_state.sales_data = default_sales_df.copy()

if "employee_data" not in st.session_state:
    st.session_state.employee_data = default_employee_df.copy()

# Upload interface
st.sidebar.divider()
st.sidebar.header("📂 Upload Your Data")

uploaded_sales = st.sidebar.file_uploader(
    "Upload Sales CSV",
    type=["csv"],
    key="sales_upload"
)

uploaded_employees = st.sidebar.file_uploader(
    "Upload Employee CSV",
    type=["csv"],
    key="employee_upload"
)

# Required columns
sales_required_columns = {
    "Date", "Department", "Product", "Region",
    "Units_Sold", "Unit_Price", "Unit_Cost",
    "Revenue", "Expenses", "Profit"
}

employee_required_columns = {
    "Employee_ID", "Department", "Age",
    "Experience_Years", "Monthly_Salary",
    "Performance_Score"
}

# Process uploaded sales data
if uploaded_sales is not None:
    try:
        uploaded_sales_df = pd.read_csv(uploaded_sales)

        missing_columns = (
            sales_required_columns -
            set(uploaded_sales_df.columns)
        )

        if missing_columns:
            st.sidebar.error(
                "Sales CSV is missing columns: "
                + ", ".join(sorted(missing_columns))
            )
        else:
            uploaded_sales_df["Date"] = pd.to_datetime(
                uploaded_sales_df["Date"],
                errors="coerce"
            )

            uploaded_sales_df = uploaded_sales_df.dropna(
                subset=["Date", "Department", "Product"]
            )

            numeric_columns = [
                "Units_Sold", "Unit_Price", "Unit_Cost",
                "Revenue", "Expenses", "Profit"
            ]

            for column in numeric_columns:
                uploaded_sales_df[column] = pd.to_numeric(
                    uploaded_sales_df[column],
                    errors="coerce"
                )

            uploaded_sales_df = uploaded_sales_df.dropna(
                subset=numeric_columns
            )

            st.session_state.sales_data = uploaded_sales_df

            st.sidebar.success(
                "Sales dataset uploaded successfully!"
            )

    except Exception as error:
        st.sidebar.error(
            f"Could not read sales CSV: {error}"
        )

# Process uploaded employee data
if uploaded_employees is not None:
    try:
        uploaded_employee_df = pd.read_csv(
            uploaded_employees
        )

        missing_columns = (
            employee_required_columns -
            set(uploaded_employee_df.columns)
        )

        if missing_columns:
            st.sidebar.error(
                "Employee CSV is missing columns: "
                + ", ".join(sorted(missing_columns))
            )
        else:
            numeric_columns = [
                "Age", "Experience_Years",
                "Monthly_Salary", "Performance_Score"
            ]

            for column in numeric_columns:
                uploaded_employee_df[column] = pd.to_numeric(
                    uploaded_employee_df[column],
                    errors="coerce"
                )

            uploaded_employee_df = uploaded_employee_df.dropna(
                subset=[
                    "Employee_ID",
                    "Department",
                    *numeric_columns
                ]
            )

            st.session_state.employee_data = (
                uploaded_employee_df
            )

            st.sidebar.success(
                "Employee dataset uploaded successfully!"
            )

    except Exception as error:
        st.sidebar.error(
            f"Could not read employee CSV: {error}"
        )

# Use the active datasets throughout the dashboard
sales_df = st.session_state.sales_data.copy()
employee_df = st.session_state.employee_data.copy()

# Recalculate financial values from source columns.
# This prevents inconsistent uploaded Revenue/Profit
# values from being used without checking them.
sales_df["Revenue"] = (
    sales_df["Units_Sold"] * sales_df["Unit_Price"]
)

sales_df["Expenses"] = (
    sales_df["Units_Sold"] * sales_df["Unit_Cost"]
)

sales_df["Profit"] = (
    sales_df["Revenue"] - sales_df["Expenses"]
)


sales_df = pd.read_csv(sales_file, parse_dates=["Date"])
employee_df = pd.read_csv(employee_file)

# ==========================================
# 3. DASHBOARD HEADER
# ==========================================

st.title("📊 Business Intelligence Dashboard")

st.markdown(
    "### Organizational Data Analysis"
)

st.caption(
    "Analyze financial performance, sales trends, "
    "and organizational metrics."
)

st.divider()

# ==========================================
# 4. SIDEBAR FILTERS
# ==========================================

st.sidebar.header("Dashboard Filters")

departments = sorted(
    sales_df["Department"].dropna().unique()
)

selected_departments = st.sidebar.multiselect(
    "Select Departments",
    options=departments,
    default=departments
)

min_date = sales_df["Date"].min().date()
max_date = sales_df["Date"].max().date()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Validate the selected date range
if not isinstance(selected_dates, (tuple, list)):
    selected_dates = (selected_dates, selected_dates)

if len(selected_dates) == 1:
    selected_dates = (selected_dates[0], selected_dates[0])

start_date, end_date = selected_dates

# ==========================================
# 5. FILTER THE SALES DATA
# ==========================================

filtered_df = sales_df[
    (sales_df["Department"].isin(selected_departments))
    & (sales_df["Date"].dt.date >= start_date)
    & (sales_df["Date"].dt.date <= end_date)
].copy()

# ==========================================
# 6. CALCULATE KEY PERFORMANCE INDICATORS
# ==========================================

total_revenue = filtered_df["Revenue"].sum()
total_expenses = filtered_df["Expenses"].sum()
total_profit = filtered_df["Profit"].sum()

profit_margin = (
    (total_profit / total_revenue) * 100
    if total_revenue > 0
    else 0
)

total_employees = len(employee_df)

# ==========================================
# 7. DISPLAY KPI CARDS
# ==========================================

st.subheader("Organizational Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Revenue",
    f"₹{total_revenue:,.0f}"
)

col2.metric(
    "Total Expenses",
    f"₹{total_expenses:,.0f}"
)

col3.metric(
    "Net Profit",
    f"₹{total_profit:,.0f}"
)

col4.metric(
    "Total Employees",
    f"{total_employees:,}"
)

st.caption(
    f"Profit margin for the selected sales data: "
    f"{profit_margin:.2f}%"
)

st.divider()

# ==========================================
# 8. REVENUE TREND CHART
# ==========================================

st.subheader("Revenue and Profit Trends")

if not filtered_df.empty:

    monthly_data = (
        filtered_df
        .set_index("Date")
        .resample("MS")[["Revenue", "Profit"]]
        .sum()
        .reset_index()
    )

    monthly_long = monthly_data.melt(
        id_vars="Date",
        value_vars=["Revenue", "Profit"],
        var_name="Metric",
        value_name="Amount"
    )

    fig_trend = px.line(
        monthly_long,
        x="Date",
        y="Amount",
        color="Metric",
        markers=True,
        title="Monthly Revenue and Profit",
        labels={
            "Date": "Month",
            "Amount": "Amount (₹)",
            "Metric": "Financial Metric"
        },
        template="plotly_white"
    )

    fig_trend.update_layout(
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_trend,
        use_container_width=True
    )

else:
    st.info(
        "No sales records match the selected filters."
    )

st.divider()

# ==========================================
# 9. DEPARTMENT PERFORMANCE
# ==========================================

st.subheader("Department Performance")

if not filtered_df.empty:

    department_data = (
        filtered_df
        .groupby("Department", as_index=False)
        [["Revenue", "Expenses", "Profit"]]
        .sum()
    )

    fig_department = px.bar(
        department_data,
        x="Department",
        y=["Revenue", "Expenses", "Profit"],
        barmode="group",
        title="Revenue, Expenses and Profit by Department",
        labels={
            "value": "Amount (₹)",
            "variable": "Financial Metric",
            "Department": "Department"
        },
        template="plotly_white"
    )

    st.plotly_chart(
        fig_department,
        use_container_width=True
    )

else:
    st.info(
        "No department data is available for these filters."
    )

st.divider()

# ==========================================
# 10. PRODUCT PERFORMANCE
# ==========================================

st.subheader("Product Performance")

if not filtered_df.empty:

    product_data = (
        filtered_df
        .groupby("Product", as_index=False)
        [["Units_Sold", "Revenue", "Profit"]]
        .sum()
        .sort_values("Revenue", ascending=False)
    )

    fig_products = px.bar(
        product_data,
        x="Product",
        y="Revenue",
        color="Product",
        title="Revenue by Product",
        labels={
            "Revenue": "Revenue (₹)",
            "Product": "Product"
        },
        template="plotly_white"
    )

    st.plotly_chart(
        fig_products,
        use_container_width=True
    )

else:
    st.info(
        "No product data is available for these filters."
    )

st.divider()

# ==========================================
# 11. SALES DATA TABLE
# ==========================================

st.subheader("Sales Records")

st.dataframe(
    filtered_df.sort_values("Date", ascending=False),
    use_container_width=True,
    hide_index=True
)

st.caption(
    f"Showing {len(filtered_df)} sales records "
    f"matching the selected filters."
)


# ==========================================
# 12. EMPLOYEE ANALYTICS
# ==========================================

st.divider()

st.header("👥 Employee Analytics")

# ------------------------------------------
# 12.1 EMPLOYEE SUMMARY
# ------------------------------------------

total_employees = employee_df["Employee_ID"].nunique()

average_salary = employee_df["Monthly_Salary"].mean()

average_experience = employee_df["Experience_Years"].mean()

average_performance = employee_df["Performance_Score"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Employees",
    f"{total_employees:,}"
)

col2.metric(
    "Average Monthly Salary",
    f"₹{average_salary:,.0f}"
)

col3.metric(
    "Average Experience",
    f"{average_experience:.1f} years"
)

col4.metric(
    "Average Performance",
    f"{average_performance:.2f}/5"
)

# ------------------------------------------
# 12.2 EMPLOYEE DISTRIBUTION
# ------------------------------------------

st.subheader("Employee Distribution by Department")

department_employees = (
    employee_df
    .groupby("Department")
    .size()
    .reset_index(name="Employee_Count")
)

fig_employee_distribution = px.pie(
    department_employees,
    names="Department",
    values="Employee_Count",
    hole=0.45,
    title="Workforce Distribution"
)

st.plotly_chart(
    fig_employee_distribution,
    use_container_width=True
)

# ------------------------------------------
# 12.3 SALARY ANALYSIS
# ------------------------------------------

st.subheader("Salary Analysis")

salary_data = (
    employee_df
    .groupby("Department", as_index=False)
    ["Monthly_Salary"]
    .mean()
)

fig_salary = px.bar(
    salary_data,
    x="Department",
    y="Monthly_Salary",
    color="Department",
    title="Average Monthly Salary by Department",
    labels={
        "Monthly_Salary": "Average Salary (₹)",
        "Department": "Department"
    },
    template="plotly_white"
)

st.plotly_chart(
    fig_salary,
    use_container_width=True
)

# ------------------------------------------
# 12.4 PERFORMANCE ANALYSIS
# ------------------------------------------

st.subheader("Employee Performance Analysis")

performance_data = (
    employee_df
    .groupby("Department", as_index=False)
    ["Performance_Score"]
    .mean()
)

fig_performance = px.bar(
    performance_data,
    x="Department",
    y="Performance_Score",
    color="Department",
    title="Average Performance Score by Department",
    labels={
        "Performance_Score": "Average Score (1–5)",
        "Department": "Department"
    },
    template="plotly_white"
)

fig_performance.update_yaxes(
    range=[0, 5]
)

st.plotly_chart(
    fig_performance,
    use_container_width=True
)

# ------------------------------------------
# 12.5 EXPERIENCE ANALYSIS
# ------------------------------------------

st.subheader("Employee Experience Distribution")

fig_experience = px.histogram(
    employee_df,
    x="Experience_Years",
    nbins=15,
    title="Distribution of Employee Experience",
    labels={
        "Experience_Years": "Experience (Years)",
        "count": "Number of Employees"
    },
    template="plotly_white"
)

st.plotly_chart(
    fig_experience,
    use_container_width=True
)

# ------------------------------------------
# 12.6 EMPLOYEE RECORDS
# ------------------------------------------

st.subheader("Employee Records")

employee_departments = sorted(
    employee_df["Department"].unique()
)

selected_employee_departments = st.multiselect(
    "Filter Employees by Department",
    options=employee_departments,
    default=employee_departments,
    key="employee_department_filter"
)

filtered_employee_df = employee_df[
    employee_df["Department"].isin(
        selected_employee_departments
    )
]

st.dataframe(
    filtered_employee_df,
    use_container_width=True,
    hide_index=True
)

st.caption(
    f"Showing {len(filtered_employee_df)} employee records."
)


# ==========================================
# 13. DOWNLOAD REPORTS
# ==========================================

st.divider()

st.header("📥 Download Reports")

st.write(
    "Export the currently filtered data for "
    "further analysis or reporting."
)

col1, col2 = st.columns(2)

# ------------------------------------------
# 13.1 DOWNLOAD SALES DATA
# ------------------------------------------

with col1:

    st.subheader("Sales Report")

    sales_csv = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Sales Report",
        data=sales_csv,
        file_name="sales_report.csv",
        mime="text/csv",
        key="download_sales"
    )

# ------------------------------------------
# 13.2 DOWNLOAD EMPLOYEE DATA
# ------------------------------------------

with col2:

    st.subheader("Employee Report")

    employee_csv = filtered_employee_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Employee Report",
        data=employee_csv,
        file_name="employee_report.csv",
        mime="text/csv",
        key="download_employees"
    )

# ==========================================
# 14. AUTOMATIC BUSINESS INSIGHTS
# ==========================================

st.divider()

st.header("💡 Business Insights")

st.write(
    "Automatically generated insights based on "
    "the currently selected sales data."
)

if not filtered_df.empty:

    # ------------------------------------------
    # 14.1 TOP PRODUCT BY REVENUE
    # ------------------------------------------

    product_revenue = (
        filtered_df
        .groupby("Product")["Revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    top_product = product_revenue.index[0]

    top_product_revenue = product_revenue.iloc[0]

    # ------------------------------------------
    # 14.2 TOP DEPARTMENT BY PROFIT
    # ------------------------------------------

    department_profit = (
        filtered_df
        .groupby("Department")["Profit"]
        .sum()
        .sort_values(ascending=False)
    )

    top_department = department_profit.index[0]

    top_department_profit = department_profit.iloc[0]

    # ------------------------------------------
    # 14.3 TOP REGION BY REVENUE
    # ------------------------------------------

    region_revenue = (
        filtered_df
        .groupby("Region")["Revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    top_region = region_revenue.index[0]

    top_region_revenue = region_revenue.iloc[0]

    # ------------------------------------------
    # 14.4 DISPLAY INSIGHTS
    # ------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.success(
            f"🏆 **Top Revenue-Generating Product:** "
            f"{top_product}\n\n"
            f"Revenue: ₹{top_product_revenue:,.0f}"
        )

        st.info(
            f"🏢 **Most Profitable Department:** "
            f"{top_department}\n\n"
            f"Profit: ₹{top_department_profit:,.0f}"
        )

    with col2:

        st.success(
            f"🌍 **Top Revenue-Generating Region:** "
            f"{top_region}\n\n"
            f"Revenue: ₹{top_region_revenue:,.0f}"
        )

        st.info(
            f"📋 **Sales Transactions Analyzed:** "
            f"{len(filtered_df):,}"
        )

    # ------------------------------------------
    # 14.5 PROFIT MARGIN INTERPRETATION
    # ------------------------------------------

    if total_revenue > 0:

        st.metric(
            "Overall Profit Margin",
            f"{profit_margin:.2f}%"
        )

        if profit_margin > 20:

            st.success(
                "The current dataset has a profit "
                "margin above 20%."
            )

        elif profit_margin > 0:

            st.info(
                "The current dataset has a positive "
                "profit margin of 20% or less."
            )

        else:

            st.warning(
                "The current dataset has zero or "
                "negative profit margin."
            )

else:

    st.warning(
        "No sales records are available to generate insights. "
        "Try changing the filters."
    )
