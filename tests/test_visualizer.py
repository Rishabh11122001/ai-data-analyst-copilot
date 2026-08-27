import sys
from pathlib import Path

import pandas as pd


# =========================================================
# ADD APP FOLDER TO PYTHON PATH
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent
APP_DIR = ROOT_DIR / "app"

sys.path.insert(0, str(APP_DIR))


from visualizer import create_visualization


# =========================================================
# SINGLE ROW → NO VISUALIZATION
# =========================================================

def test_single_row_returns_none():

    df = pd.DataFrame({
        "total_sales": [1000],
        "order_count": [10]
    })

    fig = create_visualization(
        df,
        title="Single KPI"
    )

    assert fig is None


# =========================================================
# EMPTY DATA → NO VISUALIZATION
# =========================================================

def test_empty_dataframe_returns_none():

    df = pd.DataFrame()

    fig = create_visualization(
        df
    )

    assert fig is None


# =========================================================
# CATEGORY DATA → BAR CHART
# =========================================================

def test_category_data_creates_bar_chart():

    df = pd.DataFrame({
        "category_name": [
            "health_beauty",
            "watches_gifts",
            "sports_leisure"
        ],
        "total_merchandise_sales": [
            1250000,
            1200000,
            980000
        ]
    })

    fig = create_visualization(
        df,
        title="Category Sales"
    )

    assert fig is not None
    assert len(fig.data) > 0
    assert fig.data[0].type == "bar"


# =========================================================
# TIME SERIES → LINE CHART
# =========================================================

def test_year_month_creates_line_chart():

    df = pd.DataFrame({
        "year_month": [
            "2017-01",
            "2017-02",
            "2017-03"
        ],
        "total_merchandise_sales": [
            100000,
            150000,
            200000
        ]
    })

    fig = create_visualization(
        df,
        title="Monthly Sales"
    )

    assert fig is not None
    assert len(fig.data) > 0
    assert fig.data[0].type == "scatter"

    # Plotly line charts use scatter traces
    assert fig.data[0].mode == "lines+markers"


# =========================================================
# SELLER LABEL SHORTENING
# =========================================================

def test_seller_id_is_shortened():

    df = pd.DataFrame({
        "seller_id": [
            "4869f7a5dfa277a7dca6462dcf3b52b2",
            "53243585a1d6dc2643021fd1853d8905"
        ],

        "seller_city": [
            "guariba",
            "lauro de freitas"
        ],

        "merchandise_sales": [
            229472.63,
            222776.05
        ]
    })

    fig = create_visualization(
        df,
        title="Seller Sales"
    )

    assert fig is not None

    labels = list(
        fig.data[0].x
    )

    assert "Guariba | 4869f7" in labels
    assert "Lauro De Freitas | 532435" in labels


# =========================================================
# SELLER WITHOUT CITY
# =========================================================

def test_seller_without_city_uses_short_id():

    df = pd.DataFrame({
        "seller_id": [
            "4869f7a5dfa277a7dca6462dcf3b52b2",
            "53243585a1d6dc2643021fd1853d8905"
        ],

        "merchandise_sales": [
            229472.63,
            222776.05
        ]
    })

    fig = create_visualization(
        df,
        title="Seller Sales"
    )

    labels = list(
        fig.data[0].x
    )

    assert "Seller | 4869f7" in labels
    assert "Seller | 532435" in labels


# =========================================================
# LARGE CATEGORY DATA → TOP 15 ONLY
# =========================================================

def test_large_category_chart_is_limited_to_15():

    df = pd.DataFrame({
        "category_name": [
            f"category_{i}"
            for i in range(30)
        ],

        "total_merchandise_sales": [
            i * 1000
            for i in range(30)
        ]
    })

    fig = create_visualization(
        df,
        title="Large Category Chart"
    )

    assert fig is not None

    assert len(
        fig.data[0].x
    ) == 15