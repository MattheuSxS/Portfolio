import polars as pl
import streamlit as st
import plotly.express as px
from utils.bigquery import BigQuery
from utils.brazil_map import MapOfBrazil


@st.cache_data(ttl=1800)
def load_geo_sales_data(_bq_client: BigQuery) -> pl.DataFrame:
    try:
        df = _bq_client.read_bq("sql_region_sales")
        df = df.with_columns(
            pl.col("purchase_date").str.strptime(pl.Date, "%Y-%m-%d")
        )
        return df
    except Exception as e:
        st.error(f"Error loading geographic sales data: {e}")
        return pl.DataFrame()

class GeoSalesDashboard(BigQuery, MapOfBrazil):
    def __init__(self, project: str, st: any):
        BigQuery.__init__(self, project)
        MapOfBrazil.__init__(self) # I can remove it!
        self.st = st
        self.df = None

    def create_state_choropleth(self, df):
        geojson_data = self.get_brazil_geojson()

        state_totals = df.group_by('state').agg([
            pl.sum('final_price').alias('total_sales'),
            pl.sum('discount_applied').alias('total_discount')
        ])

        state_totals = state_totals.with_columns(
            pl.col("state").replace(self.state_names).alias("state_name")
        )
        # 'R$ %{value:,.2f}'
        fig = px.choropleth(
            data_frame              = state_totals,
            geojson                 = geojson_data,
            locations               = 'state',
            featureidkey            = "properties.sigla",
            color                   = 'total_sales',
            hover_name              = 'state_name',
            hover_data              = {
                                        'total_sales': ':,.2f',
                                        'total_discount': ':,.2f',
                                        'state': False
                                    },
            color_continuous_scale  = "Blues",
            title                   = "🗺️ Geographical Distribution of Sales by State"
        )

        fig.update_geos(
            fitbounds   = "locations",
            visible     = False
        )

        fig.update_layout(
            height  = 500,
            geo     = dict(bgcolor='rgba(0,0,0,0)')
        )

        fig.update_coloraxes(
            colorbar_title      = "Sales (R$)",
            colorbar_tickformat = ',.2f'
        )

        return fig

    def create_region_temporal(self, df):
        daily_region = df.group_by(['purchase_date', 'region']).agg([
            pl.sum('final_price').alias('daily_sales'),
            pl.sum('discount_applied').alias('daily_discount')
        ]).sort('purchase_date')

        fig = px.line(
            data_frame              = daily_region,
            x                       = 'purchase_date',
            y                       = 'daily_sales',
            color                   = 'region',
            title                   = "📈 Temporal Evolution of Sales by Region",
            labels                  = {
                                        'daily_sales': 'Daily Sales (R$)',
                                        'purchase_date': 'Date',
                                        'region': 'Region'
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

    def create_top_states_chart(self, df):
        top_states = df.group_by('state').agg([
            pl.sum('final_price').alias('total_sales'),
            pl.sum('discount_applied').alias('total_discount'),
            pl.count().alias('order_count'),
            (pl.sum('discount_applied') / pl.sum('final_price') * 100).alias('discount_rate_%')
        ]).sort('total_sales', descending=True).head(10)

        top_states = top_states.with_columns(
            pl.col("state").replace(self.state_names).alias("state_name")
        )

        fig = px.bar(
            data_frame              = top_states,
            x                       = 'state',
            y                       = 'total_sales',
            color                   = 'total_sales',
            title                   = "🏆 Top 10 States by Sales Volume",
            labels                  = {
                                        'total_sales': 'Total Sales (R$)',
                                        'state': 'State',
                                        'discount_rate_%': 'Discount rate (%)'
                                    },
            color_continuous_scale  = 'Viridis',
            hover_data              = ['state_name', 'order_count', 'discount_rate_%']
        )

        fig.update_traces(
            hovertemplate='<b>%{customdata[0]}</b><br>' +
                         'Sales: R$ %{y:,.2f}<br>' +
                         'Orders: %{customdata[1]:,}<br>' +
                         'Discount: %{customdata[2]:.1f}%<extra></extra>'
        )

        fig.update_layout(
            height      = 500,
            showlegend  = False,
            xaxis_title = "State",
            yaxis_title = "Total Sales (R$)"
        )

        return fig

    def create_region_donut(self, df):
        region_share = df.group_by('region').agg([
            pl.sum('final_price').alias('total_sales'),
            pl.count().alias('order_count'),
            pl.sum('discount_applied').alias('total_discount')
        ]).sort('total_sales', descending=True)

        fig = px.pie(
            data_frame              = region_share,
            values                  = 'total_sales',
            names                   = 'region',
            title                   = "🥧 Regions' Share of Total Sales",
            hole                    = 0.5,
            color_discrete_sequence = px.colors.qualitative.Pastel
        )

        fig.update_traces(
            textposition    = 'inside',
            textinfo        = 'percent+label',
            hovertemplate   = '<b>%{label}</b><br>' +
                                'Sales: R$ %{value:,.2f}<br>' +
                                'Orders: %{customdata[0]:,}<br>' +
                                'Share: %{percent}<extra></extra>',
            customdata      = region_share.select(["order_count"]).to_numpy()
        )

        fig.update_layout(
            height      = 500,
            showlegend  = False
        )

        return fig

    def create_region_state_treemap(self, df):
        region_state = df.group_by(['region', 'state']).agg([
            pl.sum('final_price').alias('total_sales'),
            pl.sum('discount_applied').alias('total_discount'),
            pl.count().alias('order_count')
        ])

        region_state = region_state.with_columns(
            pl.col("state").replace(self.state_names).alias("state_name")
        )
        fig = px.treemap(
            data_frame              = region_state,
            path                    = ['region', 'state_name'],
            values                  = 'total_sales',
            title                   = "🌳 Hierarchical Distribution: Region → State",
            color                   = 'total_sales',
            color_continuous_scale  = 'Viridis',
            hover_data              = ['order_count', 'total_discount']
        )

        fig.update_traces(
            hovertemplate = '<b>%{label}</b><br>' +
                            'Sold: R$ %{value:,.2f}<br>' +
                            'Orders: %{customdata[0]:,}<br>' +
                            'Discounts: R$ %{customdata[1]:,.2f}<extra></extra>'
        )

        fig.update_layout(
            height  = 500
        )

        return fig

    def render_dashboard(self):
        self.df = load_geo_sales_data(self)

        if self.df.is_empty():
            self.st.warning("No geographic sales data found.")
            return

        self.st.header("🗺️ Geographic Sales Analysis")
        self.st.markdown("**Complete view of sales by region and state**")


        with self.st.container():
            col1, col2 = self.st.columns(2)

            with col1:
                regions = self.st.multiselect(
                    label   = "Regions:",
                    options = self.df['region'].unique().to_list(),
                    default = self.df['region'].unique().to_list(),
                    key     = "geo_regions"
                )

            with col2:
                states = self.st.multiselect(
                    label   = "States:",
                    options = self.df['state'].unique().to_list(),
                    default = self.df['state'].unique().to_list(),
                    key     = "geo_states",
                )

        filtered_df = self.df.filter(
            (pl.col('region').is_in(regions)) &
            (pl.col('state').is_in(states))
        )

        self.st.subheader("📈 Key Metrics")
        col1, col2, col3, col4 = self.st.columns(4)
        with col1:
            total_sales = filtered_df['final_price'].sum()
            st.metric("Total Sales", f"R$ {total_sales:,.2f}")
        with col2:
            total_orders = filtered_df.height
            st.metric("Total Orders", f"{total_orders:,}")
        with col3:
            avg_ticket = filtered_df['final_price'].mean()
            st.metric("Average Ticket", f"R$ {avg_ticket:,.2f}")
        with col4:
            total_discount = filtered_df['discount_applied'].sum()
            st.metric("Total Discounts", f"R$ {total_discount:,.2f}")

        st.subheader("📊 Main Views")

        col1, col2 = self.st.columns(2)

        with col1:
            fig1 = self.create_state_choropleth(filtered_df)
            self.st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig5 = self.create_region_donut(filtered_df)
            self.st.plotly_chart(fig5, use_container_width=True)

        fig2 = self.create_region_temporal(filtered_df)
        self.st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = self.st.columns(2)

        with col3:
            fig4 = self.create_top_states_chart(filtered_df)
            self.st.plotly_chart(fig4, use_container_width=True)

        with col4:
            fig8 = self.create_region_state_treemap(filtered_df)
            self.st.plotly_chart(fig8, use_container_width=True)

        with self.st.expander("📋 Detailed Data by State"):
            state_summary = filtered_df.group_by(['state', 'region']).agg([
                pl.sum('final_price').alias('total_sales'),
                pl.sum('discount_applied').alias('total_discount'),
                pl.count().alias('order_count'),
                pl.mean('final_price').alias('avg_ticket'),
                (pl.sum('discount_applied') / pl.sum('final_price') * 100).alias('discount_rate_%')
            ]).sort('total_sales', descending=True)

            self.st.dataframe(
                data                = state_summary,
                use_container_width = True,
                height              = 400
            )

        csv_data = filtered_df.write_csv()
        self.st.download_button(
            label="📥 Download Geographic Data",
            data=csv_data,
            file_name="vendas_geograficas.csv",
            mime="text/csv"
        )