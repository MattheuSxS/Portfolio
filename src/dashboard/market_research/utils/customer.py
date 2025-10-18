import requests
import polars as pl
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.bigquery import BigQuery

@st.cache_data(ttl=3601)
def load_data(_bq_client: BigQuery) -> pl.DataFrame:
    try:
        df = _bq_client.read_bq("customer_query")
        return df
    except Exception as e:
        st.error(f"Error loading customer data: {e}")
        return pl.DataFrame()

class CustomerDashboard(BigQuery):
    def __init__(self, project: str, st: any):
        super().__init__(project)
        self.st = st
        self.df = None
        self.state_names = {
            'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
            'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
            'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
            'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
            'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
            'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
            'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
        }

    def get_brazil_geojson(self):
        """Obtém o GeoJSON do Brasil"""
        geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
        try:
            response = requests.get(geojson_url)
            return response.json()
        except:
            return self._get_fallback_geojson()

    def _get_fallback_geojson(self):
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "SP",
                    "properties": {"name": "São Paulo"},
                    "geometry": {"type": "Polygon", "coordinates": [[[]]]}
                },
                # Adicione outros estados conforme necessário
            ]
        }

    def create_brazil_map(self, df):
        geojson_data = self.get_brazil_geojson()

        df_map = df.with_columns(
            pl.col('state').map_elements(lambda x: self.state_names.get(x, x)).alias('state_name')
        ).to_pandas()

        fig = px.choropleth(
            data_frame              = df_map,
            geojson                 = geojson_data,
            locations               = 'state',           # Siglas dos estados que devem corresponder ao 'id' no GeoJSON
            featureidkey            = "properties.sigla",  # Chave que contém as siglas no GeoJSON
            color                   = 'associate_count',     # Variável para o gradiente de cores
            hover_name              = 'state_name',     # Nome completo no hover
            hover_data              = {
                                            'region': True,
                                            'associate_count': True,
                                            'state': False
                                        },
            color_continuous_scale  = "Blues",
            title                   = "Customer Distribution by State in Brazil"
        )

        fig.update_geos(
            visible         = False,
            resolution      = 50,
            showcountries   = True,
            countrycolor    = "Black",
            showsubunits    = True,
            subunitcolor    = "Blue",
            scope           = "south america"
        )

        # Personalizar o layout
        fig.update_layout(
            height  = 600,
            margin  = dict(l=0, r=0, t=50, b=0),
            font    = dict(size=12),
            geo     = dict(
                            bgcolor         = 'rgba(0,0,0,0)',
                            showframe       = False,
                            showcoastlines  = True,
                            projection_type = 'equirectangular'
            )
        )

        fig.update_coloraxes(
            colorbar_title      = "Nº de Clientes",
            colorbar_tickformat = ',d'
        )

        return fig

    def create_brazil_map_alternative(self, df):

        geojson_data = self.get_brazil_geojson()

        df_map = df.with_columns(
            pl.col('state').map_elements(lambda x: self.state_names.get(x, x)).alias('state_name')
        ).to_pandas()

        fig = go.Figure(go.Choropleth(
            geojson             = geojson_data,
            locations           = df_map['state'],
            z                   = df_map['associate_count'],
            featureidkey        = "properties.sigla",
            colorscale          = "Blues",
            colorbar_title      = "Nº de Clientes",
            hoverinfo           = "text",
            hovertext           = df_map.apply(
                                        lambda row: f"<b>{row['state_name']}</b><br>"
                                                f"Região: {row['region']}<br>"
                                                f"Clientes: {row['associate_count']:,}",
                                        axis=1
                                    )
        ))

        fig.update_geos(
            fitbounds   = "locations",
            visible     = False,
            scope       = "south america"
        )

        fig.update_layout(
            title_text  = "Customer Distribution by State in Brazil",
            height      = 600,
            margin      = dict(l=0, r=0, t=50, b=0)
        )

        return fig

    def create_region_summary(self, df):
        region_totals = df.group_by('region').agg([
            pl.sum('associate_count').alias('total_clients')
        ]).sort('total_clients', descending=True)

        fig = px.bar(
            data_frame              = region_totals.to_pandas(),
            x                       = 'region',
            y                       = 'total_clients',
            title                   = "Total Customers by Region",
            color                   = 'total_clients',
            color_continuous_scale  = 'Viridis',
            labels                  = {'total_clients': 'Number of Customers', 'region': 'Region'}
        )

        fig.update_layout(
            height      = 400,
            showlegend  = False
        )

        return fig

    def customer_dashboard(self):
        self.df = load_data(self)

        if self.df.is_empty():
            self.st.warning("No data found or error loading data.")
            return

        self.st.header("👥 Member Distribution Analysis")

        col1, col2 = self.st.columns(2)
        with col1:
            regions = self.st.multiselect(
                "Filter by Region:",
                options = self.df['region'].unique().to_list(),
                default = self.df['region'].unique().to_list()
            )

        with col2:
            min_clients = self.st.slider(
                "Minimum Clients per State:",
                min_value   = int(self.df['associate_count'].min()),
                max_value   = int(self.df['associate_count'].max()),
                value       = int(self.df['associate_count'].min())
            )

        filtered_df = self.df.filter(
            (pl.col('region').is_in(regions)) &
            (pl.col('associate_count') >= min_clients)
        )

        col1, col2 = self.st.columns([2, 1])

        with col1:
            st.subheader("📍 Geographical Distribution")
            try:
                map_fig = self.create_brazil_map(filtered_df)
            except Exception as e:
                self.st.warning(f"Using alternative method: {e}")
                map_fig = self.create_brazil_map_alternative(filtered_df)

            self.st.plotly_chart(map_fig, use_container_width=True)

        with col2:

            st.subheader("📊 Métricas")

            total_clients = filtered_df['associate_count'].sum()
            total_estados = filtered_df.height

            if not filtered_df.is_empty():
                estado_mais_clientes = filtered_df.sort('associate_count', descending=True).row(0)
                st.metric(
                    "State with the Most Customers",
                    f"{estado_mais_clientes[2]} - {estado_mais_clientes[0]:,}"
                )
            else:
                st.metric("State with the Most Customers", "N/A")

            st.metric("Total Customers", f"{total_clients:,}")
            st.metric("States with Customers", total_estados)

            region_fig = self.create_region_summary(filtered_df)
            self.st.plotly_chart(region_fig, use_container_width=True)

        with st.expander("📋 View Detailed Data by State"):
            display_df = filtered_df.select([
                'state', 'region', 'associate_count'
            ]).sort('associate_count', descending=True)

            self.st.dataframe(
                display_df.to_pandas(),
                use_container_width = True,
                height              = 300
            )

            csv_data = filtered_df.write_csv()
            st.download_button(
                label       = "📥 Download data as CSV",
                data        = csv_data,
                file_name   = "customers_by_state.csv",
                mime        = "text/csv"
            )