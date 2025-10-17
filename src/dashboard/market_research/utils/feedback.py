import polars as pl
import streamlit as st
import plotly.express as px
from bigquery import BigQuery


@st.cache_data(ttl=3600)
def load_data(_bq_client: BigQuery) -> pl.DataFrame:
    try:
        df = _bq_client.read_bq("feedback_query")

        df = df.with_columns(
                pl.col("feedback_date").cast(pl.Utf8)
            )
        df = df.with_columns(
            pl.col("feedback_date").str.strptime(pl.Date, "%Y-%m-%d").alias("feedback_date")
        )
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados de feedback: {e}")
        return pl.DataFrame()


class FeedbackDashboard(BigQuery):
    def __init__(self, project: str, st: any):
        super().__init__(project)
        self.st = st
        self.df = None

    def feedback_dashboard(self):
        self.df = load_data(self)

        if self.df.is_empty():
            self.st.warning("Nenhum dado de feedback encontrado ou erro ao carregar dados.")
            return

        self.st.header("💬 Dashboard de Feedback")

        # Filtros para feedback
        col1, col2 = self.st.columns(2)
        with col1:
            sentiments = self.st.multiselect(
                "Sentimentos",
                options=self.df['sentiment'].unique().to_list(),
                default=self.df['sentiment'].unique().to_list(),
                key="feedback_sentiments"
            )
        with col2:
            ratings = self.st.multiselect(
                "Ratings",
                options=self.df['rating'].unique().to_list(),
                default=self.df['rating'].unique().to_list(),
                key="feedback_ratings"
            )

        # Filtro de data para feedback
        min_date = self.df['feedback_date'].min()
        max_date = self.df['feedback_date'].max()

        date_range = self.st.date_input(
            "Período do Feedback",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date,
            key="feedback_date_range"
        )

        # Aplicar filtros - CORREÇÃO AQUI
        if len(date_range) == 2:
            # Extrair ano, mês e dia dos objetos date
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

        # Layout principal de feedback
        col1, col2 = self.st.columns([2, 1])

        with col1:
            self.st.subheader("📈 Evolução Temporal de Sentimentos")

            # Agrupar dados por data e sentimento
            daily_sentiment = filtered_df.group_by(['feedback_date', 'sentiment']).agg([
                pl.count().alias('count')
            ]).sort('feedback_date')

            if not daily_sentiment.is_empty():
                daily_sentiment_pd = daily_sentiment.to_pandas()
                fig = px.line(
                    daily_sentiment_pd,
                    x='feedback_date',
                    y='count',
                    color='sentiment',
                    title="Evolução dos Sentimentos ao Longo do Tempo",
                    labels={
                        'feedback_date': 'Data do Feedback',
                        'count': 'Quantidade de Feedbacks'
                    }
                )
                fig.update_layout(height=400)
                self.st.plotly_chart(fig, use_container_width=True)

        with col2:
            self.st.subheader("📋 Métricas de Feedback")

            total_feedbacks = filtered_df.height
            sentiment_distribution = filtered_df['sentiment'].value_counts()
            avg_rating = filtered_df['rating'].mean()

            self.st.metric("Total de Feedbacks", f"{total_feedbacks:,}")
            self.st.metric("Rating Médio", f"{avg_rating:.1f} ⭐")

            self.st.subheader("🎭 Distribuição de Sentimentos")
            for sentiment, count in sentiment_distribution.sort(by='count', descending=True).rows():
                percentage = (count / total_feedbacks) * 100
                self.st.write(f"**{sentiment}:** {count} ({percentage:.1f}%)")

        # Gráficos de distribuição
        self.st.subheader("📊 Análises de Distribuição")

        col3, col4 = self.st.columns(2)

        with col3:
            # GRÁFICO DE PIZZA para sentiment
            self.st.subheader("🥧 Distribuição de Sentimentos")

            sentiment_counts = filtered_df['sentiment'].value_counts()

            if not sentiment_counts.is_empty():
                fig_pizza = px.pie(
                    sentiment_counts.to_pandas(),
                    values='count',
                    names='sentiment',
                    title="Distribuição de Sentimentos",
                    hole=0.3,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )

                fig_pizza.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}'
                )

                fig_pizza.update_layout(
                    height=500,
                    showlegend=True
                )

                self.st.plotly_chart(fig_pizza, use_container_width=True)
            else:
                self.st.info("Não há dados para exibir o gráfico de pizza.")

        with col4:
            # GRÁFICO DE BARRAS para rating
            self.st.subheader("📊 Distribuição de Ratings")

            rating_counts = filtered_df['rating'].value_counts().sort('rating')

            if not rating_counts.is_empty():
                fig_barras = px.bar(
                    rating_counts.to_pandas(),
                    x='rating',
                    y='count',
                    title="Distribuição de Ratings",
                    labels={
                        'rating': 'Rating',
                        'count': 'Quantidade de Avaliações'
                    },
                    color='count',
                    color_continuous_scale='blues'
                )

                fig_barras.update_traces(
                    hovertemplate='<b>Rating: %{x}</b><br>Quantidade: %{y}',
                    marker_line_color='black',
                    marker_line_width=1
                )

                fig_barras.update_layout(
                    height=500,
                    xaxis_title="Rating",
                    yaxis_title="Quantidade de Avaliações",
                    showlegend=False
                )

                fig_barras.update_traces(
                    texttemplate='%{y}',
                    textposition='outside'
                )

                self.st.plotly_chart(fig_barras, use_container_width=True)
            else:
                self.st.info("Não há dados para exibir o gráfico de barras.")

        # Visualização dos dados filtrados
        with self.st.expander("🔍 Visualizar Dados Filtrados"):
            self.st.write(f"**Total de registros após filtros:** {filtered_df.height}")
            self.st.dataframe(
                filtered_df.select(['sentiment', 'rating', 'feedback_date']).to_pandas(),
                use_container_width=True,
                height=300
            )