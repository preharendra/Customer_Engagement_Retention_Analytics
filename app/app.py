import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Customer Engagement & Retention Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# DATA LOADING
# =========================================================

@st.cache_data
def load_data():
    """
    Load the final analytics dataset.
    """

    file_paths = [
        "data/European_Bank_Final_Analytics_Dataset.csv",
        "European_Bank_Final_Analytics_Dataset.csv",
        "data/European_Bank(2).csv",
        "European_Bank(2).csv"
    ]

    for path in file_paths:

        try:
            data = pd.read_csv(path)

            return data

        except FileNotFoundError:
            continue

    raise FileNotFoundError(
        "No banking dataset was found. "
        "Place European_Bank_Final_Analytics_Dataset.csv "
        "inside the data folder."
    )


df = load_data()


# =========================================================
# PAGE TITLE
# =========================================================

st.title("🏦 Customer Engagement & Retention Analytics")

st.markdown(
    """
    **Behavioral Segmentation, Product Utilization, Relationship Strength 
    & High-Value Customer Risk Analysis**
    """
)

st.divider()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("Dashboard Navigation")

page = st.sidebar.radio(
    "Select Module",
    [
        "Executive Overview",
        "Engagement Analytics",
        "Product Utilization",
        "High-Value Customer Detector",
        "Retention Strength & Risk"
    ]
)


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.divider()

st.sidebar.subheader("Customer Filters")


# Geography
if "Geography" in df.columns:

    geography_options = sorted(
        df["Geography"].dropna().unique().tolist()
    )

    selected_geography = st.sidebar.multiselect(
        "Geography",
        geography_options,
        default=geography_options
    )

else:
    selected_geography = []


# Gender
if "Gender" in df.columns:

    gender_options = sorted(
        df["Gender"].dropna().unique().tolist()
    )

    selected_gender = st.sidebar.multiselect(
        "Gender",
        gender_options,
        default=gender_options
    )

else:
    selected_gender = []


# Engagement
if "Engagement_Status" in df.columns:

    engagement_options = sorted(
        df["Engagement_Status"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_engagement = st.sidebar.multiselect(
        "Engagement Status",
        engagement_options,
        default=engagement_options
    )

else:
    selected_engagement = []


# Product count
if "NumOfProducts" in df.columns:

    product_min = int(df["NumOfProducts"].min())
    product_max = int(df["NumOfProducts"].max())

    selected_products = st.sidebar.slider(
        "Number of Products",
        min_value=product_min,
        max_value=product_max,
        value=(product_min, product_max)
    )

else:
    selected_products = None


# Balance threshold
if "Balance" in df.columns:

    balance_min = float(df["Balance"].min())
    balance_max = float(df["Balance"].max())

    selected_balance = st.sidebar.slider(
        "Balance Range",
        min_value=balance_min,
        max_value=balance_max,
        value=(balance_min, balance_max)
    )

else:
    selected_balance = None


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()


if "Geography" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["Geography"].isin(
            selected_geography
        )
    ]


if "Gender" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["Gender"].isin(
            selected_gender
        )
    ]


if "Engagement_Status" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["Engagement_Status"].isin(
            selected_engagement
        )
    ]


if "NumOfProducts" in filtered_df.columns:

    filtered_df = filtered_df[
        filtered_df["NumOfProducts"].between(
            selected_products[0],
            selected_products[1]
        )
    ]


if "Balance" in filtered_df.columns:

    filtered_df = filtered_df[
        filtered_df["Balance"].between(
            selected_balance[0],
            selected_balance[1]
        )
    ]


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def calculate_churn(data):
    """
    Return churn percentage.
    """

    if len(data) == 0:
        return 0

    return data["Exited"].mean() * 100


def format_percentage(value):
    return f"{value:.2f}%"


# =========================================================
# PAGE 1 — EXECUTIVE OVERVIEW
# =========================================================

if page == "Executive Overview":

    st.header("Executive Overview")

    st.caption(
        "High-level view of customer retention, engagement and relationship risk."
    )

    total_customers = len(filtered_df)

    churn_rate = calculate_churn(filtered_df)

    active_rate = (
        filtered_df["IsActiveMember"].mean() * 100
        if len(filtered_df) > 0
        else 0
    )

    avg_products = (
        filtered_df["NumOfProducts"].mean()
        if len(filtered_df) > 0
        else 0
    )

    high_value_disengaged = (
        filtered_df["High_Value_Disengaged"].sum()
        if "High_Value_Disengaged" in filtered_df.columns
        else 0
    )


    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Customers",
        f"{total_customers:,}"
    )

    col2.metric(
        "Churn Rate",
        format_percentage(churn_rate)
    )

    col3.metric(
        "Active Rate",
        format_percentage(active_rate)
    )

    col4.metric(
        "Avg. Products",
        f"{avg_products:.2f}"
    )

    col5.metric(
        "High-Value Disengaged",
        f"{high_value_disengaged:,}"
    )


    st.divider()


    # -------------------------------
    # Churn by engagement
    # -------------------------------

    engagement_summary = (
        filtered_df
        .groupby("Engagement_Status")
        .agg(
            Customers=("CustomerId", "count"),
            Churn_Rate=("Exited", "mean")
        )
        .reset_index()
    )

    engagement_summary["Churn_Rate"] *= 100


    col1, col2 = st.columns(2)


    with col1:

        fig = px.bar(
            engagement_summary,
            x="Engagement_Status",
            y="Churn_Rate",
            title="Churn Rate by Engagement Status",
            text_auto=".1f"
        )

        fig.update_yaxes(
            title="Churn Rate (%)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # -------------------------------
    # Churn by product count
    # -------------------------------

    with col2:

        product_summary = (
            filtered_df
            .groupby("NumOfProducts")
            .agg(
                Customers=("CustomerId", "count"),
                Churn_Rate=("Exited", "mean")
            )
            .reset_index()
        )

        product_summary["Churn_Rate"] *= 100

        fig = px.bar(
            product_summary,
            x="NumOfProducts",
            y="Churn_Rate",
            title="Churn Rate by Number of Products",
            text_auto=".1f"
        )

        fig.update_yaxes(
            title="Churn Rate (%)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # -------------------------------
    # Executive message
    # -------------------------------

    st.subheader("Executive Interpretation")

    st.info(
        """
        Customer retention should be managed through behavioral and 
        relationship signals rather than financial value alone. 
        Inactive customers, single-product relationships, and financially 
        valuable but disengaged customers represent important intervention 
        opportunities.
        """
    )


# =========================================================
# PAGE 2 — ENGAGEMENT ANALYTICS
# =========================================================

elif page == "Engagement Analytics":

    st.header("Engagement Analytics")

    st.caption(
        "Analyze how customer activity and engagement relate to churn."
    )


    # Engagement profile
    profile_summary = (
        filtered_df
        .groupby("Final_Engagement_Segment")
        .agg(
            Customers=("CustomerId", "count"),
            Churned=("Exited", "sum"),
            Churn_Rate=("Exited", "mean"),
            Avg_Balance=("Balance", "mean"),
            Avg_Products=("NumOfProducts", "mean")
        )
        .reset_index()
    )

    profile_summary["Churn_Rate"] *= 100


    st.subheader("Engagement Segment Performance")

    st.dataframe(
        profile_summary.style.format(
            {
                "Churn_Rate": "{:.2f}%",
                "Avg_Balance": "{:,.2f}",
                "Avg_Products": "{:.2f}"
            }
        ),
        use_container_width=True
    )


    # Churn by engagement profile
    fig = px.bar(
        profile_summary.sort_values(
            "Churn_Rate",
            ascending=False
        ),
        x="Final_Engagement_Segment",
        y="Churn_Rate",
        title="Churn Rate by Engagement Segment",
        text_auto=".1f"
    )

    fig.update_yaxes(
        title="Churn Rate (%)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # -------------------------------
    # Engagement × Product heatmap
    # -------------------------------

    st.subheader(
        "Engagement × Product Depth"
    )

    engagement_product = (
        filtered_df
        .groupby(
            [
                "Engagement_Status",
                "Product_Depth_Group"
            ]
        )["Exited"]
        .mean()
        .mul(100)
        .reset_index()
    )

    engagement_product_pivot = (
        engagement_product
        .pivot(
            index="Engagement_Status",
            columns="Product_Depth_Group",
            values="Exited"
        )
    )


    fig = px.imshow(
        engagement_product_pivot,
        text_auto=".1f",
        aspect="auto",
        title="Churn Rate: Engagement × Product Depth",
        labels={
            "color": "Churn Rate (%)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # -------------------------------
    # Customer-level segment table
    # -------------------------------

    st.subheader(
        "Filtered Customer Segments"
    )

    segment_columns = [
        "CustomerId",
        "Geography",
        "Age",
        "Balance",
        "NumOfProducts",
        "IsActiveMember",
        "Exited",
        "Final_Engagement_Segment"
    ]

    available_columns = [
        col for col in segment_columns
        if col in filtered_df.columns
    ]

    st.dataframe(
        filtered_df[available_columns].head(500),
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# PAGE 3 — PRODUCT UTILIZATION
# =========================================================

elif page == "Product Utilization":

    st.header("Product Utilization")

    st.caption(
        "Evaluate relationship depth and product usage patterns."
    )


    product_analysis = (
        filtered_df
        .groupby("NumOfProducts")
        .agg(
            Customers=("CustomerId", "count"),
            Churned=("Exited", "sum"),
            Churn_Rate=("Exited", "mean"),
            Avg_Balance=("Balance", "mean"),
            Active_Rate=("IsActiveMember", "mean")
        )
        .reset_index()
    )

    product_analysis["Churn_Rate"] *= 100
    product_analysis["Active_Rate"] *= 100


    st.subheader(
        "Product Utilization Summary"
    )

    st.dataframe(
        product_analysis.style.format(
            {
                "Churn_Rate": "{:.2f}%",
                "Avg_Balance": "{:,.2f}",
                "Active_Rate": "{:.2f}%"
            }
        ),
        use_container_width=True
    )


    col1, col2 = st.columns(2)


    with col1:

        fig = px.bar(
            product_analysis,
            x="NumOfProducts",
            y="Churn_Rate",
            title="Churn Rate by Product Count",
            text_auto=".1f"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        fig = px.bar(
            product_analysis,
            x="NumOfProducts",
            y="Customers",
            title="Customer Distribution by Product Count",
            text_auto=True
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # -------------------------------
    # Product + engagement matrix
    # -------------------------------

    st.subheader(
        "Product Depth × Engagement"
    )

    matrix = (
        filtered_df
        .groupby(
            [
                "Engagement_Status",
                "Product_Depth_Group"
            ]
        )
        .agg(
            Customers=("CustomerId", "count"),
            Churn_Rate=("Exited", "mean")
        )
        .reset_index()
    )

    matrix["Churn_Rate"] *= 100

    st.dataframe(
        matrix.style.format(
            {
                "Churn_Rate": "{:.2f}%"
            }
        ),
        use_container_width=True
    )


    # -------------------------------
    # 3+ product diagnostic
    # -------------------------------

    st.subheader(
        "3+ Product Diagnostic"
    )

    complex_customers = filtered_df[
        filtered_df["NumOfProducts"] >= 3
    ]

    if len(complex_customers) > 0:

        complex_metrics = pd.DataFrame(
            {
                "Metric": [
                    "Customers",
                    "Churn Rate",
                    "Inactive Rate",
                    "Average Balance"
                ],
                "Value": [
                    len(complex_customers),
                    complex_customers["Exited"].mean() * 100,
                    (
                        complex_customers["IsActiveMember"] == 0
                    ).mean() * 100,
                    complex_customers["Balance"].mean()
                ]
            }
        )

        st.dataframe(
            complex_metrics.style.format(
                {
                    "Value": "{:.2f}"
                }
            ),
            use_container_width=True
        )

        st.warning(
            """
            The dataset shows unusually high observed churn among customers 
            with 3+ products. Treat this as a diagnostic signal, not proof 
            that having more products causes churn. Customer counts and 
            underlying product combinations should be investigated.
            """
        )

    else:

        st.info(
            "No 3+ product customers match the current filters."
        )


# =========================================================
# PAGE 4 — HIGH-VALUE CUSTOMER DETECTOR
# =========================================================

elif page == "High-Value Customer Detector":

    st.header(
        "High-Value Customer Detector"
    )

    st.caption(
        "Identify financially valuable customers whose engagement may be weakening."
    )


    # ---------------------------------
    # High-value filter
    # ---------------------------------

    balance_threshold = st.number_input(
        "Minimum Balance Threshold",
        min_value=0.0,
        max_value=float(
            filtered_df["Balance"].max()
        ),
        value=float(
            filtered_df["Balance"].quantile(0.75)
        )
    )


    premium_df = filtered_df[
        (
            filtered_df["Balance"]
            >= balance_threshold
        )
        &
        (
            filtered_df["IsActiveMember"] == 0
        )
    ].copy()


    # ---------------------------------
    # Metrics
    # ---------------------------------

    premium_count = len(premium_df)

    premium_churn = (
        premium_df["Exited"].mean() * 100
        if premium_count > 0
        else 0
    )

    average_balance = (
        premium_df["Balance"].mean()
        if premium_count > 0
        else 0
    )

    average_products = (
        premium_df["NumOfProducts"].mean()
        if premium_count > 0
        else 0
    )


    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "At-Risk Premium Customers",
        f"{premium_count:,}"
    )

    col2.metric(
        "Observed Churn",
        f"{premium_churn:.2f}%"
    )

    col3.metric(
        "Average Balance",
        f"{average_balance:,.0f}"
    )

    col4.metric(
        "Average Products",
        f"{average_products:.2f}"
    )


    st.divider()


    # ---------------------------------
    # Risk distribution
    # ---------------------------------

    if len(premium_df) > 0:

        risk_distribution = (
            premium_df
            .groupby("Premium_Risk_Band")
            .size()
            .reset_index(
                name="Customers"
            )
        )

        fig = px.bar(
            risk_distribution,
            x="Premium_Risk_Band",
            y="Customers",
            title="Premium Customer Risk Distribution",
            text_auto=True
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # ---------------------------------
    # Watchlist
    # ---------------------------------

    st.subheader(
        "Premium Customer Watchlist"
    )

    watchlist_columns = [
        "CustomerId",
        "Surname",
        "Geography",
        "Age",
        "Balance",
        "EstimatedSalary",
        "NumOfProducts",
        "HasCrCard",
        "IsActiveMember",
        "Exited",
        "Premium_Risk_Score",
        "Premium_Risk_Band"
    ]

    available_watchlist = [
        col for col in watchlist_columns
        if col in premium_df.columns
    ]

    watchlist = premium_df[
        available_watchlist
    ].sort_values(
        "Balance",
        ascending=False
    )

    st.dataframe(
        watchlist.head(500),
        use_container_width=True,
        hide_index=True
    )


    # ---------------------------------
    # Download button
    # ---------------------------------

    csv_data = watchlist.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Premium Customer Watchlist",
        data=csv_data,
        file_name="Premium_Customer_Watchlist.csv",
        mime="text/csv"
    )


# =========================================================
# PAGE 5 — RETENTION STRENGTH & RISK
# =========================================================

elif page == "Retention Strength & Risk":

    st.header(
        "Retention Strength & Risk"
    )

    st.caption(
        "Customer-level relationship strength and retention prioritization."
    )


    # ---------------------------------
    # RSI summary
    # ---------------------------------

    rsi_summary = (
        filtered_df
        .groupby("Relationship_Strength_Band")
        .agg(
            Customers=("CustomerId", "count"),
            Churned=("Exited", "sum"),
            Churn_Rate=("Exited", "mean"),
            Average_RSI=(
                "Relationship_Strength_Index",
                "mean"
            )
        )
        .reset_index()
    )

    rsi_summary["Churn_Rate"] *= 100


    col1, col2 = st.columns(2)


    with col1:

        fig = px.bar(
            rsi_summary,
            x="Relationship_Strength_Band",
            y="Churn_Rate",
            title="Churn Rate by Relationship Strength",
            text_auto=".1f"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        fig = px.bar(
            filtered_df,
            x="Retention_Risk_Band",
            title="Customer Distribution by Retention Risk",
        )

        fig.update_layout(
            yaxis_title="Customers"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # ---------------------------------
    # Risk summary
    # ---------------------------------

    st.subheader(
        "Retention Risk Summary"
    )

    risk_summary = (
        filtered_df
        .groupby("Retention_Risk_Band")
        .agg(
            Customers=("CustomerId", "count"),
            Churned=("Exited", "sum"),
            Actual_Churn_Rate=("Exited", "mean"),
            Average_Risk=(
                "Retention_Risk_Score_Adjusted",
                "mean"
            ),
            Average_RSI=(
                "Relationship_Strength_Index",
                "mean"
            )
        )
        .reset_index()
    )

    risk_summary["Actual_Churn_Rate"] *= 100

    st.dataframe(
        risk_summary.style.format(
            {
                "Actual_Churn_Rate": "{:.2f}%",
                "Average_Risk": "{:.2f}",
                "Average_RSI": "{:.2f}"
            }
        ),
        use_container_width=True
    )


    # ---------------------------------
    # Customer risk scorecard
    # ---------------------------------

    st.subheader(
        "Customer Retention Scorecard"
    )

    scorecard_columns = [
        "CustomerId",
        "Geography",
        "Balance",
        "NumOfProducts",
        "IsActiveMember",
        "Relationship_Strength_Index",
        "Relationship_Strength_Band",
        "Retention_Risk_Score_Adjusted",
        "Retention_Risk_Band",
        "Relationship_Classification",
        "Retention_Strategy",
        "Exited"
    ]

    available_scorecard = [
        col for col in scorecard_columns
        if col in filtered_df.columns
    ]

    scorecard = filtered_df[
        available_scorecard
    ].sort_values(
        "Retention_Risk_Score_Adjusted",
        ascending=False
    )

    st.dataframe(
        scorecard.head(500),
        use_container_width=True,
        hide_index=True
    )


    # ---------------------------------
    # Download scorecard
    # ---------------------------------

    scorecard_csv = scorecard.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Retention Scorecard",
        data=scorecard_csv,
        file_name="Customer_Retention_Scorecard.csv",
        mime="text/csv"
    )
    st.sidebar.divider()

st.sidebar.caption(
    "Customer Engagement & Product Utilization Analytics"
)

st.sidebar.caption(
    "MBA Business Analytics Project"
)