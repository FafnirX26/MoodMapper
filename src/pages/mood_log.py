import streamlit as st
from datetime import datetime
from models.database import MoodEntry

def show():
    st.title("📝 Mood Log")
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 1
    
    st.markdown("How are you feeling today? Rate each dimension from 1-10:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        happiness = st.slider("😊 Happiness", 1, 10, 5, help="How happy and content do you feel?")
        energy = st.slider("⚡ Energy Level", 1, 10, 5, help="How energetic and motivated do you feel?")
    
    with col2:
        anxiety = st.slider("😰 Anxiety Level", 1, 10, 5, help="How anxious or worried do you feel?")
        motivation = st.slider("🎯 Motivation", 1, 10, 5, help="How motivated and driven do you feel?")
    
    notes = st.text_area("Additional Notes (Optional)", 
                        placeholder="Any specific thoughts, events, or feelings you'd like to record...")
    
    weather = st.selectbox("Weather Today", 
                          ["Sunny", "Cloudy", "Rainy", "Snowy", "Stormy", "Other"])
    
    if st.button("Save Mood Entry", type="primary"):
        session = st.session_state.db_manager.get_session()
        
        try:
            mood_entry = MoodEntry(
                user_id=st.session_state.user_id,
                timestamp=datetime.now(),
                happiness=happiness,
                energy=energy,
                anxiety=anxiety,
                motivation=motivation,
                notes=notes if notes else None,
                weather=weather
            )
            
            session.add(mood_entry)
            session.commit()
            
            st.success("✅ Mood entry saved successfully!")
            
            with st.expander("Your Entry Summary"):
                st.write(f"**Happiness:** {happiness}/10")
                st.write(f"**Energy:** {energy}/10")
                st.write(f"**Anxiety:** {anxiety}/10")
                st.write(f"**Motivation:** {motivation}/10")
                st.write(f"**Weather:** {weather}")
                if notes:
                    st.write(f"**Notes:** {notes}")
                st.write(f"**Recorded:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        except Exception as e:
            st.error(f"Error saving mood entry: {str(e)}")
        
        finally:
            st.session_state.db_manager.close_session(session)
    
    st.markdown("---")
    st.subheader("Recent Entries")
    
    session = st.session_state.db_manager.get_session()
    
    try:
        recent_entries = session.query(MoodEntry).filter_by(
            user_id=st.session_state.user_id
        ).order_by(MoodEntry.timestamp.desc()).limit(5).all()
        
        if recent_entries:
            for entry in recent_entries:
                with st.expander(f"Entry from {entry.timestamp.strftime('%Y-%m-%d %H:%M')}"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Happiness", f"{entry.happiness}/10")
                    with col2:
                        st.metric("Energy", f"{entry.energy}/10")
                    with col3:
                        st.metric("Anxiety", f"{entry.anxiety}/10")
                    with col4:
                        st.metric("Motivation", f"{entry.motivation}/10")
                    
                    if entry.notes:
                        st.write(f"**Notes:** {entry.notes}")
                    if entry.weather:
                        st.write(f"**Weather:** {entry.weather}")
        else:
            st.info("No mood entries yet. Log your first mood above!")
    
    finally:
        st.session_state.db_manager.close_session(session)