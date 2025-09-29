#!/usr/bin/env python3
"""
Script to analyze existing videos that don't have notes files yet.
This is useful for testing the updated prompt and generating notes for existing videos.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager
from modules.video_analyzer import VideoAnalyzer
from modules.notes_generator import NotesGenerator
import logging

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    return logging.getLogger(__name__)

def find_videos_without_notes(videos_base_path: str) -> list:
    """Find all videos that don't have corresponding notes files"""
    videos_without_notes = []
    
    for video_file in Path(videos_base_path).rglob("*.mp4"):
        # Extract date from filename or directory
        date_str = None
        
        # Try to extract date from filename (YYYYMMDD format)
        filename = video_file.stem
        if len(filename) >= 8 and filename[:8].isdigit():
            date_str = filename[:8]
        
        if date_str:
            # Check if notes file exists
            notes_filename = f"{date_str}_Notes.txt"
            notes_path = video_file.parent / notes_filename
            
            if not notes_path.exists():
                videos_without_notes.append({
                    'video_path': str(video_file),
                    'date_str': date_str,
                    'directory': str(video_file.parent)
                })
    
    return videos_without_notes

def main():
    logger = setup_logging()
    
    # Load configuration
    config_manager = ConfigManager('config.yaml')
    config = config_manager.load_config()
    
    # Initialize analyzers
    video_analyzer = VideoAnalyzer(config, logger)
    notes_generator = NotesGenerator(config, logger)
    
    # Find videos without notes
    videos_base_path = config['target_paths']['videos']
    videos_without_notes = find_videos_without_notes(videos_base_path)
    
    logger.info(f"Found {len(videos_without_notes)} videos without notes files")
    
    if not videos_without_notes:
        logger.info("All videos already have notes files!")
        return
    
    # Analyze all videos without notes
    test_videos = videos_without_notes
    logger.info(f"Analyzing all {len(test_videos)} videos without notes...")
    
    for i, video_info in enumerate(test_videos, 1):
        logger.info(f"[{i}/{len(test_videos)}] Analyzing: {Path(video_info['video_path']).name}")
        
        try:
            # Analyze the video
            analysis_result = video_analyzer.analyze_video(video_info['video_path'])
            
            if analysis_result:
                logger.info(f"Analysis result keys: {list(analysis_result.keys())}")

                # Check if we have the expected keys
                if 'description' in analysis_result:
                    # Parse date for notes generation
                    date_str = video_info['date_str']
                    file_date = datetime.strptime(date_str, '%Y%m%d')

                    # Generate notes
                    notes_generator.add_video_note(
                        file_date,
                        Path(video_info['video_path']).name,
                        analysis_result['description'],
                        video_info['directory']
                    )

                    logger.info(f"✅ Analysis complete: {analysis_result['description'][:50]}...")
                else:
                    logger.warning(f"❌ No description in analysis result: {analysis_result}")
            else:
                logger.warning(f"❌ Analysis failed for {video_info['video_path']}")
                
        except Exception as e:
            logger.error(f"❌ Error analyzing {video_info['video_path']}: {e}")
    
    # Write all notes files
    notes_generator.write_all_notes()
    logger.info("✅ Notes generation complete!")

if __name__ == "__main__":
    main()
