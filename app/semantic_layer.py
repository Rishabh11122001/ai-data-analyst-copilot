from schema import get_database_schema, get_database_relationships


def build_schema_context():
    schema = get_database_schema()
    relationships = get_database_relationships()

    context = []

    context.append(
        """
DATABASE:
PostgreSQL analytics warehouse for an e-commerce business.

SCHEMA:
analytics

IMPORTANT BUSINESS DEFINITIONS:

1. Merchandise Sales
   - Order-level: fact_orders.merchandise_value
   - Product/category/seller-level: fact_order_items.price
   - Do NOT use payment_value as merchandise sales.

2. Total Order Value
   - fact_orders.total_order_value
   - Includes merchandise value + freight.

3. Freight
   - Order-level: fact_orders.total_freight_value
   - Item-level: fact_order_items.freight_value

4. Payments
   - fact_payments.payment_value is used for payment analysis.
   - Payment totals may differ from merchandise/order totals.

5. Customers
   - customer_id is an order-level customer identifier.
   - customer_unique_id identifies the actual customer across purchases.

6. Delivery
   - late_delivery_flag = 1 means Late.
   - late_delivery_flag = 0 means On-Time.
   - NULL means the late-delivery metric is not applicable or unavailable.

7. Reviews
   - review_score ranges from 1 to 5.
   - Higher scores represent better customer satisfaction.

IMPORTANT SQL RULES:

- Prefer dimension-to-fact joins.
- Avoid joining multiple fact tables together unless absolutely necessary.
- Never directly join fact_order_items to fact_payments for aggregation.
  This can create row multiplication and inflated totals.
- For product/category/seller analysis, use fact_order_items.
- For order-level KPIs, delivery metrics and overall sales, use fact_orders.
- For payment analysis, use fact_payments.
- For review-level text or individual review analysis, use fact_reviews.
- Use dim_date for year, month, quarter and time-based grouping.
- Use dim_product for product category names.
- Use dim_seller for seller geography.
- Use dim_customer for customer geography and customer_unique_id.
- Never rank NULL metric values as highest or lowest.
- When ranking aggregated metrics, exclude NULL aggregate values
  or explicitly use NULLS LAST.
- For MIN/MAX, top/bottom, highest/lowest and ranking questions,
  only compare rows where the requested metric has a valid non-NULL value.
  - When calculating merchandise sales over time,
  ignore rows where merchandise_value is NULL.
  - For highest/lowest monthly sales questions, remember that very sparse
  or incomplete months may not be directly comparable with full months.

- When possible, include an order count alongside monthly sales so that
  unusually low-volume months can be identified.

- Do not describe a very low-volume month as poor business performance
  unless the data proves that the month has normal/complete coverage.
- fact_order_items is item-grain and fact_orders is order-grain.

- Never calculate averages or rates from order-level columns after directly
  joining fact_orders to item-level rows, because orders with multiple items
  can be duplicated and overweighted.

- When category-level analysis requires order-level metrics such as
  avg_review_score, late_delivery_flag, delivery_days or canceled_flag,
  first create a DISTINCT order_id + category_name dataset, then join that
  order-level dataset to fact_orders.

- Aggregate item-level sales metrics separately from order-level customer,
  review and delivery metrics, then join the aggregated results by category.

- COUNT(DISTINCT order_id) should be used for category-level order counts.
- For percentage, rate or average rankings across groups,
  always include the underlying record/order count when available.

- Do not automatically exclude low-volume groups unless the user
  specifies a minimum sample size.

- Rate-based rankings should preserve both the metric and its denominator
  so small-sample results can be interpreted cautiously.
- fact_payments is payment-record grain, not order grain.

- COUNT(*) on fact_payments means number of payment records/transactions,
  not necessarily number of unique orders.

- If the user asks how many orders used a payment method,
  use COUNT(DISTINCT order_id).

- If the user asks for payment method frequency without specifying
  order-level usage, clearly label COUNT(*) as payment records.

- payment_value represents payment value and must not be described
  as merchandise sales or profit.
- When averaging a nullable metric such as review score, include the
  count of non-NULL observations when it is useful for interpretation.

- COUNT(*) and COUNT(metric_column) may have different denominators.
  COUNT(metric_column) counts only rows where that metric is non-NULL.

  - customer_id is NOT the true person-level customer identity.

- customer_unique_id from analytics.dim_customer represents the
  actual customer across multiple purchases.

- For unique customer counts, repeat customers, customer retention,
  purchase frequency or customer-level behavior, ALWAYS join
  fact_orders to dim_customer using customer_id and group/count
  using customer_unique_id.

- Never calculate repeat-customer metrics by grouping only on
  fact_orders.customer_id.

- A repeat customer is a customer_unique_id associated with more
  than one DISTINCT order_id.

- For ranking questions containing words such as top, highest, best,
  lowest, worst or leading, return only the most relevant ranked rows
  unless the user explicitly asks for all rows.

- If the user asks for a ranked list but does not specify a number,
  default to LIMIT 10.

- If the user explicitly requests Top N or Bottom N, use exactly that N.

- Do not return the full dimension table for a ranking question when
  a limited ranked result can answer the user's request.

- Always apply ORDER BY before LIMIT for ranking queries.

- SQL aggregate queries without GROUP BY may return one row even when
  no source rows match the filter.

- SUM, AVG, MIN and MAX over an empty matching set return NULL,
  while COUNT returns 0.

- NULL aggregate values must NOT be interpreted as zero.

- If an aggregate result has COUNT = 0 and the requested metric is NULL,
  interpret this as "no matching records / no available data",
  not as zero sales or zero performance.

- A NULL metric must never be ranked or described as the lowest,
  highest, best or worst recorded value.
"""
    )

    context.append("\nTABLES AND COLUMNS:\n")

    for table, columns in schema.items():
        context.append(f"\nTABLE analytics.{table}")

        for column in columns:
            context.append(
                f"  - {column['name']} ({column['type']})"
            )

    context.append("\nRELATIONSHIPS:\n")

    for rel in relationships:
        context.append(
            f"analytics.{rel['source_table']}."
            f"{rel['source_column']} -> "
            f"analytics.{rel['target_table']}."
            f"{rel['target_column']}"
        )

    return "\n".join(context)


if __name__ == "__main__":
    print(build_schema_context())