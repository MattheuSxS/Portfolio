import polars as pl
import altair as alt
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


class BrNordesteDashboard:
    def __init__(self, df: pl.DataFrame, st: any):
        self.st = st
        self.state = {
            "MA": "Maranhão",
            "PI": "Piauí",
            "CE": "Ceará",
            "RN": "Rio Grande do Norte",
            "PB": "Paraíba",
            "PE": "Pernambuco",
            "AL": "Alagoas",
            "SE": "Sergipe",
            "BA": "Bahia"
        }
        self.df = df.filter(
            pl.col("state").is_in(
                self.state.keys()
            )
        )

    def render_dashboard(self):
        if self.df.is_empty():
            self.st.warning("No feedback data found or error loading data.")
            return

        self.st.header("🗺 Region Nordeste Information about the product")

        cols = self.st.columns([1, 3])

        left_cell, right_cell = cols
        normalized = (
            self.df
            .select([
                pl.col("ds").alias("Date"),
                pl.col("actual"),
                pl.col("prophet").alias("Prophet"),
                pl.col("holt_winters").alias("Holt-Winters"),
            ])
            .group_by("Date")
            .agg([
                pl.col("actual").sum(),
                pl.col("Prophet").sum(),
                pl.col("Holt-Winters").sum(),
            ])
            .sort("Date")
)

        with right_cell:
            chart = alt.Chart(normalized.to_pandas()).transform_fold(
                fold=["actual", "Prophet", "Holt-Winters"],
                as_=["Model", "Value"]
            ).mark_line().encode(
                x="Date:T",
                y="Value:Q",
                color="Model:N"
            ).properties(
                title="Sales Forecast Comparison"
            )

            self.st.altair_chart(chart, use_container_width=True)
