import pandas as pd
import plotly.express as px
from pandas.api.types import is_numeric_dtype


# =========================================================
# NON-MEASURE COLUMNS
# =========================================================

NON_MEASURE_COLUMNS = {
    "year",
    "month",
    "month_number",
    "quarter",
    "week_number",
    "day_of_month",
    "day_of_week_number",
    "date_key",
    "purchase_date_key"
}


# =========================================================
# VISUALIZATION GENERATOR
# =========================================================

def create_visualization(
    df: pd.DataFrame,
    title: str = "Query Result"
):

    # -----------------------------------------------------
    # BASIC VALIDATION
    # -----------------------------------------------------

    if df.empty or len(df.columns) < 2:
        return None

    data = df.copy()


    # -----------------------------------------------------
    # SINGLE ROW → NO CHART
    # -----------------------------------------------------

    if len(data) == 1:
        return None


    # -----------------------------------------------------
    # DETECT TIME COLUMN
    # -----------------------------------------------------

    time_column = None

    for col in data.columns:

        if "year_month" in col.lower():

            converted = pd.to_datetime(
                data[col],
                format="%Y-%m",
                errors="coerce"
            )

            if converted.notna().all():

                data[col] = converted
                time_column = col
                break


    # -----------------------------------------------------
    # NUMERIC COLUMNS
    # -----------------------------------------------------

    numeric_columns = [
        col
        for col in data.columns
        if is_numeric_dtype(data[col])
        and col.lower() not in NON_MEASURE_COLUMNS
    ]


    # -----------------------------------------------------
    # CATEGORICAL COLUMNS
    # -----------------------------------------------------

    categorical_columns = [
        col
        for col in data.columns
        if not is_numeric_dtype(data[col])
        and col != time_column
    ]


    if not numeric_columns:
        return None


    # =====================================================
    # SELECT BEST Y-AXIS METRIC
    # =====================================================

    preferred_keywords = [
        "sales",
        "revenue",
        "value",
        "amount",
        "freight",
        "payment",
        "score",
        "rate",
        "percentage",
        "percent",
        "count",
        "orders"
    ]

    y_col = None


    for keyword in preferred_keywords:

        for col in numeric_columns:

            if keyword in col.lower():

                y_col = col
                break

        if y_col:
            break


    if y_col is None:
        y_col = numeric_columns[0]


    # =====================================================
    # TIME SERIES → LINE CHART
    # =====================================================

    if time_column is not None:

        data = data.sort_values(
            by=time_column
        )

        fig = px.line(
            data,
            x=time_column,
            y=y_col,
            markers=True,
            title=title
        )

        fig.update_layout(
            xaxis_title="Time",
            yaxis_title=(
                y_col
                .replace("_", " ")
                .title()
            ),
            hovermode="x unified"
        )

        return fig


    # =====================================================
    # CATEGORY → BAR CHART
    # =====================================================

    if categorical_columns:

        x_col = categorical_columns[0]


        # -------------------------------------------------
        # SELLER LABEL
        # -------------------------------------------------

        if "seller_id" in data.columns:

            # City exists → City | short ID
            if "seller_city" in data.columns:

                data["seller_label"] = (
                    data["seller_city"]
                    .fillna("Unknown")
                    .astype(str)
                    .str.title()
                    +
                    " | "
                    +
                    data["seller_id"]
                    .astype(str)
                    .str[:6]
                )

            # City not returned → Seller | short ID
            else:

                data["seller_label"] = (
                    "Seller | "
                    +
                    data["seller_id"]
                    .astype(str)
                    .str[:6]
                )

            x_col = "seller_label"


        # -------------------------------------------------
        # PRODUCT CATEGORY
        # -------------------------------------------------

        elif "category_name" in data.columns:

            x_col = "category_name"


        # -------------------------------------------------
        # CUSTOMER STATE
        # -------------------------------------------------

        elif "customer_state" in data.columns:

            x_col = "customer_state"


        # -------------------------------------------------
        # PAYMENT TYPE
        # -------------------------------------------------

        elif "payment_type" in data.columns:

            x_col = "payment_type"


        # -------------------------------------------------
        # DELIVERY STATUS
        # -------------------------------------------------

        elif "delivery_status" in data.columns:

            x_col = "delivery_status"


        # -------------------------------------------------
        # KEEP LARGE CHARTS READABLE
        # -------------------------------------------------

        if len(data) > 15:

            data = (
                data
                .sort_values(
                    by=y_col,
                    ascending=False
                )
                .head(15)
            )


        # -------------------------------------------------
        # BAR CHART
        # -------------------------------------------------

        fig = px.bar(
            data,
            x=x_col,
            y=y_col,
            title=title,
            text_auto=".3s"
        )


        fig.update_layout(
            xaxis_title=(
                "Seller"
                if x_col == "seller_label"
                else x_col
                .replace("_", " ")
                .title()
            ),

            yaxis_title=(
                y_col
                .replace("_", " ")
                .title()
            ),

            xaxis_tickangle=-35
        )


        return fig


    # =====================================================
    # TWO NUMERIC COLUMNS → SCATTER
    # =====================================================

    if len(numeric_columns) >= 2:

        x_col = numeric_columns[0]
        scatter_y_col = numeric_columns[1]

        fig = px.scatter(
            data,
            x=x_col,
            y=scatter_y_col,
            title=title
        )

        fig.update_layout(
            xaxis_title=(
                x_col
                .replace("_", " ")
                .title()
            ),

            yaxis_title=(
                scatter_y_col
                .replace("_", " ")
                .title()
            )
        )

        return fig


    # =====================================================
    # NO SUITABLE CHART
    # =====================================================

    return None


# =========================================================
# LOCAL TEST
# =========================================================

if __name__ == "__main__":

    test_data = pd.DataFrame({

        "seller_id": [
            "4869f7a5dfa277a7dca6462dcf3b52b2",
            "53243585a1d6dc2643021fd1853d8905",
            "4a3ca9315b744ce9f8e9374361493884"
        ],

        "merchandise_sales": [
            229472.63,
            222776.05,
            200472.92
        ],

        "order_count": [
            1132,
            358,
            1806
        ]
    })


    figure = create_visualization(
        test_data,
        title="Top Sellers by Merchandise Sales"
    )


    if figure is not None:
        figure.show()

    else:
        print(
            "No suitable visualization found."
        )