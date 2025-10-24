import streamlit as st
from utils.feedback import FeedbackDashboard
from utils.customer import CustomerDashboard
from utils.region_sales import GeoSalesDashboard
from utils.products_sales import ProductsSalesDashboard


class Dashboard:
    def __init__(self, project: str):
        self.project = project
        self.dashboards = {
            "💰 Region Sales": GeoSalesDashboard,
            "💬 Feedback": FeedbackDashboard,
            "👤 Customer": CustomerDashboard,
            "📦 Products": ProductsSalesDashboard
        }

    def main_page(self):
        st.set_page_config(
            page_title  = "LogiStream Solutions report",
            page_icon   = "📊",
            layout      = "wide"
        )

        st.sidebar.header("👇🏾 Dashboard Navigation")

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

        #TODO: Change it!
        st.sidebar.header("🌐 General Information")
        st.sidebar.info(
            "This dashboard combines sales analytics and feedback "
            "to provide a complete view of business performance."
        )

        #TODO: Change it!
        st.sidebar.header("📝 Additional Resources")
        with st.sidebar.expander("📋 Dashboard Descriptions"):
            st.write(\
                """
                    **💰 Sales Dashboard:**
                    - Sales evolution over time
                    - Total value and discounts
                    - Regional and state analysis

                    **💬 Feedback Dashboard:**
                    - Customer sentiment analysis
                    - Rating distribution
                    - Feedback trends over time

                    **👤 Customer Dashboard:**
                    - Customer distribution by region
                    - Geographic mapping
                    - Demographic insights

                    **📦 Products Dashboard:**
                    - Sales performance by product category
                    - Inventory levels and trends
                    - Product feedback analysis
                """)

        st.sidebar.header("🔄 Data Management")
        if st.sidebar.button("🔄 Reload All Data"):
            st.cache_data.clear()
            st.rerun()