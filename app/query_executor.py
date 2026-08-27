import pandas as pd

from sqlalchemy import text

from database import engine
from sql_validator import validate_sql


# =========================================================
# QUERY SETTINGS
# =========================================================

# Maximum PostgreSQL execution time per query
QUERY_TIMEOUT_MS = 10_000  # 10 seconds

# Maximum number of rows returned to the application
MAX_RESULT_ROWS = 500


# =========================================================
# CUSTOM SECURITY EXCEPTION
# =========================================================

class UnsafeSQLQueryError(ValueError):
    """
    Raised when generated SQL violates
    the application's read-only SQL policy.
    """
    pass


# =========================================================
# APPLY SERVER-SIDE ROW LIMIT
# =========================================================

def apply_row_limit(sql: str) -> str:
    """
    Wrap the validated read-only query so PostgreSQL itself
    returns at most MAX_RESULT_ROWS rows.

    This protects the application from accidentally loading
    very large query results into memory.
    """

    cleaned_sql = sql.strip().rstrip(";")

    limited_sql = f"""
    SELECT *
    FROM (
        {cleaned_sql}
    ) AS ai_analyst_query
    LIMIT {MAX_RESULT_ROWS};
    """

    return limited_sql


# =========================================================
# QUERY EXECUTOR
# =========================================================

def execute_query(sql: str) -> pd.DataFrame:

    # -----------------------------------------------------
    # STEP 1: VALIDATE ORIGINAL AI SQL
    # -----------------------------------------------------

    is_valid, message = validate_sql(sql)

    if not is_valid:

        raise UnsafeSQLQueryError(
            f"Unsafe SQL blocked: {message}"
        )


    # -----------------------------------------------------
    # STEP 2: APPLY SERVER-SIDE RESULT LIMIT
    # -----------------------------------------------------

    safe_limited_sql = apply_row_limit(sql)


    # -----------------------------------------------------
    # STEP 3: EXECUTE QUERY
    # -----------------------------------------------------

    try:

        with engine.begin() as connection:

            # Query timeout applies only to this transaction
            connection.execute(
                text(
                    f"SET LOCAL statement_timeout = "
                    f"{QUERY_TIMEOUT_MS}"
                )
            )

            result = pd.read_sql_query(
                text(safe_limited_sql),
                connection
            )

        return result


    # -----------------------------------------------------
    # DATABASE ERRORS
    # -----------------------------------------------------

    except Exception as e:

        error_message = str(e).lower()


        # PostgreSQL timeout
        if (
            "statement timeout" in error_message
            or "query canceled" in error_message
            or "canceling statement" in error_message
        ):

            raise RuntimeError(
                "The query exceeded the allowed execution "
                "time of 10 seconds and was automatically stopped."
            ) from e


        raise RuntimeError(
            f"Database query failed: {e}"
        ) from e


# =========================================================
# LOCAL TEST
# =========================================================

if __name__ == "__main__":

    # -----------------------------------------------------
    # SAFE QUERY TEST
    # -----------------------------------------------------

    safe_query = """
    SELECT *
    FROM analytics.dim_customer
    LIMIT 5;
    """

    print("\nSAFE QUERY TEST")

    try:

        result = execute_query(
            safe_query
        )

        print(result)
        print(
            f"\nRows returned: {len(result)}"
        )

    except Exception as e:

        print(e)


    # -----------------------------------------------------
    # UNSAFE QUERY TEST
    # -----------------------------------------------------

    unsafe_query = """
    DELETE FROM analytics.dim_customer;
    """

    print("\nUNSAFE QUERY TEST")

    try:

        result = execute_query(
            unsafe_query
        )

        print(result)

    except UnsafeSQLQueryError as e:

        print("SECURITY BLOCK:")
        print(e)


    # -----------------------------------------------------
    # ROW LIMIT TEST
    # -----------------------------------------------------

    large_query = """
    SELECT *
    FROM analytics.dim_customer;
    """

    print("\nROW LIMIT TEST")

    try:

        result = execute_query(
            large_query
        )

        print(
            f"Rows returned: {len(result)}"
        )

        print(
            f"Maximum allowed rows: {MAX_RESULT_ROWS}"
        )

    except Exception as e:

        print(e)


    # -----------------------------------------------------
    # TIMEOUT TEST
    # -----------------------------------------------------

    timeout_query = """
    SELECT pg_sleep(15);
    """

    print("\nTIMEOUT TEST")

    try:

        result = execute_query(
            timeout_query
        )

        print(result)

    except Exception as e:

        print(e)