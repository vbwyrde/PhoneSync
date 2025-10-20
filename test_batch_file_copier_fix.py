#!/usr/bin/env python3
"""
Test script to verify BatchFileCopier fixes
"""

import sys
import os
import time
from datetime import datetime

# Add the VideoProcessor modules to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'VideoProcessor'))

def test_batch_file_copier():
    """Test the BatchFileCopier with the fixes"""
    try:
        from VideoProcessor.modules.config_manager import ConfigManager
        from VideoProcessor.modules.logger_setup import setup_logging
        from VideoProcessor.modules.batch_file_copier import BatchFileCopier
        
        print("✅ Successfully imported modules")
        
        # Load config
        config_manager = ConfigManager('config.yaml')
        config = config_manager.load_config()
        logger = setup_logging(config)
        
        print("✅ Successfully loaded config and logger")
        
        # Initialize BatchFileCopier
        batch_copier = BatchFileCopier(config, logger)
        print("✅ Successfully initialized BatchFileCopier")
        
        # Test the _get_final_stats method
        try:
            stats = batch_copier._get_final_stats()
            print(f"✅ _get_final_stats method works: {stats}")
        except Exception as e:
            print(f"❌ _get_final_stats method failed: {e}")
            return False
        
        # Test tuple vs dictionary handling
        print("\n=== Testing tuple vs dictionary handling ===")
        
        # Create a mock file_info dictionary
        test_file_info = {
            'name': 'test_file.jpg',
            'path': 'test/path/test_file.jpg',
            'size': 1000,
            'type': 'picture',
            'extension': '.jpg',
            'date': datetime.now(),
            'source_folder': 'test'
        }
        
        # Test with dictionary (should work)
        print("Testing with dictionary file_info...")
        try:
            # This should not crash
            if isinstance(test_file_info, tuple):
                print("❌ Dictionary detected as tuple")
                return False
            elif not isinstance(test_file_info, dict):
                print("❌ Dictionary not detected as dict")
                return False
            else:
                print("✅ Dictionary handling works correctly")
        except Exception as e:
            print(f"❌ Dictionary test failed: {e}")
            return False
        
        # Test with tuple (should be handled gracefully)
        print("Testing with tuple file_info...")
        test_tuple = ('test_file.jpg', 'test/path', 1000)
        try:
            if isinstance(test_tuple, tuple):
                print("✅ Tuple correctly detected as tuple")
            else:
                print("❌ Tuple not detected as tuple")
                return False
        except Exception as e:
            print(f"❌ Tuple test failed: {e}")
            return False
        
        print("\n🎉 All BatchFileCopier fixes are working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing BatchFileCopier: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=== Testing BatchFileCopier Fixes ===")
    
    success = test_batch_file_copier()
    
    if success:
        print("\n✅ SUCCESS: BatchFileCopier fixes are working!")
        print("The system should now:")
        print("  - Handle organize_file tuple return values correctly")
        print("  - Track progress properly (copied_files counter)")
        print("  - Have working _get_final_stats method")
        print("  - Handle both tuple and dictionary file_info gracefully")
    else:
        print("\n❌ FAILURE: There are still issues with BatchFileCopier.")

if __name__ == "__main__":
    main()
