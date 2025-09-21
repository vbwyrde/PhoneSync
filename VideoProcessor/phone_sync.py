#!/usr/bin/env python3
"""
PhoneSync + VideoProcessor - Unified Python Solution
Combines file organization (PhoneSync) with video analysis (VideoProcessor)

Author: Generated for PhoneSync Project
Date: 2025-09-21
"""

import argparse
import logging
import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Import our modules (to be created)
from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logging
from modules.file_scanner import FileScanner
from modules.wudan_rules import WudanRulesEngine
from modules.deduplication import DeduplicationManager
from modules.file_organizer import FileOrganizer
from modules.video_analyzer import VideoAnalyzer
from modules.notes_generator import NotesGenerator

class PhoneSyncProcessor:
    """Main processor that orchestrates file organization and video analysis"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the processor with configuration"""
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load_config()
        
        # Initialize logging
        self.logger = setup_logging(self.config)
        
        # Initialize components
        self.file_scanner = FileScanner(self.config, self.logger)
        self.wudan_engine = WudanRulesEngine(self.config, self.logger)
        self.dedup_manager = DeduplicationManager(self.config, self.logger)
        self.file_organizer = FileOrganizer(self.config, self.logger)
        self.video_analyzer = VideoAnalyzer(self.config, self.logger)
        self.notes_generator = NotesGenerator(self.config, self.logger)
        
        self.stats = {
            'files_found': 0,
            'files_processed': 0,
            'files_skipped': 0,
            'videos_analyzed': 0,
            'errors': 0
        }
    
    def run(self, dry_run: bool = False, verbose: bool = False) -> bool:
        """
        Main execution method
        
        Args:
            dry_run: If True, don't actually copy files or create notes
            verbose: Enable verbose logging
            
        Returns:
            bool: True if successful, False if errors occurred
        """
        try:
            self.logger.info("=== PhoneSync + VideoProcessor Started ===")
            
            if dry_run:
                self.logger.warning("DRY RUN MODE - No files will be copied or modified")
            
            # Phase 1: Build deduplication cache if enabled
            if self.config['options']['enable_deduplication']:
                self.logger.info("Building deduplication cache...")
                self.dedup_manager.build_cache()
            
            # Phase 2: Scan source folders for files
            self.logger.info("Scanning source folders...")
            all_files = []
            for source_folder in self.config['source_folders']:
                files = self.file_scanner.scan_folder(source_folder)
                all_files.extend(files)
            
            self.stats['files_found'] = len(all_files)
            self.logger.info(f"Found {len(all_files)} files to process")
            
            # Phase 3: Process files (organize + analyze)
            videos_for_analysis = []
            
            for file_info in all_files:
                try:
                    # Organize file (copy to appropriate date folder)
                    success, target_path = self.file_organizer.organize_file(
                        file_info, dry_run=dry_run
                    )
                    
                    if success:
                        self.stats['files_processed'] += 1
                        
                        # If it's a video file, add to analysis queue
                        if self._is_video_file(file_info['path']):
                            videos_for_analysis.append({
                                'source_path': file_info['path'],
                                'target_path': target_path,
                                'file_date': file_info['date']
                            })
                    else:
                        self.stats['files_skipped'] += 1
                        
                except Exception as e:
                    self.logger.error(f"Error processing {file_info['path']}: {e}")
                    self.stats['errors'] += 1
            
            # Phase 4: Video Analysis (AI processing)
            if videos_for_analysis and not self.config['development']['skip_video_analysis']:
                self.logger.info(f"Analyzing {len(videos_for_analysis)} videos...")
                
                for video_info in videos_for_analysis:
                    try:
                        # Only analyze if video doesn't already exist in target
                        if self.video_analyzer.should_analyze_video(video_info['target_path']):
                            analysis_result = self.video_analyzer.analyze_video(
                                video_info['target_path'], dry_run=dry_run
                            )
                            
                            if analysis_result:
                                self.stats['videos_analyzed'] += 1
                                
                                # Generate notes file
                                self.notes_generator.add_video_note(
                                    video_info['file_date'],
                                    Path(video_info['target_path']).name,
                                    analysis_result['description'],
                                    dry_run=dry_run
                                )
                        
                    except Exception as e:
                        self.logger.error(f"Error analyzing video {video_info['target_path']}: {e}")
                        self.stats['errors'] += 1
            
            # Phase 5: Generate final notes files
            if not dry_run:
                self.notes_generator.write_all_notes()
            
            # Final statistics
            self._log_final_stats()
            
            self.logger.info("=== PhoneSync + VideoProcessor Completed ===")
            return self.stats['errors'] == 0
            
        except Exception as e:
            self.logger.error(f"Fatal error in main processing: {e}")
            return False
    
    def _is_video_file(self, file_path: str) -> bool:
        """Check if file is a video based on extension"""
        extension = Path(file_path).suffix.lower()
        return extension in self.config['file_extensions']['videos']
    
    def _log_final_stats(self):
        """Log final processing statistics"""
        self.logger.info("=== Processing Statistics ===")
        self.logger.info(f"Files found: {self.stats['files_found']}")
        self.logger.info(f"Files processed: {self.stats['files_processed']}")
        self.logger.info(f"Files skipped: {self.stats['files_skipped']}")
        self.logger.info(f"Videos analyzed: {self.stats['videos_analyzed']}")
        self.logger.info(f"Errors: {self.stats['errors']}")
        
        if self.stats['files_found'] > 0:
            success_rate = (self.stats['files_processed'] / self.stats['files_found']) * 100
            self.logger.info(f"Success rate: {success_rate:.1f}%")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="PhoneSync + VideoProcessor - Unified file organization and video analysis"
    )
    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Dry run mode - show what would be done without making changes'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    try:
        processor = PhoneSyncProcessor(args.config)
        success = processor.run(dry_run=args.dry_run, verbose=args.verbose)
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
