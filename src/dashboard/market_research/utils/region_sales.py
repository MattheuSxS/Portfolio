import polars as pl
import streamlit as st
import plotly.express as px
from utils.bigquery import BigQuery


@st.cache_data(ttl=3600)
def load_data(_bq_client: BigQuery) -> pl.DataFrame:
    try:
        df = _bq_client.read_bq("region_sales_query")
        df = df.with_columns(
            pl.col("purchase_date").str.strptime(pl.Date, "%Y-%m-%d")
        )
        return df
    except Exception as e:
        st.error(f"Error loading region sales data: {e}")
        return pl.DataFrame()


class RegionSalesDashboard(BigQuery):
    def __init__(self, project: str, st: any):
        super().__init__(project)
        self.st = st
        self.df = None

    def render_dashboard(self):
        self.df = load_data(self)

        if self.df.is_empty():
            self.st.warning("No data found or error loading data.")
        else:
            # Filters
            regions = self.st.sidebar.multiselect(
                "Regions",
                options=self.df['region'].unique().to_list(),
                default=self.df['region'].unique().to_list()
            )

            states = self.st.sidebar.multiselect(
                "States",
                options=self.df['state'].unique().to_list(),
                default=self.df['state'].unique().to_list()
            )

            # Apply filters
            filtered_df = self.df.filter(
                pl.col('region').is_in(regions) &
                pl.col('state').is_in(states)
            )

            # Layout principal
            col1, col2 = self.st.columns([2, 1])

            with col1:
                self.st.subheader("📈 Evolution of Sales Over Time")

                # Select metric for the chart
                metric = self.st.radio(
                    "Select metric:",
                    ["final_price", "discount_applied"],
                    format_func=lambda x: "Total Value" if x == "final_price" else "Discount Applied",
                    horizontal=True
                )

                # Agrupar dados por data para o gráfico de linhas
                daily_data = filtered_df.group_by('purchase_date').agg([
                    pl.col('final_price').sum().alias('final_price'),
                    pl.col('discount_applied').sum().alias('discount_applied')
                ]).sort('purchase_date')

                # Converter para pandas para o Plotly (até que o Plotly tenha suporte nativo ao Polars)
                daily_data_pd = daily_data.to_pandas()

                # Criar gráfico de linhas
                fig = px.line(
                    daily_data_pd,
                    x='purchase_date',
                    y=metric,
                    title=f"Evolution of {'Total Value' if metric == 'final_price' else 'Discount Applied'} Over Time",
                    labels={
                        'purchase_date': 'Purchase Date',
                        'final_price': 'Total Value (R$)',
                        'discount_applied': 'Discount Applied (R$)'
                    },
                    color_discrete_sequence=['#1f77b4']
                )

                # Melhorar layout do gráfico
                fig.update_layout(
                    xaxis_title="Purchase Date",
                    yaxis_title="Value (R$)",
                    hovermode='x unified',
                    height=500
                )

                self.st.plotly_chart(fig, use_container_width=True)

            with col2:
                self.st.subheader("📋 Key Metrics")

                # Calculate metrics with Polars
                total_sales = filtered_df['final_price'].sum()
                total_discount = filtered_df['discount_applied'].sum()
                avg_sale = filtered_df['final_price'].mean()

                self.st.metric("Total Sales Value", f"R$ {total_sales:,.2f}")
                self.st.metric("Total Discounts", f"R$ {total_discount:,.2f}")
                self.st.metric("Average Ticket", f"R$ {avg_sale:,.2f}")

                # Informações adicionais
                self.st.subheader("ℹ️ Informações")
                min_date = filtered_df['purchase_date'].min()
                max_date = filtered_df['purchase_date'].max()
                self.st.write(f"**Period:** {min_date.strftime('%d/%m/%Y')} - {max_date.strftime('%d/%m/%Y')}")
                self.st.write(f"**Total Records:** {filtered_df.height:,}")
                self.st.write(f"**Regions:** {len(regions)}")
                self.st.write(f"**States:** {len(states)}")

            # Análises adicionais com Polars
            self.st.subheader("🔍 Additional Analysis")

            col3, col4 = self.st.columns(2)

            with col3:
                # Vendas por região
                sales_by_region = filtered_df.group_by('region').agg([
                    pl.col('final_price').sum().alias('total_sales'),
                    pl.col('discount_applied').sum().alias('total_discount')
                ]).sort('total_sales', descending=True)

                self.st.write("**Sales by Region:**")
                self.st.dataframe(sales_by_region.to_pandas(), use_container_width=True)

            with col4:
                # Sales by state
                sales_by_state = filtered_df.group_by('state').agg([
                    pl.col('final_price').sum().alias('total_sales'),
                    pl.col('discount_applied').sum().alias('total_discount')
                ]).sort('total_sales', descending=True).head(10)

                self.st.write("**Top 10 States by Sales:**")
                self.st.dataframe(sales_by_state.to_pandas(), use_container_width=True)

            # Tabela com dados detalhados
            self.st.subheader("📊 Dados Detalhados")

            # Selecionar colunas para exibir
            available_columns = self.df.columns
            display_columns = self.st.multiselect(
                "Colunas para exibir:",
                options=available_columns,
                default=['purchase_date', 'region', 'state', 'final_price', 'discount_applied']
            )

            if display_columns:
                self.st.dataframe(
                    filtered_df.select(display_columns).sort('purchase_date', descending=True).to_pandas(),
                    use_container_width=True
                )

            # Download dos dados
            csv_data = filtered_df.write_csv()
            self.st.download_button(
                label="📥 Download data as CSV",
                data=csv_data,
                file_name="sales_data.csv",
                mime="text/csv"
            )