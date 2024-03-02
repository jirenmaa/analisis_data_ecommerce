import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from babel.numbers import format_currency

# set seaborn theme
sns.set_theme(style="dark")

# set page configuration
st.set_page_config(page_title="Sales Dashboard", page_icon="📈", layout="wide")

# load data
datas = pd.read_csv("dashboard/main_data.csv")

# convert string datetime to datetime
datas["order_purchase_timestamp"] = pd.to_datetime(datas["order_purchase_timestamp"])
datas["order_delivered_customer_date"] = pd.to_datetime(
    datas["order_delivered_customer_date"]
)


def display_dashboard_kpis():
    """
    Display Key Performance Indicators (KPIs): Total sales revenue, Average order value, Number of orders
    """

    # calculate total sales revenue in USD
    total_sales_revenue = format_currency(
        datas["total_price"].sum(), "USD", locale="en_US"
    )

    # calculate average order value
    average_order_value = round(datas.groupby("order_id")["total_price"].sum().mean())

    # calculate number of orders
    number_of_orders = datas["order_id"].nunique()

    # create columns
    col_total_sales, col_avg_orders, col_total_orders = st.columns(3)

    # display total revenue
    with col_total_sales:
        st.markdown("---")
        st.subheader("Total Revenue")
        st.subheader(total_sales_revenue)
        st.markdown("---")

    # display average of orders
    with col_avg_orders:
        st.markdown("---")
        st.subheader("Average Order Value")
        st.subheader(average_order_value)
        st.markdown("---")

    # display total orders
    with col_total_orders:
        st.markdown("---")
        st.subheader("Total Orders")
        st.subheader(format(number_of_orders, ","))
        st.markdown("---")


def display_orders_per_day_latest_year():
    """
    Display the number of orders per day for the latest year using a line chart.
    """

    # get the latest year
    latest_year = datas["order_purchase_timestamp"].dt.year.max()

    # filter orders for the latest year
    latest_year_orders = datas[datas["order_purchase_timestamp"].dt.year == latest_year]

    # date range input limited to the latest year
    start_date = pd.to_datetime(f"{latest_year}-01-01")
    end_date = pd.to_datetime(f"{latest_year}-12-31")
    selected_date_range = st.date_input(
        "Select Date Range",
        value=(start_date, end_date),
        min_value=start_date,
        max_value=end_date,
    )

    # convert the order_purchase_timestamp to date type
    latest_year_orders["order_purchase_date"] = latest_year_orders[
        "order_purchase_timestamp"
    ].dt.date

    # filter orders within the selected date range
    filtered_orders = latest_year_orders[
        (latest_year_orders["order_purchase_date"] >= selected_date_range[0])
        & (latest_year_orders["order_purchase_date"] <= selected_date_range[1])
    ]

    # group orders by date and count the number of orders for each date
    orders_per_day = filtered_orders.groupby(
        filtered_orders["order_purchase_date"]
    ).size()

    # display the bar chart
    st.title(f"Number of Orders per Day in {latest_year}")
    st.bar_chart(orders_per_day, height=400)


def display_customer_demographic():
    """
    Display bar plot of user demographic by customer city.
    """

    # aggregate count of unique users by customer city
    customer_city_count = (
        datas.groupby("customer_city")["customer_unique_id"].nunique().reset_index()
    )
    customer_city_count = customer_city_count.rename(
        columns={"customer_unique_id": "total_users"}
    )

    # select top 5 cities with the highest number of users
    top_10_cities = customer_city_count.sort_values(
        by="total_users", ascending=False
    ).head(5)

    # set colors for the bar plot
    colors = ["lightgreen", "skyblue", "salmon", "gold", "orange"]

    # visualize the customer count by cities
    plt.figure(figsize=(30, 26))
    ax = sns.barplot(
        x="customer_city", y="total_users", data=top_10_cities, palette=colors
    )

    ax.set_xlabel("", fontsize=12)
    ax.set_ylabel("", fontsize=12)

    ax.tick_params(axis="x", rotation=90, labelsize=50)
    ax.tick_params(axis="y", labelsize=50)
    plt.tight_layout()

    # display the bar chart
    st.pyplot(plt.gcf())


def display_payment_distribution():
    """
    Display pie chart of the most common payment methods used by users.
    """

    # grouping by payment type and counting occurrences
    payment_counts = datas.groupby("payment_type").size().reset_index(name="counts")

    # filtering out 'not_defined' payment type
    filtered_payment_type = payment_counts[
        payment_counts["payment_type"] != "not_defined"
    ]

    # define colors for payment types
    colors = ["lightcoral", "lightskyblue", "lightpink", "lightseagreen"]

    # streamlit layout for displaying payment type icons
    _, col_l1, col_l2, col_l3, col_l4, _ = st.columns((1, 2, 2, 2, 2, 1))

    svg = (
        lambda color, label: f'<svg width="20" height="20"><rect width="20" height="20" style="fill:{color};stroke-width:3;stroke:rgb(0,0,0)" /></svg> {label}'
    )

    # display payment type icons
    with col_l1:
        st.markdown(svg("lightcoral", "credit_card"), unsafe_allow_html=True)

    with col_l2:
        st.markdown(svg("lightskyblue", "boleto"), unsafe_allow_html=True)

    with col_l3:
        st.markdown(svg("lightpink", "voucher"), unsafe_allow_html=True)

    with col_l4:
        st.markdown(svg("lightseagreen", "debit_card"), unsafe_allow_html=True)

    # plotting the pie chart
    plt.figure(figsize=(12, 8))
    plt.pie(
        x=filtered_payment_type["counts"],
        labels=filtered_payment_type["payment_type"],
        autopct="%1.1f%%",
        colors=colors,
        textprops={"fontsize": 14},
    )
    plt.title("Distribution of Payment Types", fontsize=16)
    plt.axis("equal")

    # display the pie chart
    st.pyplot(plt.gcf())


def main():
    st.title("Sales Dashboard ✨")

    display_dashboard_kpis()

    display_orders_per_day_latest_year()

    col_customer, col_payment_type = st.columns(2)

    with col_customer:
        st.subheader("Customer Demographic")
        display_customer_demographic()

    with col_payment_type:
        st.subheader("Payment Method")
        display_payment_distribution()


if __name__ == "__main__":
    main()
