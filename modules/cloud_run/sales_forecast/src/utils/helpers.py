import polars as pl
import streamlit as st
from utils.br_sul import BrSulDashboard
from utils.br_norte import BrNorteDashboard
from utils.br_general import BrGeneralDashboard
from utils.br_sudeste import BrSulDesteDashboard
from utils.br_nordeste import BrNordesteDashboard
from utils.br_centro_oeste import BrCentroOesteDashboard

try:
    from utils.bigquery import BigQuery
except ImportError:
    from bigquery import BigQuery


@st.cache_resource(show_spinner=False, ttl="3h")
def load_data(_bq_client: BigQuery) -> pl.DataFrame:
    try:
        df = _bq_client.read_bq()
        return df
    except Exception as e:
        st.error(f"Error loading customer data: {e}")
        return pl.DataFrame()


class Dashboard(BigQuery):
    def __init__(self, project: str):
        super().__init__(project)
        self.project = project
        self.dashboards = {
            "Brazil": BrGeneralDashboard,
            "Region Sudeste": BrSulDesteDashboard,
            "Region Norte": BrNorteDashboard,
            "Region Nordeste": BrNordesteDashboard,
            "Region Centro-Oeste": BrCentroOesteDashboard,
            "Region Sul": BrSulDashboard,
        }

        self.df = load_data(self)

    def main_page(self):
        st.set_page_config(
            page_title="Sales forecast for Brazil",
            page_icon=":chart_with_upwards_trend:",
            layout="wide",
        )

        selected_dashboard = st.sidebar.radio(
            label               = "Select Dashboard:",
            options             = list(self.dashboards.keys()),
            index               = 0,
            label_visibility    = "collapsed"
        )

        dashboard_class = self.dashboards[selected_dashboard]
        dashboard_instance = dashboard_class(self.df, st)

        match selected_dashboard:
            case "Brazil":
                dashboard_instance.render_dashboard()
            case "Region Sudeste":
                dashboard_instance.render_dashboard()
            case "Region Norte":
                dashboard_instance.render_dashboard()
            case "Region Nordeste":
                dashboard_instance.render_dashboard()
            case "Region Centro-Oeste":
                dashboard_instance.render_dashboard()
            case "Region Sul":
                dashboard_instance.render_dashboard()


        with st.sidebar.expander("🌐 General Information"):
            st.write(
                """
                """
            )

        with st.sidebar.expander("📝 Add Resources"):
            st.write(
                """
                """)