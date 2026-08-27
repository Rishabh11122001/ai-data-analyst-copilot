from llm import generate_text
from semantic_layer import build_schema_context


def clean_sql_response(response: str) -> str:
    sql = response.strip()

    if sql.startswith("```sql"):
        sql = sql[6:]

    elif sql.startswith("```"):
        sql = sql[3:]

    if sql.endswith("```"):
        sql = sql[:-3]

    return sql.strip()


def generate_sql(question: str) -> str:
    schema_context = build_schema_context()

    prompt = f"""
You are an expert PostgreSQL data analyst.

Your job is to convert the user's business question
into ONE correct PostgreSQL SELECT query.

DATABASE CONTEXT:

{schema_context}

STRICT RULES:

1. Return ONLY SQL.
2. Do not include explanations.
3. Do not use Markdown code fences.
4. Generate only SELECT or WITH queries.
5. Never generate INSERT, UPDATE, DELETE, DROP,
   ALTER, CREATE or TRUNCATE statements.
6. Use only tables and columns provided in the schema.
7. Use the analytics schema explicitly.
8. Follow all business definitions from the database context.
9. Avoid unnecessary joins.
10. Do not join multiple fact tables when a single fact table
    can answer the question.
11. Use appropriate GROUP BY, ORDER BY and LIMIT clauses.
12. For sales questions, use merchandise sales unless
    the user explicitly asks for total order value or payments.

USER QUESTION:

{question}

SQL:
"""

    response = generate_text(prompt)

    return clean_sql_response(response)


if __name__ == "__main__":

    test_question = (
        "What are the top 5 customer states "
        "by merchandise sales?"
    )

    print("\nQuestion:")
    print(test_question)

    sql = generate_sql(test_question)

    print("\nGenerated SQL:")
    print(sql)