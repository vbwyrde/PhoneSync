#!/usr/bin/env python3
"""
Test Processing Script - Process the first 4 MP4 files from Camera folder
Uses the full VideoProcessor system with all enhanced features
"""

import os
import sys
import yaml
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logging
from modules.file_scanner import FileScanner
from modules.wudan_rules import WudanRulesEngine
from modules.deduplication import DeduplicationManager
from modules.target_path_resolver import TargetPathResolver
from modules.file_organizer import FileOrganizer
from modules.video_analyzer import VideoAnalyzer
from modules.notes_generator import NotesGenerator
from modules.processing_state_manager import ProcessingStateManager

def get_first_mp4_files(folder_path, limit=4):
    """Get the first N MP4 files from a folder"""
    mp4_files = []
    
    try:
        if not os.path.exists(folder_path):
            print(f"ERROR: Folder does not exist: {folder_path}")
            return []

        print(f"Scanning for MP4 files in: {folder_path}")

        # Walk through folder and find MP4 files
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.mp4'):
                    file_path = os.path.join(root, file)
                    mp4_files.append(file_path)

                    if len(mp4_files) >= limit:
                        break

            if len(mp4_files) >= limit:
                break

        print(f"   Found {len(mp4_files)} MP4 files (limit: {limit})")
        return mp4_files[:limit]

    except Exception as e:
        print(f"ERROR: Error scanning folder: {e}")
        return []

def main():
    """Main execution function"""
    print("TEST PROCESSING - First 4 MP4 Files from Camera Folder (PRODUCTION DATA)")
    print("=" * 70)

    try:
        # Initialize configuration (config.yaml is in root PhoneSync directory)
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml')
        config_manager = ConfigManager(config_path)

        # Load config and temporarily switch to PRODUCTION environment for testing
        print("Switching to PRODUCTION environment for realistic testing...")

        # First load the raw config
        with open(config_path, 'r', encoding='utf-8') as f:
            import yaml
            raw_config = yaml.safe_load(f)

        # Temporarily modify environment to PRODUCTION
        raw_config['environment'] = 'PRODUCTION'

        # Save temporarily modified config
        temp_config_path = os.path.join(os.path.dirname(__file__), '..', 'temp_test_config.yaml')
        with open(temp_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(raw_config, f, default_flow_style=False)

        # Load with modified config
        config_manager = ConfigManager(temp_config_path)
        config = config_manager.load_config()

        # DEBUG: Print all key config variables
        print("DEBUG: Configuration Variables")
        print("-" * 40)
        print(f"Environment: {config.get('environment', 'NOT SET')}")
        print(f"Source folders count: {len(config.get('source_folders', []))}")
        print("Source folders:")
        for i, folder in enumerate(config.get('source_folders', [])[:5], 1):  # Show first 5
            exists = os.path.exists(folder) if folder else False
            print(f"  {i}. {folder} (exists: {exists})")

        print(f"Target paths: {config.get('target_paths', {})}")

        # Check PROD_VARS and DEV_VARS
        prod_vars = config.get('PROD_VARS', {})
        dev_vars = config.get('DEV_VARS', {})
        print(f"PROD_VARS source_root: {prod_vars.get('source_root', 'NOT SET')}")
        print(f"PROD_VARS source_subdirs count: {len(prod_vars.get('source_subdirs', []))}")
        print(f"DEV_VARS source_root: {dev_vars.get('source_root', 'NOT SET')}")
        print(f"DEV_VARS source_subdirs count: {len(dev_vars.get('source_subdirs', []))}")

        # Check wudan rules
        wudan_rules = config.get('wudan_rules', {})
        print(f"Wudan rules configured: {bool(wudan_rules)}")

        # Check AI settings
        ai_settings = config.get('ai_settings', {})
        print(f"AI settings configured: {bool(ai_settings)}")
        print(f"LM Studio URL: {ai_settings.get('lm_studio_url', 'NOT SET')}")
        print("-" * 40)

        # Setup logging
        logger = setup_logging(config)
        logger.info("Starting test processing of 4 MP4 files")
        
        # Initialize all components
        print("Initializing components...")
        file_scanner = FileScanner(config, logger)
        wudan_engine = WudanRulesEngine(config, logger)
        dedup_manager = DeduplicationManager(config, logger)
        target_resolver = TargetPathResolver(config, logger, wudan_engine, dedup_manager)
        file_organizer = FileOrganizer(config, logger, target_resolver, dedup_manager)
        video_analyzer = VideoAnalyzer(config, logger)
        notes_generator = NotesGenerator(config, logger)
        state_manager = ProcessingStateManager(config, logger)

        # Test AI connection before processing
        print("Testing AI connection...")
        ai_test_result = video_analyzer.test_ai_connection()
        if ai_test_result.get('success', False):
            print(f"   AI CONNECTION: SUCCESS - {ai_test_result.get('response', 'Connected')}")
        else:
            print(f"   AI CONNECTION: FAILED - {ai_test_result.get('error', 'Unknown error')}")
            print(f"   WARNING: AI analysis will be skipped for videos")

        # Build deduplication cache
        print("Building deduplication cache...")
        dedup_manager.build_cache()
        print(f"   Cache built with {len(dedup_manager.existing_files_cache)} existing files")
        
        # Get source folder path
        source_folders = config.get('source_folders', [])
        camera_folder = None
        
        for folder in source_folders:
            if 'Camera' in folder:
                camera_folder = folder
                break
        
        if not camera_folder:
            print("ERROR: Camera folder not found in configuration")
            return 1

        print(f"Using source folder: {camera_folder}")

        # Get first 4 MP4 files
        mp4_files = get_first_mp4_files(camera_folder, limit=4)

        if not mp4_files:
            print("ERROR: No MP4 files found in Camera folder")
            return 1

        print(f"\nProcessing {len(mp4_files)} MP4 files:")
        for i, file_path in enumerate(mp4_files, 1):
            print(f"   {i}. {Path(file_path).name}")
        
        # Process each file
        stats = {
            'files_processed': 0,
            'files_skipped': 0,
            'videos_analyzed': 0,
            'errors': 0,
            'wudan_files': 0,
            'regular_files': 0
        }

        # Initialize movement log
        movement_log = []

        # Get log directory from config
        log_config = config.get('logging', {})
        log_path = log_config.get('log_path', 'logs/phone_sync.log')
        log_dir = os.path.dirname(log_path)

        # Create test log file in same directory as main log
        log_file_path = os.path.join(log_dir, 'test_file_movements.log')

        # Ensure logs directory exists
        os.makedirs(log_dir, exist_ok=True)

        start_time = time.time()
        
        for i, file_path in enumerate(mp4_files, 1):
            filename = Path(file_path).name
            print(f"\nProcessing file {i}/{len(mp4_files)}: {filename}")
            print("-" * 50)

            try:
                # Get file information using the private method (since no public method exists)
                file_info = file_scanner._extract_file_info(Path(file_path))
                if not file_info:
                    print(f"   ERROR: Could not get file information")
                    stats['errors'] += 1
                    continue

                print(f"   Date: {file_info['date']}")
                print(f"   Size: {file_info['size']:,} bytes")

                # Get target folder path
                target_folder = target_resolver.get_target_folder_path(file_info)
                if not target_folder:
                    print(f"   ERROR: Could not determine target folder")
                    stats['errors'] += 1
                    continue

                # Check if file already exists (duplicate)
                if dedup_manager.file_exists_in_target(
                    file_info['name'],
                    file_info['size'],
                    file_info['date'],
                    target_folder
                ):
                    print(f"   SKIPPED - File already exists in target")
                    stats['files_skipped'] += 1
                    continue

                # Determine routing (check if target is Wudan folder)
                is_wudan = 'Wudan' in target_folder
                if is_wudan:
                    print(f"   Routing: WUDAN folder")
                    stats['wudan_files'] += 1
                else:
                    print(f"   Routing: Regular Videos folder")
                    stats['regular_files'] += 1

                print(f"   Target: {target_folder}")

                # Log the planned movement
                movement_entry = {
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'source_file': file_path,
                    'target_folder': target_folder,
                    'file_size': file_info['size'],
                    'file_date': str(file_info['date']),
                    'routing': 'WUDAN' if is_wudan else 'REGULAR',
                    'action': 'DRY_RUN'  # Will change to 'COPIED' in live run
                }
                movement_log.append(movement_entry)

                # For now, do DRY RUN - just simulate the file organization
                print(f"   DRY RUN: Would copy file to {target_folder}")
                print(f"   DRY RUN: File organization simulated successfully")
                stats['files_processed'] += 1

                # Perform ACTUAL AI analysis for testing (even in dry run)
                if file_info['name'].lower().endswith('.mp4'):
                    print(f"   TESTING: Performing AI video analysis on {file_path}")

                    try:
                        # Test AI analysis with the source file (before copying)
                        analysis_result = video_analyzer.analyze_video(file_path, dry_run=False)

                        if analysis_result.get('analyzed', False):
                            print(f"   AI ANALYSIS SUCCESS:")
                            print(f"      Kung Fu Detected: {analysis_result.get('is_kung_fu', 'Unknown')}")
                            print(f"      Description: {analysis_result.get('description', 'No description')}")
                            print(f"      Confidence: {analysis_result.get('confidence', 'Unknown')}")

                            # Test note file generation
                            note_file_path = video_analyzer.generate_note_file(
                                file_path,
                                analysis_result,
                                target_folder
                            )

                            if note_file_path:
                                print(f"   NOTES FILE: Would create {note_file_path}")
                                stats['videos_analyzed'] += 1
                            else:
                                print(f"   NOTES FILE: Generation failed")
                        else:
                            print(f"   AI ANALYSIS FAILED: {analysis_result.get('reason', 'Unknown error')}")
                            print(f"   Error Type: {analysis_result.get('error_type', 'Unknown')}")

                    except Exception as e:
                        print(f"   AI ANALYSIS ERROR: {e}")
                        logger.error(f"AI analysis error for {filename}: {e}")
                        stats['errors'] += 1

                # Skip state management for dry run
                print(f"   DRY RUN: Would update processing state")
                
            except Exception as e:
                print(f"   ERROR: Error processing file: {e}")
                logger.error(f"Error processing {filename}: {e}")
                stats['errors'] += 1
                continue

        # Write movement log to file
        print(f"\nWriting movement log to file...")
        with open(log_file_path, 'w', encoding='utf-8') as f:
            f.write("FILE MOVEMENT LOG - DRY RUN TEST\n")
            f.write("=" * 50 + "\n")
            f.write(f"Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Environment: PRODUCTION (read-only test)\n")
            f.write(f"Files Processed: {len(movement_log)}\n\n")

            for entry in movement_log:
                f.write(f"Timestamp: {entry['timestamp']}\n")
                f.write(f"Source: {entry['source_file']}\n")
                f.write(f"Target: {entry['target_folder']}\n")
                f.write(f"Size: {entry['file_size']:,} bytes\n")
                f.write(f"Date: {entry['file_date']}\n")
                f.write(f"Routing: {entry['routing']}\n")
                f.write(f"Action: {entry['action']}\n")
                f.write("-" * 40 + "\n")

        print(f"Movement log written to: {log_file_path}")

        # AI analysis was performed during processing
        print(f"AI ANALYSIS: Tested on {stats['videos_analyzed']} videos")

        # Display final results
        processing_time = time.time() - start_time

        print(f"\nPROCESSING COMPLETE!")
        print("=" * 50)
        print(f"Total time: {processing_time:.1f} seconds")
        print(f"Files processed: {stats['files_processed']}")
        print(f"Files skipped: {stats['files_skipped']}")
        print(f"Videos analyzed: {stats['videos_analyzed']}")
        print(f"Wudan files: {stats['wudan_files']}")
        print(f"Regular files: {stats['regular_files']}")
        print(f"Errors: {stats['errors']}")

        if stats['files_processed'] > 0:
            avg_time = processing_time / stats['files_processed']
            print(f"Average time per file: {avg_time:.1f} seconds")

        logger.info(f"Test processing completed: {stats}")

        # Cleanup temporary config file
        if os.path.exists(temp_config_path):
            os.remove(temp_config_path)
            print(f"Cleaned up temporary config file")

        return 0 if stats['errors'] == 0 else 1

    except Exception as e:
        print(f"FATAL ERROR: {e}")
        # Cleanup temporary config file on error
        temp_config_path = os.path.join(os.path.dirname(__file__), '..', 'temp_test_config.yaml')
        if os.path.exists(temp_config_path):
            os.remove(temp_config_path)
        return 1

if __name__ == "__main__":
    sys.exit(main())
