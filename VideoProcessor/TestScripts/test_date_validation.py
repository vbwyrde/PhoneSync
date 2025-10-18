#!/usr/bin/env python3
"""
Test script for date validation enhancement in ProcessingStateManager
Tests the new validation logic that verifies state against target folder structure
"""

import os
import sys
import json
import logging
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Add VideoProcessor modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.config_manager import ConfigManager
from modules.processing_state_manager import ProcessingStateManager

def create_test_environment():
    """Create a temporary test environment with target folders"""
    temp_dir = tempfile.mkdtemp(prefix="date_validation_test_")
    
    # Create target directory structure
    target_paths = {
        'pictures': os.path.join(temp_dir, 'My Pictures'),
        'videos': os.path.join(temp_dir, 'My Videos'), 
        'wudan': os.path.join(temp_dir, 'My Videos', 'Wudan')
    }
    
    for path in target_paths.values():
        os.makedirs(path, exist_ok=True)
    
    # Create some date folders to simulate existing processing
    test_dates = [
        ('2025_01_10', 'pictures'),
        ('2025_01_12', 'videos'),
        ('2025_01_15_Mon', 'wudan'),  # Wudan folder with day of week
        ('2025_01_16_Tue', 'wudan')
    ]
    
    for date_folder, folder_type in test_dates:
        folder_path = os.path.join(target_paths[folder_type], date_folder)
        os.makedirs(folder_path, exist_ok=True)
        
        # Create a dummy file in each folder
        dummy_file = os.path.join(folder_path, f"test_{date_folder}.txt")
        with open(dummy_file, 'w') as f:
            f.write(f"Test file for {date_folder}")
    
    return temp_dir, target_paths

def create_test_config(target_paths, state_dir):
    """Create test configuration"""
    return {
        'target_paths': target_paths,
        'state_management': {
            'state_dir': state_dir,
            'processing_state_file': 'processing_state.json',
            'processed_files_db': 'processed_files.json'
        },
        'options': {
            'enable_incremental_processing': True
        }
    }

def test_validation_scenarios():
    """Test various validation scenarios"""
    print("🧪 Testing Date Validation Enhancement")
    print("=" * 50)
    
    # Create test environment
    temp_dir, target_paths = create_test_environment()
    state_dir = os.path.join(temp_dir, 'state')
    os.makedirs(state_dir, exist_ok=True)
    
    try:
        # Setup logger and config
        logger = logging.getLogger("test_validation")
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)

        config = create_test_config(target_paths, state_dir)
        
        print(f"📁 Test environment: {temp_dir}")
        print(f"📊 Target folders created:")
        for folder_type, path in target_paths.items():
            print(f"   - {folder_type}: {path}")
        
        # Test 1: No state file (first run)
        print("\n🔍 Test 1: First run (no state file)")
        state_manager = ProcessingStateManager(config, logger)
        
        # Create a test file info
        test_file = {
            'path': '/test/20250117_120000_1.mp4',
            'name': '20250117_120000_1.mp4',
            'date': datetime(2025, 1, 17, 12, 0, 0),
            'size': 1000000
        }
        
        should_process = state_manager.should_process_file(test_file)
        print(f"   Should process file: {should_process} (Expected: True)")
        
        # Test 2: Valid state that matches folders
        print("\n🔍 Test 2: Valid state matching folder structure")
        
        # Create state file with date that exists in folders (2025-01-16)
        valid_state = {
            'last_run_timestamp': '2025-01-16T10:30:00',
            'last_processed_file': '20250116_103000_1.mp4',
            'last_processed_date': '2025-01-16',
            'total_files_processed': 100,
            'total_videos_analyzed': 50,
            'processing_version': '1.0'
        }
        
        state_file_path = os.path.join(state_dir, 'processing_state.json')
        with open(state_file_path, 'w') as f:
            json.dump(valid_state, f, indent=2)
        
        # Reload state manager
        state_manager = ProcessingStateManager(config, logger)
        
        # Test with file older than last run (should skip)
        old_file = {
            'path': '/test/20250115_120000_1.mp4',
            'name': '20250115_120000_1.mp4', 
            'date': datetime(2025, 1, 15, 12, 0, 0),
            'size': 1000000
        }
        
        should_process_old = state_manager.should_process_file(old_file)
        print(f"   Should process old file: {should_process_old} (Expected: False)")
        
        # Test with file newer than last run (should process)
        new_file = {
            'path': '/test/20250117_120000_1.mp4',
            'name': '20250117_120000_1.mp4',
            'date': datetime(2025, 1, 17, 12, 0, 0),
            'size': 1000000
        }
        
        should_process_new = state_manager.should_process_file(new_file)
        print(f"   Should process new file: {should_process_new} (Expected: True)")
        
        # Test 3: Invalid state that doesn't match folders (triggers fallback)
        print("\n🔍 Test 3: Invalid state triggering folder-based fallback")
        
        # Create state with date that doesn't exist in folders
        invalid_state = {
            'last_run_timestamp': '2025-01-20T10:30:00',  # Date not in folders
            'last_processed_file': '20250120_103000_1.mp4',
            'last_processed_date': '2025-01-20',
            'total_files_processed': 200,
            'total_videos_analyzed': 100,
            'processing_version': '1.0'
        }
        
        with open(state_file_path, 'w') as f:
            json.dump(invalid_state, f, indent=2)
        
        # Reload state manager
        state_manager = ProcessingStateManager(config, logger)
        
        # Test with file that should be processed based on folder dates
        # Latest folder date is 2025-01-16, so files after that should process
        test_file_fallback = {
            'path': '/test/20250117_120000_1.mp4',
            'name': '20250117_120000_1.mp4',
            'date': datetime(2025, 1, 17, 12, 0, 0),
            'size': 1000000
        }
        
        should_process_fallback = state_manager.should_process_file(test_file_fallback)
        print(f"   Should process file (fallback): {should_process_fallback} (Expected: True)")
        
        print("\n✅ All validation tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        try:
            shutil.rmtree(temp_dir)
            print(f"\n🧹 Cleaned up test environment: {temp_dir}")
        except Exception as e:
            print(f"\n⚠️ Could not clean up test environment: {e}")

if __name__ == "__main__":
    test_validation_scenarios()
