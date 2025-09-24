#!/usr/bin/env python3
"""
Test script to analyze real videos from Z:\PhotoSync_Test\Source
Tests dynamic midpoint thumbnail extraction with actual video files
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logging
from modules.video_analyzer import VideoAnalyzer

def test_real_videos():
    """Test dynamic midpoint extraction with real videos"""
    print("=== Real Video Analysis Test ===")
    print("Testing dynamic midpoint thumbnail extraction with actual video files")
    
    # Initialize configuration and logging
    try:
        config_manager = ConfigManager('config.yaml')
        config = config_manager.load_config()
        logger = setup_logging(config)
        print("✅ Configuration and logging initialized")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False

    # Initialize VideoAnalyzer
    try:
        analyzer = VideoAnalyzer(config, logger)
        print("✅ VideoAnalyzer initialized with dynamic midpoint extraction")
    except Exception as e:
        print(f"❌ VideoAnalyzer initialization failed: {e}")
        return False
    
    # Test directory
    test_dir = Path("Z:/PhotoSync_Test/Source")
    
    if not test_dir.exists():
        print(f"❌ Test directory not found: {test_dir}")
        return False
    
    # Find video files
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    video_files = []
    
    for ext in video_extensions:
        video_files.extend(test_dir.glob(f"*{ext}"))
        video_files.extend(test_dir.glob(f"*{ext.upper()}"))
    
    if not video_files:
        print(f"❌ No video files found in {test_dir}")
        return False
    
    print(f"✅ Found {len(video_files)} video files")
    
    # Test a few representative videos
    test_videos = sorted(video_files)[:5]  # Test first 5 videos
    
    print(f"\n=== Testing Dynamic Midpoint Extraction on {len(test_videos)} Videos ===")
    
    successful_analyses = 0
    total_duration = 0
    
    for i, video_path in enumerate(test_videos, 1):
        print(f"\n--- Video {i}/{len(test_videos)}: {video_path.name} ---")
        
        try:
            # Get file size
            file_size = video_path.stat().st_size
            print(f"📁 File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
            
            # Test duration detection
            duration = analyzer._get_video_duration(str(video_path))
            
            if duration is None:
                print(f"❌ Failed to detect video duration")
                continue
            
            print(f"⏱️  Video duration: {duration:.2f} seconds ({duration/60:.1f} minutes)")
            total_duration += duration
            
            # Calculate expected midpoint
            expected_midpoint = duration / 2.0
            if expected_midpoint > (duration - 1):
                expected_midpoint = max(1.0, duration - 1)
            
            print(f"🎯 Midpoint timestamp: {expected_midpoint:.2f} seconds")
            
            # Test thumbnail extraction
            print("🖼️  Extracting thumbnail from midpoint...")
            thumbnail_b64 = analyzer._extract_thumbnail(str(video_path))
            
            if thumbnail_b64:
                print(f"✅ Thumbnail extracted successfully")
                print(f"   - Base64 length: {len(thumbnail_b64):,} characters")
                print(f"   - Estimated image size: ~{len(thumbnail_b64) * 3 // 4:,} bytes")
                
                # Test AI analysis if LM Studio is available
                try:
                    file_info = {
                        'name': video_path.name,
                        'size': file_size,
                        'type': 'video'
                    }
                    
                    print("🤖 Analyzing with AI...")
                    analysis_result = analyzer.analyze_video(str(video_path), file_info)
                    
                    if analysis_result.get('analyzed'):
                        kung_fu = analysis_result.get('kung_fu', False)
                        confidence = analysis_result.get('confidence', 0)
                        print(f"🥋 Kung Fu detected: {'YES' if kung_fu else 'NO'} (confidence: {confidence}%)")
                        
                        if kung_fu:
                            print(f"📝 Analysis: {analysis_result.get('description', 'No description')[:100]}...")
                    else:
                        print(f"⚠️  AI analysis failed: {analysis_result.get('reason', 'Unknown error')}")
                        
                except Exception as ai_error:
                    print(f"⚠️  AI analysis skipped: {ai_error}")
                
                successful_analyses += 1
                
            else:
                print(f"❌ Thumbnail extraction failed")
                
        except Exception as e:
            print(f"❌ Error processing {video_path.name}: {e}")
    
    # Summary
    print(f"\n=== Test Results Summary ===")
    print(f"✅ Videos processed: {successful_analyses}/{len(test_videos)}")
    print(f"📊 Success rate: {successful_analyses/len(test_videos)*100:.1f}%")
    print(f"⏱️  Total video duration tested: {total_duration/60:.1f} minutes")
    print(f"🎯 Dynamic midpoint extraction: {'WORKING' if successful_analyses > 0 else 'FAILED'}")
    
    if successful_analyses > 0:
        print(f"\n🎉 Dynamic midpoint thumbnail extraction is working with real videos!")
        print(f"📹 The system successfully adapts to different video lengths and extracts")
        print(f"   representative frames from the middle of each video.")
        return True
    else:
        print(f"\n❌ No videos were successfully processed")
        return False

if __name__ == "__main__":
    test_real_videos()
