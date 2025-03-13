import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import seaborn as sns
import matplotlib.pyplot as plt

sns.set(style='dark')

# Dashboard Title
st.title("E-commerce Data Analytics Dashboard")

# PNG at sidebar
st.sidebar.image("dashboard/EDA.png", caption="E-Commerce Data Analysis", use_column_width=True)

# Sidebar for file upload and date filtering
st.sidebar.header("Time-based Visualization")

# Load dataset
df = pd.read_csv("dashboard/main_data.csv")

# Convert timestamps to datetime format
df["order purchase timestamp"] = pd.to_datetime(df["order purchase timestamp"])

# Sidebar date picker for filtering
start_date = st.sidebar.date_input("Start Date", df["order purchase timestamp"].min())
end_date = st.sidebar.date_input("End Date", df["order purchase timestamp"].max())

# Convert date input to datetime format
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Name
st.sidebar.markdown("---")  # Add a horizontal line for separation
st.sidebar.markdown("### Created by:")
st.sidebar.markdown("**IHZA ZHAFRAN RAMADHAN**")
st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/ihza-zhafran-010a0b21a/)")
st.sidebar.markdown("📧 ihzazr25@gmail.com")
st.sidebar.markdown("https://github.com/zrihza/final_project_data_analysis_python")

# Filter dataset based on selected date range
df_filtered = df[(df["order purchase timestamp"] >= start_date) & (df["order purchase timestamp"] <= end_date)]

# Order Status Distribution
st.write("### Order Status Distribution")
order_status_counts = df_filtered["order status"].value_counts().reset_index()
order_status_counts.columns = ["Order Status", "Count"]
order_status_counts["Percentage"] = (order_status_counts["Count"] / order_status_counts["Count"].sum()) * 100
st.write(order_status_counts)

# Payment Type Distribution Chart
fig, ax = plt.subplots(figsize=(8, 5))
colors = sns.color_palette("plasma")

# Pie chart data
df_payment = df_filtered["payment type"].value_counts()
max_index = df_payment.idxmax()  # Ambil kategori dengan jumlah terbesar

# Explode list: top category
explode = [0.1 if index == max_index else 0 for index in df_payment.index]

# Pie Chart
wedges, texts, autotexts = ax.pie(
    df_payment, 
    labels=df_payment.index, 
    autopct="%1.1f%%", 
    startangle=140, 
    colors=colors,
    textprops={"color": "black"},  # Mengubah warna angka persen menjadi putih
    explode=explode  # Meledakkan kategori terbesar
)
ax.set_title("Payment Type Distribution", fontsize=14)
st.pyplot(fig)

# Top 10 Most Ordered Product Categories Chart
st.write("### Top 10 Most Ordered Product Categories Chart")

# Prepare data
top_product_categories = df_filtered["product category name english"].value_counts().head(10).reset_index()
top_product_categories.columns = ["Product Category", "Count"]

# Create figure and axis
fig, ax = plt.subplots(figsize=(8, 6))

# Colorful bar chart with "magma" palette
sns.barplot(x="Count", y="Product Category", data=top_product_categories, palette="magma", ax=ax)

# Add value labels on bars
for p in ax.patches:
    ax.annotate(f"{p.get_width():,.0f}", 
                (p.get_width(), p.get_y() + p.get_height() / 2), 
                ha="left", va="center", fontsize=10, color="black", xytext=(5, 0), textcoords="offset points")

# Improve styling
ax.set_xlabel("Number of Orders", fontsize=12)
ax.set_ylabel("")
ax.set_title("Top 10 Most Ordered Product Categories", fontsize=14, fontweight="bold")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Show the plot in Streamlit
st.pyplot(fig)

# Heatmap of Transactions by Customer City
st.write("### Heatmap of Transactions by Customer City")
city_data = df_filtered.groupby(["customer city", "geolocation lat customer", "geolocation lng customer"])["order id"].nunique().reset_index()
city_data.rename(columns={"order id": "transaction_count"}, inplace=True)

# Initialize map with a center in Brazil
m = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)

# Convert data to list format for heatmaps
heat_data = list(zip(city_data["geolocation lat customer"], city_data["geolocation lng customer"], city_data["transaction_count"]))

# Add heatmap to the map
HeatMap(heat_data, radius=10).add_to(m)

# Show the map in Streamlit
st_folium(m, width=700, height=500)

# Monthly Trends of Orders and Payment Value
st.write("### Monthly Trends of Orders and Payment Value")
df_filtered["year_month"] = df_filtered["order purchase timestamp"].dt.to_period("M")

# Aggregate data
monthly_orders = df_filtered.groupby("year_month")["order id"].nunique()
monthly_payment = df_filtered.groupby("year_month")["payment value"].sum()

# Plot trends
fig, ax1 = plt.subplots(figsize=(12, 6))

# Line plot for order count
color = "tab:blue"
ax1.set_xlabel("Month")
ax1.set_ylabel("Number of Orders", color=color)
order_line, = ax1.plot(monthly_orders.index.astype(str), monthly_orders, marker="o", color=color, label="Number of Orders")
ax1.tick_params(axis="y", labelcolor=color)

# Create a second y-axis for payment value
ax2 = ax1.twinx()
color = "tab:red"
ax2.set_ylabel("Total Payment Value (BRL)", color=color)
payment_line, = ax2.plot(monthly_payment.index.astype(str), monthly_payment, marker="o", color=color, label="Total Payment Value (BRL)")
ax2.tick_params(axis="y", labelcolor=color)

# Add legend
fig.legend(handles=[order_line, payment_line], loc="upper left", bbox_to_anchor=(0.1, 0.9))

# Improve layout
plt.xticks(rotation=45)
plt.grid(axis="x", linestyle="--", alpha=0.5)

# Show the plot in Streamlit
st.pyplot(fig)

# Transaction Patterns Across Different Weeks of the Month
st.write("### Transaction Patterns Across Different Weeks of the Month")

# Extract day of the month
df_filtered["day_of_month"] = df_filtered["order purchase timestamp"].dt.day

# Categorize into week groups
def categorize_week(day):
    if day <= 7:
        return "Week 1 (Day 1-7)"
    elif day <= 14:
        return "Week 2 (Day 8-14)"
    elif day <= 21:
        return "Week 3 (Day 15-21)"
    else:
        return "Week 4 (Day 22-end)"

df_filtered["week_category"] = df_filtered["day_of_month"].apply(categorize_week)

# Count unique order IDs for each week category
weekly_order_counts = df_filtered.groupby("week_category")["order id"].nunique().reset_index()
weekly_order_counts = weekly_order_counts.sort_values("week_category")  # Ensure correct order

# Plot the bar chart
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x="week_category", y="order id", data=weekly_order_counts, palette="viridis", ax=ax)

# Improve readability
ax.set_xlabel("Week of the Month")
ax.set_ylabel("Number of Unique Orders")
ax.set_title("Transaction Patterns Across Different Weeks of the Month")
plt.xticks(rotation=30)
plt.grid(axis="y", linestyle="--", alpha=0.7)

# Show the plot in Streamlit
st.pyplot(fig)

# Footer Copyright
st.markdown(
    """
    ---
    © 2025 IHZA ZHAFRAN RAMADHAN.
    """,
    unsafe_allow_html=True
)