import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from models.database import MoodEntry, BehavioralData, Insight
from utils.ml_pipeline import MoodMapperML

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
    st.title("🔍 Insights & Analytics")
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 1
    
    session = st.session_state.db_manager.get_session()
    
    try:
        mood_entries = session.query(MoodEntry).filter_by(user_id=st.session_state.user_id).all()
        behavioral_data = session.query(BehavioralData).filter_by(user_id=st.session_state.user_id).all()
        
        if not mood_entries:
            st.info("No mood data available. Please log some mood entries first.")
            return
        
        st.subheader("📈 Pattern Analysis")
        
        if st.button("Generate New Insights", type="primary"):
            with st.spinner("Analyzing your patterns..."):
                ml_pipeline = MoodMapperML()
                insights = ml_pipeline.generate_insights(mood_entries, behavioral_data)
                
                for insight in insights:
                    new_insight = Insight(
                        user_id=st.session_state.user_id,
                        insight_type=insight['type'],
                        confidence=insight['confidence'],
                        title=insight['title'],
                        description=insight['description'],
                        actionable=insight['actionable']
                    )
                    session.add(new_insight)
                
                session.commit()
                st.success("New insights generated!")
        
        existing_insights = session.query(Insight).filter_by(
            user_id=st.session_state.user_id
        ).order_by(Insight.timestamp.desc()).limit(10).all()
        
        if existing_insights:
            st.subheader("🎯 Your Personal Insights")
            
            for insight in existing_insights:
                confidence_color = "green" if insight.confidence > 0.7 else "orange" if insight.confidence > 0.4 else "red"
                
                with st.expander(f"{insight.title} (Confidence: {insight.confidence:.0%})"):
                    st.markdown(f"**Type:** {insight.insight_type.title()}")
                    st.markdown(f"**Description:** {insight.description}")
                    st.markdown(f"**Generated:** {insight.timestamp.strftime('%Y-%m-%d %H:%M')}")
                    
                    if insight.actionable:
                        st.success("💡 This insight suggests actionable steps you can take!")
        
        st.subheader("📊 Correlation Analysis")
        
        if behavioral_data and len(mood_entries) > 7:
            mood_df = pd.DataFrame([{
                'date': entry.timestamp.date(),
                'happiness': safe_convert_to_float(entry.happiness),
                'energy': safe_convert_to_float(entry.energy),
                'anxiety': safe_convert_to_float(entry.anxiety),
                'motivation': safe_convert_to_float(entry.motivation)
            } for entry in mood_entries])
            
            behavioral_df = pd.DataFrame([{
                'date': data.timestamp.date(),
                'sleep_hours': safe_convert_to_float(data.sleep_hours),
                'steps': safe_convert_to_int(data.steps),
                'screen_time': safe_convert_to_float(data.screen_time)
            } for data in behavioral_data])
            
            merged_df = pd.merge(mood_df, behavioral_df, on='date', how='inner')
            
            if not merged_df.empty:
                correlations = {
                    'Sleep & Happiness': merged_df['sleep_hours'].corr(merged_df['happiness']),
                    'Steps & Energy': merged_df['steps'].corr(merged_df['energy']),
                    'Screen Time & Anxiety': merged_df['screen_time'].corr(merged_df['anxiety']),
                    'Sleep & Energy': merged_df['sleep_hours'].corr(merged_df['energy'])
                }
                
                col1, col2 = st.columns(2)
                
                for i, (label, corr) in enumerate(correlations.items()):
                    if pd.notna(corr):
                        color = "green" if abs(corr) > 0.5 else "orange" if abs(corr) > 0.3 else "red"
                        strength = "Strong" if abs(corr) > 0.5 else "Moderate" if abs(corr) > 0.3 else "Weak"
                        
                        with col1 if i % 2 == 0 else col2:
                            st.metric(
                                label=label,
                                value=f"{corr:.2f}",
                                help=f"{strength} correlation ({'positive' if corr > 0 else 'negative'})"
                            )
        
        st.subheader("🚨 Early Warning System")
        
        if len(mood_entries) > 14:
            recent_mood = [safe_convert_to_float(entry.happiness) + safe_convert_to_float(entry.energy) - safe_convert_to_float(entry.anxiety) + safe_convert_to_float(entry.motivation) 
                          for entry in mood_entries[-7:]]
            baseline_mood = [safe_convert_to_float(entry.happiness) + safe_convert_to_float(entry.energy) - safe_convert_to_float(entry.anxiety) + safe_convert_to_float(entry.motivation) 
                           for entry in mood_entries[-14:-7]]
            
            recent_avg = np.mean(recent_mood)
            baseline_avg = np.mean(baseline_mood)
            change = recent_avg - baseline_avg
            
            if change < -3:
                st.error("⚠️ **Alert**: Your mood scores have declined significantly in the past week. Consider reaching out to a mental health professional.")
            elif change < -1.5:
                st.warning("⚠️ **Notice**: Your mood has been lower than usual. Take care of yourself and consider self-care activities.")
            elif change > 1.5:
                st.success("🎉 **Positive Trend**: Your mood has been improving! Keep up the good work.")
            else:
                st.info("📊 Your mood has been relatively stable.")
        
        st.subheader("📚 Recommendations")
        
        recommendations = [
            "🧘 Try 10 minutes of meditation daily",
            "🚶 Aim for 8,000+ steps per day",
            "😴 Maintain 7-8 hours of sleep nightly",
            "📱 Limit screen time before bed",
            "🌅 Get morning sunlight exposure",
            "📝 Keep a gratitude journal",
            "👥 Connect with friends or family",
            "🎨 Engage in creative activities"
        ]
        
        selected_recommendations = np.random.choice(recommendations, 4, replace=False)
        
        for rec in selected_recommendations:
            st.markdown(f"- {rec}")
    
    finally:
        st.session_state.db_manager.close_session(session)