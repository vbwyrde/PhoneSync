#!/usr/bin/env python3
"""
Non-Kung Fu Video Cleanup Script

This script scans Wudan folders for videos marked as "NOT KUNG FU" in notes files,
and moves them to the regular My Videos folder structure. It provides a preview mode
to show what would be moved before actually performing the operations.

Usage:
    python cleanup_non_kungfu_videos.py --preview    # Show what would be moved
    python cleanup_non_kungfu_videos.py --execute    # Actually move the files
    python cleanup_non_kungfu_videos.py --help       # Show help
"""

import os
import sys
import argparse
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# Add the parent directory to the path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logging

class NonKungFuVideoCleanup:
    """Cleanup utility for moving non-kung fu videos from Wudan folders"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the cleanup utility

        Args:
            config_path: Path to configuration file
        """
        self.logger = logging.getLogger(__name__)

        # Load config directly with yaml
        import yaml
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Failed to load config from {config_path}: {str(e)}")

        # Get target paths from config based on environment
        environment = self.config.get('environment', 'DEVELOPMENT')

        if environment == 'PRODUCTION':
            prod_vars = self.config.get('PROD_VARS', {})
            target_paths = prod_vars.get('target_paths', {})
        else:
            dev_vars = self.config.get('DEV_VARS', {})
            target_paths = dev_vars.get('target_paths', {})

        self.wudan_path = target_paths.get('wudan', '')
        self.videos_path = target_paths.get('videos', '')

        if not self.wudan_path or not self.videos_path:
            raise ValueError(f"Wudan and videos paths must be configured for {environment} environment")

        self.logger.info(f"Initialized cleanup utility")
        self.logger.info(f"Wudan path: {self.wudan_path}")
        self.logger.info(f"Videos path: {self.videos_path}")
    
    def scan_for_non_kungfu_videos(self) -> List[Dict[str, Any]]:
        """
        Scan Wudan folders for videos marked as "NOT KUNG FU"
        
        Returns:
            List of dictionaries containing video and note file information
        """
        non_kungfu_videos = []
        
        if not os.path.exists(self.wudan_path):
            self.logger.warning(f"Wudan path does not exist: {self.wudan_path}")
            return non_kungfu_videos
        
        self.logger.info(f"Scanning Wudan folders for 'NOT KUNG FU' videos...")
        
        # Scan all date folders in Wudan directory
        for item in os.listdir(self.wudan_path):
            folder_path = os.path.join(self.wudan_path, item)
            
            if not os.path.isdir(folder_path):
                continue
            
            # Check if this looks like a date folder (YYYY_MM_DD format)
            if not self._is_date_folder(item):
                self.logger.debug(f"Skipping non-date folder: {item}")
                continue
            
            self.logger.debug(f"Scanning date folder: {item}")
            
            # Look for notes files in this folder
            notes_files = self._find_notes_files(folder_path)
            
            for notes_file in notes_files:
                # Check if notes file contains "NOT KUNG FU"
                not_kungfu_entries = self._parse_notes_file_for_non_kungfu(notes_file)
                
                for entry in not_kungfu_entries:
                    # Find corresponding video file
                    video_file = self._find_video_file(folder_path, entry['video_filename'])
                    
                    if video_file:
                        non_kungfu_videos.append({
                            'video_path': video_file,
                            'video_filename': os.path.basename(video_file),
                            'notes_file': notes_file,
                            'date_folder': item,
                            'source_folder': folder_path,
                            'target_folder': self._get_target_folder(item),
                            'notes_entry': entry
                        })
                        self.logger.debug(f"Found non-kung fu video: {os.path.basename(video_file)}")
                    else:
                        self.logger.warning(f"Video file not found for notes entry: {entry['video_filename']}")
        
        self.logger.info(f"Found {len(non_kungfu_videos)} non-kung fu videos to move")
        return non_kungfu_videos
    
    def _is_date_folder(self, folder_name: str) -> bool:
        """Check if folder name matches date pattern (YYYY_MM_DD)"""
        parts = folder_name.split('_')
        if len(parts) < 3:
            return False
        
        try:
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            
            # Basic validation
            return (1900 <= year <= 2100 and 
                    1 <= month <= 12 and 
                    1 <= day <= 31)
        except ValueError:
            return False
    
    def _find_notes_files(self, folder_path: str) -> List[str]:
        """Find all notes files in a folder"""
        notes_files = []
        
        for file in os.listdir(folder_path):
            if file.endswith('_Notes.txt') or file.endswith('_analysis.txt'):
                notes_files.append(os.path.join(folder_path, file))
        
        return notes_files
    
    def _parse_notes_file_for_non_kungfu(self, notes_file: str) -> List[Dict[str, Any]]:
        """
        Parse notes file for "NOT KUNG FU" entries
        
        Args:
            notes_file: Path to notes file
            
        Returns:
            List of entries marked as "NOT KUNG FU"
        """
        not_kungfu_entries = []
        
        try:
            with open(notes_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for "NOT KUNG FU" marker
            if "NOT KUNG FU" in content:
                # Extract video filename from notes file name or content
                notes_filename = os.path.basename(notes_file)
                
                if notes_filename.endswith('_Notes.txt'):
                    # Date-based notes file format: YYYYMMDD_Notes.txt
                    # Need to parse content for individual video entries
                    entries = self._parse_date_notes_content(content)
                    not_kungfu_entries.extend([e for e in entries if e.get('is_not_kungfu')])
                elif notes_filename.endswith('_analysis.txt'):
                    # Individual video analysis file: videoname_analysis.txt
                    video_filename = notes_filename.replace('_analysis.txt', '')
                    # Add common video extensions to try
                    for ext in ['.mp4', '.avi', '.mov', '.mkv']:
                        if os.path.exists(os.path.join(os.path.dirname(notes_file), video_filename + ext)):
                            video_filename += ext
                            break
                    
                    not_kungfu_entries.append({
                        'video_filename': video_filename,
                        'notes_content': content,
                        'is_not_kungfu': True
                    })
        
        except Exception as e:
            self.logger.error(f"Error parsing notes file {notes_file}: {str(e)}")
        
        return not_kungfu_entries
    
    def _parse_date_notes_content(self, content: str) -> List[Dict[str, Any]]:
        """Parse date-based notes file content for individual video entries"""
        entries = []
        
        # Split content by lines and look for video entries
        lines = content.split('\n')
        current_entry = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for video filename pattern (filename - description)
            if ' - ' in line:
                # This looks like a video entry
                parts = line.split(' - ', 1)
                if len(parts) == 2:
                    video_filename = parts[0].strip()
                    description = parts[1].strip()

                    # Skip lines that don't look like video entries (e.g., separator lines)
                    if video_filename and not video_filename.startswith('-'):
                        current_entry = {
                            'video_filename': video_filename,
                            'description': description,
                            'is_not_kungfu': 'NOT KUNG FU' in description
                        }
                        entries.append(current_entry)
        
        return entries
    
    def _find_video_file(self, folder_path: str, video_filename: str) -> Optional[str]:
        """Find video file in folder, handling various filename formats"""
        # Try exact match first
        exact_path = os.path.join(folder_path, video_filename)
        if os.path.exists(exact_path):
            return exact_path
        
        # Try without extension and add common extensions
        base_name = os.path.splitext(video_filename)[0]
        for ext in ['.mp4', '.avi', '.mov', '.mkv']:
            test_path = os.path.join(folder_path, base_name + ext)
            if os.path.exists(test_path):
                return test_path
        
        # Try case-insensitive search
        for file in os.listdir(folder_path):
            if file.lower() == video_filename.lower():
                return os.path.join(folder_path, file)
        
        return None
    
    def _get_target_folder(self, date_folder_name: str) -> str:
        """Get target folder path in regular videos directory"""
        return os.path.join(self.videos_path, date_folder_name)

    def preview_cleanup(self, non_kungfu_videos: List[Dict[str, Any]]) -> None:
        """
        Display preview of what would be moved

        Args:
            non_kungfu_videos: List of non-kung fu videos to move
        """
        if not non_kungfu_videos:
            print("✅ No non-kung fu videos found in Wudan folders")
            return

        print(f"\n📋 Cleanup Preview - {len(non_kungfu_videos)} videos to move")
        print("=" * 80)
        print("Format: video_file --> target_folder (action)")
        print("-" * 80)

        for video_info in non_kungfu_videos:
            video_name = video_info['video_filename']
            source_folder = video_info['date_folder']
            target_folder = video_info['target_folder']

            # Check if target folder exists
            folder_exists = os.path.exists(target_folder)
            folder_status = "Existing folder" if folder_exists else "New folder will be created"

            print(f"📁 {video_name}")
            print(f"   From: Wudan/{source_folder}")
            print(f"   To:   My Videos/{os.path.basename(target_folder)} ({folder_status})")

            # Show notes entry info
            notes_entry = video_info.get('notes_entry', {})
            if notes_entry.get('description'):
                print(f"   Note: {notes_entry['description'][:100]}...")

            print()

        print("-" * 80)
        print(f"📊 Summary: {len(non_kungfu_videos)} videos will be moved from Wudan to regular video folders")
        print("💡 Use --execute to perform the actual move operations")

    def execute_cleanup(self, non_kungfu_videos: List[Dict[str, Any]], dry_run: bool = False) -> Dict[str, Any]:
        """
        Execute the cleanup operations

        Args:
            non_kungfu_videos: List of non-kung fu videos to move
            dry_run: If True, simulate operations without making changes

        Returns:
            Results dictionary with statistics
        """
        results = {
            'videos_moved': 0,
            'folders_created': 0,
            'notes_updated': 0,
            'errors': [],
            'moved_videos': []
        }

        if not non_kungfu_videos:
            self.logger.info("No non-kung fu videos to move")
            return results

        mode_str = "[DRY RUN] " if dry_run else ""
        self.logger.info(f"{mode_str}Starting cleanup of {len(non_kungfu_videos)} non-kung fu videos")

        for video_info in non_kungfu_videos:
            try:
                success = self._move_single_video(video_info, dry_run)
                if success:
                    results['videos_moved'] += 1
                    results['moved_videos'].append(video_info['video_filename'])

                    # Check if we created a new folder
                    if not os.path.exists(video_info['target_folder']) and not dry_run:
                        results['folders_created'] += 1

            except Exception as e:
                error_msg = f"Error moving {video_info['video_filename']}: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)

        # Generate summary report
        self._generate_cleanup_report(results, dry_run)

        return results

    def _move_single_video(self, video_info: Dict[str, Any], dry_run: bool = False) -> bool:
        """
        Move a single video from Wudan folder to regular videos folder

        Args:
            video_info: Video information dictionary
            dry_run: If True, simulate the operation

        Returns:
            True if successful, False otherwise
        """
        source_path = video_info['video_path']
        target_folder = video_info['target_folder']
        video_filename = video_info['video_filename']
        target_path = os.path.join(target_folder, video_filename)

        mode_str = "[DRY RUN] " if dry_run else ""
        self.logger.info(f"{mode_str}Moving {video_filename} from Wudan to regular videos")

        if not dry_run:
            # Create target folder if it doesn't exist
            os.makedirs(target_folder, exist_ok=True)

            # Move the video file
            shutil.move(source_path, target_path)
            self.logger.info(f"Moved video: {source_path} -> {target_path}")

        # Update notes file
        self._update_notes_file(video_info, dry_run)

        return True

    def _update_notes_file(self, video_info: Dict[str, Any], dry_run: bool = False) -> None:
        """
        Update or remove notes file entries for moved videos

        Args:
            video_info: Video information dictionary
            dry_run: If True, simulate the operation
        """
        notes_file = video_info['notes_file']
        video_filename = video_info['video_filename']

        mode_str = "[DRY RUN] " if dry_run else ""

        try:
            if not os.path.exists(notes_file):
                return

            with open(notes_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Remove or update the "NOT KUNG FU" entry
            updated_content = self._remove_not_kungfu_entry(content, video_filename)

            if updated_content != content:
                self.logger.info(f"{mode_str}Updating notes file: {notes_file}")

                if not dry_run:
                    # Check if notes file would be empty after removal
                    if updated_content.strip():
                        # Update the file
                        with open(notes_file, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                    else:
                        # Remove empty notes file
                        os.remove(notes_file)
                        self.logger.info(f"Removed empty notes file: {notes_file}")

        except Exception as e:
            self.logger.error(f"Error updating notes file {notes_file}: {str(e)}")

    def _remove_not_kungfu_entry(self, content: str, video_filename: str) -> str:
        """
        Remove "NOT KUNG FU" entry from notes content

        Args:
            content: Original notes content
            video_filename: Video filename to remove

        Returns:
            Updated content with entry removed
        """
        lines = content.split('\n')
        updated_lines = []
        skip_next_lines = 0

        for line in lines:
            if skip_next_lines > 0:
                skip_next_lines -= 1
                continue

            # Check if this line contains the video filename and "NOT KUNG FU"
            if (video_filename in line and "NOT KUNG FU" in line) or \
               (video_filename.replace('.mp4', '') in line and "NOT KUNG FU" in line):
                # Skip this line and potentially following description lines
                continue

            updated_lines.append(line)

        return '\n'.join(updated_lines)

    def _generate_cleanup_report(self, results: Dict[str, Any], dry_run: bool = False) -> None:
        """Generate and display cleanup report"""
        mode_str = "[DRY RUN] " if dry_run else ""

        print(f"\n📊 Cleanup Report {mode_str}")
        print("=" * 50)
        print(f"Videos moved: {results['videos_moved']}")
        print(f"Folders created: {results['folders_created']}")
        print(f"Notes updated: {results['notes_updated']}")
        print(f"Errors: {len(results['errors'])}")

        if results['moved_videos']:
            print(f"\n📁 Moved videos:")
            for video in results['moved_videos']:
                print(f"   - {video}")

        if results['errors']:
            print(f"\n❌ Errors:")
            for error in results['errors']:
                print(f"   - {error}")

        if not dry_run and results['videos_moved'] > 0:
            print(f"\n✅ Cleanup completed successfully!")
        elif dry_run:
            print(f"\n💡 This was a dry run. Use --execute to perform actual operations.")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Cleanup non-kung fu videos from Wudan folders",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python cleanup_non_kungfu_videos.py --preview
    python cleanup_non_kungfu_videos.py --execute
    python cleanup_non_kungfu_videos.py --execute --dry-run
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--preview', '-p',
        action='store_true',
        help='Preview what videos would be moved (no changes made)'
    )
    group.add_argument(
        '--execute', '-e',
        action='store_true',
        help='Execute the cleanup operations'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate operations without making actual changes (use with --execute)'
    )

    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("🧹 Non-Kung Fu Video Cleanup Utility")
    print("=" * 50)

    try:
        # Initialize cleanup utility
        print("🔧 Initializing cleanup utility...")
        cleanup = NonKungFuVideoCleanup(args.config)
        print("✅ Cleanup utility initialized")

        # Scan for non-kung fu videos
        print("🔍 Scanning Wudan folders for 'NOT KUNG FU' videos...")
        print(f"   Wudan path: {cleanup.wudan_path}")
        print(f"   Videos path: {cleanup.videos_path}")
        non_kungfu_videos = cleanup.scan_for_non_kungfu_videos()

        if args.preview:
            # Show preview
            cleanup.preview_cleanup(non_kungfu_videos)

        elif args.execute:
            # Execute cleanup
            if args.dry_run:
                print("🧪 Dry run mode - no actual changes will be made")

            results = cleanup.execute_cleanup(non_kungfu_videos, dry_run=args.dry_run)

            if results['errors']:
                return 1

        return 0

    except KeyboardInterrupt:
        print("\n⏹️  Operation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
