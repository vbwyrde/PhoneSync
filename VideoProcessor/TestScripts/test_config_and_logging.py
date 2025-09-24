#!/usr/bin/env python3
"""
Test script for configuration management and logging system
"""

import sys
import os
from pathlib import Path

# Add the parent directory to Python path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logging, log_system_info, ProgressLogger

def test_config_loading():
    """Test configuration loading and validation"""
    print("=== Testing Configuration Loading ===")
    
    try:
        # Test loading the config file
        config_manager = ConfigManager("../config.yaml")
        config = config_manager.load_config()
        
        print("✅ Configuration loaded successfully")
        
        # Test specific config access methods
        source_folders = config_manager.get_source_folders()
        print(f"✅ Source folders: {len(source_folders)} configured")
        
        target_paths = {
            'pictures': config_manager.get_target_path('pictures'),
            'videos': config_manager.get_target_path('videos'),
            'wudan': config_manager.get_target_path('wudan'),
            'notes': config_manager.get_target_path('notes')
        }
        print(f"✅ Target paths configured: {list(target_paths.keys())}")
        
        # Test file extensions
        pic_extensions = config_manager.get_file_extensions('pictures')
        vid_extensions = config_manager.get_file_extensions('videos')
        print(f"✅ Picture extensions: {len(pic_extensions)}")
        print(f"✅ Video extensions: {len(vid_extensions)}")
        
        # Test boolean settings
        dedup_enabled = config_manager.is_deduplication_enabled()
        create_folders = config_manager.should_create_missing_folders()
        print(f"✅ Deduplication enabled: {dedup_enabled}")
        print(f"✅ Create missing folders: {create_folders}")
        
        # Test AI settings
        ai_settings = config_manager.get_ai_settings()
        print(f"✅ AI settings configured: {list(ai_settings.keys())}")
        
        # Test Wudan rules
        wudan_rules = config_manager.get_wudan_rules()
        print(f"✅ Wudan rules configured: {list(wudan_rules.keys())}")
        
        return True, config
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False, None

def test_logging_setup(config):
    """Test logging system setup"""
    print("\n=== Testing Logging Setup ===")
    
    try:
        # Set up logging
        logger = setup_logging(config)
        print("✅ Logger setup successful")
        
        # Test different log levels
        logger.debug("Debug message test")
        logger.info("Info message test")
        logger.warning("Warning message test")
        logger.error("Error message test")
        
        print("✅ Log level testing complete")
        
        # Test system info logging
        log_system_info(logger, config)
        print("✅ System info logging complete")
        
        # Test progress logger
        progress = ProgressLogger(logger, 250, report_interval=50)
        for i in range(250):
            progress.update()
        progress.log_completion()
        print("✅ Progress logging test complete")
        
        # Check if log file was created
        log_path = Path(config['logging']['log_path'])
        if log_path.exists():
            log_size = log_path.stat().st_size
            print(f"✅ Log file created: {log_path} ({log_size} bytes)")
        else:
            print("⚠️  Log file not found (may be disabled in config)")
        
        return True, logger
        
    except Exception as e:
        print(f"❌ Logging setup failed: {e}")
        return False, None

def test_error_handling():
    """Test error handling in configuration"""
    print("\n=== Testing Error Handling ===")
    
    try:
        # Test missing config file
        try:
            bad_config = ConfigManager("nonexistent.yaml")
            bad_config.load_config()
            print("❌ Should have failed with missing config file")
            return False
        except FileNotFoundError:
            print("✅ Correctly handled missing config file")
        
        # Test invalid YAML (we'll create a temporary bad file)
        bad_yaml_path = Path("TestScripts/bad_config.yaml")
        with open(bad_yaml_path, 'w') as f:
            f.write("invalid: yaml: content: [unclosed")
        
        try:
            bad_config = ConfigManager(str(bad_yaml_path))
            bad_config.load_config()
            print("❌ Should have failed with invalid YAML")
            return False
        except Exception:
            print("✅ Correctly handled invalid YAML")
        finally:
            # Clean up
            if bad_yaml_path.exists():
                bad_yaml_path.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=== Configuration and Logging Test Suite ===")
    
    # Change to the correct directory
    os.chdir(Path(__file__).parent.parent)
    
    # Test 1: Configuration loading
    config_success, config = test_config_loading()
    
    if not config_success:
        print("\n❌ Configuration tests failed. Cannot proceed with logging tests.")
        return False
    
    # Test 2: Logging setup
    logging_success, logger = test_logging_setup(config)
    
    # Test 3: Error handling
    error_handling_success = test_error_handling()
    
    # Summary
    print("\n=== Test Results Summary ===")
    print(f"✅ Configuration Loading: {'PASS' if config_success else 'FAIL'}")
    print(f"✅ Logging Setup: {'PASS' if logging_success else 'FAIL'}")
    print(f"✅ Error Handling: {'PASS' if error_handling_success else 'FAIL'}")
    
    all_passed = config_success and logging_success and error_handling_success
    
    if all_passed:
        print("\n🎉 All configuration and logging tests passed!")
        if logger:
            logger.info("Configuration and logging test suite completed successfully")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
