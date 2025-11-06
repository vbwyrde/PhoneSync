#!/usr/bin/env python3
"""
Test script to verify BatchTargetResolver integration
"""

import sys
import os
import time
from datetime import datetime

# Add the VideoProcessor modules to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'VideoProcessor'))

def test_batch_target_resolver():
    """Test the BatchTargetResolver directly"""
    try:
        from VideoProcessor.modules.config_manager import ConfigManager
        from VideoProcessor.modules.logger_setup import setup_logging
        from VideoProcessor.modules.batch_target_resolver import BatchTargetResolver
        
        print("✅ Successfully imported BatchTargetResolver")
        
        # Load config
        config_manager = ConfigManager('config.yaml')
        config = config_manager.load_config()
        logger = setup_logging(config, 'test_batch_integration')
        
        print("✅ Successfully loaded config and logger")
        
        # Initialize BatchTargetResolver
        batch_resolver = BatchTargetResolver(config, logger)
        print("✅ Successfully initialized BatchTargetResolver")
        
        # Create test file data
        test_files = [
            {
                'name': '20240101_120000.jpg',
                'path': '\\\\MA-2022-C\\PHONESYNC\\TestFolder\\20240101_120000.jpg',
                'size': 1000000,
                'type': 'picture',
                'extension': '.jpg',
                'date': datetime(2024, 1, 1, 12, 0, 0),
                'source_folder': 'TestFolder'
            },
            {
                'name': '20240101_180000_kungfu.mp4',
                'path': '\\\\MA-2022-C\\PHONESYNC\\TestFolder\\20240101_180000_kungfu.mp4',
                'size': 5000000,
                'type': 'video',
                'extension': '.mp4',
                'date': datetime(2024, 1, 1, 18, 0, 0),
                'source_folder': 'TestFolder'
            }
        ]
        
        print(f"✅ Created {len(test_files)} test files")
        
        # Test batch resolution
        start_time = time.time()
        result = batch_resolver.resolve_all_target_paths(test_files)
        elapsed = time.time() - start_time
        
        print(f"✅ Batch resolution completed in {elapsed:.3f} seconds")
        print(f"✅ Resolved {len(result['target_paths'])} target paths")
        print(f"✅ Performance: {result['performance']['files_per_second']:.1f} files/sec")
        
        # Show results
        for file_key, target_path in result['target_paths'].items():
            print(f"  {file_key} -> {target_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing BatchTargetResolver: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_unified_processor_integration():
    """Test that UnifiedProcessor can import and use BatchTargetResolver"""
    try:
        from VideoProcessor.modules.unified_processor import UnifiedProcessor
        from VideoProcessor.modules.config_manager import ConfigManager
        from VideoProcessor.modules.logger_setup import setup_logging
        
        print("✅ Successfully imported UnifiedProcessor")
        
        # Load config
        config_manager = ConfigManager('config.yaml')
        config = config_manager.load_config()
        logger = setup_logging(config, 'test_unified_integration')
        
        # Initialize UnifiedProcessor
        processor = UnifiedProcessor(config, logger)
        print("✅ Successfully initialized UnifiedProcessor")
        
        # Check if BatchTargetResolver is available
        if hasattr(processor, 'batch_target_resolver'):
            print("✅ UnifiedProcessor has batch_target_resolver attribute")
            
            # Test a simple call
            test_files = [{
                'name': 'test.jpg',
                'path': 'test/path',
                'size': 1000,
                'type': 'picture',
                'extension': '.jpg',
                'date': datetime.now(),
                'source_folder': 'test'
            }]
            
            result = processor.batch_target_resolver.resolve_all_target_paths(test_files)
            print(f"✅ BatchTargetResolver working: resolved {len(result['target_paths'])} paths")
        else:
            print("❌ UnifiedProcessor missing batch_target_resolver attribute")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing UnifiedProcessor integration: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=== Testing BatchTargetResolver Integration ===")
    
    # Test 1: Direct BatchTargetResolver functionality
    print("\n1. Testing BatchTargetResolver directly...")
    test1_success = test_batch_target_resolver()
    
    # Test 2: UnifiedProcessor integration
    print("\n2. Testing UnifiedProcessor integration...")
    test2_success = test_unified_processor_integration()
    
    # Summary
    print("\n=== Test Results ===")
    print(f"BatchTargetResolver direct test: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"UnifiedProcessor integration: {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    if test1_success and test2_success:
        print("\n🎉 All tests passed! BatchTargetResolver integration is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
