#!/usr/bin/env python3
"""
Test script for core file organization modules
Tests FileScanner, WudanRulesEngine, and DeduplicationManager
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, time

# Add the parent directory to Python path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logging
from modules.file_scanner import FileScanner
from modules.wudan_rules import WudanRulesEngine
from modules.deduplication import DeduplicationManager

def create_test_files(test_dir: Path):
    """Create test files with various names and dates"""
    test_files = []
    
    # Create test files with different naming patterns
    test_file_specs = [
        ('20230615_143022.jpg', 'picture'),
        ('2023-06-15_video.mp4', 'video'),
        ('IMG_20230615_143022.jpg', 'picture'),
        ('VID_20230615_143022.mp4', 'video'),
        ('random_name.jpg', 'picture'),  # No date in filename
        ('another_video.mp4', 'video'),  # No date in filename
        ('20210307_080000.mp4', 'video'),  # Should match Wudan rules (Sunday 8am)
        ('20200615_070000.mp4', 'video'),  # Should match Wudan rules (Monday 7am, before 2021)
        ('20230615_120000.mp4', 'video'),  # Should NOT match Wudan rules
    ]
    
    for filename, file_type in test_file_specs:
        file_path = test_dir / filename
        
        # Create file with some content
        content = b"Test content for " + filename.encode()
        if file_type == 'video':
            content = b"FAKE_VIDEO_CONTENT_" + filename.encode() + b"_" * 100
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        test_files.append(file_path)
    
    return test_files

def test_file_scanner(config, logger):
    """Test FileScanner functionality"""
    print("\n=== Testing FileScanner ===")
    
    # Create temporary test directory
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # Create test files
        test_files = create_test_files(test_dir)
        print(f"✅ Created {len(test_files)} test files")
        
        # Initialize FileScanner
        scanner = FileScanner(config, logger)
        
        # Test scanning
        scanned_files = scanner.scan_folder(str(test_dir))
        print(f"✅ Scanned files: {len(scanned_files)} found")
        
        # Test file info extraction
        if scanned_files:
            sample_file = scanned_files[0]
            required_keys = ['path', 'name', 'extension', 'type', 'size', 'date']
            missing_keys = [key for key in required_keys if key not in sample_file]
            
            if not missing_keys:
                print("✅ File info extraction: All required keys present")
            else:
                print(f"❌ File info extraction: Missing keys: {missing_keys}")
                return False
        
        # Test statistics
        stats = scanner.get_file_stats(scanned_files)
        print(f"✅ Statistics: {stats['total_files']} files, "
              f"{stats['pictures']} pictures, {stats['videos']} videos")
        
        # Test date extraction
        files_with_dates = [f for f in scanned_files if f['date']]
        files_without_dates = [f for f in scanned_files if not f['date']]
        print(f"✅ Date extraction: {len(files_with_dates)} with dates, "
              f"{len(files_without_dates)} using modification time")
        
        # Test grouping by date
        grouped = scanner.group_files_by_date(scanned_files)
        print(f"✅ Date grouping: {len(grouped)} date groups")
        
        return True

def test_wudan_rules(config, logger):
    """Test WudanRulesEngine functionality"""
    print("\n=== Testing WudanRulesEngine ===")
    
    # Initialize Wudan engine
    wudan_engine = WudanRulesEngine(config, logger)
    
    # Test configuration validation
    validation_errors = wudan_engine.validate_rules_configuration()
    if validation_errors:
        print(f"❌ Configuration validation failed: {validation_errors}")
        return False
    else:
        print("✅ Configuration validation: PASS")
    
    # Test specific date/time scenarios
    test_scenarios = [
        # Before 2021 tests
        (datetime(2020, 6, 15, 7, 0), True, "Monday 7am 2020 - should match before_2021"),
        (datetime(2020, 6, 15, 12, 0), False, "Monday 12pm 2020 - should NOT match"),
        (datetime(2020, 6, 13, 19, 0), True, "Saturday 7pm 2020 - should match before_2021"),
        (datetime(2020, 6, 14, 19, 0), False, "Sunday 7pm 2020 - should NOT match (not in days)"),
        
        # After 2021 tests
        (datetime(2021, 3, 7, 10, 0), True, "Sunday 10am 2021 - should match after_2021"),
        (datetime(2021, 3, 8, 7, 0), True, "Monday 7am 2021 - should match after_2021"),
        (datetime(2021, 3, 8, 12, 0), False, "Monday 12pm 2021 - should NOT match"),
        (datetime(2021, 3, 10, 20, 0), True, "Wednesday 8pm 2021 - should match after_2021"),
        (datetime(2021, 3, 12, 14, 0), False, "Friday 2pm 2021 - should NOT match (not in days)"),
    ]
    
    passed_tests = 0
    for test_date, expected_result, description in test_scenarios:
        actual_result = wudan_engine.should_go_to_wudan_folder(test_date)
        
        if actual_result == expected_result:
            print(f"✅ {description}")
            passed_tests += 1
        else:
            print(f"❌ {description} - Expected: {expected_result}, Got: {actual_result}")
            
            # Get detailed analysis for debugging
            summary = wudan_engine.get_wudan_rule_summary(test_date)
            print(f"   Debug info: {summary}")
    
    print(f"✅ Wudan rules tests: {passed_tests}/{len(test_scenarios)} passed")
    
    return passed_tests == len(test_scenarios)

def test_deduplication(config, logger):
    """Test DeduplicationManager functionality"""
    print("\n=== Testing DeduplicationManager ===")
    
    # Create temporary directories for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create mock target directories
        pictures_dir = temp_path / "Pictures"
        videos_dir = temp_path / "Videos"
        wudan_dir = temp_path / "Videos" / "Wudan"
        
        for dir_path in [pictures_dir, videos_dir, wudan_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create some existing files in target directories
        existing_files = [
            (pictures_dir / "2023_06_15" / "IMG_001.jpg", b"existing picture content"),
            (videos_dir / "2023_06_15" / "VID_001.mp4", b"existing video content"),
            (wudan_dir / "2023_06_15_Training" / "WUDAN_001.mp4", b"existing wudan content"),
        ]
        
        for file_path, content in existing_files:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(content)
        
        # Update config with temporary paths
        test_config = config.copy()
        test_config['target_paths'] = {
            'pictures': str(pictures_dir),
            'videos': str(videos_dir),
            'wudan_videos': str(wudan_dir),
            'notes': str(temp_path / "Notes")
        }
        
        # Initialize DeduplicationManager
        dedup_manager = DeduplicationManager(test_config, logger)
        
        # Test cache building
        cached_files = dedup_manager.build_cache()
        print(f"✅ Cache building: {cached_files} files cached")
        
        if cached_files != len(existing_files):
            print(f"⚠️  Expected {len(existing_files)} files, got {cached_files}")
        
        # Test cache statistics
        stats = dedup_manager.get_cache_stats()
        print(f"✅ Cache stats: {stats['cache_entries']} entries, {stats['total_files']} total files")
        
        # Test file existence checking
        test_file_date = datetime(2023, 6, 15, 12, 0)
        
        # Test existing file detection
        exists = dedup_manager.file_exists_in_target(
            "IMG_001.jpg", len(b"existing picture content"), 
            test_file_date, str(pictures_dir / "2023_06_15")
        )
        
        if exists:
            print("✅ Existing file detection: PASS")
        else:
            print("❌ Existing file detection: FAIL - should have found existing file")
            return False
        
        # Test non-existing file detection
        not_exists = dedup_manager.file_exists_in_target(
            "NEW_FILE.jpg", 12345, 
            test_file_date, str(pictures_dir / "2023_06_15")
        )
        
        if not not_exists:
            print("✅ Non-existing file detection: PASS")
        else:
            print("❌ Non-existing file detection: FAIL - should not have found non-existing file")
            return False
        
        # Test existing date folder detection
        existing_folder = dedup_manager.find_existing_date_folder(str(wudan_dir), "2023_06_15")
        if existing_folder and "2023_06_15_Training" in existing_folder:
            print("✅ Existing date folder detection: PASS")
        else:
            print(f"❌ Existing date folder detection: FAIL - Expected folder with 2023_06_15_Training, got {existing_folder}")
            return False
        
        return True

def main():
    """Main test function"""
    print("=== Core Modules Test Suite ===")
    
    # Change to the correct directory
    os.chdir(Path(__file__).parent.parent)
    
    try:
        # Load configuration
        config_manager = ConfigManager("../config.yaml")
        config = config_manager.load_config()
        logger = setup_logging(config)
        
        print("✅ Configuration and logging initialized")
        
        # Run tests
        scanner_success = test_file_scanner(config, logger)
        wudan_success = test_wudan_rules(config, logger)
        dedup_success = test_deduplication(config, logger)
        
        # Summary
        print("\n=== Test Results Summary ===")
        print(f"✅ FileScanner: {'PASS' if scanner_success else 'FAIL'}")
        print(f"✅ WudanRulesEngine: {'PASS' if wudan_success else 'FAIL'}")
        print(f"✅ DeduplicationManager: {'PASS' if dedup_success else 'FAIL'}")
        
        all_passed = scanner_success and wudan_success and dedup_success
        
        if all_passed:
            print("\n🎉 All core module tests passed!")
            logger.info("Core modules test suite completed successfully")
        else:
            print("\n⚠️  Some core module tests failed. Check the output above for details.")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
