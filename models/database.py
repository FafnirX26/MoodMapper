from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    age = Column(Integer)
    timezone = Column(String(50))
    onboarding_complete = Column(Boolean, default=False)
    consent_version = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow)

class BehavioralData(Base):
    __tablename__ = 'behavioral_data'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    timestamp = Column(DateTime)
    data_type = Column(String(50))
    sleep_hours = Column(Float)
    steps = Column(Integer)
    screen_time = Column(Float)
    location_changes = Column(Integer)
    processed = Column(Boolean, default=False)
    anomaly_score = Column(Float)

class MoodEntry(Base):
    __tablename__ = 'mood_entries'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    happiness = Column(Integer)
    energy = Column(Integer)
    anxiety = Column(Integer)
    motivation = Column(Integer)
    notes = Column(Text)
    weather = Column(String(50))

class Insight(Base):
    __tablename__ = 'insights'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    insight_type = Column(String(50))
    confidence = Column(Float)
    title = Column(String(255))
    description = Column(Text)
    actionable = Column(Boolean)

class DatabaseManager:
    def __init__(self, database_url="sqlite:///data/moodmapper.db"):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self):
        return self.SessionLocal()
        
    def close_session(self, session):
        session.close()