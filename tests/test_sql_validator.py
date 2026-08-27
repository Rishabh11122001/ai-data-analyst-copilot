import sys
from pathlib import Path

# Add app folder to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
APP_DIR = ROOT_DIR / "app"

sys.path.insert(0, str(APP_DIR))

from sql_validator import validate_sql


# =========================================================
# SAFE QUERY TESTS
# =========================================================

def test_simple_select_is_allowed():

    sql = """
    SELECT *
    FROM analytics.dim_customer
    LIMIT 5;
    """

    valid, message = validate_sql(sql)

    assert valid is True


def test_with_cte_is_allowed():

    sql = """
    WITH customer_orders AS (
        SELECT
            customer_id,
            COUNT(*) AS order_count
        FROM analytics.fact_orders
        GROUP BY customer_id
    )
    SELECT *
    FROM customer_orders;
    """

    valid, message = validate_sql(sql)

    assert valid is True


def test_union_select_is_allowed():

    sql = """
    (
        SELECT 'highest' AS category, 100 AS value
    )
    UNION ALL
    (
        SELECT 'lowest' AS category, 10 AS value
    );
    """

    valid, message = validate_sql(sql)

    assert valid is True


# =========================================================
# UNSAFE QUERY TESTS
# =========================================================

def test_delete_is_blocked():

    sql = """
    DELETE FROM analytics.dim_customer;
    """

    valid, message = validate_sql(sql)

    assert valid is False


def test_update_is_blocked():

    sql = """
    UPDATE analytics.dim_customer
    SET customer_state = 'XX';
    """

    valid, message = validate_sql(sql)

    assert valid is False


def test_insert_is_blocked():

    sql = """
    INSERT INTO analytics.dim_customer
    VALUES ('1', '1', 12345, 'city', 'SP', 0, 0);
    """

    valid, message = validate_sql(sql)

    assert valid is False


def test_drop_is_blocked():

    sql = """
    DROP TABLE analytics.dim_customer;
    """

    valid, message = validate_sql(sql)

    assert valid is False


def test_alter_is_blocked():

    sql = """
    ALTER TABLE analytics.dim_customer
    ADD COLUMN test_column TEXT;
    """

    valid, message = validate_sql(sql)

    assert valid is False


def test_truncate_is_blocked():

    sql = """
    TRUNCATE TABLE analytics.dim_customer;
    """

    valid, message = validate_sql(sql)

    assert valid is False


# =========================================================
# MULTIPLE STATEMENT TEST
# =========================================================

def test_multiple_statements_are_blocked():

    sql = """
    SELECT *
    FROM analytics.dim_customer;

    DELETE FROM analytics.dim_customer;
    """

    valid, message = validate_sql(sql)

    assert valid is False


# =========================================================
# EMPTY QUERY TEST
# =========================================================

def test_empty_query_is_blocked():

    valid, message = validate_sql("")

    assert valid is False