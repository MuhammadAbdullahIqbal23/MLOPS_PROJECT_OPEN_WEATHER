"""
Visual Pipeline Diagram Generator
Creates ASCII art representation of the data pipeline
"""

def print_pipeline_diagram():
    """Print complete pipeline with extraction and quality gate"""
    
    diagram = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    WEATHER DATA PIPELINE ARCHITECTURE                      ║
║                        WITH QUALITY GATE PROTECTION                        ║
╚════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────┐
│  EXTERNAL DATA SOURCE                                                    │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   🌐 OpenWeatherMap API                                                 │
│   ├─ Endpoint: /data/2.5/forecast                                       │
│   ├─ Data: 5-day forecast (3-hour intervals)                           │
│   ├─ Format: JSON                                                       │
│   └─ Records: ~40 forecast points                                       │
│                                                                          │
└────────────────────────┬─────────────────────────────────────────────────┘
                         │
                         │ HTTP GET Request
                         │ with API key
                         ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  TASK 1: DATA EXTRACTION                                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  Operator: PythonOperator                                                │
│  Module: src/data_extraction.py                                          │
│  Class: WeatherDataExtractor                                             │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  📥 ACTIONS:                                                             │
│    1. Connect to API with credentials                                   │
│    2. Fetch live forecast data                                          │
│    3. Parse JSON → Structured records                                   │
│    4. Add collection_timestamp to each record                           │
│    5. Create DataFrame (40 rows × 19 columns)                           │
│    6. Generate filename: weather_data_YYYYMMDD_HHMMSS.csv              │
│    7. Save to: data/raw/                                                │
│    8. Push filepath to XCom                                             │
│                                                                          │
│  📊 OUTPUT DATA STRUCTURE:                                               │
│    ┌─────────────────────┬──────────────────────┐                      │
│    │ Metadata (5)        │ Atmospheric (5)      │                      │
│    ├─────────────────────┼──────────────────────┤                      │
│    │ collection_timestamp│ pressure             │                      │
│    │ forecast_timestamp  │ humidity             │                      │
│    │ city                │ clouds               │                      │
│    │ latitude            │ visibility           │                      │
│    │ longitude           │ weather_description  │                      │
│    └─────────────────────┴──────────────────────┘                      │
│    ┌─────────────────────┬──────────────────────┐                      │
│    │ Temperature (4)     │ Wind (2)             │                      │
│    ├─────────────────────┼──────────────────────┤                      │
│    │ temperature         │ wind_speed           │                      │
│    │ feels_like          │ wind_deg             │                      │
│    │ temp_min            │                      │                      │
│    │ temp_max            │                      │                      │
│    └─────────────────────┴──────────────────────┘                      │
│    ┌──────────────────────────────────────────┐                        │
│    │ Precipitation (3)                        │                        │
│    ├──────────────────────────────────────────┤                        │
│    │ pop (probability)                        │                        │
│    │ rain_3h                                  │                        │
│    │ snow_3h                                  │                        │
│    └──────────────────────────────────────────┘                        │
│                                                                          │
│  ✅ Status: SUCCESS                                                      │
│  📁 File: data/raw/weather_data_20251201_143052.csv                     │
│  📏 Size: ~40 rows × 19 columns (~3-5 KB)                               │
│                                                                          │
└────────────────────────┬─────────────────────────────────────────────────┘
                         │
                         │ XCom: raw_data_filepath
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  TASK 2: MANDATORY QUALITY GATE ⚠️                                       │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  Operator: PythonOperator                                                │
│  Module: src/data_quality.py                                             │
│  Class: DataQualityChecker                                               │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  🔍 QUALITY CHECKS (All Must Pass):                                      │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 1. NULL VALUE CHECK                                             │   │
│  │    Threshold: ≤1% per column                                    │   │
│  │    Method: (null_count / total_rows) × 100                      │   │
│  │    Fail Condition: ANY column > 1% nulls                        │   │
│  │    Example: 1 null in 40 rows = 2.5% → FAIL ❌                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 2. SCHEMA VALIDATION                                            │   │
│  │    Expected: 19 specific columns                                │   │
│  │    Checks: All columns present, no missing columns              │   │
│  │    Fail Condition: Missing any expected column                  │   │
│  │    Example: No 'humidity' column → FAIL ❌                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 3. DATA TYPE VALIDATION                                         │   │
│  │    Numeric Fields: temperature, pressure, humidity, etc.        │   │
│  │    Checks: Proper data types (not strings)                      │   │
│  │    Fail Condition: Numeric field contains non-numeric data      │   │
│  │    Example: temperature = "cold" → FAIL ❌                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 4. VALUE RANGE VALIDATION                                       │   │
│  │    Ranges:                                                      │   │
│  │      • temperature: -50 to 60°C                                 │   │
│  │      • humidity: 0 to 100%                                      │   │
│  │      • pressure: 900 to 1100 hPa                                │   │
│  │      • wind_speed: 0 to 150 m/s                                 │   │
│  │      • clouds: 0 to 100%                                        │   │
│  │    Fail Condition: ANY value outside realistic range            │   │
│  │    Example: temperature = 150°C → FAIL ❌                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 5. ROW COUNT VALIDATION                                         │   │
│  │    Minimum: 10 rows                                             │   │
│  │    Checks: Sufficient data volume                               │   │
│  │    Fail Condition: Less than 10 forecast records                │   │
│  │    Example: Only 5 rows → FAIL ❌                                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  📊 OUTPUTS:                                                             │
│    • Quality Report JSON with detailed results                          │
│    • Console logs with check-by-check status                            │
│    • Boolean return: ALL_CHECKS_PASSED                                  │
│                                                                          │
│  🎯 DECISION LOGIC:                                                      │
│    if all_checks_passed:                                                │
│        return True  # Continue to next task                             │
│    else:                                                                │
│        raise AirflowException("Quality checks FAILED!")                 │
│        # ⛔ PIPELINE STOPS HERE - No downstream tasks execute            │
│                                                                          │
└────────────────────────┬─────────────────────────────────────────────────┘
                         │
                    ✓ PASS │ ✗ FAIL
                         │      │
                         │      └──────────────────────────────────┐
                         │                                         │
                         ▼                                         ▼
        ┌────────────────────────────┐         ┌─────────────────────────────┐
        │  CONTINUE PIPELINE         │         │  STOP PIPELINE ⛔           │
        │  ────────────────────       │         │  ─────────────────          │
        │  ✅ Quality validated      │         │  ❌ Quality failed          │
        │  ✅ Data trustworthy       │         │  ❌ Data unreliable         │
        │  ✅ Safe to proceed        │         │  ❌ Cannot proceed          │
        └────────────┬───────────────┘         │  📧 Alert: Fix data issues  │
                     │                         │  🔄 Retry: After fixes      │
                     ▼                         └─────────────────────────────┘
        ┌────────────────────────────┐
        │  Task 3: Data Profiling    │
        │  • Pandas profile report   │
        │  • Statistics & charts     │
        │  • Log to MLflow          │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  Task 4: Transformation    │
        │  • Feature engineering     │
        │  • Calculated fields       │
        │  • Save to processed/      │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  Task 5: Load & Version    │
        │  • Upload to MinIO         │
        │  • Track with DVC          │
        │  • Version control         │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  Task 6: Completion Log    │
        │  • Log success             │
        │  • Record timestamps       │
        │  • Update metrics          │
        └────────────────────────────┘

╔════════════════════════════════════════════════════════════════════════════╗
║                            QUALITY GATE IMPACT                             ║
╚════════════════════════════════════════════════════════════════════════════╝

📈 BENEFITS:
  ✓ Prevents bad data from polluting downstream systems
  ✓ Early detection of API issues or data anomalies
  ✓ Automated quality enforcement (no manual checks)
  ✓ Detailed quality reports for debugging
  ✓ Pipeline fails fast (saves compute resources)
  ✓ Audit trail of data quality over time

⚡ EXECUTION TIME:
  • Extraction: ~10 seconds (API call + save)
  • Quality Check: ~5 seconds (5 validation checks)
  • Total Gate Time: ~15 seconds
  • Downstream Tasks: Only if quality passes

🔒 PROTECTION LEVEL:
  • CRITICAL: Pipeline cannot bypass quality gate
  • BLOCKING: No manual override without code change
  • COMPREHENSIVE: 5 different validation dimensions
  • STRICT: 1% null threshold (industry best practice)

╔════════════════════════════════════════════════════════════════════════════╗
║                              FILE OUTPUTS                                  ║
╚════════════════════════════════════════════════════════════════════════════╝

data/raw/
├── weather_data_20251201_143052.csv
│   ├─ Size: ~3-5 KB
│   ├─ Rows: 40 forecast records
│   ├─ Columns: 19 weather variables
│   └─ Timestamp: 2025-12-01 14:30:52
│
└── weather_data_20251201_143052_quality_report.json
    ├─ Size: ~2-3 KB
    ├─ Format: JSON
    ├─ Content: Detailed check results
    └─ Fields: overall_passed, checks[], timestamp

╔════════════════════════════════════════════════════════════════════════════╗
║                         CONFIGURATION REQUIRED                             ║
╚════════════════════════════════════════════════════════════════════════════╝

.env file:
┌────────────────────────────────────────────────────────────────────────┐
│ OPENWEATHER_API_KEY=9fbf8dc3b6d9aac41d2956259bb499d8                   │
│ OPENWEATHER_CITY=London                                                │
│ OPENWEATHER_LAT=51.5074                                                │
│ OPENWEATHER_LON=-0.1278                                                │
└────────────────────────────────────────────────────────────────────────┘

Get free API key: https://openweathermap.org/api

╔════════════════════════════════════════════════════════════════════════════╗
║                      ✅ IMPLEMENTATION COMPLETE                            ║
╚════════════════════════════════════════════════════════════════════════════╝

All requirements met:
✓ Python operator for API extraction
✓ Live data from OpenWeatherMap
✓ Immediate save with timestamp
✓ Mandatory quality gate after extraction
✓ >1% null value threshold
✓ Schema validation
✓ DAG stops on quality failure
✓ Detailed quality reports
✓ Production-ready implementation

"""
    
    print(diagram)

if __name__ == "__main__":
    print_pipeline_diagram()
