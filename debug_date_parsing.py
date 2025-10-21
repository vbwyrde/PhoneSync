#!/usr/bin/env python3
"""
Debug date parsing for AI Notes Generator
"""

import sys
import re
from datetime import datetime
from pathlib import Path

# Add modules directory to path
sys.path.insert(0, str(Path(__file__) / "VideoProcessor"))

def _is_wudan_date_folder(folder_name: str) -> bool:
    """Check if folder name matches Wudan date pattern (YYYY_MM_DD_DDD or YYYY_MM_DD_DDD_Additional)"""
    # Match YYYY_MM_DD_DDD pattern with optional additional text for Wudan folders
    pattern = r'^\d{4}_\d{2}_\d{2}_\w{3}(_.*)?$'
    return bool(re.match(pattern, folder_name))

def _extract_date_from_folder_name(folder_name: str):
    """Extract date from folder name"""
    try:
        # Extract YYYY_MM_DD part
        date_part = folder_name.split('_')[:3]
        if len(date_part) == 3:
            year, month, day = date_part
            return datetime(int(year), int(month), int(day))
    except (ValueError, IndexError):
        pass
    return None

def test_date_parsing():
    """Test date parsing logic"""
    
    test_folders = [
        "2025_10_19_Sun",
        "2014_04_12_Sat", 
        "2024_10_15_Wed",
        "2025_10_19_Sun_SomethingElse"
    ]
    
    test_date = "2025-10-19"
    
    print("=== Date Parsing Debug ===")
    print(f"Looking for date: {test_date}")
    print()
    
    for folder in test_folders:
        print(f"Testing folder: {folder}")
        
        # Test pattern matching
        is_wudan = _is_wudan_date_folder(folder)
        print(f"  Is Wudan folder: {is_wudan}")
        
        if is_wudan:
            # Test date extraction
            extracted_date = _extract_date_from_folder_name(folder)
            print(f"  Extracted date: {extracted_date}")
            
            if extracted_date:
                formatted_date = extracted_date.strftime('%Y-%m-%d')
                print(f"  Formatted date: {formatted_date}")
                matches = formatted_date == test_date
                print(f"  Matches target: {matches}")
            else:
                print(f"  Failed to extract date")
        
        print()

if __name__ == "__main__":
    test_date_parsing()
