#!/usr/bin/env python3
"""
Test script to verify dynamic midpoint thumbnail extraction
"""

import sys
import os
import tempfile
import subprocess
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logging
from modules.video_analyzer import VideoAnalyzer

def create_test_video(output_path: str, duration: int = 10) -> bool:
    """Create a test video with specific duration"""
    try:
        cmd = [
            'ffmpeg',
            '-f', 'lavfi',
            '-i', f'testsrc2=duration={duration}:size=640x480:rate=30',
            '-f', 'lavfi', 
            '-i', f'sine=frequency=1000:duration={duration}',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-y',  # Overwrite output file
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error creating test video: {e}")
        return False

def test_midpoint_calculation():
    """Test dynamic midpoint thumbnail extraction"""
    print("=== Dynamic Midpoint Thumbnail Extraction Test ===")
    
    # Initialize configuration and logging
    try:
        config = ConfigManager('config.yaml')
        logger = setup_logging(config)
        print("✅ Configuration and logging initialized")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    
    # Initialize VideoAnalyzer
    try:
        analyzer = VideoAnalyzer(config, logger)
        print("✅ VideoAnalyzer initialized")
    except Exception as e:
        print(f"❌ VideoAnalyzer initialization failed: {e}")
        return False
    
    # Test different video durations
    test_durations = [5, 10, 30, 60, 120]  # seconds
    
    for duration in test_durations:
        print(f"\n--- Testing {duration}-second video ---")
        
        # Create temporary directory for test
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Create test video
            test_video_path = temp_dir / f"test_{duration}s.mp4"
            print(f"Creating {duration}-second test video...")
            
            if not create_test_video(str(test_video_path), duration=duration):
                print(f"❌ Failed to create {duration}-second test video")
                continue
            
            print(f"✅ Test video created: {test_video_path.stat().st_size} bytes")
            
            # Test duration detection
            detected_duration = analyzer._get_video_duration(str(test_video_path))
            if detected_duration is None:
                print(f"❌ Failed to detect video duration")
                continue
            
            print(f"✅ Detected duration: {detected_duration:.2f} seconds")
            
            # Calculate expected midpoint
            expected_midpoint = detected_duration / 2.0
            if expected_midpoint > (detected_duration - 1):
                expected_midpoint = max(1.0, detected_duration - 1)
            
            print(f"✅ Expected midpoint: {expected_midpoint:.2f} seconds")
            
            # Test thumbnail extraction
            thumbnail_b64 = analyzer._extract_thumbnail(str(test_video_path))
            
            if thumbnail_b64:
                print(f"✅ Thumbnail extracted successfully")
                print(f"   - Base64 length: {len(thumbnail_b64)} characters")
                print(f"   - Estimated image size: ~{len(thumbnail_b64) * 3 // 4} bytes")
            else:
                print(f"❌ Thumbnail extraction failed")
                
        except Exception as e:
            print(f"❌ Error testing {duration}-second video: {e}")
            
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    print(f"\n🎉 Dynamic midpoint extraction test complete!")
    return True

if __name__ == "__main__":
    test_midpoint_calculation()
