import polars as pl
import streamlit as st
import plotly.express as px
from utils.bigquery import BigQuery

#TODO: I must finish it tomorrow!
@st.cache_data(ttl=1200)
def load_geo_sales_data(_bq_client: BigQuery) -> pl.DataFrame:
    try:
        df = _bq_client.read_bq("region_sales_query")
        df = df.with_columns(
            pl.col("purchase_date").str.strptime(pl.Date, "%Y-%m-%d")
        )
        return df
    except Exception as e:
        st.error(f"Error loading geographic sales data: {e}")
        return pl.DataFrame()

class GeoSalesDashboard(BigQuery):
    def __init__(self, project: str, st: any):
        super().__init__(project)
        self.st = st
        self.df = None

    def create_state_choropleth(self, df):
        """#1 - Mapa do Brasil com vendas por estado"""
        state_totals = df.group_by('state').agg([
            pl.sum('final_price').alias('total_sales'),
            pl.sum('discount_applied').alias('total_discount')
        ])
        
        # Mapeamento de siglas para nomes completos
        state_names = {
            'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
            'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
            'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
            'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
            'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
            'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
            'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
        }
        
        state_totals_pd = state_totals.to_pandas()
        state_totals_pd['state_name'] = state_totals_pd['state'].map(state_names)

        fig = px.choropleth(
            state_totals_pd,
            locations='state',
            locationmode="BR-states",
            color='total_sales',
            hover_name='state_name',
            hover_data={
                'total_sales': ':,2f',
                'total_discount': ':,2f',
                'state': False
            },
            title="🗺️ Distribuição Geográfica de Vendas por Estado",
            color_continuous_scale="Blues",
            scope="south america"
        )
        
        fig.update_layout(
            height=500,
            geo=dict(
                bgcolor='rgba(0,0,0,0)',
                lakecolor='#0E1117',
                landcolor='lightgray'
            )
        )
        
        fig.update_coloraxes(
            colorbar_title="Vendas (R$)",
            colorbar_tickformat=',.2f'
        )
        
        return fig

    def create_region_temporal(self, df):
        """#2 - Evolução das vendas por região ao longo do tempo"""
        daily_region = df.group_by(['purchase_date', 'region']).agg([
            pl.sum('final_price').alias('daily_sales'),
            pl.sum('discount_applied').alias('daily_discount')
        ]).sort('purchase_date')
        
        fig = px.line(
            daily_region.to_pandas(),
            x='purchase_date',
            y='daily_sales',
            color='region',
            title="📈 Evolução Temporal das Vendas por Região",
            labels={
                'daily_sales': 'Vendas Diárias (R$)',
                'purchase_date': 'Data',
                'region': 'Região'
            },
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        
        fig.update_layout(
            height=500,
            hovermode='x unified',
            xaxis_title="Data",
            yaxis_title="Vendas Diárias (R$)"
        )
        
        return fig

    def create_top_states_chart(self, df):
        """#4 - Top 10 estados com maior volume de vendas"""
        top_states = df.group_by('state').agg([
            pl.sum('final_price').alias('total_sales'),
            pl.sum('discount_applied').alias('total_discount'),
            pl.count().alias('order_count'),
            (pl.sum('discount_applied') / pl.sum('final_price') * 100).alias('discount_rate_%')
        ]).sort('total_sales', descending=True).head(10)
        
        # Adicionar nomes completos para tooltips
        state_names = {
            'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
            'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
            'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
            'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
            'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
            'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
            'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
        }
        
        top_states_pd = top_states.to_pandas()
        top_states_pd['state_name'] = top_states_pd['state'].map(state_names)

        fig = px.bar(
            top_states_pd,
            x='state',
            y='total_sales',
            color='total_sales',
            title="🏆 Top 10 Estados por Volume de Vendas",
            labels={
                'total_sales': 'Vendas Totais (R$)',
                'state': 'Estado',
                'discount_rate_%': 'Taxa de Desconto (%)'
            },
            color_continuous_scale='Viridis',
            hover_data=['state_name', 'order_count', 'discount_rate_%']
        )
        
        fig.update_traces(
            hovertemplate='<b>%{customdata[0]}</b><br>' +
                         'Vendas: R$ %{y:,.2f}<br>' +
                         'Pedidos: %{customdata[1]:,}<br>' +
                         'Desconto: %{customdata[2]:.1f}%<extra></extra>'
        )
        
        fig.update_layout(
            height=500,
            showlegend=False,
            xaxis_title="Estado",
            yaxis_title="Vendas Totais (R$)"
        )
        
        return fig

    def create_region_donut(self, df):
        """#5 - Participação percentual de cada região"""
        region_share = df.group_by('region').agg([
            pl.sum('final_price').alias('total_sales'),
            pl.count().alias('order_count'),
            pl.sum('discount_applied').alias('total_discount')
        ]).sort('total_sales', descending=True)
        
        fig = px.pie(
            region_share.to_pandas(),
            values='total_sales',
            names='region',
            title="🥧 Participação das Regiões nas Vendas Totais",
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>' +
                         'Vendas: R$ %{value:,.2f}<br>' +
                         'Pedidos: %{customdata[0]:,}<br>' +
                         'Participação: %{percent}<extra></extra>',
            customdata=region_share.to_pandas()[['order_count']].values
        )
        
        fig.update_layout(
            height=500,
            showlegend=False
        )
        
        return fig

    def create_region_state_treemap(self, df):
        """#8 - Visualização hierárquica das vendas"""
        region_state = df.group_by(['region', 'state']).agg([
            pl.sum('final_price').alias('total_sales'),
            pl.sum('discount_applied').alias('total_discount'),
            pl.count().alias('order_count')
        ])
        
        # Adicionar nomes completos dos estados
        state_names = {
            'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
            'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
            'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
            'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
            'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
            'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
            'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
        }
        
        region_state_pd = region_state.to_pandas()
        region_state_pd['state_name'] = region_state_pd['state'].map(state_names)

        fig = px.treemap(
            region_state_pd,
            path=['region', 'state_name'],
            values='total_sales',
            title="🌳 Distribuição Hierárquica: Região → Estado",
            color='total_sales',
            color_continuous_scale='Viridis',
            hover_data=['order_count', 'total_discount']
        )
        
        fig.update_traces(
            hovertemplate='<b>%{label}</b><br>' +
                         'Vendas: R$ %{value:,.2f}<br>' +
                         'Pedidos: %{customdata[0]:,}<br>' +
                         'Descontos: R$ %{customdata[1]:,.2f}<extra></extra>'
        )
        
        fig.update_layout(
            height=500
        )
        
        return fig

    def render_dashboard(self):
        self.df = load_geo_sales_data(self)

        if self.df.is_empty():
            self.st.warning("No geographic sales data found.")
            return

        self.st.header("🗺️ Análise Geográfica de Vendas")
        self.st.markdown("**Visualização completa das vendas por região e estado**")

        # Filtros
        with self.st.container():
            col1, col2 = self.st.columns(2)
            
            with col1:
                regions = self.st.multiselect(
                    "Regiões:",
                    options=self.df['region'].unique().to_list(),
                    default=self.df['region'].unique().to_list(),
                    key="geo_regions"
                )
            
            with col2:
                states = self.st.multiselect(
                    "Estados:",
                    options=self.df['state'].unique().to_list(),
                    default=self.df['state'].unique().to_list(),
                    key="geo_states",
                    max_selections=10,
                    help="Máximo 10 estados selecionados"
                )

        # Aplicar filtros
        filtered_df = self.df.filter(
            (pl.col('region').is_in(regions)) & 
            (pl.col('state').is_in(states))
        )

        # Métricas rápidas
        col1, col2, col3, col4 = self.st.columns(4)
        with col1:
            total_sales = filtered_df['final_price'].sum()
            st.metric("Vendas Totais", f"R$ {total_sales:,.2f}")
        with col2:
            total_orders = filtered_df.height
            st.metric("Total de Pedidos", f"{total_orders:,}")
        with col3:
            avg_ticket = filtered_df['final_price'].mean()
            st.metric("Ticket Médio", f"R$ {avg_ticket:,.2f}")
        with col4:
            total_discount = filtered_df['discount_applied'].sum()
            st.metric("Descontos Totais", f"R$ {total_discount:,.2f}")

        # Layout dos gráficos - TOP 5 RECOMENDADOS
        st.subheader("📊 Visualizações Principais")
        
        # Linha 1: Mapa + Donut
        col1, col2 = self.st.columns(2)
        with col1:
            fig1 = self.create_state_choropleth(filtered_df)
            self.st.plotly_chart(fig1, use_container_width=True)
        with col2:
            fig5 = self.create_region_donut(filtered_df)
            self.st.plotly_chart(fig5, use_container_width=True)

        # Linha 2: Evolução Temporal
        fig2 = self.create_region_temporal(filtered_df)
        self.st.plotly_chart(fig2, use_container_width=True)

        # Linha 3: Top Estados + Treemap
        col3, col4 = self.st.columns(2)
        with col3:
            fig4 = self.create_top_states_chart(filtered_df)
            self.st.plotly_chart(fig4, use_container_width=True)
        with col4:
            fig8 = self.create_region_state_treemap(filtered_df)
            self.st.plotly_chart(fig8, use_container_width=True)

        # Tabela detalhada
        with self.st.expander("📋 Dados Detalhados por Estado"):
            state_summary = filtered_df.group_by(['state', 'region']).agg([
                pl.sum('final_price').alias('total_sales'),
                pl.sum('discount_applied').alias('total_discount'),
                pl.count().alias('order_count'),
                pl.mean('final_price').alias('avg_ticket'),
                (pl.sum('discount_applied') / pl.sum('final_price') * 100).alias('discount_rate_%')
            ]).sort('total_sales', descending=True)
            
            self.st.dataframe(
                state_summary.to_pandas(),
                use_container_width=True,
                height=400
            )

        # Download
        csv_data = filtered_df.write_csv()
        self.st.download_button(
            label="📥 Download dos Dados Geográficos",
            data=csv_data,
            file_name="vendas_geograficas.csv",
            mime="text/csv"
        )