#!/usr/bin/env python3
"""
AI Notes Generator - Standalone Script
Generate AI analysis notes for existing video files in Wudan folders

This script focuses on Wudan folders since regular videos get notes during main processing.
It can be run independently to:
- Analyze existing videos in Wudan folders (My Videos/Wudan/*)
- Generate Notes_YYYYMMDD.txt files for each Wudan date folder
- Skip videos that already have notes (unless --force is used)
- Process specific date ranges or folders

Usage:
    python Scripts/generate_ai_notes.py                            # Analyze all Wudan videos
    python Scripts/generate_ai_notes.py --dry-run                  # Preview what would be analyzed
    python Scripts/generate_ai_notes.py --force                    # Regenerate existing notes
    python Scripts/generate_ai_notes.py --date 2024-04-12          # Analyze specific date
    python Scripts/generate_ai_notes.py --folder "2024_04_12_Sat"  # Analyze specific folder
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
import re
from typing import Dict, Any, List, Optional

# Add modules directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logging
from modules.video_analyzer import VideoAnalyzer
from modules.file_scanner import FileScanner

class AINotesGenerator:
    """Standalone AI notes generator for existing video files"""
    
    def __init__(self, config_path: str):
        """Initialize the notes generator"""
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load_config()
        self.logger = setup_logging(self.config)
        
        # Initialize video analyzer
        self.video_analyzer = VideoAnalyzer(self.config, self.logger)
        
        # Get target paths
        self.target_paths = self.config.get('target_paths', {})
        
        # Statistics
        self.stats = {
            'folders_scanned': 0,
            'videos_found': 0,
            'videos_analyzed': 0,
            'kung_fu_detected': 0,
            'notes_files_created': 0,
            'notes_files_skipped': 0,
            'errors': 0
        }
        
        self.logger.info("AI Notes Generator initialized")
    
    def scan_target_folders(self, specific_folder: Optional[str] = None,
                          specific_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Scan target folders for video files that need analysis
        Focus on Wudan folders since regular videos get notes during main processing

        Args:
            specific_folder: Analyze only this folder name
            specific_date: Analyze only folders matching this date (YYYY-MM-DD)

        Returns:
            List of folder information with videos to analyze
        """
        folders_to_analyze = []

        # Focus specifically on Wudan target path
        wudan_path = self.target_paths.get('wudan')
        if not wudan_path:
            self.logger.warning("No 'wudan' target path found in configuration")
            return folders_to_analyze

        if not os.path.exists(wudan_path):
            self.logger.warning(f"Wudan target path does not exist: {wudan_path}")
            return folders_to_analyze

        self.logger.info(f"Scanning Wudan folders: {wudan_path}")

        # Scan for date folders in Wudan directory
        try:
            for item in os.listdir(wudan_path):
                folder_path = os.path.join(wudan_path, item)

                if not os.path.isdir(folder_path):
                    continue

                # Check if this looks like a date folder (YYYY_MM_DD_DDD format for Wudan)
                if not self._is_wudan_date_folder(item):
                    continue

                # Apply filters
                if specific_folder and item != specific_folder:
                    continue

                if specific_date:
                    folder_date = self._extract_date_from_folder_name(item)
                    if folder_date:
                        formatted_date = folder_date.strftime('%Y-%m-%d')
                        self.logger.info(f"Checking folder {item}: extracted date {formatted_date}, looking for {specific_date}")
                        if formatted_date != specific_date:
                            continue
                    else:
                        self.logger.warning(f"Could not extract date from folder: {item}")
                        continue

                # Find videos in this folder
                videos = self._find_videos_in_folder(folder_path)

                if videos:
                    folders_to_analyze.append({
                        'folder_name': item,
                        'folder_path': folder_path,
                        'target_name': 'wudan',
                        'videos': videos,
                        'date': self._extract_date_from_folder_name(item)
                    })

                    self.stats['folders_scanned'] += 1
                    self.stats['videos_found'] += len(videos)

        except Exception as e:
            self.logger.error(f"Error scanning Wudan directory {wudan_path}: {e}")

        return folders_to_analyze
    
    def _is_date_folder(self, folder_name: str) -> bool:
        """Check if folder name matches date pattern"""
        # Match YYYY_MM_DD or YYYY_MM_DD_DDD patterns
        pattern = r'^\d{4}_\d{2}_\d{2}(_\w+)?$'
        return bool(re.match(pattern, folder_name))

    def _is_wudan_date_folder(self, folder_name: str) -> bool:
        """Check if folder name matches Wudan date pattern (YYYY_MM_DD_DDD or YYYY_MM_DD_DDD_Additional)"""
        # Match YYYY_MM_DD_DDD pattern with optional additional text for Wudan folders
        pattern = r'^\d{4}_\d{2}_\d{2}_\w{3}(_.*)?$'
        return bool(re.match(pattern, folder_name))
    
    def _extract_date_from_folder_name(self, folder_name: str) -> Optional[datetime]:
        """Extract date from folder name"""
        try:
            # Extract YYYY_MM_DD part
            date_part = folder_name.split('_')[:3]
            if len(date_part) == 3:
                year, month, day = date_part
                return datetime(int(year), int(month), int(day))
        except (ValueError, IndexError):
            pass
        return None
    
    def _find_videos_in_folder(self, folder_path: str) -> List[Dict[str, Any]]:
        """Find video files in a folder"""
        videos = []
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
        
        try:
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                
                if os.path.isfile(item_path):
                    file_ext = Path(item).suffix.lower()
                    if file_ext in video_extensions:
                        videos.append({
                            'name': item,
                            'path': item_path,
                            'size': os.path.getsize(item_path)
                        })
        except Exception as e:
            self.logger.error(f"Error scanning folder {folder_path}: {e}")
        
        return videos
    
    def _notes_file_exists(self, folder_path: str, folder_date: datetime) -> bool:
        """Check if notes file already exists for this folder"""
        date_str = folder_date.strftime("%Y%m%d")
        notes_filename = f"Notes_{date_str}.txt"
        notes_path = os.path.join(folder_path, notes_filename)
        return os.path.exists(notes_path)
    
    def generate_notes_for_folders(self, folders: List[Dict[str, Any]], 
                                 dry_run: bool = False, force: bool = False) -> Dict[str, Any]:
        """
        Generate AI notes for video folders
        
        Args:
            folders: List of folder information
            dry_run: Preview mode - don't actually create files
            force: Regenerate existing notes files
            
        Returns:
            Processing results
        """
        results = {
            'success': True,
            'folders_processed': 0,
            'notes_created': 0,
            'errors': []
        }
        
        for folder_info in folders:
            try:
                folder_path = folder_info['folder_path']
                folder_name = folder_info['folder_name']
                videos = folder_info['videos']
                folder_date = folder_info['date']
                
                if not folder_date:
                    self.logger.warning(f"Could not extract date from folder: {folder_name}")
                    continue
                
                # Check if notes file already exists
                if not force and self._notes_file_exists(folder_path, folder_date):
                    self.logger.info(f"Notes file already exists for {folder_name}, skipping (use --force to regenerate)")
                    self.stats['notes_files_skipped'] += 1
                    continue
                
                if dry_run:
                    self.logger.info(f"[DRY RUN] Would analyze {len(videos)} videos in {folder_name}")
                    continue
                
                self.logger.info(f"Analyzing {len(videos)} videos in {folder_name}")
                
                # Analyze videos in this folder
                video_analyses = []
                for video in videos:
                    try:
                        analysis_result = self.video_analyzer.analyze_video(video['path'], dry_run=False)
                        
                        if analysis_result.get('analyzed', False):
                            video_analyses.append({
                                'filename': video['name'],
                                'analysis_result': analysis_result
                            })
                            
                            self.stats['videos_analyzed'] += 1
                            
                            if analysis_result.get('is_kung_fu', False):
                                self.stats['kung_fu_detected'] += 1
                        else:
                            self.logger.warning(f"Failed to analyze {video['name']}: {analysis_result.get('reason', 'Unknown error')}")
                            
                    except Exception as e:
                        self.logger.error(f"Error analyzing video {video['name']}: {e}")
                        self.stats['errors'] += 1
                
                # Generate notes file
                if video_analyses:
                    self._create_notes_file(folder_path, folder_date, video_analyses)
                    self.stats['notes_files_created'] += 1
                    results['notes_created'] += 1
                
                results['folders_processed'] += 1
                
            except Exception as e:
                error_msg = f"Error processing folder {folder_info.get('folder_name', 'unknown')}: {e}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
                self.stats['errors'] += 1
                results['success'] = False
        
        return results
    
    def _create_notes_file(self, folder_path: str, folder_date: datetime, 
                          video_analyses: List[Dict[str, Any]]):
        """Create notes file for a folder"""
        date_str = folder_date.strftime("%Y%m%d")
        notes_filename = f"Notes_{date_str}.txt"
        notes_path = os.path.join(folder_path, notes_filename)
        
        # Create notes content
        notes_content = f"Video Analysis Notes - {folder_date.strftime('%Y_%m_%d')}\n"
        notes_content += "=" * 50 + "\n\n"
        
        for video_analysis in video_analyses:
            filename = video_analysis['filename']
            analysis = video_analysis['analysis_result']
            
            # Format: filename - description
            description = analysis.get('description', 'No description available')
            # Keep only ASCII letters, numbers, apostrophes, and spaces
            cleaned_description = re.sub(r"[^a-zA-Z0-9' ]", '', description)
            # format: filename - description (with padding)
            padding_length = 28 - len(filename)  # Calculate spaces needed
            padding = ' ' * max(0, padding_length)  # Ensure non-negative padding
    
            if analysis.get('is_kung_fu', False):
                notes_content += f"{filename}{padding}- {cleaned_description}\n"
            else:
                notes_content += f"{filename}{padding}- NOT KUNG FU: {cleaned_description}\n"
        
        # Write notes file
        with open(notes_path, 'w', encoding='utf-8') as f:
            f.write(notes_content)
        
        self.logger.info(f"Created notes file: {notes_path}")
    
    def print_summary(self):
        """Print processing summary"""
        print("\n" + "="*60)
        print("AI NOTES GENERATION SUMMARY")
        print("="*60)
        print(f"Folders scanned: {self.stats['folders_scanned']}")
        print(f"Videos found: {self.stats['videos_found']}")
        print(f"Videos analyzed: {self.stats['videos_analyzed']}")
        print(f"Kung fu detected: {self.stats['kung_fu_detected']}")
        print(f"Notes files created: {self.stats['notes_files_created']}")
        print(f"Notes files skipped: {self.stats['notes_files_skipped']}")
        print(f"Errors: {self.stats['errors']}")
        print("="*60)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate AI analysis notes for existing video files"
    )

    print("AI Notes Generator - Standalone Script")
    print("Current working directory:", os.getcwd())
    
    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Preview mode - show what would be analyzed without making changes'
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Regenerate existing notes files'
    )
    parser.add_argument(
        '--date',
        help='Analyze only folders matching this date (YYYY-MM-DD format)'
    )
    parser.add_argument(
        '--folder',
        help='Analyze only this specific folder name'
    )
    
    args = parser.parse_args()
    
    try:
        print("AI Notes Generator - Standalone Script")
        print("=" * 50)
        
        # Initialize generator
        generator = AINotesGenerator(args.config)
        
        # Test AI connection
        print("Testing AI connection...")
        ai_test = generator.video_analyzer.test_ai_connection()
        if not ai_test.get('success', False):
            print(f"AI connection failed: {ai_test.get('reason', 'Unknown error')}")
            print("Make sure LM Studio is running and accessible")
            return 1
        else:
            print("AI connection successful")
        
        # Scan for folders to analyze
        print(f"\nScanning target folders...")
        folders = generator.scan_target_folders(
            specific_folder=args.folder,
            specific_date=args.date
        )
        
        if not folders:
            print("No folders found to analyze")
            return 0
        
        print(f"Found {len(folders)} folders with {sum(len(f['videos']) for f in folders)} videos")
        
        # Generate notes
        if args.dry_run:
            print("\n DRY RUN MODE - No files will be created")
        
        results = generator.generate_notes_for_folders(
            folders, 
            dry_run=args.dry_run, 
            force=args.force
        )
        
        # Print summary
        generator.print_summary()
        
        if results['errors']:
            print(f"\n  {len(results['errors'])} errors occurred:")
            for error in results['errors']:
                print(f"   - {error}")
        
        return 0 if results['success'] else 1
        
    except KeyboardInterrupt:
        print("\n\n[WARNING] Processing interrupted by user")
        return 130
    
    except Exception as e:
        print(f"\n[ERROR] Application error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
