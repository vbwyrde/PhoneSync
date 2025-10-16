#!/usr/bin/env python3
"""
Test AI Analysis Only - No File Movement

This script tests the AI video analysis functionality on existing files
without moving or copying them. Perfect for testing the AI analysis and
notes generation components.
"""

import os
import sys
import yaml
import logging
import tempfile
from pathlib import Path

# Add the VideoProcessor directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.config_manager import ConfigManager
from modules.video_analyzer import VideoAnalyzer
from modules.notes_generator import NotesGenerator

def main():
    """Test AI analysis on existing video files"""
    print("AI ANALYSIS TESTING - Real Video Files")
    print("=" * 50)
    
    try:
        # Initialize configuration
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml')
        config_manager = ConfigManager(config_path)
        
        # Load config and temporarily switch to PRODUCTION environment
        print("Loading PRODUCTION configuration...")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            raw_config = yaml.safe_load(f)
        
        # Temporarily modify environment to PRODUCTION
        raw_config['environment'] = 'PRODUCTION'
        
        # Save temporarily modified config
        temp_config_path = config_path + '.temp_ai_test'
        with open(temp_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(raw_config, f, default_flow_style=False)
        
        # Load resolved config
        temp_config_manager = ConfigManager(temp_config_path)
        config = temp_config_manager.load_config()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        logger = logging.getLogger(__name__)
        
        # Initialize AI components
        print("Initializing AI components...")
        video_analyzer = VideoAnalyzer(config, logger)
        notes_generator = NotesGenerator(config, logger)
        
        # Test AI connection
        print("Testing AI connection...")
        ai_test_result = video_analyzer.test_ai_connection()
        if ai_test_result.get('success', False):
            print(f"   AI CONNECTION: SUCCESS")
            print(f"   Response: {ai_test_result.get('response', 'Connected')[:100]}...")
        else:
            print(f"   AI CONNECTION: FAILED - {ai_test_result.get('error', 'Unknown error')}")
            print("   Cannot proceed with AI testing")
            return
        
        # Find some test video files
        print("\nFinding test video files...")
        source_folders = config.get('source_folders', [])
        test_videos = []
        
        # Look for MP4 files in the first source folder
        if source_folders:
            camera_folder = source_folders[0]  # Camera folder
            print(f"Scanning: {camera_folder}")
            
            if os.path.exists(camera_folder):
                for file in os.listdir(camera_folder):
                    if file.lower().endswith('.mp4'):
                        file_path = os.path.join(camera_folder, file)
                        test_videos.append(file_path)
                        
                        # Limit to 3 files for testing
                        if len(test_videos) >= 3:
                            break
        
        if not test_videos:
            print("   No MP4 files found for testing")
            return
            
        print(f"   Found {len(test_videos)} test videos")
        
        # Test AI analysis on each video
        print(f"\nTesting AI analysis on {len(test_videos)} videos...")
        print("=" * 50)
        
        for i, video_path in enumerate(test_videos, 1):
            filename = os.path.basename(video_path)
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            
            print(f"\nVideo {i}/{len(test_videos)}: {filename}")
            print(f"   Size: {file_size:.1f} MB")
            print(f"   Path: {video_path}")
            
            try:
                # Perform AI analysis
                print("   Performing AI analysis...")
                analysis_result = video_analyzer.analyze_video(video_path, dry_run=False)
                
                if analysis_result.get('analyzed', False):
                    print("   ✅ AI ANALYSIS SUCCESS:")
                    print(f"      Kung Fu Detected: {analysis_result.get('is_kung_fu', 'Unknown')}")
                    print(f"      Confidence: {analysis_result.get('confidence', 'Unknown')}")
                    print(f"      Description: {analysis_result.get('description', 'No description')}")
                    
                    # Test note file generation (to temp directory)
                    print("   Testing note file generation...")
                    with tempfile.TemporaryDirectory() as temp_dir:
                        note_file_path = video_analyzer.generate_note_file(
                            video_path, 
                            analysis_result, 
                            temp_dir
                        )
                        
                        if note_file_path and os.path.exists(note_file_path):
                            print(f"   ✅ NOTES FILE: Generated successfully")
                            
                            # Read and display note content
                            with open(note_file_path, 'r', encoding='utf-8') as f:
                                note_content = f.read()
                            print(f"   Note content preview:")
                            for line in note_content.split('\n')[:5]:  # First 5 lines
                                if line.strip():
                                    print(f"      {line}")
                        else:
                            print(f"   ❌ NOTES FILE: Generation failed")
                else:
                    print("   ❌ AI ANALYSIS FAILED:")
                    print(f"      Reason: {analysis_result.get('reason', 'Unknown error')}")
                    print(f"      Error Type: {analysis_result.get('error_type', 'Unknown')}")
                    
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                logger.error(f"AI analysis error for {filename}: {e}")
        
        print(f"\n" + "=" * 50)
        print("AI ANALYSIS TESTING COMPLETE!")
        print("=" * 50)
        
    except Exception as e:
        print(f"ERROR: {e}")
        logger.error(f"Test execution error: {e}")
        
    finally:
        # Clean up temp config file
        if 'temp_config_path' in locals() and os.path.exists(temp_config_path):
            os.remove(temp_config_path)
            print("Cleaned up temporary config file")

if __name__ == "__main__":
    main()
