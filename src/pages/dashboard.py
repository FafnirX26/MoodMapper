import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from models.database import MoodEntry, BehavioralData

def safe_convert_to_float(value):
    """Safely convert value to float, handling bytes and None values"""
    if value is None:
        return 0.0
    if isinstance(value, bytes):
        try:
            decoded = value.decode('utf-8', errors='ignore').strip()
            if not decoded or decoded == '\x00' * len(decoded):
                return 0.0
            return float(decoded)
        except (ValueError, UnicodeDecodeError):
            return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def safe_convert_to_int(value):
    """Safely convert value to int, handling bytes and None values"""
    if value is None:
        return 0
    if isinstance(value, bytes):
        try:
            decoded = value.decode('utf-8', errors='ignore').strip()
            if not decoded or decoded == '\x00' * len(decoded):
                return 0
            return int(float(decoded))
        except (ValueError, UnicodeDecodeError):
            return 0
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0

def show():
    st.title("📊 Dashboard")
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 1
    
    session = st.session_state.db_manager.get_session()
    
    try:
        col1, col2, col3, col4 = st.columns(4)
        
        mood_entries = session.query(MoodEntry).filter_by(user_id=st.session_state.user_id).all()
        behavioral_data = session.query(BehavioralData).filter_by(user_id=st.session_state.user_id).all()
        
        with col1:
            st.metric("Total Mood Entries", len(mood_entries))
        
        with col2:
            if mood_entries:
                avg_happiness = sum(safe_convert_to_float(entry.happiness) for entry in mood_entries[-7:]) / len(mood_entries[-7:])
                st.metric("Avg Happiness (7d)", f"{avg_happiness:.1f}/10")
            else:
                st.metric("Avg Happiness (7d)", "No data")
        
        with col3:
            if mood_entries:
                avg_energy = sum(safe_convert_to_float(entry.energy) for entry in mood_entries[-7:]) / len(mood_entries[-7:])
                st.metric("Avg Energy (7d)", f"{avg_energy:.1f}/10")
            else:
                st.metric("Avg Energy (7d)", "No data")
        
        with col4:
            if behavioral_data:
                avg_sleep = sum(data.sleep_hours for data in behavioral_data[-7:] if data.sleep_hours) / len([d for d in behavioral_data[-7:] if d.sleep_hours])
                st.metric("Avg Sleep (7d)", f"{avg_sleep:.1f}h")
            else:
                st.metric("Avg Sleep (7d)", "No data")
        
        if mood_entries:
            st.subheader("Mood Trends")
            
            mood_df = pd.DataFrame([{
                'date': entry.timestamp.date(),
                'happiness': safe_convert_to_float(entry.happiness),
                'energy': safe_convert_to_float(entry.energy),
                'anxiety': safe_convert_to_float(entry.anxiety),
                'motivation': safe_convert_to_float(entry.motivation)
            } for entry in mood_entries])
            
            fig = px.line(mood_df, x='date', y=['happiness', 'energy', 'anxiety', 'motivation'],
                         title="Mood Trends Over Time")
            st.plotly_chart(fig, use_container_width=True)
        
        if behavioral_data:
            st.subheader("Behavioral Patterns")
            
            behavioral_df = pd.DataFrame([{
                'date': data.timestamp.date(),
                'sleep_hours': safe_convert_to_float(data.sleep_hours),
                'steps': safe_convert_to_int(data.steps),
                'screen_time': safe_convert_to_float(data.screen_time)
            } for data in behavioral_data])
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_sleep = px.bar(behavioral_df, x='date', y='sleep_hours', title="Sleep Hours")
                st.plotly_chart(fig_sleep, use_container_width=True)
            
            with col2:
                fig_steps = px.line(behavioral_df, x='date', y='steps', title="Daily Steps")
                st.plotly_chart(fig_steps, use_container_width=True)
        
        if not mood_entries and not behavioral_data:
            st.info("No data available. Start by logging your mood or generating demo data in Settings.")
    
    finally:
        st.session_state.db_manager.close_session(session)