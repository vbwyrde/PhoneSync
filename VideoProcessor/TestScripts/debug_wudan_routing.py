#!/usr/bin/env python3
"""
Debug script for Wudan routing issues
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add the parent directory to Python path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logging
from modules.wudan_rules import WudanRulesEngine

def main():
    """Debug Wudan routing"""
    print("=== Wudan Routing Debug ===")
    
    # Change to the correct directory
    os.chdir(Path(__file__).parent.parent)
    
    try:
        # Load configuration
        config_manager = ConfigManager("config.yaml")
        config = config_manager.load_config()
        logger = setup_logging(config)
        
        # Initialize Wudan engine
        wudan_engine = WudanRulesEngine(config, logger)
        
        # Test the specific dates from our test files
        test_dates = [
            (datetime(2021, 3, 7, 10, 0, 0), "WUDAN_20210307_100000.mp4", "Sunday 10:00 AM 2021"),
            (datetime(2020, 6, 15, 7, 0, 0), "TRAINING_20200615_070000.mp4", "Monday 7:00 AM 2020"),
        ]
        
        for test_date, filename, description in test_dates:
            print(f"\n--- Testing {filename} ---")
            print(f"Date/Time: {description}")
            print(f"Weekday: {test_date.weekday()} (Monday=0)")
            print(f"ISO Weekday: {test_date.isoweekday()} (Monday=1)")
            print(f"Python weekday(): {test_date.weekday()}")
            
            # Get detailed analysis
            summary = wudan_engine.get_wudan_rule_summary(test_date)
            print(f"Rule Summary: {summary}")
            
            # Test the main function
            should_match = wudan_engine.should_go_to_wudan_folder(test_date)
            print(f"Should go to Wudan folder: {should_match}")
            
            # Expected result
            if "2021" in filename:
                print("Expected: TRUE (Sunday 10am should match after_2021 rules)")
            else:
                print("Expected: TRUE (Monday 7am should match before_2021 rules)")
        
        print("\n=== Configuration Check ===")
        print("Before 2021 days:", config['wudan_rules']['before_2021']['days_of_week'])
        print("After 2021 days:", config['wudan_rules']['after_2021']['days_of_week'])
        
        # Check Sunday rules specifically
        sunday_rules = config['wudan_rules']['after_2021']['time_ranges'].get(0, [])
        print(f"Sunday (0) rules: {sunday_rules}")
        
        # Check Monday rules
        monday_before = config['wudan_rules']['before_2021']
        print(f"Before 2021 Monday in days: {1 in monday_before['days_of_week']}")
        print(f"Before 2021 time ranges: {monday_before['time_ranges']}")
        
    except Exception as e:
        print(f"❌ Debug failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
