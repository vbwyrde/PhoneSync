#!/usr/bin/env python3
"""
Test script to verify that the new optimized code is being executed
"""

import sys
import os

# Add the VideoProcessor modules to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'VideoProcessor'))

def test_unified_processor_execution():
    """Test that UnifiedProcessor uses the new optimized code path"""
    try:
        from VideoProcessor.modules.config_manager import ConfigManager
        from VideoProcessor.modules.logger_setup import setup_logging
        from VideoProcessor.modules.unified_processor import UnifiedProcessor
        
        print("✅ Successfully imported modules")
        
        # Load config
        config_manager = ConfigManager('config.yaml')
        config = config_manager.load_config()
        logger = setup_logging(config)
        
        print("✅ Successfully loaded config and logger")
        
        # Initialize UnifiedProcessor
        processor = UnifiedProcessor(config, logger)
        print("✅ Successfully initialized UnifiedProcessor")
        
        # Check if all the new modules are available
        if hasattr(processor, 'batch_target_resolver'):
            print("✅ BatchTargetResolver is available")
        else:
            print("❌ BatchTargetResolver is missing")
            return False
            
        if hasattr(processor, 'fast_batch_processor'):
            print("✅ FastBatchProcessor is available")
        else:
            print("❌ FastBatchProcessor is missing")
            return False
            
        if hasattr(processor, 'batch_file_copier'):
            print("✅ BatchFileCopier is available")
        else:
            print("❌ BatchFileCopier is missing")
            return False
        
        # Check if the _get_final_stats method exists
        if hasattr(processor.batch_file_copier, '_get_final_stats'):
            print("✅ BatchFileCopier._get_final_stats method exists")
        else:
            print("❌ BatchFileCopier._get_final_stats method is missing")
            return False
        
        # Test the method call
        try:
            stats = processor.batch_file_copier._get_final_stats()
            print(f"✅ _get_final_stats method works: {stats}")
        except Exception as e:
            print(f"❌ _get_final_stats method failed: {e}")
            return False
        
        print("\n🎉 All new optimized modules are properly loaded and functional!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing UnifiedProcessor: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=== Testing New Optimized Code Execution ===")
    
    success = test_unified_processor_execution()
    
    if success:
        print("\n✅ SUCCESS: New optimized code is properly loaded and ready to use!")
        print("The system should now use:")
        print("  - FastBatchProcessor for file identification")
        print("  - BatchTargetResolver for path resolution")
        print("  - BatchFileCopier for optimized file copying")
    else:
        print("\n❌ FAILURE: There are issues with the new optimized code.")
        print("The system may fall back to old individual file processing.")

if __name__ == "__main__":
    main()
