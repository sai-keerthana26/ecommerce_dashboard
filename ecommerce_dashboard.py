# ecommerce_dashboard_safe_search.py

import pandas as pd
import streamlit as st
import plotly.express as px
import calendar

# -----------------------------
# Load Dataset
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv', encoding='latin1')  # fix utf-8 issues
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['Revenue'] = df['Quantity'] * df['UnitPrice']
    df['Month'] = df['InvoiceDate'].dt.month
    df['Year'] = df['InvoiceDate'].dt.year
    return df

data = load_data()

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Filters")
countries = st.sidebar.multiselect("Select Country(s)", options=data['Country'].unique(), default=data['Country'].unique())
start_date, end_date = st.sidebar.date_input("Select Date Range", [data['InvoiceDate'].min(), data['InvoiceDate'].max()])

filtered_data = data[
    (data['Country'].isin(countries)) &
    (data['InvoiceDate'] >= pd.to_datetime(start_date)) &
    (data['InvoiceDate'] <= pd.to_datetime(end_date))
]

# -----------------------------
# Dashboard Title
# -----------------------------
st.title("E-commerce Analytics Dashboard")
st.markdown("Interactive dashboard with KPIs, trends, and safe search functionality.")

# -----------------------------
# KPI Cards
# -----------------------------
st.subheader("Key Metrics")
total_revenue = filtered_data['Revenue'].sum()
total_orders = filtered_data['InvoiceNo'].nunique()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
unique_customers = filtered_data['CustomerID'].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
col2.metric("📦 Total Orders", f"{total_orders}")
col3.metric("🛒 Avg Order Value", f"${avg_order_value:,.2f}")
col4.metric("👤 Unique Customers", f"{unique_customers}")

# -----------------------------
# Tabs for Sections
# -----------------------------
tab1, tab2, tab3 = st.tabs(["Overview", "Products", "Customers"])

# -----------------------------
# Overview Tab
# -----------------------------
with tab1:
    st.subheader("Monthly Revenue Trend")
    monthly_revenue = filtered_data.groupby(['Year', 'Month'])['Revenue'].sum().reset_index()
    monthly_revenue['MonthName'] = monthly_revenue['Month'].apply(lambda x: calendar.month_abbr[x])
    fig = px.line(monthly_revenue, x='MonthName', y='Revenue', color='Year', markers=True, title="Monthly Revenue Trend")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Revenue by Country")
    country_revenue = filtered_data.groupby('Country')['Revenue'].sum().reset_index()
    fig2 = px.bar(country_revenue, x='Country', y='Revenue', color='Revenue', title="Revenue by Country")
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# Products Tab
# -----------------------------
with tab2:
    st.subheader("Top 10 Products by Revenue")
    top_products = filtered_data.groupby('Description')['Revenue'].sum().sort_values(ascending=False).head(10).reset_index()
    fig3 = px.bar(top_products, x='Revenue', y='Description', orientation='h', color='Revenue', title="Top 10 Products")
    st.plotly_chart(fig3, use_container_width=True)

    # -----------------------------
    # Safe Search
    # -----------------------------
    st.subheader("Search Product / Company")
    search_product = st.text_input("Enter product name to search")
    if search_product:
        results = filtered_data[filtered_data['Description'].str.contains(search_product, case=False, na=False)]
        if results.empty:
            st.warning("No matching product found.")
        else:
            st.dataframe(results)

# -----------------------------
# Customers Tab
# -----------------------------
with tab3:
    st.subheader("Top 10 Customers by Revenue")
    top_customers = filtered_data.groupby('CustomerID')['Revenue'].sum().sort_values(ascending=False).head(10).reset_index()
    fig4 = px.bar(top_customers, x='Revenue', y='CustomerID', orientation='h', color='Revenue', title="Top 10 Customers")
    st.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# Download Filtered Data
# -----------------------------
st.markdown("---")
st.download_button(
    label="Download Filtered Data as CSV",
    data=filtered_data.to_csv(index=False),
    file_name='filtered_data.csv',
    mime='text/csv'
)
