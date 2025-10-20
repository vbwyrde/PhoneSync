#!/usr/bin/env python3
"""
Debug script to check the current state of UnifiedProcessor
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from VideoProcessor.modules.config_manager import ConfigManager
from VideoProcessor.modules.unified_processor import UnifiedProcessor
from VideoProcessor.modules.logger_setup import setup_logging

def debug_processor():
    """Debug the current state of UnifiedProcessor"""
    print("=== Debugging UnifiedProcessor ===")
    
    try:
        # Initialize configuration
        config_path = os.path.join(project_root, 'config.yaml')
        config_manager = ConfigManager(config_path)
        config = config_manager.load_config()
        
        # Setup logging
        logger = setup_logging(config)
        
        # Initialize processor
        processor = UnifiedProcessor(config, logger)
        print("✅ UnifiedProcessor initialized successfully")
        
        # Check available methods and attributes
        print("\n=== Checking Processor Attributes ===")
        
        # Check for batch file copier
        if hasattr(processor, 'batch_file_copier'):
            print("✅ batch_file_copier is available")
        else:
            print("❌ batch_file_copier is NOT available")
            
        # Check for fast batch processor
        if hasattr(processor, 'fast_batch_processor'):
            print("✅ fast_batch_processor is available")
        else:
            print("❌ fast_batch_processor is NOT available")
            
        # Check for old methods that should be removed
        if hasattr(processor, '_process_file_batch'):
            print("⚠️  WARNING: Old _process_file_batch method still exists")
        else:
            print("✅ Old _process_file_batch method properly removed")
            
        if hasattr(processor, '_process_single_file'):
            print("⚠️  WARNING: Old _process_single_file method still exists")
        else:
            print("✅ Old _process_single_file method properly removed")
            
        # Check for required methods
        if hasattr(processor, 'process_all_sources'):
            print("✅ process_all_sources method is available")
        else:
            print("❌ process_all_sources method is NOT available")
            
        # Check the source code of process_all_sources to see what it's calling
        print("\n=== Checking process_all_sources Implementation ===")
        import inspect
        source = inspect.getsource(processor.process_all_sources)
        
        if 'batch_file_copier' in source:
            print("✅ process_all_sources uses batch_file_copier")
        else:
            print("❌ process_all_sources does NOT use batch_file_copier")
            
        if '_process_file_batch' in source:
            print("⚠️  WARNING: process_all_sources still calls _process_file_batch")
        else:
            print("✅ process_all_sources does not call old _process_file_batch")
            
        print("\n=== Source Code Preview ===")
        lines = source.split('\n')
        for i, line in enumerate(lines[:20], 1):  # Show first 20 lines
            print(f"{i:2d}: {line}")
        if len(lines) > 20:
            print("... (truncated)")
            
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_processor()
