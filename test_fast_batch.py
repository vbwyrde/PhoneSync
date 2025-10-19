#!/usr/bin/env python3
"""
Test the fast batch processing approach
"""

import os
import sys
import yaml
import logging
import time
from pathlib import Path

# Add the VideoProcessor modules to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'VideoProcessor'))

from modules.fast_batch_processor import FastBatchProcessor
from modules.config_manager import ConfigManager

def setup_logging():
    """Setup logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    return logging.getLogger(__name__)

def test_fast_batch_processing():
    """Test the fast batch processing approach"""
    
    print("=== Fast Batch Processing Test ===")
    
    # Setup logging
    logger = setup_logging()
    
    # Load configuration using ConfigManager
    config_path = "config.yaml"
    config_manager = ConfigManager(config_path)
    config = config_manager.load_config()

    print(f"Loaded config: {config_path}")
    print(f"Environment: {config.get('environment', 'Unknown')}")

    # Debug: Print available config keys
    print(f"Config keys: {list(config.keys())}")

    # Initialize fast batch processor
    processor = FastBatchProcessor(config, logger)

    # Get source folders and target paths
    source_folders = config.get('source_folders', [])
    target_paths = config.get('target_paths', {})

    print(f"Source folders: {len(source_folders)}")
    print(f"Target paths: {list(target_paths.keys())}")
    print(f"Source root: {config.get('source_root', 'NOT FOUND')}")

    # Debug: Show actual paths
    print(f"\nFirst few source folders:")
    for i, folder in enumerate(source_folders[:3]):
        print(f"  {i+1}. {folder}")

    print(f"\nTarget paths:")
    for key, path in target_paths.items():
        print(f"  {key}: {path}")
    
    # Time the entire process
    total_start = time.time()
    
    try:
        # Step 1: Build source inventory (flat file list)
        print("\n--- Step 1: Building Source Inventory ---")
        source_files = processor.build_source_inventory(source_folders)
        
        # Step 2: Build target inventory (flat file list)
        print("\n--- Step 2: Building Target Inventory ---")
        target_files = processor.build_target_inventory(target_paths)
        
        # Step 3: Find files needing processing (set difference)
        print("\n--- Step 3: Computing Files Needing Processing ---")
        files_to_process = processor.find_files_needing_processing(source_files, target_files)
        
        # Step 4: Get statistics
        print("\n--- Step 4: Processing Statistics ---")
        stats = processor.get_processing_statistics(source_files, target_files, files_to_process)
        
        print(f"📊 Total source files: {stats['total_source_files']:,}")
        print(f"📊 Total target files: {stats['total_target_files']:,}")
        print(f"📊 Files needing processing: {stats['files_needing_processing']:,}")
        print(f"📊 Files already processed: {stats['files_already_processed']:,}")
        print(f"📊 Completion percentage: {stats['completion_percentage']:.1f}%")
        
        # Step 5: Convert to file info (only for files that need processing)
        if len(files_to_process) > 0:
            print(f"\n--- Step 5: Converting {len(files_to_process)} Files to File Info ---")
            file_info_list = processor.convert_keys_to_file_info(files_to_process, source_folders)
            print(f"✅ Converted {len(file_info_list)} files to file info format")
            
            # Show sample of files that need processing
            print(f"\n📋 Sample files needing processing:")
            for i, file_info in enumerate(file_info_list[:10]):
                print(f"  {i+1}. {file_info['name']} ({file_info['size']:,} bytes) - {file_info['type']}")
            
            if len(file_info_list) > 10:
                print(f"  ... and {len(file_info_list) - 10} more files")
        
        total_elapsed = time.time() - total_start
        print(f"\n🎉 Fast batch processing complete in {total_elapsed:.2f} seconds")
        
        # Compare with estimated old method time
        if len(source_files) > 0:
            estimated_old_time = len(source_files) * 0.5  # Assume 0.5 seconds per file for old method
            speedup = estimated_old_time / total_elapsed if total_elapsed > 0 else 0

            print(f"⚡ Estimated speedup: {speedup:.1f}x faster than individual file processing")
            print(f"⚡ Old method would take ~{estimated_old_time/60:.1f} minutes")
            print(f"⚡ New method took {total_elapsed:.1f} seconds")
        else:
            print(f"⚠️  No source files found - check configuration")
        
        return len(files_to_process)
        
    except Exception as e:
        print(f"❌ Error during fast batch processing: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    files_needing_processing = test_fast_batch_processing()
    
    if files_needing_processing is not None:
        print(f"\n✅ Fast batch processing successful!")
        print(f"📝 Result: {files_needing_processing} files need processing")
        
        if files_needing_processing > 0:
            print(f"\n💡 Next step: Process these {files_needing_processing} files with the main system")
        else:
            print(f"\n🎉 All files are already processed!")
    else:
        print(f"\n❌ Fast batch processing failed")
