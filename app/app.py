import streamlit as st

from analyzer import analyze_question


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Data Analyst Copilot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
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


    # -----------------------------------------------------
    # DATA SOURCE
    # -----------------------------------------------------

    st.subheader("Data Source")

    st.success(
        "● PostgreSQL Connected"
    )

    st.write(
        "**Database:** `ecommerce_analytics`"
    )

    st.write(
        "**Schema:** `analytics`"
    )

    st.write(
        "**Access:** 🔒 Read Only"
    )


    st.divider()


    # -----------------------------------------------------
    # CAPABILITIES
    # -----------------------------------------------------

    st.subheader("Capabilities")

    st.write(
        "✓ Natural Language to SQL"
    )

    st.write(
        "✓ SQL Safety Validation"
    )

    st.write(
        "✓ Automated Data Analysis"
    )

    st.write(
        "✓ Dynamic Visualizations"
    )

    st.write(
        "✓ AI Business Insights"
    )

    st.write(
        "✓ Multi-Provider LLM Fallback"
    )


    st.divider()


    st.caption(
        "Powered by PostgreSQL, Gemini, Groq, "
        "Pandas, Plotly & Streamlit"
    )


# =========================================================
# HEADER
# =========================================================

st.title(
    "📊 AI Data Analyst Copilot"
)

st.markdown(
    """
Ask questions about your business data in plain English.

The Copilot automatically generates safe SQL, queries the database,
visualizes the result and explains the key business insights.
"""
)


# =========================================================
# SUGGESTED QUESTIONS
# =========================================================

st.subheader(
    "💡 Suggested Questions"
)


suggested_questions = [

    "What are the top 5 product categories by merchandise sales?",

    "What are the top 5 customer states by merchandise sales?",

    "Which customer states have the highest late delivery rate?",

    "How does customer review score differ between late and on-time deliveries?",

    "What are the most commonly used payment methods and their total payment value?",

    "How have merchandise sales changed month by month?",

    "How many unique customers made repeat purchases, and what percentage of customers were repeat customers?",

    "Which sellers generate the highest merchandise sales and how many orders do they handle?"
]


selected_question = st.selectbox(
    "Choose an example or write your own question below:",
    ["Write my own question"] + suggested_questions
)


# =========================================================
# QUESTION INPUT
# =========================================================

if selected_question != "Write my own question":

    default_question = selected_question

else:

    default_question = ""


question = st.text_area(
    "Ask your business question",
    value=default_question,
    placeholder=(
        "Example: Which product categories generated "
        "the highest merchandise sales?"
    ),
    height=90
)


analyze_button = st.button(
    "🚀 Analyze Data",
    type="primary",
    use_container_width=True
)


# =========================================================
# ANALYSIS
# =========================================================

if analyze_button:

    # -----------------------------------------------------
    # EMPTY QUESTION
    # -----------------------------------------------------

    if not question.strip():

        st.warning(
            "Please enter a business question before "
            "running the analysis."
        )

    else:

        try:

            # -------------------------------------------------
            # RUN PIPELINE
            # -------------------------------------------------

            with st.spinner(
                "Generating SQL, querying PostgreSQL "
                "and analyzing results..."
            ):

                analysis = analyze_question(
                    question.strip()
                )


            # =================================================
            # HANDLE PIPELINE FAILURE
            # =================================================

            if not analysis["success"]:


                # =============================================
                # SECURITY BLOCK
                # =============================================

                if analysis["stage"] == "security_block":

                    st.error(
                        "🔒 Unsafe Request Blocked"
                    )

                    st.warning(
                        "This AI Data Analyst Copilot only "
                        "executes read-only analytics queries."
                    )

                    st.info(
                        "Database modification commands such as "
                        "DELETE, UPDATE, INSERT, DROP, ALTER, "
                        "TRUNCATE, CREATE and similar operations "
                        "are not permitted."
                    )

                    st.markdown(
                        """
**Try asking a read-only analytics question instead**, for example:

`How many customer records are currently in the database?`
"""
                    )


                    if analysis["sql"]:

                        with st.expander(
                            "View Blocked AI Output"
                        ):

                            st.code(
                                analysis["sql"],
                                language="text"
                            )


                    st.stop()


                # =============================================
                # LLM / SQL GENERATION FAILURE
                # =============================================

                elif analysis["stage"] == "sql_generation":

                    st.warning(
                        "⚠️ AI service temporarily unavailable"
                    )

                    st.error(
                        analysis["error"]
                    )

                    st.info(
                        "The PostgreSQL database is connected "
                        "and working correctly. However, all "
                        "configured AI providers are currently "
                        "unavailable or have reached their "
                        "usage limits."
                    )

                    st.caption(
                        "Please retry when one of the configured "
                        "LLM providers becomes available."
                    )

                    st.stop()


                # =============================================
                # DATABASE / QUERY FAILURE
                # =============================================

                elif analysis["stage"] == "query_execution":

                    st.error(
                        "⚠️ Query execution failed"
                    )

                    st.warning(
                        analysis["error"]
                    )


                    if analysis["sql"]:

                        with st.expander(
                            "View Generated SQL"
                        ):

                            st.code(
                                analysis["sql"],
                                language="sql"
                            )


                    st.stop()


                # =============================================
                # UNKNOWN FAILURE
                # =============================================

                else:

                    st.error(
                        "The analysis could not be completed."
                    )

                    st.warning(
                        analysis["error"]
                        or "Unknown analysis error."
                    )

                    st.stop()


            # =================================================
            # SUCCESS
            # =================================================

            st.success(
                "✅ Analysis completed successfully"
            )


            result = analysis["result"]


            # =================================================
            # SUMMARY METRICS
            # =================================================

            col1, col2, col3 = st.columns(3)


            with col1:

                st.metric(
                    "Rows Returned",
                    f"{len(result):,}"
                )


            with col2:

                st.metric(
                    "Columns",
                    len(result.columns)
                )


            with col3:

                visualization_status = (
                    "Available"
                    if analysis["figure"] is not None
                    else "Not Required"
                )

                st.metric(
                    "Visualization",
                    visualization_status
                )


            # =================================================
            # RESULT TABS
            # =================================================

            insight_tab, chart_tab, data_tab, sql_tab = st.tabs(
                [
                    "🤖 AI Insights",
                    "📈 Visualization",
                    "📋 Data",
                    "🧠 Generated SQL"
                ]
            )


            # =================================================
            # AI INSIGHTS
            # =================================================

            with insight_tab:

                st.subheader(
                    "AI Business Insights"
                )


                if analysis["insight"]:

                    # Prevent Streamlit Markdown from
                    # interpreting Brazilian currency
                    # symbol as LaTeX syntax
                    formatted_insight = (
                        analysis["insight"]
                        .replace(
                            "R$",
                            "R\\$"
                        )
                    )


                    st.markdown(
                        formatted_insight
                    )

                else:

                    st.info(
                        "AI insights are not available "
                        "for this analysis."
                    )


            # =================================================
            # VISUALIZATION
            # =================================================

            with chart_tab:

                st.subheader(
                    "Automated Visualization"
                )


                if analysis["figure"] is not None:

                    st.plotly_chart(
                        analysis["figure"],
                        use_container_width=True
                    )

                else:

                    st.info(
                        "The returned data does not require "
                        "a visualization."
                    )


            # =================================================
            # QUERY RESULT
            # =================================================

            with data_tab:

                st.subheader(
                    "Query Result"
                )


                if result.empty:

                    st.info(
                        "The SQL query returned no rows."
                    )

                else:

                    st.dataframe(
                        result,
                        use_container_width=True,
                        hide_index=True
                    )


                    # -----------------------------------------
                    # CSV DOWNLOAD
                    # -----------------------------------------

                    csv_data = (
                        result
                        .to_csv(index=False)
                        .encode("utf-8")
                    )


                    st.download_button(
                        label="⬇️ Download Result as CSV",
                        data=csv_data,
                        file_name="ai_analyst_result.csv",
                        mime="text/csv"
                    )


            # =================================================
            # GENERATED SQL
            # =================================================

            with sql_tab:

                st.subheader(
                    "Generated PostgreSQL Query"
                )


                if analysis["sql"]:

                    st.code(
                        analysis["sql"],
                        language="sql"
                    )


                    st.caption(
                        "The SQL query is validated before execution. "
                        "The application also connects to PostgreSQL "
                        "using a read-only database account."
                    )

                else:

                    st.info(
                        "No SQL query is available."
                    )


        # =====================================================
        # UNEXPECTED APPLICATION ERROR
        # =====================================================

        except Exception as e:

            st.error(
                "An unexpected application error occurred."
            )

            with st.expander(
                "Technical details"
            ):

                st.exception(e)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "AI Data Analyst Copilot • "
    "Schema-aware analytics assistant with "
    "safe read-only SQL execution"
)