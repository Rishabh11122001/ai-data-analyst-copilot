import sys
from pathlib import Path

import pandas as pd
import pytest


# =========================================================
# ADD APP FOLDER TO PYTHON PATH
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent
APP_DIR = ROOT_DIR / "app"

sys.path.insert(0, str(APP_DIR))


import query_executor
from query_executor import (
    execute_query,
    apply_row_limit,
    UnsafeSQLQueryError,
    MAX_RESULT_ROWS
)


# =========================================================
# FAKE DATABASE OBJECTS
# =========================================================

class FakeConnection:

    def __init__(self):
        self.executed_commands = []

    def execute(self, command):
        self.executed_commands.append(
            str(command)
        )

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ):
        pass


class FakeEngine:

    def __init__(self):
        self.connection = FakeConnection()

    def begin(self):
        return self.connection


# =========================================================
# ROW LIMIT TESTS
# =========================================================

def test_apply_row_limit_adds_limit():

    sql = """
    SELECT *
    FROM analytics.dim_customer;
    """

    limited_sql = apply_row_limit(sql)

    assert f"LIMIT {MAX_RESULT_ROWS}" in limited_sql
    assert "analytics.dim_customer" in limited_sql


def test_apply_row_limit_removes_trailing_semicolon():

    sql = """
    SELECT *
    FROM analytics.fact_orders;
    """

    limited_sql = apply_row_limit(sql)

    assert "FROM analytics.fact_orders" in limited_sql
    assert f"LIMIT {MAX_RESULT_ROWS}" in limited_sql


# =========================================================
# UNSAFE SQL TEST
# =========================================================

def test_execute_query_blocks_delete():

    sql = """
    DELETE FROM analytics.dim_customer;
    """

    with pytest.raises(
        UnsafeSQLQueryError
    ):

        execute_query(sql)


# =========================================================
# SAFE QUERY EXECUTION TEST
# =========================================================

def test_execute_safe_query(monkeypatch):

    fake_engine = FakeEngine()

    monkeypatch.setattr(
        query_executor,
        "engine",
        fake_engine
    )


    expected_df = pd.DataFrame({
        "customer_state": [
            "SP",
            "RJ"
        ]
    })


    def fake_read_sql_query(
        sql,
        connection
    ):

        sql_text = str(sql)

        assert (
            f"LIMIT {MAX_RESULT_ROWS}"
            in sql_text
        )

        return expected_df


    monkeypatch.setattr(
        query_executor.pd,
        "read_sql_query",
        fake_read_sql_query
    )


    result = execute_query(
        """
        SELECT customer_state
        FROM analytics.dim_customer;
        """
    )


    assert isinstance(
        result,
        pd.DataFrame
    )

    assert len(result) == 2

    assert list(
        result["customer_state"]
    ) == [
        "SP",
        "RJ"
    ]


    # Confirm PostgreSQL timeout command was applied
    commands = " ".join(
        fake_engine.connection.executed_commands
    )

    assert "statement_timeout" in commands


# =========================================================
# DATABASE ERROR TEST
# =========================================================

def test_database_error_is_wrapped(
    monkeypatch
):

    fake_engine = FakeEngine()

    monkeypatch.setattr(
        query_executor,
        "engine",
        fake_engine
    )


    def fake_read_sql_query(
        sql,
        connection
    ):

        raise Exception(
            "database connection lost"
        )


    monkeypatch.setattr(
        query_executor.pd,
        "read_sql_query",
        fake_read_sql_query
    )


    with pytest.raises(
        RuntimeError,
        match="Database query failed"
    ):

        execute_query(
            """
            SELECT *
            FROM analytics.dim_customer;
            """
        )


# =========================================================
# TIMEOUT ERROR TEST
# =========================================================

def test_timeout_error_is_handled(
    monkeypatch
):

    fake_engine = FakeEngine()

    monkeypatch.setattr(
        query_executor,
        "engine",
        fake_engine
    )


    def fake_read_sql_query(
        sql,
        connection
    ):

        raise Exception(
            "canceling statement due to statement timeout"
        )


    monkeypatch.setattr(
        query_executor.pd,
        "read_sql_query",
        fake_read_sql_query
    )


    with pytest.raises(
        RuntimeError,
        match="exceeded the allowed execution time"
    ):

        execute_query(
            """
            SELECT *
            FROM analytics.fact_orders;
            """
        )