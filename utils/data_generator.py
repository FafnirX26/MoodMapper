import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from models.database import MoodEntry, BehavioralData

def generate_demo_data(session, user_id, days=30, pattern="Mixed"):
    """Generate synthetic mood and behavioral data for demo purposes"""
    
    start_date = datetime.now() - timedelta(days=days)
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        
        # Generate mood data based on pattern
        if pattern == "Stable":
            base_happiness = 6 + np.random.normal(0, 0.8)
            base_energy = 6 + np.random.normal(0, 0.8)
            base_anxiety = 4 + np.random.normal(0, 0.8)
            base_motivation = 6 + np.random.normal(0, 0.8)
        
        elif pattern == "Improving":
            progress = day / days
            base_happiness = 4 + 3 * progress + np.random.normal(0, 0.8)
            base_energy = 4 + 3 * progress + np.random.normal(0, 0.8)
            base_anxiety = 6 - 2 * progress + np.random.normal(0, 0.8)
            base_motivation = 4 + 3 * progress + np.random.normal(0, 0.8)
        
        elif pattern == "Declining":
            progress = day / days
            base_happiness = 7 - 3 * progress + np.random.normal(0, 0.8)
            base_energy = 7 - 3 * progress + np.random.normal(0, 0.8)
            base_anxiety = 3 + 3 * progress + np.random.normal(0, 0.8)
            base_motivation = 7 - 3 * progress + np.random.normal(0, 0.8)
        
        elif pattern == "Seasonal":
            # Simulate seasonal affective pattern
            seasonal_factor = np.sin(2 * np.pi * day / 365) * 2
            base_happiness = 6 + seasonal_factor + np.random.normal(0, 0.8)
            base_energy = 6 + seasonal_factor + np.random.normal(0, 0.8)
            base_anxiety = 4 - seasonal_factor + np.random.normal(0, 0.8)
            base_motivation = 6 + seasonal_factor + np.random.normal(0, 0.8)
        
        else:  # Mixed pattern
            base_happiness = 3 + np.random.beta(2, 2) * 7
            base_energy = 3 + np.random.beta(2, 2) * 7
            base_anxiety = 1 + np.random.beta(2, 2) * 8
            base_motivation = 3 + np.random.beta(2, 2) * 7
        
        # Ensure values are within 1-10 range
        happiness = max(1, min(10, int(base_happiness)))
        energy = max(1, min(10, int(base_energy)))
        anxiety = max(1, min(10, int(base_anxiety)))
        motivation = max(1, min(10, int(base_motivation)))
        
        # Add weekend effect
        if current_date.weekday() >= 5:  # Weekend
            happiness += np.random.choice([-1, 0, 1, 2])
            energy += np.random.choice([-2, -1, 0, 1])
            anxiety += np.random.choice([-2, -1, 0, 1])
        
        # Ensure bounds again
        happiness = max(1, min(10, happiness))
        energy = max(1, min(10, energy))
        anxiety = max(1, min(10, anxiety))
        motivation = max(1, min(10, motivation))
        
        # Generate weather
        weather_options = ["Sunny", "Cloudy", "Rainy", "Snowy", "Stormy"]
        weather = np.random.choice(weather_options, p=[0.4, 0.3, 0.15, 0.1, 0.05])
        
        # Create mood entry
        mood_entry = MoodEntry(
            user_id=user_id,
            timestamp=current_date,
            happiness=happiness,
            energy=energy,
            anxiety=anxiety,
            motivation=motivation,
            weather=weather,
            notes=generate_random_note(happiness, energy, anxiety) if np.random.random() < 0.3 else None
        )
        
        session.add(mood_entry)
        
        # Generate behavioral data
        sleep_hours = 6 + np.random.normal(1.5, 1)
        sleep_hours = max(4, min(12, sleep_hours))
        
        # Correlate steps with energy and mood
        base_steps = 5000 + (energy * 800) + np.random.normal(0, 2000)
        steps = max(1000, int(base_steps))
        
        # Screen time inversely correlated with mood
        screen_time = 8 - (happiness * 0.5) + np.random.normal(0, 2)
        screen_time = max(2, min(16, screen_time))
        
        # Location changes
        location_changes = np.random.poisson(3)
        
        behavioral_data = BehavioralData(
            user_id=user_id,
            timestamp=current_date,
            data_type="daily_summary",
            sleep_hours=sleep_hours,
            steps=steps,
            screen_time=screen_time,
            location_changes=location_changes,
            processed=False,
            anomaly_score=None
        )
        
        session.add(behavioral_data)

def generate_random_note(happiness, energy, anxiety):
    """Generate realistic mood notes based on scores"""
    
    positive_notes = [
        "Feeling great today! Had a good workout.",
        "Productive day at work, feeling accomplished.",
        "Spent time with friends, feeling connected.",
        "Beautiful weather today, went for a walk.",
        "Completed a personal project, feeling proud."
    ]
    
    neutral_notes = [
        "Regular day, nothing special.",
        "Work was okay, feeling steady.",
        "Did some reading, feeling calm.",
        "Routine day, staying consistent.",
        "Balanced day with work and rest."
    ]
    
    negative_notes = [
        "Feeling a bit overwhelmed with work.",
        "Didn't sleep well last night.",
        "Feeling anxious about upcoming deadlines.",
        "Low energy today, stayed indoors.",
        "Struggling to stay motivated."
    ]
    
    if happiness >= 7 and energy >= 6:
        return np.random.choice(positive_notes)
    elif happiness <= 4 or anxiety >= 7:
        return np.random.choice(negative_notes)
    else:
        return np.random.choice(neutral_notes)