#!/usr/bin/env python3
"""
Test the integrated fast processing in UnifiedProcessor
"""

import os
import sys
import time
from pathlib import Path

# Add the VideoProcessor modules to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'VideoProcessor'))

from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logging
from modules.unified_processor import UnifiedProcessor

def test_integrated_fast_processing():
    """Test the integrated fast processing approach"""
    
    print("=== Testing Integrated Fast Processing ===")
    
    # Load configuration first
    config_path = "config.yaml"
    config_manager = ConfigManager(config_path)
    config = config_manager.load_config()

    # Setup logging using config
    logger = setup_logging(config)
    
    print(f"Loaded config: {config_path}")
    print(f"Environment: {config.get('environment', 'Unknown')}")
    print(f"Source folders: {len(config.get('source_folders', []))}")
    print(f"Target paths: {list(config.get('target_paths', {}).keys())}")
    
    # Initialize unified processor with fast batch processing
    processor = UnifiedProcessor(config, logger)
    
    # Test the fast batch processing (dry run mode for safety)
    print(f"\n=== Running Fast Batch Processing Test (Dry Run) ===")
    
    # Enable dry run mode for testing
    config['options']['dry_run'] = True
    
    start_time = time.time()
    
    try:
        # Run the processing with fast batch approach
        results = processor.process_all_sources()
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        print(f"\n🎉 Fast batch processing test completed in {elapsed:.2f} seconds")
        print(f"📊 Results: {len(results)} files processed")
        
        # Show statistics
        stats = processor.get_processing_statistics()
        print(f"\n📈 Processing Statistics:")
        print(f"  Files scanned: {stats.get('files_scanned', 0):,}")
        print(f"  Files processed: {stats.get('files_processed', 0):,}")
        print(f"  Files copied: {stats.get('files_copied', 0):,}")
        print(f"  Files skipped: {stats.get('files_skipped', 0):,}")
        print(f"  Videos analyzed: {stats.get('videos_analyzed', 0):,}")
        print(f"  Kung Fu detected: {stats.get('kung_fu_detected', 0):,}")
        print(f"  Notes generated: {stats.get('notes_generated', 0):,}")
        print(f"  Errors: {stats.get('errors', 0):,}")
        
        if elapsed > 0:
            files_per_second = stats.get('files_scanned', 0) / elapsed
            print(f"  Processing speed: {files_per_second:.1f} files/second")
        
        return True
        
    except Exception as e:
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"❌ Error after {elapsed:.2f} seconds: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    success = test_integrated_fast_processing()
    
    if success:
        print(f"\n✅ Integrated fast processing test successful!")
        print(f"\n💡 The system is ready for production use with fast batch processing")
        print(f"🚀 To run the full processing, use: python VideoProcessor/Scripts/main.py")
    else:
        print(f"\n❌ Integrated fast processing test failed")
        print(f"🔧 Please check the error messages above and fix any issues")

if __name__ == "__main__":
    main()
