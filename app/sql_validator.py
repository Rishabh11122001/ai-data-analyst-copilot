import re
import sqlparse


FORBIDDEN_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE",
    "COPY",
    "CALL",
    "EXECUTE",
    "MERGE",
    "VACUUM",
]


def validate_sql(sql: str):

    if not sql or not sql.strip():
        return False, "SQL query is empty."

    # Remove comments
    cleaned_sql = sqlparse.format(
        sql,
        strip_comments=True
    ).strip()

    # Only one complete SQL statement
    statements = [
        statement
        for statement in sqlparse.parse(cleaned_sql)
        if str(statement).strip()
    ]

    if len(statements) != 1:
        return False, "Only one SQL statement is allowed."

    upper_sql = cleaned_sql.upper()

    # -------------------------------------------------
    # Allow:
    # SELECT ...
    # WITH ...
    # (SELECT ...)
    # ((SELECT ...))
    # -------------------------------------------------

    if not re.match(
        r"^\s*\(*\s*(SELECT|WITH)\b",
        upper_sql
    ):
        return False, "Only read-only SELECT or WITH queries are allowed."

    # -------------------------------------------------
    # Block dangerous commands anywhere in the query
    # -------------------------------------------------

    for keyword in FORBIDDEN_KEYWORDS:

        if re.search(
            rf"\b{keyword}\b",
            upper_sql
        ):
            return False, (
                f"Forbidden SQL keyword detected: {keyword}"
            )

    return True, "SQL query is safe."


if __name__ == "__main__":

    safe_query = """
    SELECT *
    FROM analytics.dim_customer
    LIMIT 5;
    """

    union_query = """
    (
        SELECT 'highest' AS type, 100 AS sales
    )
    UNION ALL
    (
        SELECT 'lowest' AS type, 10 AS sales
    );
    """

    dangerous_query = """
    DROP TABLE analytics.dim_customer;
    """

    multiple_queries = """
    SELECT * FROM analytics.dim_customer;
    DELETE FROM analytics.dim_customer;
    """

    test_queries = [
        ("SAFE QUERY", safe_query),
        ("UNION QUERY", union_query),
        ("DANGEROUS QUERY", dangerous_query),
        ("MULTIPLE QUERIES", multiple_queries),
    ]

    for name, query in test_queries:

        valid, message = validate_sql(query)

        print(f"\n{name}")
        print("Valid:", valid)
        print("Message:", message)