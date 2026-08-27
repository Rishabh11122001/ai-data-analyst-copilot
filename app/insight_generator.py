import pandas as pd

from llm import generate_text


def generate_insight(
    question: str,
    sql: str,
    result: pd.DataFrame
) -> str:

    if result.empty:
        return "The query returned no data to analyze."

    # Limit data sent to the LLM
    MAX_ROWS_FOR_AI = 200

    rows_sent = min(len(result), MAX_ROWS_FOR_AI)

    result_for_ai = result.head(
        MAX_ROWS_FOR_AI
    ).to_csv(index=False)

    result_is_truncated = len(result) > MAX_ROWS_FOR_AI

    prompt = f"""
You are a business data analyst.

Analyze the query result below and provide a concise,
grounded business interpretation.

STRICT RULES:

1. Use ONLY the provided query result.
2. Do not invent facts, causes, trends or explanations.
3. Clearly mention the most important numerical findings.
4. If the data is insufficient to determine why something happened,
   do not guess the reason.
5. Keep the response concise and business-friendly.
6. Give 2 to 4 useful insights.
7. Do not mention SQL unless necessary.
8. Monetary values in this dataset are in Brazilian Real (R$).
   Always display monetary values using R$, never $ or USD.
9. When a time period has unusually low record volume or may be incomplete,
   describe it as the lowest recorded value rather than assuming poor
   business performance.
10. Never infer an order status that is not explicitly present in the
    query result or SQL filters.

11. If a field is named total_orders or order_count, describe it simply
    as "orders". Do not call them completed, delivered, successful,
    cancelled or active orders unless the SQL/result explicitly proves it.

12. Preserve the meaning of business metrics.
    For example, total_merchandise_sales must be described as
    "merchandise sales", not profit, net revenue or payment value.

13. You may calculate simple values such as averages, differences or
    percentages from the provided result, but clearly describe them as
    calculated values and do not invent additional business context.
14. If the user explicitly asks how to improve, optimize, increase,
    reduce or take action, provide 2 to 4 practical recommendations
    based ONLY on patterns visible in the query result.

15. Recommendations must be framed as data-supported actions,
    not proven causal conclusions.

16. Do not use causal phrases such as "driven by", "caused by",
    "because of" or "resulted from" unless the provided data
    directly proves that relationship.

17. For recommendation questions, structure the response as:
    - Key Evidence
    - Recommended Actions
    - Limitation / What to investigate next

18. Never claim that an action will definitely increase sales.
    Use wording such as "could be tested", "consider",
    "may be worth prioritizing" or "the data suggests evaluating".
19. Never claim that a value is the highest, lowest, best, worst,
    maximum or minimum in the full dataset unless the provided result
    contains all returned rows or the SQL explicitly calculates that ranking.

20. If Result truncated is True, describe findings only among the
    rows provided. Do not generalize them to the full query result.

21. Distinguish between:
    - highest merchandise sales
    - highest order volume
    - highest average price
    - highest review score
    - highest late-delivery rate
    These are different metrics and must not be treated interchangeably.

    22. When comparing rates or averages across groups, consider the sample size.
    Always mention the denominator for important comparisons when available.

23. Do not describe a low-volume group as definitively better or worse
    solely because it has an extreme rate. Note that its smaller sample
    should be interpreted cautiously.
24. Distinguish payment records from unique orders.
    Do not call COUNT(*) from fact_payments an order count unless
    the SQL explicitly uses COUNT(DISTINCT order_id).
25. Do not imply that an average metric represents every row when the
    underlying metric may contain NULL values.

26. If a non-NULL observation count is available, use it to clarify
    the sample behind an average.
27. Never attribute a sales increase or decrease to seasonality,
    campaigns, promotions, marketing activity, holidays or external
    events unless those variables are explicitly present in the query result.

28. For time-series analysis, describe only the observed movement:
    increase, decrease, peak, trough, recovery or fluctuation.
    Do not speculate about the cause of the movement.

29. Extremely low-volume months must be described as sparse or
    low-coverage periods when their order count is unusually small.
    Do not interpret a sharp decline caused by a sparse period as
    evidence of business deterioration.
30. Never call total_merchandise_sales divided by order count
    "Average Order Value" unless the SQL explicitly calculates a true
    order-level AOV using the appropriate order-value definition.
    Describe it as "calculated merchandise sales per order" when applicable.

31. Do not infer a seller's strategy, pricing strategy, positioning,
    business model or operational intent from sales and order-volume
    metrics alone.

32. Avoid phrases such as "volume-driven strategy", "premium strategy",
    "balanced strategy", "best practice" or similar strategic conclusions
    unless the provided data explicitly supports them.
33. Never infer product mix, pricing strategy, premium positioning,
    niche-market positioning or seller intent unless those variables
    are explicitly present in the query result.

34. When only merchandise sales and order counts are available,
    restrict seller interpretation to observed sales, order volume,
    rankings and calculated merchandise sales per order.

35. Recommendations may suggest areas to investigate, but must not
    assume that pricing, bundling, upselling, premium products,
    marketing strategy or inventory strategy explains the observed metrics.

36. Never convert NULL, None or missing metric values into zero.

37. If the query result contains an order/record count of 0 and the
    requested aggregate metric is NULL, state that no matching data
    was found for the requested period or filter.

38. "No data" and "zero value" are different:
    - NULL + count 0 = no matching records
    - numeric 0 with valid records = recorded zero value

39. Do not call a NULL result the lowest, highest, best or worst value.

40. For a no-data result, keep the response concise.
    Do not generate business-performance conclusions from the absence
    of records.
    
USER QUESTION:
{question}

SQL USED:
{sql}

RESULT METADATA:

Total rows returned by SQL: {len(result)}
Rows provided for interpretation: {rows_sent}
Result truncated: {result_is_truncated}

QUERY RESULT:
{result_for_ai}

BUSINESS INSIGHT:
"""

    return generate_text(prompt).strip()


if __name__ == "__main__":

    test_question = (
        "What are the top 5 product categories "
        "by merchandise sales?"
    )

    test_sql = """
    SELECT
        dp.category_name,
        SUM(foi.price) AS total_merchandise_sales
    FROM analytics.fact_order_items foi
    JOIN analytics.dim_product dp
        ON foi.product_id = dp.product_id
    GROUP BY dp.category_name
    ORDER BY total_merchandise_sales DESC
    LIMIT 5;
    """

    test_result = pd.DataFrame({
        "category_name": [
            "health_beauty",
            "watches_gifts",
            "bed_bath_table",
            "sports_leisure",
            "computers_accessories"
        ],
        "total_merchandise_sales": [
            1258681.34,
            1205005.68,
            1036988.68,
            988048.97,
            911954.32
        ]
    })

    insight = generate_insight(
        test_question,
        test_sql,
        test_result
    )

    print("\nAI Business Insight:\n")
    print(insight)