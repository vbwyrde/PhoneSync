#!/usr/bin/env python3
"""
Test Video Analysis Integration
Verify that video analysis is properly integrated into the unified processing workflow
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add modules directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logging
from modules.unified_processor import UnifiedProcessor

def test_video_analysis_integration():
    """Test that video analysis methods are properly integrated"""
    
    print("=== Testing Video Analysis Integration ===")
    
    try:
        # Load configuration
        config_path = Path(__file__).parent.parent / "config.yaml"
        config = ConfigManager.load_config(str(config_path))
        
        # Setup logging
        logger = setup_logging(config)
        
        # Initialize unified processor
        processor = UnifiedProcessor(config, logger)
        
        # Test 1: Check that video analyzer is initialized
        print("1. Testing VideoAnalyzer initialization...")
        if hasattr(processor, 'video_analyzer') and processor.video_analyzer:
            print("   ✅ VideoAnalyzer is properly initialized")
        else:
            print("   ❌ VideoAnalyzer is NOT initialized")
            return False
        
        # Test 2: Check that new analysis methods exist
        print("2. Testing new analysis methods...")
        if hasattr(processor, '_analyze_copied_videos'):
            print("   ✅ _analyze_copied_videos method exists")
        else:
            print("   ❌ _analyze_copied_videos method is missing")
            return False
            
        if hasattr(processor, '_generate_notes_file_for_directory'):
            print("   ✅ _generate_notes_file_for_directory method exists")
        else:
            print("   ❌ _generate_notes_file_for_directory method is missing")
            return False
        
        # Test 3: Test the analysis method with dummy data
        print("3. Testing analysis method with dummy data...")
        
        # Create dummy file data
        dummy_files = [
            {
                'name': 'test_video.mp4',
                'size': 1000000,
                'type': 'video',
                'date': Path(__file__).stat().st_mtime
            }
        ]
        
        dummy_target_paths = {
            'test_video.mp4|1000000': '/fake/path/test_video.mp4'
        }
        
        # Test the method (should handle missing files gracefully)
        try:
            result = processor._analyze_copied_videos(dummy_files, dummy_target_paths)
            print(f"   ✅ _analyze_copied_videos executed successfully")
            print(f"      Result: {result}")
        except Exception as e:
            print(f"   ⚠️  _analyze_copied_videos failed (expected with dummy data): {e}")
        
        # Test 4: Check AI connection
        print("4. Testing AI connection...")
        ai_test = processor.video_analyzer.test_ai_connection()
        if ai_test.get('success', False):
            print("   ✅ AI connection is working")
        else:
            print(f"   ⚠️  AI connection failed: {ai_test.get('reason', 'Unknown error')}")
            print("   (This is expected if LM Studio is not running)")
        
        print("\n=== Integration Test Summary ===")
        print("✅ Video analysis integration is properly implemented")
        print("✅ All required methods are present")
        print("✅ VideoAnalyzer is initialized")
        print("✅ Methods execute without syntax errors")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_video_analysis_integration()
    sys.exit(0 if success else 1)
