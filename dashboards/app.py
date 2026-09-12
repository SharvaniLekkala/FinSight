"""FinSight Financial Analytics Dashboard
An interactive Streamlit dashboard built on top of PostgreSQL data warehouse and analytical marts.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import text
from src.ingestion.loader import load_db_engine

# Page Configuration
st.set_page_config(
    page_title="FinSight | Financial Intelligence",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .metric-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        margin-bottom: 12px;
    }
    .metric-label {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .metric-val {
        color: #f8fafc;
        font-size: 1.7rem;
        font-weight: 700;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #38bdf8;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_engine():
    return load_db_engine("config/db.yaml")


@st.cache_data(ttl=60)
def load_all_data():
    engine = get_engine()
    data = {}
    with engine.connect() as conn:
        try:
            data["fraud"] = pd.read_sql_table("vw_fraud_summary", con=conn)
        except Exception:
            data["fraud"] = pd.DataFrame()
            
        try:
            data["transactions"] = pd.read_sql_table("vw_transaction_summary", con=conn)
        except Exception:
            data["transactions"] = pd.DataFrame()
            
        try:
            data["credit"] = pd.read_sql_table("vw_credit_default_summary", con=conn)
        except Exception:
            data["credit"] = pd.DataFrame()
            
        try:
            data["customers"] = pd.read_sql_table("vw_customer_transactions", con=conn)
        except Exception:
            data["customers"] = pd.DataFrame()

        try:
            data["validation_log"] = pd.read_sql("SELECT * FROM validation_log ORDER BY id DESC LIMIT 50", con=conn)
        except Exception:
            data["validation_log"] = pd.DataFrame()

        try:
            data["ingestion_log"] = pd.read_sql("SELECT * FROM ingestion_log ORDER BY id DESC LIMIT 50", con=conn)
        except Exception:
            data["ingestion_log"] = pd.DataFrame()

        try:
            data["fact_sample"] = pd.read_sql("""
                SELECT f.transaction_id, f.amount, f.balance_before, f.balance_after, 
                       f.is_fraud, f.is_flagged_fraud, f.hour_of_day,
                       dc.customer_id, da.account_id, dt.transaction_type
                FROM fact_transactions f
                JOIN dim_customer dc ON dc.customer_key = f.customer_key
                JOIN dim_account da ON da.account_key = f.account_key
                JOIN dim_transaction_type dt ON dt.type_key = f.transaction_type_key
                LIMIT 5000
            """, con=conn)
        except Exception:
            data["fact_sample"] = pd.DataFrame()

    return data


def main():
    data = load_all_data()

    # Sidebar Header
    st.sidebar.markdown("## 💳 FinSight Analytics")
    st.sidebar.caption("Enterprise FinTech Intelligence Platform")
    st.sidebar.markdown("---")

    if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    menu = st.sidebar.radio(
        "Navigation",
        [
            "📊 Executive Overview",
            "💳 Transaction Analytics",
            "🛡️ Fraud Risk",
            "📉 Credit Risk",
            "👥 Customer Insights",
            "📋 Data Quality Logs",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🗄️ Database Connection")
    st.sidebar.success("Connected: `PostgreSQL @ localhost:5432/finsight`")

    # ==============================================================================
    # TAB 1: EXECUTIVE OVERVIEW
    # ==============================================================================
    if menu == "📊 Executive Overview":
        st.title("📊 Executive FinTech Overview")
        st.markdown("Real-time operational metrics across transaction flow, credit defaults, and fraud exposure.")

        txn_df = data["transactions"]
        fraud_df = data["fraud"]
        credit_df = data["credit"]
        cust_df = data["customers"]

        total_volume = txn_df["total_amount"].sum() if not txn_df.empty else 0
        total_txns = txn_df["txn_count"].sum() if not txn_df.empty else 0
        total_customers = len(cust_df) if not cust_df.empty else 0
        
        fraud_txns = fraud_df["fraud_txn_count"].sum() if not fraud_df.empty else 0
        fraud_rate = (fraud_txns / total_txns * 100) if total_txns > 0 else 0
        fraud_amount = fraud_df["fraud_total_amount"].sum() if not fraud_df.empty else 0
        
        total_credit_clients = len(credit_df) if not credit_df.empty else 0
        total_defaults = credit_df["default_count"].sum() if not credit_df.empty else 0
        default_rate = (total_defaults / total_credit_clients * 100) if total_credit_clients > 0 else 0

        # KPI Row
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Total Volume</div>
                <div class="metric-val">${total_volume:,.0f}</div>
                <div class="metric-sub">Active Payments Flow</div>
            </div>
            """, unsafe_allow_html=True)
        with k2:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Total Transactions</div>
                <div class="metric-val">{total_txns:,}</div>
                <div class="metric-sub">Processed in Warehouse</div>
            </div>
            """, unsafe_allow_html=True)
        with k3:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Total Customers</div>
                <div class="metric-val">{total_customers:,}</div>
                <div class="metric-sub">Unified Customer Dimension</div>
            </div>
            """, unsafe_allow_html=True)
        with k4:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Fraud Rate</div>
                <div class="metric-val">{fraud_rate:.2f}%</div>
                <div class="metric-sub">${fraud_amount:,.0f} Flagged Value</div>
            </div>
            """, unsafe_allow_html=True)
        with k5:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Default Rate</div>
                <div class="metric-val">{default_rate:.2f}%</div>
                <div class="metric-sub">{total_defaults:,.0f} Client Defaults</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        c1, c2 = st.columns(2)
        with c1:
            if not txn_df.empty:
                fig_pie = px.pie(
                    txn_df,
                    names="transaction_type",
                    values="total_amount",
                    title="💰 Volume Share by Payment Type",
                    hole=0.45,
                    color_discrete_sequence=px.colors.qualitative.Bold,
                )
                fig_pie.update_layout(template="plotly_dark", margin=dict(t=40, b=20, l=20, r=20))
                st.plotly_chart(fig_pie, use_container_width=True)

        with c2:
            if not credit_df.empty:
                age_summary = credit_df.groupby("age_group")[["default_count"]].sum().reset_index()
                age_total = credit_df.groupby("age_group").size().reset_index(name="total_clients")
                age_merged = pd.merge(age_summary, age_total, on="age_group")
                age_merged["default_rate"] = (age_merged["default_count"] / age_merged["total_clients"] * 100).round(2)
                
                fig_age = px.bar(
                    age_merged,
                    x="age_group",
                    y="default_rate",
                    text="default_rate",
                    title="📉 Default Rate (%) by Age Bracket",
                    color="default_rate",
                    color_continuous_scale="Reds",
                )
                fig_age.update_layout(template="plotly_dark", yaxis_title="Default Rate (%)", margin=dict(t=40, b=20, l=20, r=20))
                st.plotly_chart(fig_age, use_container_width=True)

    # ==============================================================================
    # TAB 2: TRANSACTION ANALYTICS
    # ==============================================================================
    elif menu == "💳 Transaction Analytics":
        st.title("💳 Transaction Analytics")
        st.markdown("Breakdown of transaction activity, volume metrics, and type distribution.")

        txn_df = data["transactions"]
        fact_df = data["fact_sample"]

        if not txn_df.empty:
            tc1, tc2 = st.columns([3, 2])
            with tc1:
                fig_types = px.bar(
                    txn_df,
                    x="transaction_type",
                    y="total_amount",
                    color="transaction_type",
                    title="Total Volume ($) by Transaction Type",
                    text_auto='.2s',
                    color_discrete_sequence=px.colors.qualitative.Safe,
                )
                fig_types.update_layout(template="plotly_dark", showlegend=False)
                st.plotly_chart(fig_types, use_container_width=True)

            with tc2:
                fig_avg = px.bar(
                    txn_df,
                    x="transaction_type",
                    y="avg_amount",
                    color="transaction_type",
                    title="Average Ticket Size ($)",
                    text_auto='.2s',
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                )
                fig_avg.update_layout(template="plotly_dark", showlegend=False)
                st.plotly_chart(fig_avg, use_container_width=True)

            if not fact_df.empty and "hour_of_day" in fact_df.columns:
                st.markdown("### Hourly Transaction Velocity")
                hourly = fact_df.groupby("hour_of_day")["amount"].agg(["count", "sum"]).reset_index()
                fig_hourly = px.line(
                    hourly,
                    x="hour_of_day",
                    y="count",
                    title="Transaction Velocity Throughout the Day (Hours 0-23)",
                    markers=True,
                )
                fig_hourly.update_layout(template="plotly_dark", xaxis_title="Hour of Day", yaxis_title="Number of Transactions")
                st.plotly_chart(fig_hourly, use_container_width=True)

            st.markdown("### Transaction Type Summary")
            st.dataframe(txn_df, use_container_width=True)

    # ==============================================================================
    # TAB 3: FRAUD RISK ANALYTICS
    # ==============================================================================
    elif menu == "🛡️ Fraud Risk":
        st.title("🛡️ Fraud Risk & Threat Monitoring")
        st.markdown("Identification of fraudulent patterns, high-value transfers, and unauthorized outflows.")

        fraud_df = data["fraud"]
        fact_df = data["fact_sample"]

        if not fraud_df.empty:
            fraud_count = fraud_df["fraud_txn_count"].iloc[0]
            legit_count = fraud_df["legit_txn_count"].iloc[0]
            fraud_amount = fraud_df["fraud_total_amount"].iloc[0]
            legit_amount = fraud_df["legit_total_amount"].iloc[0]
            fraud_avg = fraud_df["fraud_avg_amount"].iloc[0]
            legit_avg = fraud_df["legit_avg_amount"].iloc[0]

            f_c1, f_c2, f_c3 = st.columns(3)
            with f_c1:
                st.metric("Total Fraud Incidents", f"{fraud_count:,}", f"{(fraud_count/(fraud_count+legit_count)*100):.2f}% of txns", delta_color="inverse")
            with f_c2:
                st.metric("Total Fraud Loss Exposure", f"${fraud_amount:,.2f}", delta_color="inverse")
            with f_c3:
                st.metric("Avg Fraud Ticket Size", f"${fraud_avg:,.2f}", f"vs ${legit_avg:,.2f} legit", delta_color="off")

            st.markdown("---")

            if not fact_df.empty:
                fc_col1, fc_col2 = st.columns(2)
                with fc_col1:
                    fig_fraud_pie = px.pie(
                        names=["Legitimate", "Fraudulent"],
                        values=[legit_count, fraud_count],
                        title="Transaction Legitimacy Ratio",
                        color_discrete_sequence=["#10b981", "#ef4444"],
                        hole=0.4,
                    )
                    fig_fraud_pie.update_layout(template="plotly_dark")
                    st.plotly_chart(fig_fraud_pie, use_container_width=True)

                with fc_col2:
                    fraud_by_type = fact_df.groupby(["transaction_type", "is_fraud"])["amount"].count().reset_index(name="count")
                    fig_fbt = px.bar(
                        fraud_by_type,
                        x="transaction_type",
                        y="count",
                        color="is_fraud",
                        barmode="group",
                        title="Transaction Types vs Fraud Incidence",
                        color_discrete_map={False: "#3b82f6", True: "#ef4444", 0: "#3b82f6", 1: "#ef4444"},
                    )
                    fig_fbt.update_layout(template="plotly_dark")
                    st.plotly_chart(fig_fbt, use_container_width=True)

                st.markdown("### High-Risk / Flagged Transactions")
                flagged = fact_df[fact_df["is_fraud"] == 1]
                if not flagged.empty:
                    st.dataframe(flagged.head(100), use_container_width=True)
                else:
                    st.info("No active fraud flags in this sample.")

    # ==============================================================================
    # TAB 4: CREDIT RISK ANALYTICS
    # ==============================================================================
    elif menu == "📉 Credit Risk":
        st.title("📉 Credit Risk & Default Probability")
        st.markdown("Assessment of default risk across demographic, marital status, and educational cohorts.")

        credit_df = data["credit"]

        if not credit_df.empty:
            total_clients = len(credit_df)
            total_defaults = credit_df["default_count"].sum()
            overall_default_rate = (total_defaults / total_clients * 100) if total_clients > 0 else 0

            cr1, cr2, cr3 = st.columns(3)
            with cr1:
                st.metric("Total Credit Portfolio Clients", f"{total_clients:,}")
            with cr2:
                st.metric("Total Default Count", f"{total_defaults:,.0f}")
            with cr3:
                st.metric("Overall Default Rate", f"{overall_default_rate:.2f}%")

            st.markdown("---")

            cr_col1, cr_col2 = st.columns(2)
            with cr_col1:
                edu_summary = credit_df.groupby("education")[["default_count"]].sum().reset_index()
                edu_total = credit_df.groupby("education").size().reset_index(name="total")
                edu_merged = pd.merge(edu_summary, edu_total, on="education")
                edu_merged["default_rate"] = (edu_merged["default_count"] / edu_merged["total"] * 100).round(2)
                
                fig_edu = px.bar(
                    edu_merged,
                    x="education",
                    y="default_rate",
                    title="Default Rate (%) by Education Level",
                    color="default_rate",
                    color_continuous_scale="Viridis",
                    text="default_rate"
                )
                fig_edu.update_layout(template="plotly_dark")
                st.plotly_chart(fig_edu, use_container_width=True)

            with cr_col2:
                mrg_summary = credit_df.groupby("marriage")[["default_count"]].sum().reset_index()
                mrg_total = credit_df.groupby("marriage").size().reset_index(name="total")
                mrg_merged = pd.merge(mrg_summary, mrg_total, on="marriage")
                mrg_merged["default_rate"] = (mrg_merged["default_count"] / mrg_merged["total"] * 100).round(2)

                fig_mrg = px.bar(
                    mrg_merged,
                    x="marriage",
                    y="default_rate",
                    title="Default Rate (%) by Marital Status",
                    color="default_rate",
                    color_continuous_scale="Purples",
                    text="default_rate"
                )
                fig_mrg.update_layout(template="plotly_dark")
                st.plotly_chart(fig_mrg, use_container_width=True)

            st.markdown("### Detailed Credit Risk Client Records")
            st.dataframe(credit_df.head(200), use_container_width=True)

    # ==============================================================================
    # TAB 5: CUSTOMER INSIGHTS
    # ==============================================================================
    elif menu == "👥 Customer Insights":
        st.title("👥 Customer Activity & Profiles")
        st.markdown("Customer spending distribution, activity frequencies, and transaction counts.")

        cust_df = data["customers"]
        if not cust_df.empty:
            top_spenders = cust_df.sort_values(by="total_amount", ascending=False).head(20)
            
            st.markdown("### Top 20 Customers by Spending Volume")
            fig_cust = px.bar(
                top_spenders,
                x="customer_id",
                y="total_amount",
                color="total_amount",
                title="Top 20 Customers by Total Transaction Amount ($)",
                color_continuous_scale="Plasma",
            )
            fig_cust.update_layout(template="plotly_dark")
            st.plotly_chart(fig_cust, use_container_width=True)

            st.markdown("### Customer Transactions Summary")
            st.dataframe(cust_df.head(200), use_container_width=True)

    # ==============================================================================
    # TAB 6: DATA QUALITY LOGS
    # ==============================================================================
    elif menu == "📋 Data Quality Logs":
        st.title("📋 Data Quality & Ingestion Logs")
        st.markdown("Live audit trail of data validation rules, integrity tests, and dataset ingestion records.")

        log_c1, log_c2 = st.columns(2)
        with log_c1:
            st.subheader("Data Quality Validation Log (`validation_log`)")
            vlog = data["validation_log"]
            if not vlog.empty:
                st.dataframe(vlog, use_container_width=True)
            else:
                st.info("No validation logs recorded yet.")

        with log_c2:
            st.subheader("Ingestion Audit Log (`ingestion_log`)")
            ilog = data["ingestion_log"]
            if not ilog.empty:
                st.dataframe(ilog, use_container_width=True)
            else:
                st.info("No ingestion logs recorded yet.")


if __name__ == "__main__":
    main()
