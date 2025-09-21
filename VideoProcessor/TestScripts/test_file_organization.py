#!/usr/bin/env python3
"""
Test script for file organization modules
Tests TargetPathResolver and FileOrganizer
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
from modules.file_scanner import FileScanner
from modules.wudan_rules import WudanRulesEngine
from modules.deduplication import DeduplicationManager
from modules.target_path_resolver import TargetPathResolver
from modules.file_organizer import FileOrganizer

def create_test_environment():
    """Create a complete test environment with source and target directories"""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create source directory with test files
    source_dir = temp_dir / "source"
    source_dir.mkdir()
    
    # Create target directories
    pictures_dir = temp_dir / "Pictures"
    videos_dir = temp_dir / "Videos"
    wudan_dir = temp_dir / "Videos" / "Wudan"
    notes_dir = temp_dir / "Notes"
    
    for dir_path in [pictures_dir, videos_dir, wudan_dir, notes_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create test files with specific dates and content
    test_files = [
        # Pictures
        ("IMG_20230615_143022.jpg", b"Test picture content 1", datetime(2023, 6, 15, 14, 30, 22)),
        ("20230616_photo.jpg", b"Test picture content 2", datetime(2023, 6, 16, 10, 0, 0)),
        
        # Regular videos (should NOT match Wudan rules)
        ("VID_20230615_120000.mp4", b"Regular video content 1", datetime(2023, 6, 15, 12, 0, 0)),
        ("20230616_150000.mp4", b"Regular video content 2", datetime(2023, 6, 16, 15, 0, 0)),
        
        # Wudan videos (should match Wudan rules)
        ("WUDAN_20210307_100000.mp4", b"Wudan video content 1", datetime(2021, 3, 7, 10, 0, 0)),  # Sunday 10am
        ("TRAINING_20200615_070000.mp4", b"Wudan video content 2", datetime(2020, 6, 15, 7, 0, 0)),  # Monday 7am
    ]
    
    created_files = []
    for filename, content, file_date in test_files:
        file_path = source_dir / filename
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Set file modification time to match the intended date
        timestamp = file_date.timestamp()
        os.utime(file_path, (timestamp, timestamp))
        
        created_files.append(file_path)
    
    return temp_dir, source_dir, {
        'pictures': str(pictures_dir),
        'videos': str(videos_dir),
        'wudan_videos': str(wudan_dir),
        'notes': str(notes_dir)
    }, created_files

def test_target_path_resolver(config, logger):
    """Test TargetPathResolver functionality"""
    print("\n=== Testing TargetPathResolver ===")
    
    # Create test environment
    temp_dir, source_dir, target_paths, test_files = create_test_environment()
    
    try:
        # Update config with test paths
        test_config = config.copy()
        test_config['target_paths'] = target_paths
        
        # Initialize components
        wudan_engine = WudanRulesEngine(test_config, logger)
        dedup_manager = DeduplicationManager(test_config, logger)
        target_resolver = TargetPathResolver(test_config, logger, wudan_engine, dedup_manager)
        file_scanner = FileScanner(test_config, logger)
        
        # Scan test files
        scanned_files = file_scanner.scan_folder(str(source_dir))
        print(f"✅ Scanned {len(scanned_files)} test files")
        
        # Test target path resolution for each file
        resolution_results = []
        for file_info in scanned_files:
            target_folder = target_resolver.get_target_folder_path(file_info)
            
            result = {
                'filename': file_info['name'],
                'type': file_info['type'],
                'date': file_info['date'],
                'target_folder': target_folder
            }
            
            # Determine expected target type
            if file_info['type'] == 'picture':
                expected_base = target_paths['pictures']
            elif file_info['type'] == 'video':
                if wudan_engine.should_go_to_wudan_folder(file_info['date']):
                    expected_base = target_paths['wudan_videos']
                else:
                    expected_base = target_paths['videos']
            
            result['expected_base'] = expected_base
            result['correct'] = target_folder and expected_base in target_folder
            
            resolution_results.append(result)
        
        # Check results
        correct_resolutions = sum(1 for r in resolution_results if r['correct'])
        print(f"✅ Target path resolution: {correct_resolutions}/{len(resolution_results)} correct")
        
        # Test specific scenarios - check files that should match Wudan rules
        wudan_expected_files = []
        for result in resolution_results:
            if wudan_engine.should_go_to_wudan_folder(result['date']):
                wudan_expected_files.append(result)

        wudan_correct = sum(1 for r in wudan_expected_files if target_paths['wudan_videos'] in r['target_folder'])
        print(f"✅ Wudan file routing: {wudan_correct}/{len(wudan_expected_files)} correct")
        
        # Test target structure analysis
        analysis = target_resolver.analyze_target_structure(scanned_files)
        print(f"✅ Target analysis: {analysis['total_files']} files, "
              f"{analysis['wudan_matches']} Wudan matches, "
              f"{analysis['folders_to_create']} folders needed")
        
        # Test target path validation
        validation = target_resolver.validate_target_paths()
        print(f"✅ Target path validation: {'PASS' if validation['all_valid'] else 'FAIL'}")
        
        return correct_resolutions == len(resolution_results)
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_file_organizer(config, logger):
    """Test FileOrganizer functionality"""
    print("\n=== Testing FileOrganizer ===")
    
    # Create test environment
    temp_dir, source_dir, target_paths, test_files = create_test_environment()
    
    try:
        # Update config with test paths
        test_config = config.copy()
        test_config['target_paths'] = target_paths
        
        # Initialize components
        wudan_engine = WudanRulesEngine(test_config, logger)
        dedup_manager = DeduplicationManager(test_config, logger)
        target_resolver = TargetPathResolver(test_config, logger, wudan_engine, dedup_manager)
        file_organizer = FileOrganizer(test_config, logger, target_resolver, dedup_manager)
        file_scanner = FileScanner(test_config, logger)
        
        # Build deduplication cache
        dedup_manager.build_cache()
        
        # Scan test files
        scanned_files = file_scanner.scan_folder(str(source_dir))
        print(f"✅ Prepared {len(scanned_files)} files for organization")
        
        # Test organization preview
        preview = file_organizer.get_organization_preview(scanned_files)
        print(f"✅ Organization preview: {preview['total_files']} files, "
              f"{len(preview['potential_issues'])} potential issues")
        
        # Test dry run organization
        dry_run_results = file_organizer.organize_files_batch(scanned_files, dry_run=True)
        print(f"✅ Dry run: {dry_run_results['total_files']} files processed, "
              f"{dry_run_results['success_rate']:.1f}% success rate")
        
        # Test actual organization
        actual_results = file_organizer.organize_files_batch(scanned_files, dry_run=False)
        print(f"✅ Actual organization: {len(actual_results['successful_files'])} successful, "
              f"{len(actual_results['failed_files'])} failed")
        
        # Verify files were actually copied
        copied_files_exist = 0
        for success_info in actual_results['successful_files']:
            if os.path.exists(success_info['target']):
                copied_files_exist += 1
        
        print(f"✅ File verification: {copied_files_exist}/{len(actual_results['successful_files'])} files exist at target")
        
        # Test statistics
        stats = file_organizer.get_statistics()
        print(f"✅ Statistics: {stats['files_copied']} copied, "
              f"{stats['files_skipped']} skipped, "
              f"{stats['bytes_copied_mb']:.2f} MB processed")
        
        # Test duplicate detection (run organization again)
        duplicate_results = file_organizer.organize_files_batch(scanned_files, dry_run=False)
        duplicates_detected = duplicate_results['statistics']['duplicates_found']
        print(f"✅ Duplicate detection: {duplicates_detected} duplicates found on second run")
        
        success = (
            len(actual_results['failed_files']) == 0 and
            copied_files_exist == len(actual_results['successful_files']) and
            duplicates_detected > 0  # Should detect duplicates on second run
        )
        
        return success
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    """Main test function"""
    print("=== File Organization Test Suite ===")
    
    # Change to the correct directory
    os.chdir(Path(__file__).parent.parent)
    
    try:
        # Load configuration
        config_manager = ConfigManager("config.yaml")
        config = config_manager.load_config()
        logger = setup_logging(config)
        
        print("✅ Configuration and logging initialized")
        
        # Run tests
        resolver_success = test_target_path_resolver(config, logger)
        organizer_success = test_file_organizer(config, logger)
        
        # Summary
        print("\n=== Test Results Summary ===")
        print(f"✅ TargetPathResolver: {'PASS' if resolver_success else 'FAIL'}")
        print(f"✅ FileOrganizer: {'PASS' if organizer_success else 'FAIL'}")
        
        all_passed = resolver_success and organizer_success
        
        if all_passed:
            print("\n🎉 All file organization tests passed!")
            logger.info("File organization test suite completed successfully")
        else:
            print("\n⚠️  Some file organization tests failed. Check the output above for details.")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
