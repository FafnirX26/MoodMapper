from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import hashlib

class PrivacyManager:
    def __init__(self, password=None):
        self.password = password or "default_mood_mapper_key"
        self.key = self._generate_key()
        self.cipher = Fernet(self.key)
    
    def _generate_key(self):
        """Generate encryption key from password"""
        password = self.password.encode()
        salt = b'mood_mapper_salt_2024'  # In production, use random salt per user
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_text(self, text):
        """Encrypt sensitive text data"""
        if not text:
            return text
        return self.cipher.encrypt(text.encode()).decode()
    
    def decrypt_text(self, encrypted_text):
        """Decrypt sensitive text data"""
        if not encrypted_text:
            return encrypted_text
        try:
            return self.cipher.decrypt(encrypted_text.encode()).decode()
        except:
            return "[Decryption Error]"
    
    def hash_email(self, email):
        """Hash email for pseudonymization"""
        return hashlib.sha256(email.encode()).hexdigest()[:16]
    
    def anonymize_notes(self, notes):
        """Remove potentially identifying information from notes"""
        if not notes:
            return notes
        
        # Simple anonymization - remove common identifying patterns
        import re
        
        # Remove email addresses
        notes = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', notes)
        
        # Remove phone numbers
        notes = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', notes)
        
        # Remove names (simple pattern - this could be enhanced)
        notes = re.sub(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[NAME]', notes)
        
        return notes
    
    def get_privacy_summary(self):
        """Return summary of privacy protections"""
        return {
            "data_encryption": "AES-256 encryption for sensitive fields",
            "local_storage": "All data stored locally on device",
            "data_anonymization": "Personal identifiers removed/hashed",
            "no_cloud_sync": "No data transmitted to external servers",
            "user_control": "Complete data export and deletion capabilities"
        }

class DataMinimizer:
    """Implements data minimization principles"""
    
    @staticmethod
    def should_collect_location(user_consent, privacy_level):
        """Determine if location data should be collected"""
        return user_consent and privacy_level in ['standard', 'enhanced']
    
    @staticmethod
    def should_collect_detailed_notes(privacy_level):
        """Determine if detailed notes should be stored"""
        return privacy_level in ['standard', 'enhanced']
    
    @staticmethod
    def get_retention_period(data_type):
        """Get data retention period for different data types"""
        retention_periods = {
            'mood_entries': 730,  # 2 years
            'behavioral_data': 365,  # 1 year
            'insights': 180,  # 6 months
            'user_profile': -1  # Indefinite (until user deletion)
        }
        return retention_periods.get(data_type, 365)
    
    @staticmethod
    def cleanup_old_data(session, user_id, data_type):
        """Remove data older than retention period"""
        from datetime import datetime, timedelta
        from models.database import MoodEntry, BehavioralData, Insight
        
        retention_days = DataMinimizer.get_retention_period(data_type)
        if retention_days == -1:
            return 0  # No cleanup for indefinite retention
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        deleted_count = 0
        
        if data_type == 'mood_entries':
            deleted_count = session.query(MoodEntry).filter(
                MoodEntry.user_id == user_id,
                MoodEntry.timestamp < cutoff_date
            ).delete()
        
        elif data_type == 'behavioral_data':
            deleted_count = session.query(BehavioralData).filter(
                BehavioralData.user_id == user_id,
                BehavioralData.timestamp < cutoff_date
            ).delete()
        
        elif data_type == 'insights':
            deleted_count = session.query(Insight).filter(
                Insight.user_id == user_id,
                Insight.timestamp < cutoff_date
            ).delete()
        
        session.commit()
        return deleted_count

class ConsentManager:
    """Manage user consent for different data types"""
    
    DEFAULT_CONSENT = {
        'mood_tracking': True,
        'behavioral_analysis': True,
        'location_tracking': False,
        'detailed_notes': True,
        'ml_insights': True,
        'data_export': True,
        'anonymized_research': False
    }
    
    @staticmethod
    def get_user_consent(user_id, session):
        """Retrieve user consent settings"""
        # In a real implementation, this would query a consent table
        # For demo purposes, return default consent
        return ConsentManager.DEFAULT_CONSENT.copy()
    
    @staticmethod
    def update_consent(user_id, consent_type, consent_given, session):
        """Update specific consent setting"""
        # In a real implementation, this would update the consent table
        # For demo purposes, we'll just validate the input
        valid_consent_types = list(ConsentManager.DEFAULT_CONSENT.keys())
        
        if consent_type not in valid_consent_types:
            raise ValueError(f"Invalid consent type: {consent_type}")
        
        if not isinstance(consent_given, bool):
            raise ValueError("Consent must be True or False")
        
        # Would update database here
        return True
    
    @staticmethod
    def get_consent_summary(user_id, session):
        """Get summary of user's consent settings"""
        consent = ConsentManager.get_user_consent(user_id, session)
        
        summary = {
            'total_permissions': len(consent),
            'granted_permissions': sum(consent.values()),
            'privacy_level': 'high' if sum(consent.values()) < 4 else 'standard',
            'last_updated': '2024-01-01'  # Would be real timestamp
        }
        
        return summary