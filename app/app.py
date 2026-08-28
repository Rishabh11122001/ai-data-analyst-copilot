import streamlit as st

from analyzer import analyze_question


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Data Analyst Copilot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.title("📊 AI Analyst")
    st.caption(
        "Natural Language → SQL → PostgreSQL → "
        "Visualization → Business Insights"
    )

    st.divider()

    st.subheader("🗄️ Data Source")
    st.success("● Cloud PostgreSQL Connected")
    st.write("**Platform:** Supabase PostgreSQL")
    st.write("**Schema:** `analytics`")
    st.write("**Access:** 🔒 Read Only")

    st.divider()

    st.subheader("⚡ Capabilities")
    st.write("✓ Natural Language to SQL")
    st.write("✓ Schema-Aware Query Generation")
    st.write("✓ Business Semantic Layer")
    st.write("✓ SQL Safety Validation")
    st.write("✓ Automated Data Analysis")
    st.write("✓ Dynamic Visualizations")
    st.write("✓ Grounded AI Business Insights")
    st.write("✓ Multi-Provider LLM Fallback")

    st.divider()

    st.caption(
        "Built with Python, PostgreSQL, Gemini, Groq, "
        "Supabase, Pandas, Plotly & Streamlit"
    )


# =========================================================
# COMPACT PROJECT OVERVIEW
# =========================================================

st.title("📊 AI-Powered Data Analyst Copilot")

st.markdown(
    """
Ask business questions in **plain English** and get **safe SQL, live data,
automatic visualizations and grounded AI insights** from a cloud PostgreSQL warehouse.
"""
)

# Quick dataset snapshot
metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("Orders", "99,441")
metric2.metric("Customers", "96,096")
metric3.metric("Products", "32,951")
metric4.metric("Sellers", "3,095")

left, right = st.columns(2)

with left:
    st.markdown("### 💼 Why this project?")
    st.write(
        "Business users often need quick answers from data but may not know SQL. "
        "This Copilot turns natural-language questions into validated analytical queries."
    )

with right:
    st.markdown("### ⚡ Business Value")
    st.markdown(
        """
- **Self-service analytics** without SQL knowledge
- **Faster exploration** with automatic charts and insights
- **Controlled access** through safe, read-only query execution
"""
    )

st.info(
    "🔒 Read-only database access • Destructive SQL commands are blocked"
)

with st.expander("ℹ️ About the data & how it works"):
    st.markdown(
        """
**Dataset:** Brazilian Olist E-commerce data (2016–2018), transformed into a PostgreSQL analytical warehouse.

The model contains customer, product, seller and date dimensions plus order, order-item, payment and review facts.

**Workflow:** `Business Question → AI → Safe SQL → PostgreSQL → Data → Chart → Insight`

A semantic layer keeps key business metrics consistent, while a dedicated read-only database role protects the source data.
"""
    )

st.divider()


# =========================================================
# ASK THE DATA
# =========================================================

st.markdown("## 💬 Ask the Data")
st.write(
    "Choose an example business question or write your own. "
    "The Copilot will generate and validate SQL before querying the database."
)

suggested_questions = [
    "What are the top 5 product categories by merchandise sales?",
    "What are the top 5 customer states by merchandise sales?",
    "Which customer states have the highest late delivery rate?",
    "How does customer review score differ between late and on-time deliveries?",
    "What are the most commonly used payment methods and their total payment value?",
    "How have merchandise sales changed month by month?",
    (
        "How many unique customers made repeat purchases, and what percentage "
        "of customers were repeat customers?"
    ),
    (
        "Which sellers generate the highest merchandise sales and how many "
        "orders do they handle?"
    ),
]

selected_question = st.selectbox(
    "Choose an example or write your own question below:",
    ["Write my own question"] + suggested_questions,
)

default_question = (
    selected_question if selected_question != "Write my own question" else ""
)

question = st.text_area(
    "Ask your business question",
    value=default_question,
    placeholder="Example: Which product categories generated the highest merchandise sales?",
    height=90,
)

analyze_button = st.button(
    "🚀 Analyze Data",
    type="primary",
    use_container_width=True,
)


# =========================================================
# ANALYSIS
# =========================================================

if analyze_button:
    if not question.strip():
        st.warning("Please enter a business question before running the analysis.")

    else:
        try:
            with st.spinner(
                "Understanding the question, generating SQL, querying "
                "PostgreSQL and analysing results..."
            ):
                analysis = analyze_question(question.strip())

            if not analysis["success"]:
                if analysis["stage"] == "security_block":
                    st.error("🔒 Unsafe Request Blocked")
                    st.warning(
                        "This AI Data Analyst Copilot only executes read-only analytics queries."
                    )
                    st.info(
                        "Database modification commands such as DELETE, UPDATE, INSERT, "
                        "DROP, ALTER, TRUNCATE and CREATE are not permitted."
                    )
                    st.markdown(
                        "**Try a read-only question instead:** "
                        "`How many customer records are currently in the database?`"
                    )

                    if analysis.get("sql"):
                        with st.expander("View Blocked AI Output"):
                            st.code(analysis["sql"], language="text")

                    st.stop()

                elif analysis["stage"] == "sql_generation":
                    st.warning("⚠️ AI service temporarily unavailable")
                    st.error(analysis["error"])
                    st.info(
                        "The PostgreSQL database may still be available, but all "
                        "configured AI providers are currently unavailable or have "
                        "reached their usage limits."
                    )
                    st.stop()

                elif analysis["stage"] == "query_execution":
                    st.error("⚠️ Query execution failed")
                    st.warning(analysis["error"])

                    if analysis.get("sql"):
                        with st.expander("View Generated SQL"):
                            st.code(analysis["sql"], language="sql")

                    st.stop()

                else:
                    st.error("The analysis could not be completed.")
                    st.warning(analysis.get("error") or "Unknown analysis error.")
                    st.stop()

            st.success("✅ Analysis completed successfully")
            result = analysis["result"]

            summary1, summary2, summary3 = st.columns(3)
            summary1.metric("Rows Returned", f"{len(result):,}")
            summary2.metric("Columns", len(result.columns))
            summary3.metric(
                "Visualization",
                "Available" if analysis["figure"] is not None else "Not Required",
            )

            insight_tab, chart_tab, data_tab, sql_tab = st.tabs(
                [
                    "🤖 AI Insights",
                    "📈 Visualization",
                    "📋 Data",
                    "🧠 Generated SQL",
                ]
            )

            with insight_tab:
                st.subheader("AI Business Insights")

                if analysis.get("insight"):
                    formatted_insight = analysis["insight"].replace("R$", "R\\$")
                    st.markdown(formatted_insight)
                else:
                    st.info("AI insights are not available for this analysis.")

            with chart_tab:
                st.subheader("Automated Visualization")

                if analysis["figure"] is not None:
                    st.plotly_chart(
                        analysis["figure"],
                        use_container_width=True,
                    )
                else:
                    st.info("The returned data does not require a visualization.")

            with data_tab:
                st.subheader("Query Result")

                if result.empty:
                    st.info("The SQL query returned no rows.")
                else:
                    st.dataframe(
                        result,
                        use_container_width=True,
                        hide_index=True,
                    )

                    csv_data = result.to_csv(index=False).encode("utf-8")

                    st.download_button(
                        label="⬇️ Download Result as CSV",
                        data=csv_data,
                        file_name="ai_analyst_result.csv",
                        mime="text/csv",
                    )

            with sql_tab:
                st.subheader("Generated PostgreSQL Query")

                if analysis.get("sql"):
                    st.code(analysis["sql"], language="sql")
                    st.caption(
                        "The SQL query is validated before execution and runs "
                        "through a dedicated read-only PostgreSQL account."
                    )
                else:
                    st.info("No SQL query is available.")

        except Exception as exc:
            st.error("An unexpected application error occurred.")

            with st.expander("Technical details"):
                st.exception(exc)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "AI Data Analyst Copilot • Natural Language → Safe SQL → "
    "Cloud PostgreSQL → Visualization → Grounded Business Insights"
)
