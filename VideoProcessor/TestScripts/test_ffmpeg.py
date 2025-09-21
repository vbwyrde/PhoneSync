#!/usr/bin/env python3
"""
Test script to verify FFmpeg availability and basic thumbnail extraction
"""

import subprocess
import sys
import os
from pathlib import Path
import tempfile

def test_ffmpeg_availability():
    """Test if FFmpeg is available in PATH"""
    try:
        print("Testing FFmpeg availability...")
        
        # Try to run ffmpeg -version
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        
        if result.returncode == 0:
            # Extract version info from first line
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg found: {version_line}")
            return True
        else:
            print(f"❌ FFmpeg command failed with return code: {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ FFmpeg not found in PATH")
        print("Please install FFmpeg and add it to your system PATH")
        return False
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg command timed out")
        return False
    except Exception as e:
        print(f"❌ Unexpected error testing FFmpeg: {e}")
        return False

def create_test_video():
    """Create a simple test video using FFmpeg"""
    try:
        print("\nCreating test video...")
        
        # Create a temporary test video (5 seconds, solid color)
        test_video_path = "TestScripts/test_video.mp4"
        
        cmd = [
            'ffmpeg', '-y',  # -y to overwrite existing file
            '-f', 'lavfi',   # Use lavfi (libavfilter) input
            '-i', 'color=blue:size=320x240:duration=5',  # Blue 320x240 for 5 seconds
            '-c:v', 'libx264',  # Use H.264 codec
            '-pix_fmt', 'yuv420p',  # Pixel format
            test_video_path
        ]
        
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True, 
                              timeout=30)
        
        if result.returncode == 0 and os.path.exists(test_video_path):
            file_size = os.path.getsize(test_video_path)
            print(f"✅ Test video created: {test_video_path} ({file_size} bytes)")
            return test_video_path
        else:
            print(f"❌ Failed to create test video")
            print(f"Command: {' '.join(cmd)}")
            print(f"Error: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ Test video creation timed out")
        return None
    except Exception as e:
        print(f"❌ Error creating test video: {e}")
        return None

def test_thumbnail_extraction(video_path):
    """Test thumbnail extraction from video"""
    try:
        print(f"\nTesting thumbnail extraction from: {video_path}")
        
        thumbnail_path = "TestScripts/test_thumbnail.png"
        
        # FFmpeg command to extract thumbnail at 2-second mark
        cmd = [
            'ffmpeg', '-y',  # -y to overwrite existing file
            '-i', video_path,  # Input video
            '-ss', '00:00:02',  # Seek to 2 seconds
            '-vframes', '1',  # Extract 1 frame
            '-vf', 'scale=320:240',  # Scale to 320x240
            '-f', 'image2',  # Output format
            thumbnail_path
        ]
        
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True, 
                              timeout=30)
        
        if result.returncode == 0 and os.path.exists(thumbnail_path):
            file_size = os.path.getsize(thumbnail_path)
            print(f"✅ Thumbnail extracted: {thumbnail_path} ({file_size} bytes)")
            return thumbnail_path
        else:
            print(f"❌ Failed to extract thumbnail")
            print(f"Command: {' '.join(cmd)}")
            print(f"Error: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ Thumbnail extraction timed out")
        return None
    except Exception as e:
        print(f"❌ Error extracting thumbnail: {e}")
        return None

def test_pipe_output():
    """Test FFmpeg pipe output (for base64 encoding)"""
    try:
        print("\nTesting FFmpeg pipe output...")
        
        # Create a simple 1-second test video in memory
        cmd = [
            'ffmpeg',
            '-f', 'lavfi',
            '-i', 'color=red:size=100x100:duration=1',
            '-ss', '00:00:00.5',  # Seek to 0.5 seconds
            '-vframes', '1',  # Extract 1 frame
            '-vf', 'scale=100:100',  # Scale to 100x100
            '-f', 'image2pipe',  # Output to pipe
            '-vcodec', 'png',  # PNG format
            '-'  # Output to stdout
        ]
        
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              timeout=30)
        
        if result.returncode == 0 and len(result.stdout) > 0:
            print(f"✅ Pipe output successful: {len(result.stdout)} bytes received")
            
            # Verify it's a valid PNG by checking header
            if result.stdout.startswith(b'\x89PNG'):
                print("✅ Valid PNG header detected")
                return True
            else:
                print("❌ Invalid PNG header")
                return False
        else:
            print(f"❌ Pipe output failed")
            print(f"Error: {result.stderr.decode() if result.stderr else 'No error message'}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Pipe output test timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing pipe output: {e}")
        return False

def cleanup_test_files():
    """Clean up test files"""
    test_files = [
        "TestScripts/test_video.mp4",
        "TestScripts/test_thumbnail.png"
    ]
    
    for file_path in test_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🧹 Cleaned up: {file_path}")
        except Exception as e:
            print(f"⚠️  Could not clean up {file_path}: {e}")

if __name__ == "__main__":
    print("=== FFmpeg Test Suite ===")
    
    # Test 1: FFmpeg availability
    ffmpeg_available = test_ffmpeg_availability()
    
    if not ffmpeg_available:
        print("\n❌ FFmpeg is not available. Please install FFmpeg before proceeding.")
        sys.exit(1)
    
    # Test 2: Create test video
    test_video = create_test_video()
    
    if test_video:
        # Test 3: Extract thumbnail
        thumbnail = test_thumbnail_extraction(test_video)
        
        # Test 4: Pipe output
        pipe_success = test_pipe_output()
        
        # Summary
        print("\n=== Test Results ===")
        print(f"✅ FFmpeg Available: {ffmpeg_available}")
        print(f"✅ Video Creation: {test_video is not None}")
        print(f"✅ Thumbnail Extraction: {thumbnail is not None}")
        print(f"✅ Pipe Output: {pipe_success}")
        
        if all([ffmpeg_available, test_video, thumbnail, pipe_success]):
            print("\n🎉 All FFmpeg tests passed! Ready for video processing.")
        else:
            print("\n⚠️  Some FFmpeg tests failed. Check the output above.")
        
        # Cleanup
        cleanup_test_files()
    else:
        print("\n❌ Could not create test video. FFmpeg may not be properly configured.")
        
    print("\n=== FFmpeg Test Complete ===")
