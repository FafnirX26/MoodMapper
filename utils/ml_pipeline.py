import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from scipy import stats
from datetime import datetime, timedelta
import joblib

def safe_convert_to_float(value):
    """Safely convert value to float, handling bytes and None values"""
    if value is None:
        return 0.0
    if isinstance(value, bytes):
        try:
            # Try to decode bytes to string first
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
            # Try to decode bytes to string first
            decoded = value.decode('utf-8', errors='ignore').strip()
            if not decoded or decoded == '\x00' * len(decoded):
                return 0
            return int(float(decoded))  # Convert to float first to handle decimal strings
        except (ValueError, UnicodeDecodeError):
            return 0
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0

class MoodMapperML:
    def __init__(self):
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.mood_predictor = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def preprocess_data(self, mood_entries, behavioral_data):
        """Clean and prepare data for ML analysis"""
        
        # Convert mood entries to DataFrame
        mood_df = pd.DataFrame([{
            'date': entry.timestamp.date(),
            'timestamp': entry.timestamp,
            'happiness': safe_convert_to_float(entry.happiness),
            'energy': safe_convert_to_float(entry.energy),
            'anxiety': safe_convert_to_float(entry.anxiety),
            'motivation': safe_convert_to_float(entry.motivation),
            'mood_score': safe_convert_to_float(entry.happiness) + safe_convert_to_float(entry.energy) - safe_convert_to_float(entry.anxiety) + safe_convert_to_float(entry.motivation)
        } for entry in mood_entries])
        
        # Convert behavioral data to DataFrame
        if behavioral_data:
            behavioral_df = pd.DataFrame([{
                'date': data.timestamp.date(),
                'sleep_hours': safe_convert_to_float(data.sleep_hours),
                'steps': safe_convert_to_int(data.steps),
                'screen_time': safe_convert_to_float(data.screen_time),
                'location_changes': safe_convert_to_int(data.location_changes)
            } for data in behavioral_data])
            
            # Merge datasets
            combined_df = pd.merge(mood_df, behavioral_df, on='date', how='inner')
        else:
            combined_df = mood_df
        
        # Add time-based features
        combined_df['day_of_week'] = pd.to_datetime(combined_df['timestamp']).dt.dayofweek
        combined_df['is_weekend'] = combined_df['day_of_week'].isin([5, 6]).astype(int)
        
        # Handle missing values (only for numeric columns)
        numeric_columns = combined_df.select_dtypes(include=[np.number]).columns
        combined_df[numeric_columns] = combined_df[numeric_columns].fillna(combined_df[numeric_columns].mean())
        
        return combined_df
    
    def detect_anomalies(self, df):
        """Detect unusual behavioral patterns using Isolation Forest"""
        
        if len(df) < 7:
            return []
        
        # Select features for anomaly detection
        feature_columns = ['happiness', 'energy', 'anxiety', 'motivation']
        
        if 'sleep_hours' in df.columns:
            feature_columns.extend(['sleep_hours', 'steps', 'screen_time'])
        
        features = df[feature_columns].values
        
        # Fit and predict anomalies
        anomaly_scores = self.anomaly_detector.fit_predict(features)
        outlier_scores = self.anomaly_detector.decision_function(features)
        
        # Identify anomalous days
        anomalies = []
        for idx, (score, outlier_score) in enumerate(zip(anomaly_scores, outlier_scores)):
            if score == -1:  # Anomaly detected
                anomalies.append({
                    'date': df.iloc[idx]['date'],
                    'anomaly_score': abs(outlier_score),
                    'mood_score': df.iloc[idx]['mood_score'],
                    'type': 'behavioral_anomaly'
                })
        
        return anomalies
    
    def analyze_correlations(self, df):
        """Find correlations between mood and behavioral factors"""
        
        correlations = []
        
        if len(df) < 7:
            return correlations
        
        mood_metrics = ['happiness', 'energy', 'anxiety', 'motivation']
        behavioral_metrics = []
        
        if 'sleep_hours' in df.columns:
            behavioral_metrics = ['sleep_hours', 'steps', 'screen_time', 'location_changes']
        
        # Calculate correlations
        for mood_metric in mood_metrics:
            for behavioral_metric in behavioral_metrics:
                if behavioral_metric in df.columns:
                    corr_coef, p_value = stats.pearsonr(
                        df[mood_metric].fillna(df[mood_metric].mean()),
                        df[behavioral_metric].fillna(df[behavioral_metric].mean())
                    )
                    
                    if abs(corr_coef) > 0.3 and p_value < 0.05:
                        correlations.append({
                            'mood_factor': mood_metric,
                            'behavioral_factor': behavioral_metric,
                            'correlation': corr_coef,
                            'p_value': p_value,
                            'strength': self._get_correlation_strength(abs(corr_coef)),
                            'direction': 'positive' if corr_coef > 0 else 'negative'
                        })
        
        return sorted(correlations, key=lambda x: abs(x['correlation']), reverse=True)
    
    def predict_mood_risk(self, df):
        """Predict potential mood episodes based on recent patterns"""
        
        if len(df) < 14:
            return None
        
        # Calculate recent vs baseline metrics
        recent_data = df.tail(7)
        baseline_data = df.iloc[-14:-7]
        
        recent_mood = recent_data['mood_score'].mean()
        baseline_mood = baseline_data['mood_score'].mean()
        
        mood_change = recent_mood - baseline_mood
        mood_volatility = recent_data['mood_score'].std()
        
        # Risk assessment
        risk_factors = []
        
        if mood_change < -3:
            risk_factors.append("Significant mood decline")
        
        if mood_volatility > 3:
            risk_factors.append("High mood volatility")
        
        if recent_data['anxiety'].mean() > 7:
            risk_factors.append("Elevated anxiety levels")
        
        if recent_data['energy'].mean() < 4:
            risk_factors.append("Low energy levels")
        
        if 'sleep_hours' in recent_data.columns:
            if recent_data['sleep_hours'].mean() < 6:
                risk_factors.append("Insufficient sleep")
        
        # Calculate risk score
        risk_score = len(risk_factors) / 5.0  # Normalize to 0-1
        
        return {
            'risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score),
            'risk_factors': risk_factors,
            'mood_change': mood_change,
            'recent_mood': recent_mood,
            'baseline_mood': baseline_mood
        }
    
    def generate_insights(self, mood_entries, behavioral_data):
        """Generate comprehensive insights from user data"""
        
        insights = []
        
        # Preprocess data
        df = self.preprocess_data(mood_entries, behavioral_data)
        
        if len(df) < 7:
            return [{
                'type': 'info',
                'title': 'Insufficient Data',
                'description': 'Keep logging your mood for at least a week to get personalized insights.',
                'confidence': 1.0,
                'actionable': False
            }]
        
        # Detect anomalies
        anomalies = self.detect_anomalies(df)
        for anomaly in anomalies:
            insights.append({
                'type': 'anomaly',
                'title': f'Unusual Pattern Detected',
                'description': f'Your mood pattern on {anomaly["date"]} was significantly different from your typical patterns. This could indicate external stressors or changes in routine.',
                'confidence': min(0.9, anomaly['anomaly_score']),
                'actionable': True
            })
        
        # Analyze correlations
        correlations = self.analyze_correlations(df)
        for corr in correlations[:3]:  # Top 3 correlations
            direction = "positively" if corr['direction'] == 'positive' else "negatively"
            insights.append({
                'type': 'correlation',
                'title': f'{corr["behavioral_factor"].title()} Affects {corr["mood_factor"].title()}',
                'description': f'Your {corr["behavioral_factor"].replace("_", " ")} is {direction} correlated with your {corr["mood_factor"]} levels (r={corr["correlation"]:.2f}). This suggests that changes in {corr["behavioral_factor"].replace("_", " ")} may influence how you feel.',
                'confidence': min(0.95, abs(corr['correlation'])),
                'actionable': True
            })
        
        # Risk assessment
        risk_analysis = self.predict_mood_risk(df)
        if risk_analysis:
            if risk_analysis['risk_score'] > 0.6:
                insights.append({
                    'type': 'warning',
                    'title': 'Elevated Risk Detected',
                    'description': f'Based on recent patterns, there may be increased risk for mood difficulties. Key concerns: {", ".join(risk_analysis["risk_factors"])}. Consider implementing self-care strategies or reaching out for support.',
                    'confidence': risk_analysis['risk_score'],
                    'actionable': True
                })
            elif risk_analysis['risk_score'] < 0.2:
                insights.append({
                    'type': 'positive',
                    'title': 'Stable Mood Patterns',
                    'description': 'Your mood patterns have been relatively stable recently. Keep up the good work with your current routine and self-care practices.',
                    'confidence': 1.0 - risk_analysis['risk_score'],
                    'actionable': False
                })
        
        # Trend analysis
        if len(df) >= 14:
            recent_trend = df.tail(14)['mood_score'].diff().mean()
            if recent_trend > 0.5:
                insights.append({
                    'type': 'positive',
                    'title': 'Improving Mood Trend',
                    'description': 'Your overall mood has been trending upward over the past two weeks. This is a positive sign that your current strategies are working well.',
                    'confidence': 0.8,
                    'actionable': False
                })
            elif recent_trend < -0.5:
                insights.append({
                    'type': 'concern',
                    'title': 'Declining Mood Trend',
                    'description': 'Your mood has been trending downward recently. Consider reviewing your recent activities, stress levels, and self-care practices. It might be helpful to talk to someone you trust.',
                    'confidence': 0.8,
                    'actionable': True
                })
        
        return insights if insights else [{
            'type': 'info',
            'title': 'Keep Tracking',
            'description': 'Continue logging your mood and activities to build a more complete picture of your patterns.',
            'confidence': 1.0,
            'actionable': False
        }]
    
    def _get_correlation_strength(self, correlation):
        """Categorize correlation strength"""
        if correlation >= 0.7:
            return "Strong"
        elif correlation >= 0.4:
            return "Moderate"
        elif correlation >= 0.2:
            return "Weak"
        else:
            return "Very Weak"
    
    def _get_risk_level(self, risk_score):
        """Categorize risk level"""
        if risk_score >= 0.7:
            return "High"
        elif risk_score >= 0.4:
            return "Moderate"
        elif risk_score >= 0.2:
            return "Low"
        else:
            return "Very Low"