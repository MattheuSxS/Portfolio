import polars as pl
import streamlit as st
from utils.mockup import MockupDashboard
from utils.br_general import BrGeneralDashboard

try:
    from utils.bigquery import BigQuery
except ImportError:
    from bigquery import BigQuery


# state_dict = {
#     "centro_oeste": {
#         "DF": "Distrito Federal",
#         "GO": "Goiás",
#         "MT": "Mato Grosso",
#         "MS": "Mato Grosso do Sul"
#     },
#     "norte": {
#         "AC": "Acre",
#         "AP": "Amapá",
#         "AM": "Amazonas",
#         "PA": "Pará",
#         "RO": "Rondônia",
#         "RR": "Roraima",
#         "TO": "Tocantins"
#     },
#     "nordeste": {
#         "AL": "Alagoas",
#         "BA": "Bahia",
#         "CE": "Ceará",
#         "MA": "Maranhão",
#         "PB": "Paraíba",
#         "PE": "Pernambuco",
#         "PI": "Piauí",
#         "RN": "Rio Grande do Norte",
#         "SE": "Sergipe"
#     },
#     "sudeste": {
#         "ES": "Espírito Santo",
#         "MG": "Minas Gerais",
#         "RJ": "Rio de Janeiro",
#         "SP": "São Paulo"
#     },
#     "sul": {
#         "PR": "Paraná",
#         "RS": "Rio Grande do Sul",
#         "SC": "Santa Catarina"
#     }
# }

STATES_DICT = {
    "Region Centro-Oeste": {
        "DF": "Distrito Federal",
        "GO": "Goiás",
        "MT": "Mato Grosso",
        "MS": "Mato Grosso do Sul"
    },
    "Region Norte": {
        "AC": "Acre",
        "AP": "Amapá",
        "AM": "Amazonas",
        "PA": "Pará",
        "RO": "Rondônia",
        "RR": "Roraima",
        "TO": "Tocantins"
    },
    "Region Nordeste": {
        "AL": "Alagoas",
        "BA": "Bahia",
        "CE": "Ceará",
        "MA": "Maranhão",
        "PB": "Paraíba",
        "PE": "Pernambuco",
        "PI": "Piauí",
        "RN": "Rio Grande do Norte",
        "SE": "Sergipe"
    },
    "Region Sudeste": {
        "ES": "Espírito Santo",
        "MG": "Minas Gerais",
        "RJ": "Rio de Janeiro",
        "SP": "São Paulo"
    },
    "Region Sul": {
        "PR": "Paraná",
        "RS": "Rio Grande do Sul",
        "SC": "Santa Catarina"
    }
}

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
        self.region_list = [
            "Brazil",
            "Region Sudeste",
            "Region Norte",
            "Region Nordeste",
            "Region Centro-Oeste",
            "Region Sul",
        ]

        self.df = load_data(self)

    def main_page(self):
        st.set_page_config(
            page_title="Sales forecast for Brazil",
            page_icon=":chart_with_upwards_trend:",
            layout="wide",
        )

        selected_dashboard = st.sidebar.radio(
            label               = "Select Dashboard:",
            options             = self.region_list,
            index               = 0,
            label_visibility    = "collapsed"
        )

        if selected_dashboard == "Brazil":
            dashboard_instance = BrGeneralDashboard(self.df, st)
        else:
            dashboard_instance = MockupDashboard(self.df, STATES_DICT[selected_dashboard], st)

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