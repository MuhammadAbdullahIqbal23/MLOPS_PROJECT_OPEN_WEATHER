"""
Data Transformation Module
Feature engineering for weather prediction
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Tuple
import os


class WeatherFeatureEngineering:
    """Transform raw weather data with time-series features"""
    
    def __init__(self):
        pass
    
    def create_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create time-based features
        
        Args:
            df: DataFrame with forecast_timestamp column
            
        Returns:
            DataFrame with additional time features
        """
        df = df.copy()
        
        # Ensure forecast_timestamp is datetime
        df['forecast_timestamp'] = pd.to_datetime(df['forecast_timestamp'])
        
        # Extract time components
        df['hour'] = df['forecast_timestamp'].dt.hour
        df['day_of_week'] = df['forecast_timestamp'].dt.dayofweek
        df['month'] = df['forecast_timestamp'].dt.month
        df['day_of_year'] = df['forecast_timestamp'].dt.dayofyear
        
        # Create cyclical features (important for ML models)
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        # Is weekend
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Time of day categories
        df['time_of_day'] = pd.cut(df['hour'], 
                                     bins=[0, 6, 12, 18, 24],
                                     labels=['night', 'morning', 'afternoon', 'evening'],
                                     include_lowest=True)
        
        return df
    
    def create_lag_features(self, df: pd.DataFrame, target_col: str = 'temperature', 
                           lags: list = [1, 2, 3, 6, 12]) -> pd.DataFrame:
        """
        Create lag features for time series prediction
        
        Args:
            df: DataFrame sorted by time
            target_col: Column to create lags for
            lags: List of lag periods (in rows)
            
        Returns:
            DataFrame with lag features
        """
        df = df.copy()
        df = df.sort_values('forecast_timestamp').reset_index(drop=True)
        
        for lag in lags:
            df[f'{target_col}_lag_{lag}'] = df[target_col].shift(lag)
        
        return df
    
    def create_rolling_features(self, df: pd.DataFrame, target_col: str = 'temperature',
                                windows: list = [3, 6, 12, 24]) -> pd.DataFrame:
        """
        Create rolling window features
        
        Args:
            df: DataFrame sorted by time
            target_col: Column to create rolling features for
            windows: List of window sizes (in rows)
            
        Returns:
            DataFrame with rolling features
        """
        df = df.copy()
        df = df.sort_values('forecast_timestamp').reset_index(drop=True)
        
        for window in windows:
            # Rolling mean
            df[f'{target_col}_rolling_mean_{window}'] = df[target_col].rolling(
                window=window, min_periods=1
            ).mean()
            
            # Rolling std
            df[f'{target_col}_rolling_std_{window}'] = df[target_col].rolling(
                window=window, min_periods=1
            ).std()
            
            # Rolling min/max
            df[f'{target_col}_rolling_min_{window}'] = df[target_col].rolling(
                window=window, min_periods=1
            ).min()
            
            df[f'{target_col}_rolling_max_{window}'] = df[target_col].rolling(
                window=window, min_periods=1
            ).max()
        
        return df
    
    def create_weather_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create domain-specific weather features
        
        Args:
            df: DataFrame with weather data
            
        Returns:
            DataFrame with additional weather features
        """
        df = df.copy()
        
        # Temperature range
        df['temp_range'] = df['temp_max'] - df['temp_min']
        
        # Feels like difference
        df['feels_like_diff'] = df['feels_like'] - df['temperature']
        
        # Comfort index (simplified)
        df['comfort_index'] = df['temperature'] - (0.55 * (1 - df['humidity']/100) * 
                                                    (df['temperature'] - 14))
        
        # Wind chill (simplified, for temp < 10°C)
        df['wind_chill'] = np.where(
            df['temperature'] < 10,
            13.12 + 0.6215 * df['temperature'] - 11.37 * (df['wind_speed'] ** 0.16) + 
            0.3965 * df['temperature'] * (df['wind_speed'] ** 0.16),
            df['temperature']
        )
        
        # Precipitation indicator
        df['has_precipitation'] = ((df['rain_3h'] > 0) | (df['snow_3h'] > 0)).astype(int)
        
        # Weather severity score (custom metric)
        df['weather_severity'] = (
            (df['wind_speed'] / 50) * 0.3 +  # Normalize wind
            (df['pop']) * 0.3 +  # Probability of precipitation
            (df['clouds'] / 100) * 0.2 +  # Cloud cover
            (df['rain_3h'] / 10).clip(0, 1) * 0.2  # Rain amount
        )
        
        return df
    
    def create_target_variable(self, df: pd.DataFrame, target_col: str = 'temperature',
                              hours_ahead: int = 6) -> pd.DataFrame:
        """
        Create target variable for prediction (future value)
        
        Args:
            df: DataFrame sorted by time
            target_col: Column to predict
            hours_ahead: Number of hours ahead to predict (3-hour intervals)
            
        Returns:
            DataFrame with target variable
        """
        df = df.copy()
        df = df.sort_values('forecast_timestamp').reset_index(drop=True)
        
        # Shift backwards to get future value
        steps_ahead = hours_ahead // 3  # Convert hours to 3-hour intervals
        df[f'{target_col}_target_{hours_ahead}h'] = df[target_col].shift(-steps_ahead)
        
        return df
    
    def transform(self, input_filepath: str, output_filepath: str) -> str:
        """
        Complete transformation pipeline
        
        Args:
            input_filepath: Path to raw data CSV
            output_filepath: Path to save processed data
            
        Returns:
            Path to processed file
        """
        print(f"Loading data from {input_filepath}")
        df = pd.read_csv(input_filepath)
        
        print(f"Initial shape: {df.shape}")
        
        # Apply transformations
        print("Creating time features...")
        df = self.create_time_features(df)
        
        print("Creating lag features for temperature...")
        df = self.create_lag_features(df, target_col='temperature', lags=[1, 2, 3, 6])
        
        print("Creating lag features for humidity...")
        df = self.create_lag_features(df, target_col='humidity', lags=[1, 2, 3, 6])
        
        print("Creating rolling features for temperature...")
        df = self.create_rolling_features(df, target_col='temperature', windows=[3, 6, 12])
        
        print("Creating weather-specific features...")
        df = self.create_weather_features(df)
        
        print("Creating target variable (6 hours ahead)...")
        df = self.create_target_variable(df, target_col='temperature', hours_ahead=6)
        
        # Drop rows with NaN in target (last few rows)
        df = df.dropna(subset=[col for col in df.columns if '_target_' in col])
        
        print(f"Final shape: {df.shape}")
        print(f"Total features: {len(df.columns)}")
        
        # Save processed data
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        df.to_csv(output_filepath, index=False)
        
        print(f"Processed data saved to {output_filepath}")
        
        return output_filepath


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 2:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
    else:
        # Default paths
        input_path = "/opt/airflow/data/raw/weather_data_latest.csv"
        output_path = "/opt/airflow/data/processed/weather_data_processed.csv"
    
    transformer = WeatherFeatureEngineering()
    transformer.transform(input_path, output_path)
