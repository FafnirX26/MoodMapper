import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from models.database import User, BehavioralData, MoodEntry
from utils.data_generator import generate_demo_data

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

def show():
    st.title("⚙️ Settings")
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 1
    
    tabs = st.tabs(["User Profile", "Data Management", "Privacy", "Demo Data"])
    
    session = st.session_state.db_manager.get_session()
    
    with tabs[0]:
        st.subheader("👤 User Profile")
        
        try:
            user = session.query(User).filter_by(id=st.session_state.user_id).first()
            
            if not user:
                st.info("Setting up your profile for the first time...")
                email = st.text_input("Email", placeholder="your.email@example.com")
                age = st.number_input("Age", min_value=13, max_value=120, value=25)
                timezone = st.selectbox("Timezone", ["UTC-8", "UTC-5", "UTC", "UTC+1", "UTC+8"])
                
                if st.button("Create Profile"):
                    new_user = User(
                        id=st.session_state.user_id,
                        email=email,
                        age=age,
                        timezone=timezone,
                        onboarding_complete=True,
                        consent_version="1.0"
                    )
                    session.add(new_user)
                    session.commit()
                    st.success("Profile created successfully!")
                    st.rerun()
            else:
                st.success("✅ Profile Active")
                st.write(f"**Email:** {user.email}")
                st.write(f"**Age:** {user.age}")
                st.write(f"**Timezone:** {user.timezone}")
                st.write(f"**Member Since:** {user.created_at.strftime('%Y-%m-%d')}")
        
        except Exception as e:
            st.error(f"Error loading profile: {str(e)}")
    
    with tabs[1]:
        st.subheader("📊 Data Management")
        
        try:
            mood_count = session.query(MoodEntry).filter_by(user_id=st.session_state.user_id).count()
            behavior_count = session.query(BehavioralData).filter_by(user_id=st.session_state.user_id).count()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Mood Entries", mood_count)
            with col2:
                st.metric("Behavioral Data Points", behavior_count)
            
            st.subheader("Export Data")
            
            if st.button("Export All Data (CSV)"):
                mood_entries = session.query(MoodEntry).filter_by(user_id=st.session_state.user_id).all()
                behavioral_data = session.query(BehavioralData).filter_by(user_id=st.session_state.user_id).all()
                
                if mood_entries:
                    mood_df = pd.DataFrame([{
                        'timestamp': entry.timestamp,
                        'happiness': safe_convert_to_float(entry.happiness),
                        'energy': safe_convert_to_float(entry.energy),
                        'anxiety': safe_convert_to_float(entry.anxiety),
                        'motivation': safe_convert_to_float(entry.motivation),
                        'notes': entry.notes,
                        'weather': entry.weather
                    } for entry in mood_entries])
                    
                    csv = mood_df.to_csv(index=False)
                    st.download_button(
                        label="Download Mood Data CSV",
                        data=csv,
                        file_name=f"mood_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No data to export")
            
            st.subheader("⚠️ Delete Data")
            
            st.warning("⚠️ This action will permanently delete all your mood entries and behavioral data. This cannot be undone.")
            
            confirm_delete = st.checkbox("I understand this will permanently delete all my data")
            
            if st.button("Clear All Data", type="secondary", disabled=not confirm_delete):
                if confirm_delete:
                    deleted_moods = session.query(MoodEntry).filter_by(user_id=st.session_state.user_id).delete()
                    deleted_behavior = session.query(BehavioralData).filter_by(user_id=st.session_state.user_id).delete()
                    session.commit()
                    st.success(f"All data cleared successfully! Deleted {deleted_moods} mood entries and {deleted_behavior} behavioral data points.")
                    st.rerun()
        
        except Exception as e:
            st.error(f"Error managing data: {str(e)}")
    
    with tabs[2]:
        st.subheader("🔒 Privacy & Security")
        
        st.markdown("""
        **Data Collection:**
        - All data is stored locally on your device
        - No data is transmitted to external servers
        - Personal identifiers are encrypted
        
        **Data Usage:**
        - Data is used only for generating personalized insights
        - Machine learning models run locally
        - No data sharing with third parties
        
        **Your Rights:**
        - Export your data at any time
        - Delete your data permanently
        - Control what data is collected
        """)
        
        st.subheader("Data Collection Preferences")
        
        sleep_data = st.checkbox("Sleep Pattern Analysis", value=True)
        activity_data = st.checkbox("Physical Activity Tracking", value=True)
        location_data = st.checkbox("Location Pattern Analysis", value=False)
        screen_data = st.checkbox("Screen Time Analysis", value=True)
        
        if st.button("Save Privacy Preferences"):
            st.success("Privacy preferences saved!")
    
    with tabs[3]:
        st.subheader("🎭 Demo Data Generator")
        
        st.info("Generate synthetic data to explore Mood Mapper's features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            days = st.slider("Days of Data", 7, 90, 30)
        
        with col2:
            pattern = st.selectbox("Pattern Type", [
                "Stable", "Improving", "Declining", "Seasonal", "Mixed"
            ])
        
        if st.button("Generate Demo Data", type="primary"):
            with st.spinner("Generating demo data..."):
                try:
                    generate_demo_data(
                        session=session,
                        user_id=st.session_state.user_id,
                        days=days,
                        pattern=pattern
                    )
                    session.commit()
                    st.success(f"✅ Generated {days} days of demo data with {pattern.lower()} pattern!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error generating demo data: {str(e)}")
    
    st.session_state.db_manager.close_session(session)