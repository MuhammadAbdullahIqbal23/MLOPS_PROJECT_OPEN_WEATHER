"""
Data Quality Checks Module
Implements mandatory quality gates for the MLOps pipeline
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
from datetime import datetime


class DataQualityChecker:
    """Performs data quality validation checks"""
    
    def __init__(self, null_threshold: float = 0.01):
        """
        Initialize quality checker
        
        Args:
            null_threshold: Maximum allowed percentage of null values (default: 1%)
        """
        self.null_threshold = null_threshold
        self.quality_report = {}
        
    def check_null_values(self, df: pd.DataFrame) -> Tuple[bool, Dict]:
        """
        Check if null values exceed threshold
        
        Args:
            df: DataFrame to check
            
        Returns:
            Tuple of (passed, report)
        """
        null_counts = df.isnull().sum()
        null_percentages = (null_counts / len(df)) * 100
        
        failed_columns = null_percentages[null_percentages > (self.null_threshold * 100)]
        
        report = {
            'check': 'null_values',
            'passed': len(failed_columns) == 0,
            'threshold_percent': self.null_threshold * 100,
            'null_counts': null_counts.to_dict(),
            'null_percentages': null_percentages.to_dict(),
            'failed_columns': failed_columns.to_dict() if len(failed_columns) > 0 else {}
        }
        
        return report['passed'], report
    
    def check_schema(self, df: pd.DataFrame, expected_columns: List[str]) -> Tuple[bool, Dict]:
        """
        Validate DataFrame schema
        
        Args:
            df: DataFrame to check
            expected_columns: List of expected column names
            
        Returns:
            Tuple of (passed, report)
        """
        actual_columns = set(df.columns)
        expected_columns_set = set(expected_columns)
        
        missing_columns = expected_columns_set - actual_columns
        extra_columns = actual_columns - expected_columns_set
        
        report = {
            'check': 'schema_validation',
            'passed': len(missing_columns) == 0,
            'expected_columns': expected_columns,
            'actual_columns': list(actual_columns),
            'missing_columns': list(missing_columns),
            'extra_columns': list(extra_columns)
        }
        
        return report['passed'], report
    
    def check_data_types(self, df: pd.DataFrame) -> Tuple[bool, Dict]:
        """
        Check data types are appropriate
        
        Args:
            df: DataFrame to check
            
        Returns:
            Tuple of (passed, report)
        """
        type_issues = []
        
        # Check numeric columns
        numeric_columns = ['temperature', 'feels_like', 'pressure', 'humidity', 
                          'wind_speed', 'clouds', 'visibility']
        
        for col in numeric_columns:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    type_issues.append(f"{col} is not numeric")
        
        report = {
            'check': 'data_types',
            'passed': len(type_issues) == 0,
            'data_types': df.dtypes.astype(str).to_dict(),
            'issues': type_issues
        }
        
        return report['passed'], report
    
    def check_value_ranges(self, df: pd.DataFrame) -> Tuple[bool, Dict]:
        """
        Check if values are within expected ranges
        
        Args:
            df: DataFrame to check
            
        Returns:
            Tuple of (passed, report)
        """
        range_issues = []
        
        # Define expected ranges
        ranges = {
            'temperature': (-50, 60),
            'humidity': (0, 100),
            'pressure': (900, 1100),
            'wind_speed': (0, 150),
            'clouds': (0, 100)
        }
        
        for col, (min_val, max_val) in ranges.items():
            if col in df.columns:
                out_of_range = df[(df[col] < min_val) | (df[col] > max_val)]
                if len(out_of_range) > 0:
                    range_issues.append({
                        'column': col,
                        'expected_range': [min_val, max_val],
                        'out_of_range_count': len(out_of_range),
                        'actual_range': [df[col].min(), df[col].max()]
                    })
        
        report = {
            'check': 'value_ranges',
            'passed': len(range_issues) == 0,
            'issues': range_issues
        }
        
        return report['passed'], report
    
    def check_row_count(self, df: pd.DataFrame, min_rows: int = 10) -> Tuple[bool, Dict]:
        """
        Check if DataFrame has minimum number of rows
        
        Args:
            df: DataFrame to check
            min_rows: Minimum required rows
            
        Returns:
            Tuple of (passed, report)
        """
        row_count = len(df)
        passed = row_count >= min_rows
        
        report = {
            'check': 'row_count',
            'passed': passed,
            'row_count': row_count,
            'min_required': min_rows
        }
        
        return passed, report
    
    def run_all_checks(self, df: pd.DataFrame, expected_columns: List[str]) -> Tuple[bool, Dict]:
        """
        Run all quality checks
        
        Args:
            df: DataFrame to check
            expected_columns: List of expected column names
            
        Returns:
            Tuple of (all_passed, full_report)
        """
        checks = []
        
        # Run all checks
        passed, report = self.check_null_values(df)
        checks.append(report)
        
        passed, report = self.check_schema(df, expected_columns)
        checks.append(report)
        
        passed, report = self.check_data_types(df)
        checks.append(report)
        
        passed, report = self.check_value_ranges(df)
        checks.append(report)
        
        passed, report = self.check_row_count(df)
        checks.append(report)
        
        # Aggregate results
        all_passed = all(check['passed'] for check in checks)
        
        full_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_passed': all_passed,
            'total_checks': len(checks),
            'passed_checks': sum(1 for c in checks if c['passed']),
            'failed_checks': sum(1 for c in checks if not c['passed']),
            'checks': checks
        }
        
        return all_passed, full_report
    
    def print_report(self, report: Dict):
        """Print quality report"""
        print("\n" + "="*50)
        print("DATA QUALITY REPORT")
        print("="*50)
        print(f"Timestamp: {report['timestamp']}")
        print(f"Overall Status: {'✓ PASSED' if report['overall_passed'] else '✗ FAILED'}")
        print(f"Passed: {report['passed_checks']}/{report['total_checks']}")
        print("-"*50)
        
        for check in report['checks']:
            status = "✓" if check['passed'] else "✗"
            print(f"{status} {check['check'].upper()}")
            if not check['passed']:
                print(f"  Issues: {check.get('issues', check.get('failed_columns', 'See details'))}")
        
        print("="*50 + "\n")


def validate_data_quality(filepath: str, expected_columns: List[str]) -> bool:
    """
    Validate data quality from file
    
    Args:
        filepath: Path to CSV file
        expected_columns: List of expected column names
        
    Returns:
        True if all checks pass, False otherwise
    """
    # Load data
    df = pd.read_csv(filepath)
    
    # Run checks
    checker = DataQualityChecker(null_threshold=0.01)
    all_passed, report = checker.run_all_checks(df, expected_columns)
    
    # Print report
    checker.print_report(report)
    
    # Save report
    import json
    report_path = filepath.replace('.csv', '_quality_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Quality report saved to: {report_path}")
    
    return all_passed


if __name__ == "__main__":
    # Example usage
    expected_cols = [
        'collection_timestamp', 'forecast_timestamp', 'city', 'latitude', 'longitude',
        'temperature', 'feels_like', 'temp_min', 'temp_max', 'pressure', 'humidity',
        'weather_main', 'weather_description', 'clouds', 'wind_speed', 'wind_deg',
        'visibility', 'pop', 'rain_3h', 'snow_3h'
    ]
    
    import sys
    if len(sys.argv) > 1:
        validate_data_quality(sys.argv[1], expected_cols)
