#!/usr/bin/env python3
"""
Test script for optimized batch processing with progress tracking
"""

import sys
import os
import time
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from VideoProcessor.modules.config_manager import ConfigManager
from VideoProcessor.modules.unified_processor import UnifiedProcessor
from VideoProcessor.modules.logger_setup import setup_logging


def main():
    """Test the optimized batch processing system"""
    
    print("=" * 60)
    print("Testing Optimized Batch Processing with Progress Tracking")
    print("=" * 60)
    
    try:
        # Setup
        config_path = os.path.join(project_root, 'config.yaml')
        config_manager = ConfigManager(config_path)
        config = config_manager.load_config()
        
        # Setup logger
        logger = setup_logging(config)
        
        logger.info("=== Starting Optimized Batch Processing Test ===")
        
        # Initialize unified processor
        processor = UnifiedProcessor(config, logger)
        
        # Run the optimized processing
        start_time = time.time()
        result = processor.process_all_sources()
        end_time = time.time()
        
        # Display results
        elapsed_time = end_time - start_time
        
        print(f"\n=== OPTIMIZED BATCH PROCESSING RESULTS ===")
        print(f"Success: {result['success']}")
        print(f"Total time: {elapsed_time:.2f} seconds")
        print(f"Files processed: {result.get('files_processed', 0)}")
        
        if result['success']:
            stats = result.get('statistics', {})
            print(f"Files copied: {stats.get('files_copied', 0)}")
            print(f"Errors: {stats.get('errors', 0)}")
            
            # Calculate performance metrics
            files_processed = result.get('files_processed', 0)
            if files_processed > 0 and elapsed_time > 0:
                files_per_second = files_processed / elapsed_time
                print(f"Processing speed: {files_per_second:.2f} files/second")
                
                # Compare to old method (estimated 5-6 seconds per file)
                old_method_time = files_processed * 5.5  # Average of 5-6 seconds
                speedup = old_method_time / elapsed_time if elapsed_time > 0 else 0
                print(f"Estimated speedup vs old method: {speedup:.1f}x faster")
                print(f"Old method would have taken: {old_method_time/60:.1f} minutes")
                print(f"New method took: {elapsed_time/60:.1f} minutes")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            
        # Display module statistics if available
        module_stats = result.get('module_stats', {})
        if module_stats:
            print(f"\n=== MODULE STATISTICS ===")
            for module_name, stats in module_stats.items():
                print(f"{module_name}: {stats}")
        
        logger.info("=== Optimized Batch Processing Test Complete ===")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
