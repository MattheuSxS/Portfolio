import polars as pl
import streamlit as st
import plotly.express as px
from utils.bigquery import BigQuery


@st.cache_data(ttl=1800)
def load_data(_bq_client: BigQuery) -> pl.DataFrame:
    try:
        df = _bq_client.read_bq("sql_feedback")

        df = df.with_columns(
                pl.col("feedback_date").cast(pl.Utf8)
            )
        df = df.with_columns(
            pl.col("feedback_date").str.strptime(pl.Date, "%Y-%m-%d").alias("feedback_date")
        )
        return df
    except Exception as e:
        st.error(f"Error loading feedback data: {e}")
        return pl.DataFrame()


class FeedbackDashboard(BigQuery):
    def __init__(self, project: str, st: any):
        super().__init__(project)
        self.st = st
        self.df = None

    def render_dashboard(self):
        self.df = load_data(self)

        if self.df.is_empty():
            self.st.warning("No feedback data found or error loading data.")
            return

        self.st.header("💬 Customer feedback regarding the product")

        col1, col2 = self.st.columns(2)
        with col1:
            sentiments = self.st.multiselect(
                label   = "Feelings",
                options = self.df['sentiment'].unique().to_list(),
                default = self.df['sentiment'].unique().to_list(),
                key     = "feedback_sentiments"
            )
        with col2:
            ratings = self.st.multiselect(
                label   = "Ratings",
                options = self.df['rating'].unique().to_list(),
                default = self.df['rating'].unique().to_list(),
                key     = "feedback_ratings"
            )

        min_date = self.df['feedback_date'].min()
        max_date = self.df['feedback_date'].max()

        date_range = self.st.date_input(
            label       = "Feedback Period",
            value       = [min_date, max_date],
            min_value   = min_date,
            max_value   = max_date,
            key         = "feedback_date_range"
        )

        if len(date_range) == 2:
            start_date = date_range[0]
            end_date = date_range[1]

            filtered_df = self.df.filter(
                (pl.col('sentiment').is_in(sentiments)) &
                (pl.col('rating').is_in(ratings)) &
                (pl.col('feedback_date') >= pl.date(start_date.year, start_date.month, start_date.day)) &
                (pl.col('feedback_date') <= pl.date(end_date.year, end_date.month, end_date.day))
            )
        else:
            filtered_df = self.df.filter(
                (pl.col('sentiment').is_in(sentiments)) &
                (pl.col('rating').is_in(ratings))
            )

        col1, col2 = self.st.columns([2, 1])

        with col1:
            self.st.subheader("📈 Evolution of Feelings Over Time")

            daily_sentiment = filtered_df.group_by(['feedback_date', 'sentiment']).agg([
                pl.count().alias('count')
            ]).sort('feedback_date')

            if not daily_sentiment.is_empty():
                daily_sentiment_pd = daily_sentiment
                fig = px.line(
                    data_frame  = daily_sentiment_pd,
                    x           = 'feedback_date',
                    y           = 'count',
                    color       = 'sentiment',
                    title       = "Evolution of Feelings Over Time",
                    labels      = {
                                    'feedback_date': 'Feedback Date',
                                    'count': 'Number of Feedbacks'
                                }
                )
                fig.update_layout(height=400)
                self.st.plotly_chart(fig, use_container_width=True)

        with col2:
            self.st.subheader("📋 Feedback Metrics")

            total_feedbacks = filtered_df.height
            sentiment_distribution = filtered_df['sentiment'].value_counts()
            avg_rating = filtered_df['rating'].mean()

            self.st.metric("Total Feedbacks", f"{total_feedbacks:,}")
            self.st.metric("Average Rating", f"{avg_rating:.1f} ⭐")

            self.st.subheader("🎭 Distribution of Feelings")
            for sentiment, count in sentiment_distribution.sort(by='count', descending=True).rows():
                percentage = (count / total_feedbacks) * 100
                self.st.write(f"**{sentiment}:** {count} ({percentage:.1f}%)")

        col3, col4 = self.st.columns(2)

        with col3:
            self.st.subheader("🥧 Distribution of Feelings")

            sentiment_counts = filtered_df['sentiment'].value_counts()

            if not sentiment_counts.is_empty():
                fig_pizza = px.pie(
                    data_frame              = sentiment_counts,
                    values                  = 'count',
                    names                   = 'sentiment',
                    title                   = "Distribution of Feelings",
                    hole                    = 0.3,
                    color_discrete_sequence = px.colors.qualitative.Set3
                )

                fig_pizza.update_traces(
                    textposition    = 'inside',
                    textinfo        = 'percent+label',
                    hovertemplate   = '<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}'
                )

                fig_pizza.update_layout(
                    height      = 500,
                    showlegend  = True
                )

                self.st.plotly_chart(fig_pizza, use_container_width=True)
            else:
                self.st.info(" No data available to display the pie chart.")

        with col4:
            self.st.subheader("📊 Distribution of Ratings")

            rating_counts = filtered_df['rating'].value_counts().sort('rating')

            if not rating_counts.is_empty():
                fig_barras = px.bar(
                    data_frame              = rating_counts,
                    y                       = 'count',
                    x                       = 'rating',
                    title                   = "Distribution of Ratings",
                    labels                  = {
                                                'rating': 'Rating',
                                                'count': 'Number of Ratings'
                                            },
                    color                   = 'count',
                    color_continuous_scale  = 'blues'
                )

                fig_barras.update_traces(
                    hovertemplate       = '<b>Rating: %{x}</b><br>Quantidade: %{y}',
                    marker_line_color   = 'black',
                    marker_line_width   = 1
                )

                fig_barras.update_layout(
                    height      = 500,
                    xaxis_title = "Rating",
                    yaxis_title = "Number of Ratings",
                    showlegend  = False
                )

                fig_barras.update_traces(
                    texttemplate = '%{y}',
                    textposition = 'outside'
                )

                self.st.plotly_chart(fig_barras, use_container_width=True)
            else:
                self.st.info("No data available to display the bar chart.")

        with self.st.expander("🔍 View Filtered Data"):
            self.st.write(f"**Total records after filters:** {filtered_df.height}")
            self.st.dataframe(
                filtered_df.select(['sentiment', 'rating', 'feedback_date']),
                use_container_width = True,
                height              = 300
            )