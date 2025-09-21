#!/usr/bin/env python3
"""
Test script for flexible filename deduplication
Tests the updated DeduplicationManager with appended text handling
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add the parent directory to Python path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logging
from modules.deduplication import DeduplicationManager

def create_flexible_deduplication_test_environment():
    """Create test environment with source and target files for flexible matching"""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create target directories
    pictures_dir = temp_dir / "Pictures"
    videos_dir = temp_dir / "Videos"
    wudan_dir = temp_dir / "Videos" / "Wudan"
    
    for dir_path in [pictures_dir, videos_dir, wudan_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create existing files in target directories with appended text
    existing_files = [
        # Pictures with appended text
        (pictures_dir / "2025_04_12" / "20250412_110016_1_KungFu_GimStyle.jpg", b"Picture with appended text", 1000),
        (pictures_dir / "2025_04_12" / "20250412_110020_2_Training_Session.jpg", b"Another picture", 1500),
        
        # Videos with appended text
        (videos_dir / "2025_04_12" / "20250412_292993_1_KungFu_GimStyle.mp4", b"Video with appended text", 5000),
        (videos_dir / "2025_04_12" / "20250412_292995_2_Sparring_Match.mp4", b"Another video", 7500),
        
        # Wudan videos with appended text
        (wudan_dir / "2025_04_12_Training" / "20250412_080000_1_MorningPractice.mp4", b"Wudan morning practice", 3000),
        
        # Files without appended text (exact matches)
        (videos_dir / "2025_04_13" / "20250413_150000_1.mp4", b"Exact match video", 2000),
        
        # Non-date-named files
        (videos_dir / "2025_04_14" / "M4H01890_CameraFootage.MP4", b"Camera footage with text", 4000),
    ]
    
    for file_path, content, size in existing_files:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file with specific size
        with open(file_path, 'wb') as f:
            f.write(content)
            # Pad to exact size if needed
            current_size = len(content)
            if current_size < size:
                f.write(b'0' * (size - current_size))
    
    return temp_dir, {
        'pictures': str(pictures_dir),
        'videos': str(videos_dir),
        'wudan_videos': str(wudan_dir),
        'notes': str(temp_dir / "Notes")
    }

def test_flexible_filename_matching(config, logger):
    """Test flexible filename matching with appended text"""
    print("\n=== Testing Flexible Filename Matching ===")
    
    # Create test environment
    temp_dir, target_paths = create_flexible_deduplication_test_environment()
    
    try:
        # Update config with test paths
        test_config = config.copy()
        test_config['target_paths'] = target_paths
        
        # Initialize DeduplicationManager
        dedup_manager = DeduplicationManager(test_config, logger)
        
        # Build cache of existing files
        cached_files = dedup_manager.build_cache()
        print(f"✅ Built cache with {cached_files} existing files")
        
        # Test cases for flexible matching
        test_cases = [
            # Should match existing files with appended text
            {
                'source_filename': '20250412_110016_1.jpg',
                'file_size': 1000,
                'target_dir': target_paths['pictures'] + '/2025_04_12',
                'should_exist': True,
                'description': 'Picture matches existing file with appended text'
            },
            {
                'source_filename': '20250412_292993_1.mp4',
                'file_size': 5000,
                'target_dir': target_paths['videos'] + '/2025_04_12',
                'should_exist': True,
                'description': 'Video matches existing file with appended text'
            },
            {
                'source_filename': '20250412_080000_1.mp4',
                'file_size': 3000,
                'target_dir': target_paths['wudan_videos'] + '/2025_04_12_Training',
                'should_exist': True,
                'description': 'Wudan video matches existing file with appended text'
            },
            
            # Should match exact filename
            {
                'source_filename': '20250413_150000_1.mp4',
                'file_size': 2000,
                'target_dir': target_paths['videos'] + '/2025_04_13',
                'should_exist': True,
                'description': 'Exact filename match'
            },
            
            # Should NOT match (different size)
            {
                'source_filename': '20250412_110016_1.jpg',
                'file_size': 999,  # Different size
                'target_dir': target_paths['pictures'] + '/2025_04_12',
                'should_exist': False,
                'description': 'Same filename but different size - should not match'
            },
            
            # Should NOT match (no existing file)
            {
                'source_filename': '20250412_999999_1.mp4',
                'file_size': 1000,
                'target_dir': target_paths['videos'] + '/2025_04_12',
                'should_exist': False,
                'description': 'Non-existing file - should not match'
            },
            
            # Non-date-named file matching
            {
                'source_filename': 'M4H01890.MP4',
                'file_size': 4000,
                'target_dir': target_paths['videos'] + '/2025_04_14',
                'should_exist': True,
                'description': 'Non-date-named file matches existing file with appended text'
            },
        ]
        
        # Run test cases
        results = []
        for i, test_case in enumerate(test_cases):
            print(f"\n--- Test Case {i+1}: {test_case['description']} ---")
            
            file_date = datetime(2025, 4, 12, 12, 0, 0)  # Dummy date for testing
            
            exists = dedup_manager.file_exists_in_target(
                test_case['source_filename'],
                test_case['file_size'],
                file_date,
                test_case['target_dir']
            )
            
            expected = test_case['should_exist']
            success = exists == expected
            
            status = "✅" if success else "❌"
            print(f"{status} {test_case['source_filename']} (size: {test_case['file_size']})")
            print(f"    Expected: {'EXISTS' if expected else 'NOT EXISTS'}")
            print(f"    Actual: {'EXISTS' if exists else 'NOT EXISTS'}")
            
            results.append({
                'test_case': test_case,
                'expected': expected,
                'actual': exists,
                'success': success
            })
        
        # Test base filename pattern extraction
        print(f"\n--- Testing Base Filename Pattern Extraction ---")
        pattern_tests = [
            ('20250412_110016_1.mp4', '20250412_110016_1'),
            ('20250412_292993_2.jpg', '20250412_292993_2'),
            ('M4H01890.MP4', 'M4H01890'),
            ('random_file.mp4', 'random_file'),
        ]
        
        pattern_results = []
        for filename, expected_pattern in pattern_tests:
            actual_pattern = dedup_manager._extract_base_filename_pattern(filename)
            success = actual_pattern == expected_pattern
            
            status = "✅" if success else "❌"
            print(f"{status} {filename} -> '{actual_pattern}' (expected: '{expected_pattern}')")
            
            pattern_results.append(success)
        
        # Test flexible filename matching
        print(f"\n--- Testing Flexible Filename Matching Logic ---")
        matching_tests = [
            ('20250412_110016_1.mp4', '20250412_110016_1_KungFu_GimStyle.mp4', '20250412_110016_1', True),
            ('20250412_110016_1.mp4', '20250412_110016_1.mp4', '20250412_110016_1', True),
            ('20250412_110016_1.mp4', '20250412_110016_2.mp4', '20250412_110016_1', False),
            ('M4H01890.MP4', 'M4H01890_CameraFootage.MP4', 'M4H01890', True),
            ('M4H01890.MP4', 'M4H01891.MP4', 'M4H01890', False),
        ]
        
        matching_results = []
        for source, target, base_pattern, expected in matching_tests:
            actual = dedup_manager._filenames_match_flexible(source, target, base_pattern)
            success = actual == expected
            
            status = "✅" if success else "❌"
            print(f"{status} '{source}' vs '{target}' -> {actual} (expected: {expected})")
            
            matching_results.append(success)
        
        # Summary
        main_tests_passed = sum(1 for r in results if r['success'])
        pattern_tests_passed = sum(pattern_results)
        matching_tests_passed = sum(matching_results)
        
        print(f"\n--- Results Summary ---")
        print(f"✅ Main deduplication tests: {main_tests_passed}/{len(results)} passed")
        print(f"✅ Pattern extraction tests: {pattern_tests_passed}/{len(pattern_results)} passed")
        print(f"✅ Flexible matching tests: {matching_tests_passed}/{len(matching_results)} passed")
        
        total_passed = main_tests_passed + pattern_tests_passed + matching_tests_passed
        total_tests = len(results) + len(pattern_results) + len(matching_results)
        
        success = total_passed == total_tests
        
        if success:
            print(f"\n🎉 All flexible deduplication tests passed!")
            print(f"📁 System correctly handles files with appended text")
        else:
            print(f"\n⚠️  Some tests failed. Check output above for details.")
        
        return success
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    """Main test function"""
    print("=== Flexible Deduplication Test Suite ===")
    
    # Change to the correct directory
    os.chdir(Path(__file__).parent.parent)
    
    try:
        # Load configuration
        config_manager = ConfigManager("config.yaml")
        config = config_manager.load_config()
        logger = setup_logging(config)
        
        print("✅ Configuration and logging initialized")
        
        # Run test
        success = test_flexible_filename_matching(config, logger)
        
        # Summary
        print("\n=== Test Results Summary ===")
        print(f"✅ Flexible Deduplication: {'PASS' if success else 'FAIL'}")
        
        if success:
            print("\n🎉 All flexible deduplication tests passed!")
            print("📁 Deduplication system ready for production with appended text handling")
            logger.info("Flexible deduplication test suite completed successfully")
        else:
            print("\n⚠️  Some flexible deduplication tests failed. Check the output above for details.")
        
        return success
        
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
