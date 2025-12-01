#!/usr/bin/env python3
"""
Test script to demonstrate data extraction and quality check
This simulates what happens in the Airflow DAG
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from data_extraction import WeatherDataExtractor
from data_quality import validate_data_quality

# Expected columns for quality check
EXPECTED_COLUMNS = [
    'collection_timestamp', 'forecast_timestamp', 'city', 'latitude', 'longitude',
    'temperature', 'feels_like', 'temp_min', 'temp_max', 'pressure', 'humidity',
    'weather_main', 'weather_description', 'clouds', 'wind_speed', 'wind_deg',
    'visibility', 'pop', 'rain_3h', 'snow_3h'
]

def main():
    """Test extraction and quality check pipeline"""
    
    print("="*60)
    print("WEATHER DATA EXTRACTION & QUALITY CHECK TEST")
    print("="*60)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Step 1: Data Extraction
    print("\n[STEP 1] DATA EXTRACTION")
    print("-"*60)
    try:
        extractor = WeatherDataExtractor()
        output_path = 'data/raw'
        
        print(f"API Configuration:")
        print(f"  - City: {extractor.city}")
        print(f"  - Latitude: {extractor.lat}")
        print(f"  - Longitude: {extractor.lon}")
        print(f"  - API Key: {'*' * 32}...{extractor.api_key[-4:]}")
        
        print(f"\nFetching data from OpenWeatherMap API...")
        filepath = extractor.extract_and_save(output_path)
        
        print(f"\n✓ Data extraction SUCCESSFUL!")
        print(f"  - File saved: {filepath}")
        
        # Show file info
        import pandas as pd
        df = pd.read_csv(filepath)
        print(f"  - Records: {len(df)} rows")
        print(f"  - Columns: {len(df.columns)} columns")
        print(f"  - File size: {os.path.getsize(filepath) / 1024:.2f} KB")
        
    except Exception as e:
        print(f"\n✗ Data extraction FAILED!")
        print(f"  Error: {str(e)}")
        return False
    
    # Step 2: Data Quality Check
    print("\n" + "="*60)
    print("[STEP 2] MANDATORY QUALITY CHECK")
    print("-"*60)
    
    try:
        print("Running comprehensive quality checks...")
        print("  - Null value check (>1% threshold)")
        print("  - Schema validation")
        print("  - Data type validation")
        print("  - Value range validation")
        print("  - Row count validation")
        
        passed = validate_data_quality(filepath, EXPECTED_COLUMNS)
        
        if passed:
            print("\n" + "="*60)
            print("✓✓✓ ALL QUALITY CHECKS PASSED ✓✓✓")
            print("="*60)
            print("✓ Pipeline can continue to next stage")
            print("✓ Data meets quality standards")
            print("✓ No blocking issues found")
            return True
        else:
            print("\n" + "="*60)
            print("✗✗✗ QUALITY CHECKS FAILED ✗✗✗")
            print("="*60)
            print("✗ Pipeline MUST STOP here")
            print("✗ Data does NOT meet quality standards")
            print("✗ Fix data issues before proceeding")
            return False
            
    except Exception as e:
        print(f"\n✗ Quality check encountered an error!")
        print(f"  Error: {str(e)}")
        return False
    
    finally:
        print("\n" + "="*60)
        print("TEST COMPLETE")
        print("="*60)


if __name__ == "__main__":
    success = main()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
