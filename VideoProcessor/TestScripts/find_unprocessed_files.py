#!/usr/bin/env python3
"""
Find unprocessed MP4 files for AI testing

This script scans all source folders to find MP4 files that haven't been processed yet,
so we can test the AI analysis functionality with real video files.
"""

import os
import sys
import yaml
import logging
from pathlib import Path

# Add the VideoProcessor directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.file_scanner import FileScanner
from modules.deduplication import DeduplicationManager
from modules.processing_state_manager import ProcessingStateManager
from modules.config_manager import ConfigManager

def load_config():
    """Load configuration from config.yaml"""
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml')

    # Use ConfigManager to properly resolve environment
    config_manager = ConfigManager(config_path)

    # Load raw config and temporarily switch to PRODUCTION
    with open(config_path, 'r', encoding='utf-8') as f:
        raw_config = yaml.safe_load(f)

    # Force PRODUCTION environment for real data
    raw_config['environment'] = 'PRODUCTION'

    # Save temporarily modified config
    temp_config_path = config_path + '.temp'
    with open(temp_config_path, 'w', encoding='utf-8') as f:
        yaml.dump(raw_config, f, default_flow_style=False)

    # Load resolved config
    temp_config_manager = ConfigManager(temp_config_path)
    config = temp_config_manager.get_config()

    # Clean up temp file
    os.remove(temp_config_path)

    return config

def main():
    """Find unprocessed MP4 files for testing"""
    print("FINDING UNPROCESSED MP4 FILES FOR AI TESTING")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    
    # Initialize components
    file_scanner = FileScanner(config, logger)
    dedup_manager = DeduplicationManager(config, logger)
    state_manager = ProcessingStateManager(config, logger)
    
    # Build deduplication cache
    print("Building deduplication cache...")
    dedup_manager.build_cache()
    print(f"   Found {len(dedup_manager.existing_files_cache)} existing files in target directories")
    
    # Get list of processed files
    processed_files = state_manager.get_processed_files()
    print(f"   Found {len(processed_files)} previously processed files")
    
    # Scan all source folders for MP4 files
    source_folders = config.get('source_folders', [])
    unprocessed_mp4s = []
    
    print(f"\nScanning {len(source_folders)} source folders...")
    
    for i, folder_path in enumerate(source_folders, 1):
        print(f"\n{i}. Scanning: {folder_path}")
        
        if not os.path.exists(folder_path):
            print(f"   SKIP: Folder does not exist")
            continue
            
        try:
            files = file_scanner.scan_folder(folder_path)
            mp4_files = [f for f in files if f['name'].lower().endswith('.mp4')]
            
            print(f"   Found {len(mp4_files)} MP4 files")
            
            for file_info in mp4_files:
                file_path = file_info['path']
                filename = file_info['name']
                
                # Check if already processed
                if file_path in processed_files:
                    continue
                    
                # Check if duplicate exists in target
                if dedup_manager.is_duplicate(file_info):
                    continue
                    
                # This is an unprocessed file!
                unprocessed_mp4s.append({
                    'path': file_path,
                    'name': filename,
                    'size': file_info['size'],
                    'folder': folder_path
                })
                
                # Limit to first 10 for testing
                if len(unprocessed_mp4s) >= 10:
                    break
                    
        except Exception as e:
            print(f"   ERROR: {e}")
            continue
            
        if len(unprocessed_mp4s) >= 10:
            break
    
    # Report results
    print(f"\n" + "=" * 60)
    print(f"FOUND {len(unprocessed_mp4s)} UNPROCESSED MP4 FILES")
    print("=" * 60)
    
    if unprocessed_mp4s:
        print("\nUnprocessed files suitable for AI testing:")
        for i, file_info in enumerate(unprocessed_mp4s, 1):
            size_mb = file_info['size'] / (1024 * 1024)
            print(f"   {i:2d}. {file_info['name']} ({size_mb:.1f} MB)")
            print(f"       Path: {file_info['path']}")
            print(f"       Folder: {file_info['folder']}")
            print()
            
        print(f"These {len(unprocessed_mp4s)} files can be used for AI analysis testing!")
        
    else:
        print("\nNo unprocessed MP4 files found.")
        print("All MP4 files have either been processed or already exist in target directories.")
        print("\nTo test AI analysis, you could:")
        print("1. Add new MP4 files to a source folder")
        print("2. Temporarily remove some files from target folders")
        print("3. Clear the processing state to reprocess existing files")

if __name__ == "__main__":
    main()
