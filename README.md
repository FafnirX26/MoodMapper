# 🧠 Mood Mapper

**Intelligent Mental Health Monitoring Application**

Mood Mapper uses passive behavioral data analysis and machine learning to detect early signs of depression and anxiety episodes, providing predictive insights and gentle interventions for proactive mental healthcare.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the repository**
```bash
git clone <repository_url>
cd MoodMapper
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
streamlit run app.py
```

4. **Open your browser**
The app will automatically open at `http://localhost:8501`

## 📱 Features

### Core Functionality
- **📝 Mood Logging**: Quick daily mood tracking with multiple dimensions
- **📊 Dashboard**: Visual analytics of mood trends and behavioral patterns  
- **🔍 ML Insights**: AI-powered pattern recognition and early warning system
- **⚙️ Privacy Controls**: Complete data ownership with local storage
- **🎭 Demo Data**: Generate synthetic data to explore features

### Advanced Analytics
- **Anomaly Detection**: Identifies unusual behavioral patterns
- **Correlation Analysis**: Discovers relationships between mood and activities
- **Risk Assessment**: Early warning system for potential mood episodes
- **Trend Analysis**: Long-term mood pattern recognition
- **Weather Integration**: Environmental impact on mood tracking

## 🏗️ Architecture

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Backend**: SQLAlchemy with SQLite database
- **ML/Analytics**: scikit-learn, pandas, numpy
- **Visualization**: Plotly, matplotlib, seaborn
- **Privacy**: Local data processing with encryption

### Project Structure
```
MoodMapper/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── models/
│   └── database.py       # SQLAlchemy data models
├── src/
│   └── pages/            # Streamlit page components
│       ├── dashboard.py
│       ├── mood_log.py
│       ├── insights.py
│       └── settings.py
├── utils/
│   ├── ml_pipeline.py    # Machine learning algorithms
│   ├── data_generator.py # Demo data generation
│   ├── privacy.py        # Privacy and encryption tools
│   └── weather_api.py    # Weather integration
└── data/                 # Local SQLite database storage
```

## 🔒 Privacy & Security

### Data Protection
- **Local Storage**: All data stored locally on your device
- **AES-256 Encryption**: Sensitive data encrypted at rest
- **No Cloud Sync**: Zero data transmission to external servers
- **Anonymization**: Personal identifiers removed from analytics
- **User Control**: Complete data export and deletion capabilities

### Compliance
- HIPAA-compliant data handling practices
- GDPR-ready privacy controls
- Granular consent management
- Automatic data retention policies

## 🧪 Demo Mode

To explore Mood Mapper's features with synthetic data:

1. Navigate to **Settings** → **Demo Data**
2. Choose pattern type (Stable, Improving, Declining, Seasonal, Mixed)
3. Select number of days (7-90)
4. Click **Generate Demo Data**
5. Explore the **Dashboard** and **Insights** pages

## 📊 Usage Guide

### Getting Started
1. **Create Profile**: Set up your user profile in Settings
2. **Log First Mood**: Use the Mood Log page to record your current state
3. **Generate Demo Data**: Create sample data to explore features
4. **View Dashboard**: See your mood trends and patterns
5. **Check Insights**: Get AI-powered analysis and recommendations

### Daily Workflow
1. **Morning Check-in**: Log your mood and energy levels
2. **Review Insights**: Check for any new patterns or alerts
3. **Follow Recommendations**: Implement suggested self-care activities
4. **Evening Reflection**: Optional additional mood entry

## 🤖 Machine Learning Features

### Pattern Recognition
- **Isolation Forest**: Detects unusual behavioral anomalies
- **Correlation Analysis**: Identifies mood-behavior relationships
- **Trend Detection**: Recognizes long-term mood patterns
- **Risk Scoring**: Calculates early warning indicators

### Insight Types
- **Behavioral Anomalies**: Unusual patterns in daily activities
- **Correlation Insights**: Relationships between lifestyle and mood
- **Risk Warnings**: Early indicators of potential mood episodes
- **Positive Reinforcement**: Recognition of improving trends

## 🛠️ Development

### Local Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py

# Run tests (if available)
pytest tests/

# Code formatting
black src/ models/ utils/

# Linting
flake8 src/ models/ utils/
```

### Adding New Features
1. Create new page in `src/pages/`
2. Add database models in `models/database.py`
3. Implement ML algorithms in `utils/ml_pipeline.py`
4. Update main navigation in `app.py`

## 📈 Roadmap

### Phase 1 (Current)
- ✅ Core mood logging functionality
- ✅ Basic ML pattern recognition
- ✅ Privacy-first data handling
- ✅ Interactive dashboard

### Phase 2 (Future)
- 🔄 Care team integration
- 🔄 Advanced predictive modeling
- 🔄 Wearable device integration
- 🔄 Community support features

### Phase 3 (Vision)
- 🔮 Clinical trial integration
- 🔮 Healthcare provider dashboard
- 🔮 Research collaboration tools
- 🔮 Mobile app development

## 🆘 Support & Resources

### Mental Health Resources
- **Crisis Hotline**: 988 (US Suicide & Crisis Lifeline)
- **Crisis Text Line**: Text HOME to 741741
- **International**: Visit findahelpline.com

### Technical Support
- Check the Issues section for known problems
- Review documentation in the code comments
- Consult Streamlit documentation for UI questions

## ⚖️ Legal & Ethics

### Disclaimer
Mood Mapper is a wellness tool for personal insights and is not intended to diagnose, treat, cure, or prevent any medical condition. Always consult healthcare professionals for medical advice.

### Data Responsibility
- Users maintain full ownership of their data
- No data is shared without explicit consent
- All processing occurs locally on user devices
- Regular data backups are user's responsibility

### Ethical AI
- Transparent algorithmic decision-making
- Bias-aware model development
- User agency in all AI-driven recommendations
- Continuous model validation and improvement

---

**🧠 Mood Mapper** - Transforming reactive mental healthcare into predictive, preventive care through intelligent behavioral pattern analysis.

*Built with ❤️ for mental health awareness and proactive wellbeing.*