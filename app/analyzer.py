import pandas as pd

from sql_generator import generate_sql

from query_executor import (
    execute_query,
    UnsafeSQLQueryError
)

from insight_generator import generate_insight
from visualizer import create_visualization


# =========================================================
# MAIN ANALYSIS PIPELINE
# =========================================================

def analyze_question(question: str):

    print("\nUser Question:")
    print(question)


    # =====================================================
    # STEP 1: GENERATE SQL
    # =====================================================

    print("\nGenerating SQL...")

    try:

        sql = generate_sql(
            question
        )

        print("\nGenerated SQL:")
        print(sql)

    except Exception as e:

        print("\nSQL generation unavailable:")
        print(e)

        return {
            "success": False,
            "stage": "sql_generation",
            "question": question,
            "sql": None,
            "result": pd.DataFrame(),
            "figure": None,
            "insight": None,
            "error": (
                "The configured AI providers are temporarily "
                "unavailable or have reached their usage limits. "
                "SQL could not be generated."
            )
        }


    # =====================================================
    # STEP 2: EXECUTE SQL
    # =====================================================

    print("\nExecuting Query...")

    try:

        result = execute_query(
            sql
        )

        print("\nQuery Result:")
        print(result)


    # =====================================================
    # SECURITY BLOCK
    # =====================================================

    except UnsafeSQLQueryError as e:

        print("\nSECURITY BLOCK:")
        print(e)

        return {
            "success": False,
            "stage": "security_block",
            "question": question,
            "sql": sql,
            "result": pd.DataFrame(),
            "figure": None,
            "insight": None,
            "error": str(e)
        }


    # =====================================================
    # DATABASE / SQL EXECUTION ERROR
    # =====================================================

    except Exception as e:

        print("\nQuery execution failed:")
        print(e)

        return {
            "success": False,
            "stage": "query_execution",
            "question": question,
            "sql": sql,
            "result": pd.DataFrame(),
            "figure": None,
            "insight": None,
            "error": (
                f"Database query could not be executed: {e}"
            )
        }


    # =====================================================
    # STEP 3: VISUALIZATION
    # =====================================================

    print("\nCreating Visualization...")

    try:

        figure = create_visualization(
            result,
            title=question
        )

        if figure is None:

            print(
                "No suitable visualization found."
            )

    except Exception as e:

        print("\nVisualization generation failed:")
        print(e)

        # Visualization failure should not kill analysis
        figure = None


    # =====================================================
    # STEP 4: AI BUSINESS INSIGHT
    # =====================================================

    print("\nGenerating Business Insight...")

    try:

        insight = generate_insight(
            question=question,
            sql=sql,
            result=result
        )

        print("\nAI Business Insight:")
        print(insight)

    except Exception as e:

        print("\nAI insight generation unavailable:")
        print(e)

        insight = (
            "⚠️ AI business insights are temporarily unavailable "
            "because all configured LLM providers are currently "
            "unavailable or have reached their usage limits.\n\n"
            "The SQL query, database result and visualization were "
            "generated successfully and remain available."
        )


    # =====================================================
    # STEP 5: RETURN RESULT
    # =====================================================

    return {
        "success": True,
        "stage": "complete",
        "question": question,
        "sql": sql,
        "result": result,
        "figure": figure,
        "insight": insight,
        "error": None
    }


# =========================================================
# LOCAL TEST
# =========================================================

if __name__ == "__main__":

    test_question = (
        "How have merchandise sales changed month by month?"
    )

    analysis = analyze_question(
        test_question
    )


    print("\n================================")
    print("PIPELINE RESULT")
    print("================================")

    print("\nSuccess:")
    print(
        analysis["success"]
    )

    print("\nStage:")
    print(
        analysis["stage"]
    )

    if analysis["sql"]:

        print("\nGenerated SQL:")
        print(
            analysis["sql"]
        )

    if analysis["success"]:

        print("\nResult:")
        print(
            analysis["result"]
        )

        print("\nInsight:")
        print(
            analysis["insight"]
        )

    else:

        print("\nError:")
        print(
            analysis["error"]
        )