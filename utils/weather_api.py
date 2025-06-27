import requests
from datetime import datetime
import json

class WeatherAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key or "demo_key"
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.demo_mode = api_key is None or api_key == "demo_key"
    
    def get_current_weather(self, city="New York"):
        """Get current weather data for a city"""
        
        if self.demo_mode:
            return self._get_demo_weather()
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'],
                'main': data['weather'][0]['main'],
                'city': data['name'],
                'country': data['sys']['country'],
                'timestamp': datetime.now()
            }
        
        except requests.RequestException as e:
            print(f"Weather API error: {e}")
            return self._get_demo_weather()
        except KeyError as e:
            print(f"Weather data parsing error: {e}")
            return self._get_demo_weather()
    
    def get_weather_forecast(self, city="New York", days=5):
        """Get weather forecast for upcoming days"""
        
        if self.demo_mode:
            return self._get_demo_forecast(days)
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (every 3 hours)
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            forecast = []
            for item in data['list'][::8]:  # Take one forecast per day
                forecast.append({
                    'date': datetime.fromtimestamp(item['dt']).date(),
                    'temperature': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'description': item['weather'][0]['description'],
                    'main': item['weather'][0]['main']
                })
            
            return forecast
        
        except requests.RequestException as e:
            print(f"Weather forecast API error: {e}")
            return self._get_demo_forecast(days)
        except KeyError as e:
            print(f"Weather forecast parsing error: {e}")
            return self._get_demo_forecast(days)
    
    def _get_demo_weather(self):
        """Return demo weather data when API is not available"""
        import random
        
        weather_conditions = [
            {'main': 'Clear', 'description': 'clear sky'},
            {'main': 'Clouds', 'description': 'scattered clouds'},
            {'main': 'Rain', 'description': 'light rain'},
            {'main': 'Snow', 'description': 'light snow'},
            {'main': 'Clouds', 'description': 'overcast clouds'}
        ]
        
        condition = random.choice(weather_conditions)
        
        return {
            'temperature': round(random.uniform(15, 25), 1),
            'humidity': random.randint(40, 80),
            'pressure': random.randint(1000, 1020),
            'description': condition['description'],
            'main': condition['main'],
            'city': 'Demo City',
            'country': 'Demo',
            'timestamp': datetime.now()
        }
    
    def _get_demo_forecast(self, days):
        """Return demo forecast data"""
        import random
        from datetime import timedelta
        
        forecast = []
        base_temp = random.uniform(15, 25)
        
        weather_conditions = ['Clear', 'Clouds', 'Rain', 'Snow']
        
        for i in range(days):
            date = datetime.now().date() + timedelta(days=i+1)
            temp_variation = random.uniform(-5, 5)
            
            forecast.append({
                'date': date,
                'temperature': round(base_temp + temp_variation, 1),
                'humidity': random.randint(40, 80),
                'description': f"{random.choice(weather_conditions).lower()} sky",
                'main': random.choice(weather_conditions)
            })
        
        return forecast
    
    def get_weather_impact_on_mood(self, weather_data, user_mood_history):
        """Analyze correlation between weather and mood"""
        
        if not weather_data or not user_mood_history:
            return None
        
        # Simple correlation analysis
        weather_mood_correlations = {
            'Clear': 0.2,      # Sunny weather slightly improves mood
            'Clouds': -0.1,    # Cloudy weather slightly lowers mood
            'Rain': -0.3,      # Rainy weather tends to lower mood
            'Snow': -0.2,      # Snowy weather slightly lowers mood
            'Thunderstorm': -0.4  # Storms tend to negatively impact mood
        }
        
        weather_condition = weather_data.get('main', 'Clear')
        expected_impact = weather_mood_correlations.get(weather_condition, 0)
        
        recommendations = []
        
        if expected_impact < -0.2:
            recommendations.extend([
                "Consider indoor activities today",
                "Light therapy might be helpful",
                "Practice mindfulness or meditation",
                "Connect with friends virtually"
            ])
        elif expected_impact > 0.1:
            recommendations.extend([
                "Take advantage of the nice weather",
                "Go for a walk outside",
                "Spend time in natural light",
                "Consider outdoor activities"
            ])
        
        return {
            'weather_condition': weather_condition,
            'expected_mood_impact': expected_impact,
            'impact_description': self._get_impact_description(expected_impact),
            'recommendations': recommendations,
            'temperature': weather_data.get('temperature'),
            'description': weather_data.get('description')
        }
    
    def _get_impact_description(self, impact_score):
        """Convert impact score to descriptive text"""
        if impact_score > 0.2:
            return "Likely to boost your mood"
        elif impact_score > 0:
            return "Slightly positive for mood"
        elif impact_score > -0.2:
            return "Minimal impact on mood"
        elif impact_score > -0.3:
            return "May slightly lower mood"
        else:
            return "Could negatively impact mood"

# Singleton instance for global use
weather_api = WeatherAPI()