import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.pages import dashboard, mood_log, insights, settings
from models.database import DatabaseManager

st.set_page_config(
    page_title="Mood Mapper",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_database():
    if 'db_manager' not in st.session_state:
        os.makedirs('data', exist_ok=True)
        st.session_state.db_manager = DatabaseManager()
        st.session_state.db_manager.create_tables()

def main():
    initialize_database()
    
    st.sidebar.title("🧠 Mood Mapper")
    st.sidebar.markdown("---")
    
    pages = {
        "Dashboard": dashboard,
        "Mood Log": mood_log,
        "Insights": insights,
        "Settings": settings
    }
    
    selected_page = st.sidebar.selectbox("Navigate", list(pages.keys()))
    
    if selected_page in pages:
        pages[selected_page].show()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("*Privacy-focused mental health monitoring*")

if __name__ == "__main__":
    main()