import streamlit as st
from utils.feedback import FeedbackDashboard
from utils.customer import CustomerDashboard
from utils.region_sales import RegionSalesDashboard



class Dashboard:
    def __init__(self, project: str):
        self.project = project

    def main_page(self):
        st.set_page_config(
            page_title="Complete Dashboard - Sales & Feedback",
            page_icon="📊",
            layout="wide"
        )

        st.title("📊 Complete Dashboard - Business Analysis")


        RSD = RegionSalesDashboard(self.project, st)
        FBD = FeedbackDashboard(self.project, st)
        CD = CustomerDashboard(self.project, st)

        tab1, tab2, tab3 = st.tabs(["💰 Sales Dashboard", "💬 Feedback Dashboard", "👤 Customer Dashboard"])

        with tab1:
            RSD.render_dashboard()

        with tab2:
            FBD.feedback_dashboard()

        with tab3:
            CD.customer_dashboard()

        st.sidebar.header("🌐 General Information")
        st.sidebar.info(
            "This dashboard combines sales analytics and feedback"
            " to provide a complete view of business performance."
        )


        if st.sidebar.button("🔄 Reload All Data"):
            st.cache_data.clear()
            st.rerun()