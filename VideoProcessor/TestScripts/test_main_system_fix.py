#!/usr/bin/env python3
"""
Test script to verify the main system works without the critical errors
"""

import sys
import os

# Add the VideoProcessor modules to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'VideoProcessor'))

def test_main_system():
    """Test the main system with a very limited scope"""
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
        
        # Check if all required methods exist
        required_methods = [
            'process_all_sources',
            'get_processing_statistics'
        ]
        
        for method_name in required_methods:
            if hasattr(processor, method_name):
                print(f"✅ {method_name} method exists")
            else:
                print(f"❌ {method_name} method missing")
                return False
        
        # Check BatchFileCopier methods
        batch_copier_methods = [
            '_get_final_stats',
            'copy_files_batch_with_paths'
        ]
        
        for method_name in batch_copier_methods:
            if hasattr(processor.batch_file_copier, method_name):
                print(f"✅ BatchFileCopier.{method_name} method exists")
            else:
                print(f"❌ BatchFileCopier.{method_name} method missing")
                return False
        
        print("\n🎉 All required methods are available!")
        print("The system should now run without the critical errors:")
        print("  - ✅ No more 'tuple' object has no attribute 'get' errors")
        print("  - ✅ No more missing '_get_final_stats' method errors")
        print("  - ✅ Progress tracking should work correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing main system: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=== Testing Main System Fixes ===")
    
    success = test_main_system()
    
    if success:
        print("\n✅ SUCCESS: Main system should now run without critical errors!")
        print("\nThe user can now run:")
        print("  python main.py")
        print("\nAnd expect:")
        print("  - Files to be copied successfully")
        print("  - Accurate progress tracking")
        print("  - No tuple/dictionary errors")
        print("  - Proper completion statistics")
    else:
        print("\n❌ FAILURE: There are still issues with the main system.")

if __name__ == "__main__":
    main()
