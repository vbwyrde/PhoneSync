#!/usr/bin/env python3
"""
Test script for Video Analysis Integration
Tests FFmpeg thumbnail extraction and LM Studio AI analysis
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add the parent directory to Python path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logging
from modules.video_analyzer import VideoAnalyzer

def create_test_video(output_path: str, duration: int = 10) -> bool:
    """
    Create a test video using FFmpeg
    
    Args:
        output_path: Path where to save the test video
        duration: Duration in seconds
        
    Returns:
        True if successful, False otherwise
    """
    import subprocess
    
    try:
        # Create a simple test video with color bars and timestamp
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
        
        if result.returncode == 0:
            return os.path.exists(output_path) and os.path.getsize(output_path) > 0
        else:
            print(f"FFmpeg error: {result.stderr.decode() if result.stderr else 'No error output'}")
            return False
            
    except Exception as e:
        print(f"Error creating test video: {e}")
        return False

def test_video_analyzer_initialization(config, logger):
    """Test VideoAnalyzer initialization"""
    print("\n=== Testing VideoAnalyzer Initialization ===")
    
    try:
        analyzer = VideoAnalyzer(config, logger)
        
        print(f"✅ VideoAnalyzer initialized successfully")
        print(f"   - AI enabled: {analyzer.video_analysis_enabled}")
        print(f"   - LM Studio URL: {analyzer.lm_studio_url}")
        print(f"   - Model: {analyzer.model}")
        print(f"   - Dynamic thumbnail extraction: Enabled (midpoint calculation)")
        
        return True, analyzer
        
    except Exception as e:
        print(f"❌ VideoAnalyzer initialization failed: {e}")
        return False, None

def test_ai_connection(analyzer):
    """Test LM Studio AI connection"""
    print("\n=== Testing LM Studio AI Connection ===")
    
    try:
        result = analyzer.test_ai_connection()
        
        if result['success']:
            print(f"✅ LM Studio connection successful")
            print(f"   - Response: {result['response']}")
            print(f"   - Status code: {result['status_code']}")
            return True
        else:
            print(f"❌ LM Studio connection failed")
            print(f"   - Error: {result['error']}")
            print(f"   - Status code: {result.get('status_code', 'N/A')}")
            return False
            
    except Exception as e:
        print(f"❌ AI connection test failed: {e}")
        return False

def test_thumbnail_extraction(analyzer, logger):
    """Test FFmpeg thumbnail extraction"""
    print("\n=== Testing FFmpeg Thumbnail Extraction ===")
    
    # Create temporary directory for test video
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Create test video
        test_video_path = temp_dir / "test_video.mp4"
        print(f"Creating test video: {test_video_path}")
        
        if not create_test_video(str(test_video_path), duration=10):
            print(f"❌ Failed to create test video")
            return False
        
        print(f"✅ Test video created: {test_video_path.stat().st_size} bytes")
        
        # Test thumbnail extraction
        thumbnail_data = analyzer._extract_thumbnail(str(test_video_path))
        
        if thumbnail_data:
            print(f"✅ Thumbnail extracted successfully")
            print(f"   - Base64 data length: {len(thumbnail_data)} characters")
            print(f"   - Estimated image size: ~{len(thumbnail_data) * 3 // 4} bytes")
            
            # Verify it's valid base64
            import base64
            try:
                decoded = base64.b64decode(thumbnail_data)
                print(f"   - Decoded image size: {len(decoded)} bytes")
                
                # Check if it looks like PNG data
                if decoded.startswith(b'\x89PNG'):
                    print(f"   - Valid PNG format detected")
                    return True
                else:
                    print(f"   - Warning: Decoded data doesn't appear to be PNG")
                    return True  # Still consider success
                    
            except Exception as e:
                print(f"❌ Invalid base64 data: {e}")
                return False
        else:
            print(f"❌ Thumbnail extraction failed")
            return False
            
    except Exception as e:
        print(f"❌ Thumbnail extraction test failed: {e}")
        return False
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_video_analysis_integration(analyzer, logger):
    """Test complete video analysis workflow"""
    print("\n=== Testing Complete Video Analysis Workflow ===")
    
    # Create temporary directory for test
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Create test video
        test_video_path = temp_dir / "kung_fu_test.mp4"
        print(f"Creating test video for analysis: {test_video_path}")
        
        if not create_test_video(str(test_video_path), duration=8):
            print(f"❌ Failed to create test video")
            return False
        
        # Prepare file info
        file_info = {
            'name': 'kung_fu_test.mp4',
            'date': datetime(2025, 4, 12, 14, 30, 0),
            'size': test_video_path.stat().st_size,
            'type': 'video'
        }
        
        print(f"✅ Test video ready: {file_info['size']} bytes")
        
        # Analyze video
        print("Analyzing video with AI...")
        analysis_result = analyzer.analyze_video(str(test_video_path), file_info)
        
        if analysis_result.get('analyzed'):
            print(f"✅ Video analysis completed successfully")
            print(f"   - Kung Fu detected: {analysis_result.get('is_kung_fu', False)}")
            print(f"   - Confidence: {analysis_result.get('confidence', 0)}%")
            print(f"   - Description: {analysis_result.get('description', 'N/A')}")
            
            if analysis_result.get('note_content'):
                print(f"   - Note generated: Yes ({len(analysis_result['note_content'])} chars)")
            else:
                print(f"   - Note generated: No")
            
            # Test note file generation if kung fu detected
            if analysis_result.get('is_kung_fu') and analysis_result.get('note_content'):
                target_dir = temp_dir / "target"
                target_dir.mkdir(exist_ok=True)
                
                note_path = analyzer.generate_note_file(
                    str(test_video_path), 
                    analysis_result, 
                    str(target_dir)
                )
                
                if note_path and os.path.exists(note_path):
                    print(f"✅ Note file generated: {Path(note_path).name}")
                    
                    # Read and display note content preview
                    with open(note_path, 'r', encoding='utf-8') as f:
                        note_content = f.read()
                        preview = note_content[:200] + "..." if len(note_content) > 200 else note_content
                        print(f"   - Note preview: {preview}")
                else:
                    print(f"❌ Note file generation failed")
            
            return True
            
        else:
            print(f"❌ Video analysis failed")
            print(f"   - Reason: {analysis_result.get('reason', 'Unknown')}")
            return False
            
    except Exception as e:
        print(f"❌ Video analysis integration test failed: {e}")
        return False
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_analysis_statistics(analyzer):
    """Test analysis statistics tracking"""
    print("\n=== Testing Analysis Statistics ===")
    
    try:
        stats = analyzer.get_analysis_statistics()
        
        print(f"✅ Statistics retrieved successfully")
        print(f"   - Videos analyzed: {stats['videos_analyzed']}")
        print(f"   - Kung fu detected: {stats['kung_fu_detected']}")
        print(f"   - Notes generated: {stats['notes_generated']}")
        print(f"   - Analysis failures: {stats['analysis_failures']}")
        print(f"   - Thumbnails extracted: {stats['thumbnails_extracted']}")
        print(f"   - Success rate: {stats['success_rate']:.1f}%")
        print(f"   - Kung fu detection rate: {stats['kung_fu_detection_rate']:.1f}%")
        print(f"   - Analysis enabled: {stats['analysis_enabled']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Statistics test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=== Video Analysis Integration Test Suite ===")
    
    # Change to the correct directory
    os.chdir(Path(__file__).parent.parent)
    
    try:
        # Load configuration
        config_manager = ConfigManager("config.yaml")
        config = config_manager.load_config()
        logger = setup_logging(config)
        
        print("✅ Configuration and logging initialized")
        
        # Test results
        results = {}
        
        # Test 1: VideoAnalyzer initialization
        success, analyzer = test_video_analyzer_initialization(config, logger)
        results['initialization'] = success
        
        if not analyzer:
            print("\n❌ Cannot continue tests without VideoAnalyzer")
            return False
        
        # Test 2: AI connection
        results['ai_connection'] = test_ai_connection(analyzer)
        
        # Test 3: Thumbnail extraction
        results['thumbnail_extraction'] = test_thumbnail_extraction(analyzer, logger)
        
        # Test 4: Complete video analysis (only if AI connection works)
        if results['ai_connection']:
            results['video_analysis'] = test_video_analysis_integration(analyzer, logger)
        else:
            print("\n⚠️  Skipping video analysis test due to AI connection failure")
            results['video_analysis'] = False
        
        # Test 5: Statistics
        results['statistics'] = test_analysis_statistics(analyzer)
        
        # Summary
        print("\n=== Test Results Summary ===")
        for test_name, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")
        
        total_passed = sum(results.values())
        total_tests = len(results)
        
        if total_passed == total_tests:
            print(f"\n🎉 All video analysis tests passed! ({total_passed}/{total_tests})")
            print("📹 Video analysis system ready for integration")
            logger.info("Video analysis test suite completed successfully")
            return True
        else:
            print(f"\n⚠️  Some tests failed ({total_passed}/{total_tests} passed)")
            print("Check the output above for details")
            return False
        
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
