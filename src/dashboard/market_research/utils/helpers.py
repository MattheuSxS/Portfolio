import streamlit as st
from feedback import FeedbackDashboard
from region_sales import RegionSalesDashboard

# Configuração da página
st.set_page_config(
    page_title="Dashboard Completo - Vendas & Feedback",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard Completo - Análise de Negócios")


RSD = RegionSalesDashboard('mts-default-portfolio', st)
FBD = FeedbackDashboard('mts-default-portfolio', st)

tab1, tab2 = st.tabs(["💰 Dashboard de Vendas", "💬 Dashboard de Feedback"])

with tab1:
    RSD.render_dashboard()

with tab2:
    FBD.feedback_dashboard()

st.sidebar.header("🌐 Informações Gerais")
st.sidebar.info(
    "Este dashboard combina análises de vendas e feedback para fornecer "
    "uma visão completa do desempenho do negócio."
)

# Botão para recarregar todos os dados
if st.sidebar.button("🔄 Recarregar Todos os Dados"):
    st.cache_data.clear()
    st.rerun()