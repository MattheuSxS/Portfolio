# streamlit_app.py (exemplo)
import pandas as pd
import streamlit as st
from backup.test import SalesForecastingPipeline, StreamlitHelper

# Configurar página
st.set_page_config(page_title="Previsão de Vendas", layout="wide")

# Título
st.title("📊 Previsão de Vendas - Prophet")

# Sidebar para controles
st.sidebar.header("Configurações")

# Carregar modelos
@st.cache_resource
def load_models():
    pipeline = SalesForecastingPipeline()
    return pipeline.load_existing_models()

forecaster = load_models()

# Selecionar grupo
available_groups = forecaster.get_available_groups()
selected_group = st.sidebar.selectbox("Selecionar Grupo", available_groups)

# Obter dados para o grupo selecionado
chart_data = StreamlitHelper.prepare_forecast_chart_data(forecaster, selected_group)
summary = forecaster.get_forecast_summary(selected_group)
metrics = forecaster.get_performance_metrics(selected_group)

if chart_data and summary:
    # Métricas de performance
    st.sidebar.subheader("Métricas de Performance")
    st.sidebar.markdown(StreamlitHelper.get_metrics_display(metrics))

    # Gráfico principal
    st.subheader(f"Previsão de Vendas - {selected_group}")

    # Aqui você pode usar chart_data para criar gráficos com:
    # st.line_chart, st.area_chart, plotly, etc.

    # Resumo
    st.subheader("Resumo da Previsão")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Período Histórico", summary['historical_data_points'])

    with col2:
        st.metric("Dias Previstos", summary['forecast_periods'])

    with col3:
        st.metric("Previsão Total 30d", f"R$ {summary['total_forecast_30d']:,.2f}")

    # Tabela de previsões recentes
    st.subheader("Previsões Recentes")
    recent_df = pd.DataFrame(summary['recent_forecasts'])
    st.dataframe(recent_df)