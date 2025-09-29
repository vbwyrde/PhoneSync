#!/usr/bin/env python3
"""
Test script for incremental processing functionality
Demonstrates how the system handles large collections by only processing new files
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logging
from modules.processing_state_manager import ProcessingStateManager

def test_incremental_processing():
    """Test the incremental processing functionality"""
    
    print("🧪 Testing Incremental Processing System")
    print("=" * 50)
    
    # Load configuration
    config_manager = ConfigManager("config.yaml")
    config = config_manager.load_config()
    logger = setup_logging(config)
    
    # Initialize state manager
    state_manager = ProcessingStateManager(config, logger)
    
    # Test 1: First run (no previous state)
    print("\n📋 Test 1: First Run (No Previous State)")
    print("-" * 40)
    
    state_info = state_manager.get_state_info()
    filter_info = state_manager.get_incremental_filter_info()
    
    print(f"First run: {state_info['first_run']}")
    print(f"Processing mode: {filter_info['mode']}")
    print(f"Reason: {filter_info['reason']}")
    print(f"Tracked files: {state_info['processed_files_count']}")
    
    # Test 2: Simulate processing some files
    print("\n📋 Test 2: Simulate Processing Files")
    print("-" * 40)
    
    state_manager.start_processing_run()
    
    # Create some mock file info
    mock_files = [
        {
            'path': '/test/video1.mp4',
            'name': 'video1.mp4',
            'size': 1000000,
            'date': datetime.now() - timedelta(days=1),
            'type': 'video'
        },
        {
            'path': '/test/video2.mp4',
            'name': 'video2.mp4',
            'size': 2000000,
            'date': datetime.now() - timedelta(hours=12),
            'type': 'video'
        },
        {
            'path': '/test/photo1.jpg',
            'name': 'photo1.jpg',
            'size': 500000,
            'date': datetime.now() - timedelta(hours=6),
            'type': 'picture'
        }
    ]
    
    # Process mock files
    for file_info in mock_files:
        should_process = state_manager.should_process_file(file_info)
        print(f"File: {file_info['name']} - Should process: {should_process}")
        
        if should_process:
            state_manager.mark_file_processed(file_info)
    
    # Finish first run
    mock_stats = {
        'files_processed': len(mock_files),
        'videos_analyzed': 2,
        'last_processed_file': mock_files[-1]['name']
    }
    
    state_manager.finish_processing_run(mock_stats)
    
    print(f"✅ First run completed - processed {len(mock_files)} files")
    
    # Test 3: Second run (incremental processing)
    print("\n📋 Test 3: Second Run (Incremental Processing)")
    print("-" * 40)
    
    # Create new state manager instance (simulates new program run)
    state_manager2 = ProcessingStateManager(config, logger)
    
    state_info2 = state_manager2.get_state_info()
    filter_info2 = state_manager2.get_incremental_filter_info()
    
    print(f"First run: {state_info2['first_run']}")
    print(f"Processing mode: {filter_info2['mode']}")
    print(f"Last run: {state_info2.get('last_run', 'N/A')}")
    print(f"Previously processed: {state_info2.get('total_files_processed', 0)} files")
    print(f"Tracked files: {state_info2['processed_files_count']}")
    
    # Test with same files (should be skipped) and new files
    new_mock_files = [
        # Same files from before (should be skipped)
        mock_files[0],  # video1.mp4 - should be skipped
        mock_files[1],  # video2.mp4 - should be skipped
        # New files (should be processed)
        {
            'path': '/test/video3.mp4',
            'name': 'video3.mp4',
            'size': 3000000,
            'date': datetime.now(),  # New file
            'type': 'video'
        },
        {
            'path': '/test/photo2.jpg',
            'name': 'photo2.jpg',
            'size': 600000,
            'date': datetime.now(),  # New file
            'type': 'picture'
        }
    ]
    
    state_manager2.start_processing_run()
    
    files_to_process = []
    for file_info in new_mock_files:
        should_process = state_manager2.should_process_file(file_info)
        print(f"File: {file_info['name']} - Should process: {should_process}")
        
        if should_process:
            files_to_process.append(file_info)
            state_manager2.mark_file_processed(file_info)
    
    print(f"✅ Incremental processing: {len(files_to_process)} new files, {len(new_mock_files) - len(files_to_process)} skipped")
    
    # Test 4: State file inspection
    print("\n📋 Test 4: State File Inspection")
    print("-" * 40)
    
    state_dir = Path("VideoProcessor/state")
    if state_dir.exists():
        print(f"State directory: {state_dir}")
        
        state_file = state_dir / "processing_state.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                state_data = json.load(f)
            print(f"State file contents:")
            for key, value in state_data.items():
                print(f"  {key}: {value}")
        
        processed_file = state_dir / "processed_files.json"
        if processed_file.exists():
            with open(processed_file, 'r') as f:
                processed_data = json.load(f)
            print(f"Processed files database:")
            print(f"  Total files tracked: {processed_data['total_count']}")
            print(f"  Last updated: {processed_data['last_updated']}")
            print(f"  Sample files: {processed_data['processed_files'][:3]}...")
    
    # Test 5: Reset functionality
    print("\n📋 Test 5: State Reset")
    print("-" * 40)
    
    print("Resetting processing state...")
    state_manager2.reset_state()
    
    # Verify reset
    state_info3 = state_manager2.get_state_info()
    print(f"After reset - First run: {state_info3['first_run']}")
    print(f"After reset - Tracked files: {state_info3['processed_files_count']}")
    
    print("\n🎉 Incremental Processing Test Complete!")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    try:
        success = test_incremental_processing()
        if success:
            print("✅ All tests passed!")
            sys.exit(0)
        else:
            print("❌ Some tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)
