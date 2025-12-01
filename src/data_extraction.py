"""
Data Extraction Module
Fetches weather data from OpenWeatherMap API
"""
import os
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


class WeatherDataExtractor:
    """Extract weather data from OpenWeatherMap API"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.lat = float(os.getenv('OPENWEATHER_LAT', '51.5074'))
        self.lon = float(os.getenv('OPENWEATHER_LON', '-0.1278'))
        self.city = os.getenv('OPENWEATHER_CITY', 'London')
        
        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY not found in environment variables")
        
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    def fetch_current_weather(self) -> Dict[str, Any]:
        """Fetch current weather data"""
        url = f"{self.base_url}/weather"
        params = {
            'lat': self.lat,
            'lon': self.lon,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def fetch_forecast(self) -> Dict[str, Any]:
        """Fetch 5-day forecast data (3-hour intervals)"""
        url = f"{self.base_url}/forecast"
        params = {
            'lat': self.lat,
            'lon': self.lon,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def extract_and_save(self, output_path: str) -> str:
        """
        Extract weather data and save to CSV with timestamp
        
        Args:
            output_path: Base path for saving data
            
        Returns:
            Path to saved file
        """
        # Fetch data
        current = self.fetch_current_weather()
        forecast = self.fetch_forecast()
        
        # Create timestamp
        collection_time = datetime.now()
        timestamp_str = collection_time.strftime('%Y%m%d_%H%M%S')
        
        # Parse forecast data
        records = []
        for item in forecast['list']:
            record = {
                'collection_timestamp': collection_time,
                'forecast_timestamp': datetime.fromtimestamp(item['dt']),
                'city': self.city,
                'latitude': self.lat,
                'longitude': self.lon,
                'temperature': item['main']['temp'],
                'feels_like': item['main']['feels_like'],
                'temp_min': item['main']['temp_min'],
                'temp_max': item['main']['temp_max'],
                'pressure': item['main']['pressure'],
                'humidity': item['main']['humidity'],
                'weather_main': item['weather'][0]['main'],
                'weather_description': item['weather'][0]['description'],
                'clouds': item['clouds']['all'],
                'wind_speed': item['wind']['speed'],
                'wind_deg': item['wind']['deg'],
                'visibility': item.get('visibility', None),
                'pop': item.get('pop', 0),  # Probability of precipitation
                'rain_3h': item.get('rain', {}).get('3h', 0),
                'snow_3h': item.get('snow', {}).get('3h', 0)
            }
            records.append(record)
        
        # Create DataFrame
        df = pd.DataFrame(records)
        
        # Save to CSV
        filename = f"weather_data_{timestamp_str}.csv"
        filepath = os.path.join(output_path, filename)
        os.makedirs(output_path, exist_ok=True)
        df.to_csv(filepath, index=False)
        
        print(f"Data extracted and saved to {filepath}")
        print(f"Shape: {df.shape}")
        print(f"Collection time: {collection_time}")
        
        return filepath


if __name__ == "__main__":
    extractor = WeatherDataExtractor()
    output = extractor.extract_and_save("/opt/airflow/data/raw")
    print(f"Saved to: {output}")
