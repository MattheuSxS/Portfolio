import polars as pl
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.bigquery import BigQuery


@st.cache_data(ttl=1200)
def load_products_data(_bq_client: BigQuery) -> pl.DataFrame:
    try:
        df = _bq_client.read_bq("sql_products_sales")
        df = df.with_columns(
            pl.col("purchase_date").str.strptime(pl.Date, "%Y-%m-%d")
        )
        return df
    except Exception as e:
        st.error(f"Error loading products sales data: {e}")
        return pl.DataFrame()


class ProductsSalesDashboard(BigQuery):
    def __init__(self, project: str, st: any):
        super().__init__(project)
        self.st = st
        self.df = None

    def create_top_products_chart(self, df):
        top_products = df.group_by(['region', 'name']).agg([
            pl.sum('final_price').alias('total_sales'),
            pl.sum('discount_applied').alias('total_discount')
        ]).sort('total_sales', descending=True).head(20)

        fig = px.bar(
            top_products.to_pandas(),
            x                       = 'name',
            y                       = 'total_sales',
            color                   = 'region',
            title                   = "📊 Top 20 Products by Region (Last 90 Days)",
            barmode                 = 'group',
            labels                  = {
                                        'total_sales': 'Total Value (R$)',
                                        'name': 'Product',
                                        'region': 'Region'
                                    },
            color_discrete_sequence = px.colors.qualitative.Set3
        )

        fig.update_layout(
            height          = 500,
            xaxis_tickangle = -45,
            showlegend      = True
        )

        return fig

    def create_status_region_chart(self, df):
        status_by_region = df.group_by(['region', 'order_status']).agg([
            pl.sum('final_price').alias('total_sales'),
            pl.count().alias('order_count')
        ])

        fig = px.bar(
            status_by_region.to_pandas(),
            x                       = 'region',
            y                       = 'total_sales',
            color                   = 'order_status',
            title                   = "🔄 Order Status by Region",
            barmode                 = 'stack',
            labels                  = {
                                        'total_sales': 'Total Value (R$)',
                                        'region': 'Region',
                                        'order_status': 'Status'
                                    },
            color_discrete_sequence  = ['#EF553B','#00CC96']
        )

        fig.update_layout(
            height      = 400,
            showlegend  = True
        )

        return fig

    def create_heatmap_products_region(self, df):
        top_products = df.group_by('name').agg([
            pl.sum('final_price').alias('total_sales')
        ]).sort('total_sales', descending=True).head(15)['name'].to_list()

        filtered_df = df.filter(pl.col('name').is_in(top_products))

        pivot_data = filtered_df.group_by(['name', 'region']).agg([
            pl.sum('final_price').alias('total_sales')
        ]).to_pandas().pivot_table(
            index       = 'name',
            columns     = 'region',
            values      = 'total_sales',
            fill_value  = 0
        )

        fig = px.imshow(
            pivot_data,
            title                   = "🔥 Heatmap: Sales by Product and Region",
            labels                  = dict(x="Region", y="Product", color="Sales (R$)"),
            aspect                  = "auto",
            color_continuous_scale  = "YlOrRd",
            text_auto               = True
        )

        fig.update_layout(
            height      = 600,
            xaxis_title = "Region",
            yaxis_title = "Product"
        )

        return fig

    def create_donut_products_chart(self, df):
        category_sales = df.group_by('name').agg([
            pl.sum('final_price').alias('total_sales'),
            pl.count().alias('order_count')
        ]).sort('total_sales', descending=True).head(10)

        fig = px.pie(
            data_frame              = category_sales,
            values                  = 'total_sales',
            names                   = 'name',
            title                   = "🥧 Top 10 Products - Share of Sales",
            hole                    = 0.4,
            color_discrete_sequence = px.colors.sequential.Viridis
        )

        fig.update_traces(
            textposition    = 'inside',
            textinfo        = 'percent+label',
            hovertemplate   = '<b>%{label}</b><br>Vendas: R$ %{value:,.2f}<br>Percentual: %{percent}'
        )

        fig.update_layout(
            height      = 500,
            showlegend  = False
        )

        return fig

    def create_temporal_top_products(self, df):
        top_5_products = df.group_by('name').agg([
            pl.sum('final_price').alias('total_sales')
        ]).sort('total_sales', descending=True).head(5)['name'].to_list()

        top_products_data = df.filter(pl.col('name').is_in(top_5_products))

        daily_top_products = top_products_data.group_by(['purchase_date', 'name']).agg([
            pl.sum('final_price').alias('daily_sales')
        ]).sort('purchase_date')

        fig = px.line(
            data_frame              = daily_top_products,
            x                       = 'purchase_date',
            y                       = 'daily_sales',
            color                   = 'name',
            title                   = "📈 Evolution of the 5 Best-Selling Products",
            labels                  = {
                                        'daily_sales': 'Daily Sales (R$)',
                                        'purchase_date': 'Date',
                                        'name': 'Product'
                                    },
            color_discrete_sequence = px.colors.qualitative.Bold
        )

        fig.update_layout(
            height      = 500,
            hovermode   = 'x unified',
            xaxis_title = "Date",
            yaxis_title = "Daily Sales (R$)"
        )

        return fig

    def create_weekly_heatmap(self, df):
        try:
            if df['purchase_date'].dtype != pl.Utf8:
                df = df.with_columns(pl.col("purchase_date").cast(pl.Utf8))

            df_weekly = df.with_columns(
                pl.col('purchase_date')
                .str.strptime(pl.Date, "%Y-%m-%d", strict=False)
                .dt.truncate("1w")
                .alias('week_start')
            )

            top_products = df.group_by('name').agg([
                pl.sum('final_price').alias('total_sales')
            ]).sort('total_sales', descending=True).head(12)

            top_product_names = top_products['name'].to_list()

            weekly_data = df_weekly.filter(
                pl.col('name').is_in(top_product_names)
            ).group_by(['week_start', 'name']).agg([
                pl.sum('final_price').alias('weekly_sales')
            ]).sort('week_start')

            weekly_pd = weekly_data.to_pandas()

            weekly_pd['week_label'] = weekly_pd['week_start'].dt.strftime('%d/%m')

            pivot_data = weekly_pd.pivot_table(
                index       = 'name',
                columns     = 'week_label',
                values      = 'weekly_sales',
                fill_value  = 0
            )

            fig = px.imshow(
                pivot_data,
                title                   = "🗓️ Weekly sales by product",
                labels                  = dict(x="Semana", y="Produto", color="Vendas (R$)"),
                aspect                  = "auto",
                color_continuous_scale  = "Blues",
                text_auto               = '.2s'
            )

            fig.update_layout(
                height      = 600,
                xaxis_title = "Week (Start)",
                yaxis_title = "Product"
            )

            return fig

        except Exception as e:
            self.st.error(f"Error creating weekly heatmap: {e}")

            fig = go.Figure()
            fig.update_layout(
                title   = "🗓️ Weekly Sales by Product (Data Temporarily Unavailable)",
                height  = 400
            )
            return fig


    def create_category_donut(self, df):
        category_share = df.group_by('category').agg([
            pl.sum('final_price').alias('total_sales'),
            pl.count().alias('order_count')
        ]).sort('total_sales', descending=True)

        fig = px.pie(
            category_share.to_pandas(),
            values                  = 'total_sales',
            names                   = 'category',
            title                   = "🥧 Market Share by Category",
            hole                    = 0.5,
            color_discrete_sequence = px.colors.qualitative.Pastel
        )

        fig.update_traces(
            textposition    = 'inside',
            textinfo        = 'percent+label',
            hovertemplate   = '<b>%{label}</b><br>Vendas: R$ %{value:,.2f}<br>Participação: %{percent}'
        )

        fig.update_layout(height=500, showlegend=False)
        return fig

    def create_category_status_heatmap(self, df):
        category_status = df.group_by(['category', 'order_status']).agg([
            pl.sum('final_price').alias('total_sales')
        ])

        pivot_data = category_status.to_pandas().pivot_table(
            index       = 'category',
            columns     = 'order_status',
            values      = 'total_sales',
            fill_value  = 0
        )

        fig = px.imshow(
            pivot_data,
            title                   = "🔥 Performance by Category and Status",
            labels                  = dict(x="Status", y="Category", color="Sales (R$)"),
            aspect                  = "auto",
            color_continuous_scale  = "YlOrRd",
            text_auto               = True
        )

        fig.update_layout(height=400)
        return fig

    def create_category_region_stacked(self, df):
        category_region = df.group_by(['category', 'region']).agg([
            pl.sum('final_price').alias('total_sales'),
            pl.count().alias('order_count')
        ])

        fig = px.bar(
            data_frame  = category_region,
            x           = 'region',
            y           = 'total_sales',
            color       = 'category',
            title       = "📦 Sales by Category and Region",
            barmode     = 'stack',
            labels      = {'total_sales': 'Sales (R$)', 'region': 'Region', 'category': 'Category'}
        )

        fig.update_layout(height=500)
        return fig

    def create_category_discount_scatter(self, df):
        category_discount = df.group_by('category').agg([
            pl.sum('final_price').alias('total_sales'),
            pl.sum('discount_applied').alias('total_discount'),
            (pl.sum('discount_applied') / pl.sum('final_price') * 100).alias('discount_rate_%'),
            pl.count().alias('order_count')
        ])

        fig = px.scatter(
            data_frame              = category_discount,
            x                       = 'total_sales',
            y                       = 'total_discount',
            size                    = 'order_count',
            color                   = 'discount_rate_%',
            hover_name              = 'category',
            title                   = "🎯 Relationship: Sales vs Discounts by Category",
            labels                  = {
                                            'total_sales': 'Total Sales (R$)',
                                            'total_discount': 'Total Discounts (R$)',
                                            'discount_rate_%': 'Discount Rate (%)'
                                        },
            color_continuous_scale  = 'Viridis'
        )

        fig.update_layout(height=500)
        return fig

    def create_category_sunburst(self, df):
        top_products_per_category = df.group_by(['category', 'name']).agg([
            pl.sum('final_price').alias('total_sales')
        ]).sort(['category', 'total_sales'], descending=[False, True])

        categories = top_products_per_category['category'].unique().to_list()
        filtered_data = pl.DataFrame()

        for category in categories:
            top_3 = top_products_per_category.filter(
                pl.col('category') == category
            ).head(3)
            filtered_data = pl.concat([filtered_data, top_3])

        hierarchical_data = df.filter(
            pl.col('name').is_in(filtered_data['name'].to_list())
        ).group_by(['category', 'name', 'region']).agg([
            pl.sum('final_price').alias('total_sales')
        ])

        fig = px.sunburst(
            data_frame              = hierarchical_data,
            path                    = ['category', 'name', 'region'],
            values                  = 'total_sales',
            title                   = "🌐 Sales Hierarchy: Category > Product > Region",
            color                   = 'total_sales',
            color_continuous_scale  = 'Viridis'
        )

        fig.update_layout(height=600)
        return fig

    def create_category_temporal(self, df):
        df_weekly = df.with_columns(
            pl.col('purchase_date').cast(pl.Utf8).str.strptime(pl.Date, "%Y-%m-%d").dt.truncate("1w")
        )

        weekly_categories = df_weekly.group_by(['purchase_date', 'category']).agg([
            pl.sum('final_price').alias('weekly_sales')
        ]).sort('purchase_date')

        fig = px.line(
            data_frame  = weekly_categories,
            x           = 'purchase_date',
            y           = 'weekly_sales',
            color       = 'category',
            title       = "📈 Weekly Evolution by Category",
            labels      = {'weekly_sales': 'Weekly Sales (R$)', 'purchase_date': 'Week', 'category': 'Category'}
        )

        fig.update_layout(height=500, hovermode='x unified')
        return fig

    def create_category_pivot_table(self, df):
        category_metrics = df.group_by(['category', 'region', 'order_status']).agg([
            pl.sum('final_price').alias('total_sales'),
            pl.sum('discount_applied').alias('total_discount'),
            pl.count().alias('order_count'),
            (pl.sum('discount_applied') / pl.sum('final_price') * 100).alias('discount_rate_%'),
            pl.mean('final_price').alias('avg_ticket')
        ]).sort('total_sales', descending=True)

        return category_metrics

    def add_category_analysis(self, filtered_df):

        self.st.header("📁 Analysis by Product Category")

        categories = self.st.multiselect(
            label   = "Categories:",
            options = filtered_df['category'].unique().to_list(),
            default = filtered_df['category'].unique().to_list(),
            key     = "products_categories"
        )

        category_df = filtered_df.filter(pl.col('category').is_in(categories))

        col1, col2 = self.st.columns(2)

        with col1:
            fig_donut = self.create_category_donut(category_df)
            self.st.plotly_chart(fig_donut, use_container_width=True)

            fig_heatmap = self.create_category_status_heatmap(category_df)
            self.st.plotly_chart(fig_heatmap, use_container_width=True)

        with col2:
            fig_stacked = self.create_category_region_stacked(category_df)
            self.st.plotly_chart(fig_stacked, use_container_width=True)

            fig_scatter = self.create_category_discount_scatter(category_df)
            self.st.plotly_chart(fig_scatter, use_container_width=True)

        self.st.plotly_chart(self.create_category_sunburst(category_df), use_container_width=True)
        self.st.plotly_chart(self.create_category_temporal(category_df), use_container_width=True)

        with self.st.expander("📊 Detailed Table by Category"):
            pivot_table = self.create_category_pivot_table(category_df)
            self.st.dataframe(pivot_table.to_pandas(), use_container_width=True, height=400)

    def render_dashboard(self):
        self.df = load_products_data(self)

        if self.df.is_empty():
            self.st.warning("No products sales data found.")
            return

        self.st.header("📦 Product Analysis by Region (Last 90 Days)")

        with self.st.container():
            col1, col2 = self.st.columns(2)

            with col1:
                regions = self.st.multiselect(
                    label   = "Regiões:",
                    options = self.df['region'].unique().to_list(),
                    default = self.df['region'].unique().to_list(),
                    key     = "products_regions"
                )

            with col2:
                status_options = self.st.multiselect(
                    label   = "Status:",
                    options = self.df['order_status'].unique().to_list(),
                    default = self.df['order_status'].unique().to_list(),
                    key     = "products_status"
                )

        filtered_df = self.df.filter(
            (pl.col('region').is_in(regions)) &
            (pl.col('order_status').is_in(status_options))
        )

        col1, col2 = self.st.columns(2)

        with col1:
            fig1 = self.create_top_products_chart(filtered_df)
            self.st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig5 = self.create_status_region_chart(filtered_df)
            self.st.plotly_chart(fig5, use_container_width=True)

        col3, col4 = self.st.columns(2)

        with col3:
            fig8 = self.create_donut_products_chart(filtered_df)
            self.st.plotly_chart(fig8, use_container_width=True)

        with col4:
            fig4 = self.create_temporal_top_products(filtered_df)
            self.st.plotly_chart(fig4, use_container_width=True)

        self.st.plotly_chart(self.create_heatmap_products_region(filtered_df), use_container_width=True)
        self.st.plotly_chart(self.create_weekly_heatmap(filtered_df), use_container_width=True)

        with self.st.expander("📋 Tabela Resumo - Top Produtos"):
            summary_table = filtered_df.group_by(['name', 'region', 'order_status']).agg([
                pl.sum('final_price').alias('total_sales'),
                pl.sum('discount_applied').alias('total_discount'),
                pl.count().alias('order_count')
            ]).sort('total_sales', descending=True).head(20)

            self.st.dataframe(
                summary_table,
                use_container_width = True,
                height              = 400
            )


        self.add_category_analysis(filtered_df)


        csv_data = filtered_df.write_csv()
        self.st.download_button(
            label="📥 Data Download ....",
            data=csv_data,
            file_name="dados_produtos.csv",
            mime="text/csv"
        )