#!/usr/bin/env python3
"""
Test script for real-world filename patterns
Tests the updated FileScanner with actual file naming patterns
"""

import sys
import os
import tempfile
from pathlib import Path
from datetime import datetime

# Add the parent directory to Python path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logging
from modules.file_scanner import FileScanner
from modules.wudan_rules import WudanRulesEngine

def create_real_world_test_files(test_dir: Path):
    """Create test files with real-world naming patterns"""
    test_files = []
    
    # Real-world file patterns from user examples
    test_file_specs = [
        # Date-named MP4 files (should extract date/time from filename)
        ('20250406_110016_1.mp4', b"Test video content 1", datetime(2025, 4, 6, 11, 0, 16)),
        ('20250504_113836_1.mp4', b"Test video content 2", datetime(2025, 5, 4, 11, 38, 36)),
        ('20250622_100122.mp4', b"Test video content 3", datetime(2025, 6, 22, 10, 1, 22)),
        
        # Non-date-named files (should use file modification time)
        ('M4H01890.MP4', b"Camera video content 1", None),  # Will use file mod time
        ('M4H01892.MP4', b"Camera video content 2", None),  # Will use file mod time
        
        # Date-named JPG files (for completeness)
        ('20250406_110016_1.jpg', b"Test picture content 1", datetime(2025, 4, 6, 11, 0, 16)),
        ('20250622_100122.jpg', b"Test picture content 2", datetime(2025, 6, 22, 10, 1, 22)),
        
        # Legacy patterns (should still work)
        ('IMG_20230615_143022.jpg', b"Legacy picture", datetime(2023, 6, 15, 14, 30, 22)),
        ('VID_20230615_120000.mp4', b"Legacy video", datetime(2023, 6, 15, 12, 0, 0)),
    ]
    
    for filename, content, expected_date in test_file_specs:
        file_path = test_dir / filename
        
        # Create file with content
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Set file modification time to a known value for non-date-named files
        if expected_date is None:
            # Use a specific modification time for testing
            mod_time = datetime(2025, 3, 15, 14, 30, 0)
            timestamp = mod_time.timestamp()
            os.utime(file_path, (timestamp, timestamp))
            expected_date = mod_time
        else:
            # Set modification time to match expected date for consistency
            timestamp = expected_date.timestamp()
            os.utime(file_path, (timestamp, timestamp))
        
        test_files.append({
            'path': file_path,
            'filename': filename,
            'expected_date': expected_date,
            'should_extract_from_filename': expected_date is not None and filename not in ['M4H01890.MP4', 'M4H01892.MP4']
        })
    
    return test_files

def test_real_world_filename_extraction(config, logger):
    """Test filename date extraction with real-world patterns"""
    print("\n=== Testing Real-World Filename Patterns ===")
    
    # Create temporary test directory
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # Create test files
        test_files = create_real_world_test_files(test_dir)
        print(f"✅ Created {len(test_files)} test files with real-world naming patterns")
        
        # Initialize FileScanner
        scanner = FileScanner(config, logger)
        
        # Test individual filename date extraction
        print("\n--- Individual Filename Date Extraction ---")
        extraction_results = []
        
        for test_file in test_files:
            filename = test_file['filename']
            expected_date = test_file['expected_date']
            should_extract = test_file['should_extract_from_filename']
            
            # Test the private method directly
            extracted_date = scanner._extract_date_from_filename(filename)
            
            result = {
                'filename': filename,
                'expected_date': expected_date,
                'extracted_date': extracted_date,
                'should_extract': should_extract,
                'extraction_success': extracted_date is not None if should_extract else True
            }
            
            if should_extract:
                if extracted_date and extracted_date == expected_date:
                    print(f"✅ {filename}: Correctly extracted {extracted_date}")
                    result['correct'] = True
                elif extracted_date:
                    print(f"⚠️  {filename}: Extracted {extracted_date}, expected {expected_date}")
                    result['correct'] = False
                else:
                    print(f"❌ {filename}: Failed to extract date, expected {expected_date}")
                    result['correct'] = False
            else:
                if extracted_date is None:
                    print(f"✅ {filename}: Correctly identified as non-date-named file")
                    result['correct'] = True
                else:
                    print(f"⚠️  {filename}: Unexpectedly extracted date {extracted_date}")
                    result['correct'] = False
            
            extraction_results.append(result)
        
        # Test full file scanning
        print("\n--- Full File Scanning Test ---")
        scanned_files = scanner.scan_folder(str(test_dir))
        print(f"✅ Scanned {len(scanned_files)} files")
        
        # Verify scanned results
        scan_results = []
        for scanned_file in scanned_files:
            filename = scanned_file['name']
            scanned_date = scanned_file['date']
            
            # Find corresponding test file
            test_file = next((tf for tf in test_files if tf['filename'] == filename), None)
            
            if test_file:
                expected_date = test_file['expected_date']
                should_extract = test_file['should_extract_from_filename']
                
                if should_extract:
                    # Should match extracted date exactly
                    correct = scanned_date == expected_date
                else:
                    # Should use file modification time (within reasonable tolerance)
                    time_diff = abs((scanned_date - expected_date).total_seconds())
                    correct = time_diff < 2  # Allow 2 second tolerance for file system timing
                
                scan_results.append({
                    'filename': filename,
                    'correct': correct,
                    'scanned_date': scanned_date,
                    'expected_date': expected_date
                })
                
                status = "✅" if correct else "❌"
                print(f"{status} {filename}: Scanned date {scanned_date}")
        
        # Test Wudan rule matching with real dates
        print("\n--- Wudan Rules Test with Real Dates ---")
        wudan_engine = WudanRulesEngine(config, logger)
        
        wudan_test_results = []
        for scanned_file in scanned_files:
            if scanned_file['type'] == 'video':
                filename = scanned_file['name']
                file_date = scanned_file['date']
                
                should_match_wudan = wudan_engine.should_go_to_wudan_folder(file_date)
                
                wudan_test_results.append({
                    'filename': filename,
                    'date': file_date,
                    'matches_wudan': should_match_wudan
                })
                
                status = "🥋" if should_match_wudan else "📹"
                print(f"{status} {filename} ({file_date}): {'Wudan' if should_match_wudan else 'Regular'}")
        
        # Summary
        extraction_correct = sum(1 for r in extraction_results if r['correct'])
        scan_correct = sum(1 for r in scan_results if r['correct'])
        wudan_matches = sum(1 for r in wudan_test_results if r['matches_wudan'])
        
        print(f"\n--- Results Summary ---")
        print(f"✅ Filename extraction: {extraction_correct}/{len(extraction_results)} correct")
        print(f"✅ File scanning: {scan_correct}/{len(scan_results)} correct")
        print(f"🥋 Wudan matches: {wudan_matches}/{len(wudan_test_results)} videos")
        
        return extraction_correct == len(extraction_results) and scan_correct == len(scan_results)

def main():
    """Main test function"""
    print("=== Real-World Filename Pattern Test Suite ===")
    
    # Change to the correct directory
    os.chdir(Path(__file__).parent.parent)
    
    try:
        # Load configuration
        config_manager = ConfigManager("config.yaml")
        config = config_manager.load_config()
        logger = setup_logging(config)
        
        print("✅ Configuration and logging initialized")
        
        # Run test
        success = test_real_world_filename_extraction(config, logger)
        
        # Summary
        print("\n=== Test Results Summary ===")
        print(f"✅ Real-World Filename Patterns: {'PASS' if success else 'FAIL'}")
        
        if success:
            print("\n🎉 All real-world filename pattern tests passed!")
            print("📁 File scanner is ready for production use with actual file naming patterns")
            logger.info("Real-world filename pattern test suite completed successfully")
        else:
            print("\n⚠️  Some real-world filename pattern tests failed. Check the output above for details.")
        
        return success
        
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
