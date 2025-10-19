import streamlit as st
from utils.feedback import FeedbackDashboard
from utils.customer import CustomerDashboard
from utils.region_sales import RegionSalesDashboard

class Dashboard:
    def __init__(self, project: str):
        self.project = project
        self.dashboards = {
            "💰 Sales": RegionSalesDashboard,
            "💬 Feedback": FeedbackDashboard,
            "👤 Customer": CustomerDashboard
        }

    def main_page(self):
        st.set_page_config(
            page_title  = "Complete Dashboard - Sales & Feedback",
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

        st.title("📊 Complete Dashboard - Business Analysis")

        dashboard_class = self.dashboards[selected_dashboard]
        dashboard_instance = dashboard_class(self.project, st)

        match selected_dashboard:
            case "💰 Sales":
                dashboard_instance.render_dashboard()
            case "💬 Feedback":
                dashboard_instance.feedback_dashboard()
            case "👤 Customer":
                dashboard_instance.customer_dashboard()

        st.sidebar.header("🌐 General Information")
        st.sidebar.info(
            "This dashboard combines sales analytics and feedback "
            "to provide a complete view of business performance."
        )

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
                """)

        st.sidebar.header("🔄 Data Management")
        if st.sidebar.button("🔄 Reload All Data"):
            st.cache_data.clear()
            st.rerun()