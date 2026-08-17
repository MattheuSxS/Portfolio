import polars as pl
import altair as alt


class MockupDashboard:
    def __init__(self, df: pl.DataFrame, state: dict, st: any):
        self.df = df
        self.state = state
        self.st = st

        self.df = df.filter(
            pl.col("state").is_in(
                self.state.keys()
            )
        )
        self.model_colors = {
            "Actual": "#EFAFAD",
            "Prophet": "#3566C1",
            "Holt-Winters": "#95C6FB",
        }

        self.delta_colors = {
            "Prophet vs Actual": self.model_colors["Prophet"],
            "Holt-Winters vs Actual": self.model_colors["Holt-Winters"],
        }

    def render_dashboard(self):
        if self.df.is_empty():
            self.st.warning(
                "No sales data found or error loading data."
            )
            return

        self.st.header(
            "🗺 Region Sudeste Information about the product"
        )

    # ============================================================
    # HORIZON CONFIGURATION
        # ============================================================

        horizon_map = {
            "1 Month": "1mo",
            "3 Months": "3mo",
            "6 Months": "6mo",
            "1 Year": "1y",
            "5 Years": "5y",
            "10 Years": "10y",
            "20 Years": "20y",
        }

        # ============================================================
        # LAYOUT
        # ============================================================

        cols = self.st.columns([1, 3])

        left_cell, right_cell = cols

        # ============================================================
        # TOP LEFT - FILTERS
        # ============================================================

        top_left_cell = cols[0].container(
            border = True,
            height = "stretch",
            vertical_alignment = "center",
        )

        # ============================================================
        # STATE FILTER
        # ============================================================

        if "tickers_input" not in self.st.session_state:
            self.st.session_state.tickers_input = (
                self.st.query_params.get(
                    "states",
                    list(self.state.keys()),
                )
            )


        with top_left_cell:
            tickers = self.st.multiselect(
                label = "Select States",
                options = sorted(set(self.state.keys())),
                default = list(self.state.keys()),
                format_func = lambda x: self.state[x],
                placeholder = (
                    "Select the states to compare. "
                    "Example: SP"
                ),
                accept_new_options = True,
            )

        # ============================================================
        # TIME HORIZON
        # ============================================================

        with top_left_cell:
            selected_horizon = self.st.pills(
                label = "Time horizon",
                options = list(
                    horizon_map.keys()
                ),
                default = "6 Months",
            )

        # ============================================================
        # VALIDATE STATE SELECTION
        # ============================================================

        if not tickers:
            self.st.warning(
                "Please select at least one state."
            )

            return

        # ============================================================
        # FORECAST ORIGIN
        # ============================================================

        forecast_origin = (
            self.df
            .filter(
                pl.col("actual").is_not_null()
            )
            .select(
                pl.col("ds").max()
            )
            .item()
        )

        if forecast_origin is None:

            self.st.error(
                "Could not determine the forecast origin date."
            )

            return

        # ============================================================
        # CALCULATE HORIZON
        # ============================================================

        horizon = horizon_map[
            selected_horizon
        ]

        forecast_end = (
            pl.select(
                pl.lit(forecast_origin)
                .cast(pl.Date)
                .dt.offset_by(horizon)
            )
            .item()
        )

        history_start = (
            pl.select(
                pl.lit(forecast_origin)
                .cast(pl.Date)
                .dt.offset_by(
                    f"-{horizon}"
                )
            )
            .item()
        )

        # ============================================================
        # FILTER DATA BY DATE
        # ============================================================

        filtered_df = self.df.filter(
            pl.col("ds").is_between(
                lower_bound = history_start,
                upper_bound = forecast_end,
                closed="both",
            )
        )

        # ============================================================
        # FILTER DATA BY STATE
        # ============================================================

        filtered_df = filtered_df.filter(
            pl.col("state").is_in(
                tickers
            )
        )

        if filtered_df.is_empty():

            self.st.warning(
                "No data available for the selected "
                "states and time horizon."
            )

            return

        # ============================================================
        # NORMALIZED DATA
        # ============================================================
        #
        # We aggregate the selected states by date.
        #
        # IMPORTANT:
        # Actual values after forecast_origin are explicitly
        # converted to null.
        #
        # This guarantees that the Actual line stops exactly
        # at the last historical date.
        #

        normalized = (
            filtered_df
            .group_by("ds")
            .agg([
                pl.col("actual").sum().alias("Actual"),
                pl.col("prophet").sum().alias("Prophet"),
                pl.col("holt_winters").sum().alias("Holt-Winters"),
            ])
            .with_columns(
                pl.when(pl.col("ds") > forecast_origin).then(pl.lit(None))
                .otherwise(pl.col("Actual")).alias("Actual")
            )
            .rename({
                "ds": "Date",
            })
            .sort("Date")
        )

        # ============================================================
        # STATE AGGREGATION
        # ============================================================
        #
        # Only historical actual sales are used.
        #

        state_agg = (
            filtered_df
            .filter(pl.col("ds") <= forecast_origin)
            .group_by("state")
            .agg(
                pl.col("actual").sum().alias("actual"),
                pl.col("ds").max().alias("Date"),
            )
        )

        # ============================================================
        # CHART
        # ============================================================

        with right_cell:

            # --------------------------------------------------------
            # Base chart
            # --------------------------------------------------------

            base_chart = (
                alt.Chart(normalized)
                .transform_fold(
                    fold=[
                        "Actual",
                        "Prophet",
                        "Holt-Winters",
                    ],
                    as_=[
                        "Model",
                        "Value",
                    ],
                )
                .mark_line(
                    point = False,
                    interpolate = "linear",
                )
                .encode(
                    x = alt.X(
                        shorthand = "Date:T",
                        title = "Date",
                    ),

                    y=alt.Y(
                        shorthand = "Value:Q",
                        title = "Sales",
                        scale = alt.Scale(
                            zero = False,
                            padding = 20,
                        ),
                    ),

                    color = alt.Color(
                        shorthand = "Model:N",
                        title="Model",
                        scale=alt.Scale(
                            domain=[
                                "Holt-Winters",
                                "Prophet",
                                "Actual",
                            ],
                            range=[
                                self.model_colors["Holt-Winters"],
                                self.model_colors["Prophet"],
                                self.model_colors["Actual"],
                            ],
                        ),
                    ),

                    tooltip=[
                        alt.Tooltip(
                            shorthand = "Date:T",
                            title = "Date",
                            format = "%Y-%m-%d",
                        ),

                        alt.Tooltip(
                            shorthand = "Model:N",
                            title = "Model",
                        ),

                        alt.Tooltip(
                            shorthand = "Value:Q",
                            title = "Sales",
                            format = ",.2f",
                        ),
                    ],
                )
                .properties(
                    title = (
                        "Sales Forecast Comparison "
                        f"— {selected_horizon}"
                    ),
                )
            )

            # --------------------------------------------------------
            # Forecast origin
            # --------------------------------------------------------

            forecast_rule = (
                alt.Chart(
                    pl.DataFrame({
                        "forecast_origin": [
                            forecast_origin
                        ]
                    })
                )
                .mark_rule(
                    strokeDash = [
                        6,
                        4,
                    ],
                )
                .encode(
                    x = alt.X(
                        shorthand = "forecast_origin:T"
                    ),

                    tooltip=[
                        alt.Tooltip(
                            shorthand = "forecast_origin:T",
                            title = "Forecast starts",
                            format = "%Y-%m-%d",
                        )
                    ],
                )
            )

            # --------------------------------------------------------
            # Combine charts
            # --------------------------------------------------------

            chart = (
                base_chart
                + forecast_rule
            )

            self.st.altair_chart(
                chart,
                use_container_width = True,
            )

        # ============================================================
        # BOTTOM LEFT - METRICS
        # ============================================================

        bottom_left_cell = cols[0].container(
            border = True,
            height = "stretch",
            vertical_alignment = "center",
        )

        # ============================================================
        # SELECTED STATES
        # ============================================================

        selected_states = (
            state_agg
            .filter(
                pl.col("state").is_in(
                    tickers
                )
            )
            .sort(
                "actual",
                descending=True,
            )
        )

        if selected_states.is_empty():

            self.st.warning(
                "No sales data available for "
                "the selected states."
            )

            return

        # ============================================================
        # AVERAGE SALES
        # ============================================================

        average_sales = (
            selected_states
            .select(
                pl.col("actual").mean()
            )
            .item()
        )

        # ============================================================
        # BEST / WORST STATE
        # ============================================================

        best_state = (
            selected_states
            .row(
                0,
                named = True,
            )
        )

        worst_state = (
            selected_states
            .row(
                -1,
                named = True,
            )
        )

        # ============================================================
        # DELTA VS AVERAGE
        # ============================================================

        if (
            average_sales is not None
            and average_sales != 0
        ):

            best_delta = (
                (
                    best_state["actual"]
                    - average_sales
                )
                / average_sales
            ) * 100

            worst_delta = (
                (
                    worst_state["actual"]
                    - average_sales
                )
                / average_sales
            ) * 100

        else:

            best_delta = 0
            worst_delta = 0

        # ============================================================
        # METRICS
        # ============================================================

        with bottom_left_cell:

            metric_cols = self.st.columns(2)

            metric_cols[0].metric(
                label = "Best state in sales",

                value=best_state[
                    "state"
                ],

                delta = (
                    f"{best_delta:+.2f}% "
                    "vs average"
                ),

                width = "content",
            )

            metric_cols[1].metric(
                label = "Worst state in sales",

                value = worst_state[
                    "state"
                ],

                delta = (
                    f"{worst_delta:+.2f}% "
                    "vs average"
                ),

                width = "content",
            )

        state_normalized = (
            filtered_df
            .group_by(["ds", "state"])
            .agg([
                pl.col("actual")
                .sum()
                .alias("Actual"),

                pl.col("prophet")
                .sum()
                .alias("Prophet"),

                pl.col("holt_winters")
                .sum()
                .alias("Holt-Winters"),
            ])
            .sort(["state", "ds"])
        )

        # ============================================================
        # STATE FORECAST COMPARISON
        # ============================================================

        self.st.subheader(
            "📊 State Sales Forecast Comparison"
        )

        NUM_COLS = 2

        chart_cols = self.st.columns(NUM_COLS)


        # ============================================================
        # STATE NORMALIZED DATA
        # ============================================================

        state_normalized = (
            filtered_df
            .group_by(["ds", "state"])
            .agg([
                pl.col("actual")
                .sum()
                .alias("Actual"),

                pl.col("prophet")
                .sum()
                .alias("Prophet"),

                pl.col("holt_winters")
                .sum()
                .alias("Holt-Winters"),
            ])
            .with_columns(
                pl.when(
                    pl.col("ds") > forecast_origin
                )
                .then(
                    pl.lit(None)
                )
                .otherwise(
                    pl.col("Actual")
                )
                .alias("Actual")
            )
            .sort([
                "state",
                "ds",
            ])
        )


        # ============================================================
        # CREATE ONE SET OF CHARTS FOR EACH STATE
        # ============================================================

        for i, ticker in enumerate(tickers):

            # --------------------------------------------------------
            # Current state
            # --------------------------------------------------------

            current_state = (
                state_normalized
                .filter(
                    pl.col("state") == ticker
                )
                .sort("ds")
            )

            if current_state.is_empty():
                continue

            # ========================================================
            # FIRST CHART
            # ========================================================

            plot_data = (
                current_state
                .select([
                    "ds",
                    "Actual",
                    "Prophet",
                    "Holt-Winters",
                ])
                .unpivot(
                    index = "ds",
                    on = [
                        "Actual",
                        "Prophet",
                        "Holt-Winters",
                    ],
                    variable_name = "Model",
                    value_name = "Value",
                )
            )

            chart = (
                alt.Chart(plot_data)
                .mark_line(
                    point = False,
                    interpolate = "linear",
                )
                .encode(
                    x = alt.X(
                        shorthand = "ds:T",
                        title = "Date",
                    ),

                    y = alt.Y(
                        shorthand = "Value:Q",
                        title = "Sales",
                        scale = alt.Scale(
                            zero = False
                        ),
                    ),

                    color = alt.Color(
                        shorthand = "Model:N",
                        title = "Model",
                        scale = alt.Scale(
                            domain = [
                                "Holt-Winters",
                                "Prophet",
                                "Actual",
                            ],
                            range=[
                                self.model_colors["Holt-Winters"],
                                self.model_colors["Prophet"],
                                self.model_colors["Actual"],
                            ],
                        ),
                    ),

                    tooltip=[
                        alt.Tooltip(
                            shorthand = "ds:T",
                            title = "Date",
                            format = "%Y-%m-%d",
                        ),

                        alt.Tooltip(
                            shorthand = "Model:N",
                            title = "Model",
                        ),

                        alt.Tooltip(
                            shorthand = "Value:Q",
                            title = "Sales",
                            format = ",.2f",
                        ),
                    ],
                )
                .properties(
                    title = (
                        f"{ticker} — Sales Forecast"
                    ),
                    height = 300,
                )
            )

            # --------------------------------------------------------
            # Forecast origin
            # --------------------------------------------------------

            forecast_rule = (
                alt.Chart(
                    pl.DataFrame({
                        "forecast_origin": [
                            forecast_origin
                        ]
                    })
                )
                .mark_rule(
                    strokeDash = [
                        6,
                        4,
                    ]
                )
                .encode(
                    x = alt.X(
                        shorthand = "forecast_origin:T"
                    ),

                    tooltip=[
                        alt.Tooltip(
                            shorthand = "forecast_origin:T",
                            title = "Forecast starts",
                            format = "%Y-%m-%d",
                        )
                    ],
                )
            )

            chart = (
                chart
                + forecast_rule
            )

            cell = chart_cols[
                0
            ].container(
                border = True
            )

            cell.altair_chart(
                chart,
                use_container_width = True,
            )

            # ========================================================
            # SECOND CHART - DELTA BETWEEN MODELS
            # ========================================================
            #
            # Instead of comparing with Peer Average, this chart
            # shows the difference between the forecast models.
            #
            # Prophet - Actual
            # Holt-Winters - Actual
            #

            delta_data = (
                current_state
                .select([
                    "ds",

                    (
                        pl.col("Prophet")
                        - pl.col("Actual")
                    )
                    .alias("Prophet vs Actual"),

                    (
                        pl.col("Holt-Winters")
                        - pl.col("Actual")
                    )
                    .alias(
                        "Holt-Winters vs Actual"
                    ),
                ])
                .unpivot(
                    index = "ds",
                    on = [
                        "Prophet vs Actual",
                        "Holt-Winters vs Actual",
                    ],
                    variable_name = "Comparison",
                    value_name = "Delta",
                )
            )

            delta_chart = (
                alt.Chart(delta_data)
                .mark_area(
                    opacity = 0.5
                )
                .encode(
                    x = alt.X(
                        shorthand = "ds:T",
                        title = "Date",
                    ),

                    y=alt.Y(
                        shorthand = "Delta:Q",
                        title = "Difference",
                        scale = alt.Scale(
                            zero = False
                        ),
                    ),

                    color = alt.Color(
                        shorthand = "Comparison:N",
                        title = "Comparison",
                        scale = alt.Scale(
                            domain = [
                                "Holt-Winters vs Actual",
                                "Prophet vs Actual",
                            ],
                            range = [
                                self.delta_colors["Holt-Winters vs Actual"],
                                self.delta_colors["Prophet vs Actual"],
                            ],
                        ),
                    ),

                    tooltip = [
                        alt.Tooltip(
                            shorthand = "ds:T",
                            title = "Date",
                            format = "%Y-%m-%d",
                        ),

                        alt.Tooltip(
                            shorthand = "Comparison:N",
                            title = "Comparison",
                        ),

                        alt.Tooltip(
                            shorthand = "Delta:Q",
                            title = "Difference",
                            format = ",.2f",
                        ),
                    ],
                )
                .properties(
                    title = (
                        f"{ticker} — Forecast Delta"
                    ),
                    height = 300,
                )
            )

            # --------------------------------------------------------
            # Forecast origin for delta chart
            # --------------------------------------------------------

            delta_forecast_rule = (
                alt.Chart(
                    pl.DataFrame({
                        "forecast_origin": [
                            forecast_origin
                        ]
                    })
                )
                .mark_rule(
                    strokeDash = [
                        6,
                        4,
                    ]
                )
                .encode(
                    x = alt.X(
                        shorthand = "forecast_origin:T"
                    ),

                    tooltip = [
                        alt.Tooltip(
                            shorthand = "forecast_origin:T",
                            title = "Forecast starts",
                            format = "%Y-%m-%d",
                        )
                    ],
                )
            )

            delta_chart = (
                delta_chart
                + delta_forecast_rule
            )

            cell = chart_cols[
                1
            ].container(
                border = True
            )

            cell.altair_chart(
                delta_chart,
                use_container_width = True,
            )