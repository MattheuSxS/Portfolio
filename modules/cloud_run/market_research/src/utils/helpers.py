import streamlit as st
from utils.feedback import FeedbackDashboard
from utils.customer import CustomerDashboard
from utils.region_sales import GeoSalesDashboard
from utils.products_sales import ProductsSalesDashboard


class Dashboard:
    def __init__(self, project: str):
        self.project    = project
        self.dashboards = {
            "💰 Region Sales": GeoSalesDashboard,
            "💬 Feedback": FeedbackDashboard,
            "👤 Customer": CustomerDashboard,
            "📦 Products": ProductsSalesDashboard
        }
        self.STATES_DICT = {
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

    def main_page(self):
        st.set_page_config(
            page_title  = "LogiStream Solutions report",
            page_icon   = "📊",
            layout      = "wide"
        )

        st.sidebar.header(body = "👇🏾 Navigation")

        selected_dashboard = st.sidebar.radio(
            label               = "Select Dashboard:",
            options             = list(self.dashboards.keys()),
            index               = 0,
            label_visibility    = "collapsed"
        )

        st.title("📊 LogiStream Solutions report")

        dashboard_class = self.dashboards[selected_dashboard]
        dashboard_instance = dashboard_class(self.project, st)

        match selected_dashboard:
            case "💰 Region Sales":
                dashboard_instance.render_dashboard()
            case "💬 Feedback":
                dashboard_instance.render_dashboard()
            case "👤 Customer":
                dashboard_instance.render_dashboard()
            case "📦 Products":
                dashboard_instance.render_dashboard()

        with st.sidebar.expander("🌐 General Information"):
            st.write(
                """
                    This dashboard provides insights into various aspects of LogiStream Solutions'
                    operations, including sales performance across regions, customer feedback analysis,
                    customer demographics, and product sales trends.
                """
            )

        with st.sidebar.expander("📝 Add Resources"):
            st.write(
                """
                - **Region Sales**: Visualizes sales data across different regions, highlighting top-performing areas and trends over time.
                - **Feedback**: Analyzes customer feedback to identify common themes, sentiment trends, and areas for improvement.
                - **Customer**: Provides insights into customer demographics, purchasing behavior, and lifetime value.
                - **Products**: Examines product performance, including sales trends, top-selling items, and inventory status.
                """)

        st.sidebar.header("🔄 Data Management")
        if st.sidebar.button("🔄 Reload All Data"):
            st.cache_data.clear()
            st.rerun()