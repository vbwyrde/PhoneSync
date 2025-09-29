#!/usr/bin/env python3
"""
Test Environment Setup Script
Creates controlled test conditions for validating the PhoneSync + VideoProcessor system
"""

import os
import sys
import shutil
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any
import yaml
import random
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

class TestEnvironmentSetup:
    """Setup and manage test environment for PhoneSync + VideoProcessor"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize test environment setup"""
        self.logger = logging.getLogger(__name__)
        
        # Load config
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # Always use development/test paths for test environment setup
        dev_vars = self.config.get('DEV_VARS', {})
        target_paths = dev_vars.get('target_paths', {})
        self.source_folders = dev_vars.get('source_folders', [])

        self.videos_path = target_paths.get('videos', '')
        self.wudan_path = target_paths.get('wudan', '')
        self.pictures_path = target_paths.get('pictures', '')
        
        if not all([self.source_folders, self.videos_path, self.wudan_path]):
            raise ValueError("Development paths must be configured in config.yaml")
        
        self.logger.info(f"Test environment paths:")
        self.logger.info(f"  Source: {self.source_folders}")
        self.logger.info(f"  Videos: {self.videos_path}")
        self.logger.info(f"  Wudan: {self.wudan_path}")
        self.logger.info(f"  Pictures: {self.pictures_path}")
    
    def reset_processing_state(self) -> None:
        """Reset processing state to force full reprocessing"""
        state_file = "VideoProcessor/state/processing_state.json"
        if os.path.exists(state_file):
            os.remove(state_file)
            self.logger.info("✅ Processing state reset")
        else:
            self.logger.info("ℹ️  No processing state to reset")
    
    def create_test_conditions(self, scenario: str = "mixed") -> Dict[str, Any]:
        """
        Create specific test conditions by manipulating existing files

        Args:
            scenario: Test scenario to create
                - "mixed": Mix of processed and unprocessed videos
                - "clean": Remove all notes files to force reprocessing
                - "partial": Remove some notes files randomly
                - "wudan_only": Focus on Wudan folder testing
                - "mock_not_kungfu": Create mock "NOT KUNG FU" notes files for testing cleanup

        Returns:
            Dictionary with test condition details
        """
        results = {
            'scenario': scenario,
            'notes_removed': [],
            'videos_found': [],
            'wudan_videos': [],
            'regular_videos': []
        }
        
        self.logger.info(f"🧪 Creating test scenario: {scenario}")
        
        # Scan for existing videos and notes
        videos_found = self._scan_existing_videos()
        results['videos_found'] = videos_found
        
        if scenario == "clean":
            # Remove all notes files to force complete reprocessing
            removed_notes = self._remove_all_notes_files()
            results['notes_removed'] = removed_notes
            
        elif scenario == "partial":
            # Remove random selection of notes files
            removed_notes = self._remove_random_notes_files(percentage=0.3)
            results['notes_removed'] = removed_notes
            
        elif scenario == "wudan_only":
            # Focus on Wudan folder - remove notes from Wudan videos only
            removed_notes = self._remove_wudan_notes_files()
            results['notes_removed'] = removed_notes
            
        elif scenario == "mixed":
            # Create mixed conditions - some processed, some not
            removed_notes = self._create_mixed_conditions()
            results['notes_removed'] = removed_notes

        elif scenario == "mock_not_kungfu":
            # Create mock "NOT KUNG FU" notes files for testing cleanup functionality
            created_notes = self._create_mock_not_kungfu_notes()
            results['notes_created'] = created_notes
            results['notes_removed'] = []  # No notes removed in this scenario
        
        # Categorize videos by location
        results['wudan_videos'] = self._get_wudan_videos()
        results['regular_videos'] = self._get_regular_videos()
        
        return results
    
    def _scan_existing_videos(self) -> List[str]:
        """Scan for existing video files in target directories"""
        videos = []
        
        for root_path in [self.videos_path, self.wudan_path]:
            if os.path.exists(root_path):
                for root, dirs, files in os.walk(root_path):
                    for file in files:
                        if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                            videos.append(os.path.join(root, file))
        
        self.logger.info(f"Found {len(videos)} existing video files")
        return videos
    
    def _remove_all_notes_files(self) -> List[str]:
        """Remove all notes files to force complete reprocessing"""
        removed = []
        
        for root_path in [self.videos_path, self.wudan_path]:
            if os.path.exists(root_path):
                for root, dirs, files in os.walk(root_path):
                    for file in files:
                        if file.endswith('_Notes.txt') or file.endswith('_analysis.txt'):
                            file_path = os.path.join(root, file)
                            os.remove(file_path)
                            removed.append(file_path)
        
        self.logger.info(f"Removed {len(removed)} notes files")
        return removed
    
    def _remove_random_notes_files(self, percentage: float = 0.3) -> List[str]:
        """Remove random selection of notes files"""
        all_notes = []
        
        # Find all notes files
        for root_path in [self.videos_path, self.wudan_path]:
            if os.path.exists(root_path):
                for root, dirs, files in os.walk(root_path):
                    for file in files:
                        if file.endswith('_Notes.txt') or file.endswith('_analysis.txt'):
                            all_notes.append(os.path.join(root, file))
        
        # Remove random selection
        num_to_remove = int(len(all_notes) * percentage)
        to_remove = random.sample(all_notes, min(num_to_remove, len(all_notes)))
        
        removed = []
        for file_path in to_remove:
            os.remove(file_path)
            removed.append(file_path)
        
        self.logger.info(f"Removed {len(removed)} of {len(all_notes)} notes files ({percentage*100:.1f}%)")
        return removed
    
    def _remove_wudan_notes_files(self) -> List[str]:
        """Remove notes files from Wudan folder only"""
        removed = []
        
        if os.path.exists(self.wudan_path):
            for root, dirs, files in os.walk(self.wudan_path):
                for file in files:
                    if file.endswith('_Notes.txt') or file.endswith('_analysis.txt'):
                        file_path = os.path.join(root, file)
                        os.remove(file_path)
                        removed.append(file_path)
        
        self.logger.info(f"Removed {len(removed)} notes files from Wudan folder")
        return removed
    
    def _create_mixed_conditions(self) -> List[str]:
        """Create mixed test conditions"""
        # Remove 40% of regular video notes, 60% of Wudan notes
        removed = []
        
        # Regular videos - remove 40%
        regular_notes = []
        if os.path.exists(self.videos_path):
            for root, dirs, files in os.walk(self.videos_path):
                # Skip Wudan subfolder
                if 'Wudan' in root:
                    continue
                for file in files:
                    if file.endswith('_Notes.txt') or file.endswith('_analysis.txt'):
                        regular_notes.append(os.path.join(root, file))
        
        regular_to_remove = random.sample(regular_notes, int(len(regular_notes) * 0.4))
        for file_path in regular_to_remove:
            os.remove(file_path)
            removed.append(file_path)
        
        # Wudan videos - remove 60%
        wudan_notes = []
        if os.path.exists(self.wudan_path):
            for root, dirs, files in os.walk(self.wudan_path):
                for file in files:
                    if file.endswith('_Notes.txt') or file.endswith('_analysis.txt'):
                        wudan_notes.append(os.path.join(root, file))
        
        wudan_to_remove = random.sample(wudan_notes, int(len(wudan_notes) * 0.6))
        for file_path in wudan_to_remove:
            os.remove(file_path)
            removed.append(file_path)
        
        self.logger.info(f"Mixed conditions: removed {len(regular_to_remove)} regular + {len(wudan_to_remove)} Wudan notes")
        return removed

    def _create_mock_not_kungfu_notes(self) -> List[str]:
        """Create mock 'NOT KUNG FU' notes files for testing cleanup functionality"""
        created_notes = []

        # Ensure test directories exist
        os.makedirs(self.wudan_path, exist_ok=True)
        os.makedirs(self.videos_path, exist_ok=True)

        # Create some test date folders in Wudan with mock videos and "NOT KUNG FU" notes
        test_scenarios = [
            {
                'date_folder': '2024_09_15',
                'videos': ['20240915_101500_1.mp4', '20240915_103000_1.mp4'],
                'not_kungfu_videos': ['20240915_101500_1.mp4']  # First video is not kung fu
            },
            {
                'date_folder': '2024_09_22',
                'videos': ['20240922_094500_1.mp4', '20240922_100000_1.mp4', '20240922_102000_1.mp4'],
                'not_kungfu_videos': ['20240922_094500_1.mp4', '20240922_102000_1.mp4']  # Two videos are not kung fu
            },
            {
                'date_folder': '2024_10_06',
                'videos': ['20241006_095000_1.mp4'],
                'not_kungfu_videos': ['20241006_095000_1.mp4']  # Only video is not kung fu
            }
        ]

        for scenario in test_scenarios:
            date_folder = scenario['date_folder']
            wudan_date_path = os.path.join(self.wudan_path, date_folder)
            os.makedirs(wudan_date_path, exist_ok=True)

            # Create mock video files (empty files for testing)
            for video_name in scenario['videos']:
                video_path = os.path.join(wudan_date_path, video_name)
                if not os.path.exists(video_path):
                    with open(video_path, 'w') as f:
                        f.write('')  # Create empty file

            # Create notes file with both kung fu and "NOT KUNG FU" entries
            notes_filename = f"{date_folder.replace('_', '')}_Notes.txt"
            notes_path = os.path.join(wudan_date_path, notes_filename)

            notes_content = []
            for video_name in scenario['videos']:
                video_base = video_name.replace('.mp4', '')
                if video_name in scenario['not_kungfu_videos']:
                    # Create "NOT KUNG FU" entry
                    notes_content.append(f"{video_base} - NOT KUNG FU - Video does not contain martial arts content.")
                    notes_content.append("")
                    notes_content.append("AI Analysis:")
                    notes_content.append("This video appears to show casual conversation or non-martial arts activity. No kung fu techniques, forms, or training visible.")
                    notes_content.append("")
                    notes_content.append(f"Analyzed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    notes_content.append("")
                    notes_content.append("Note: This video was routed to Wudan folder based on time rules but AI analysis indicates it does not contain kung fu/martial arts content.")
                else:
                    # Create regular kung fu entry
                    notes_content.append(f"{video_base} - Kung Fu/Martial Arts training session")
                    notes_content.append("")
                    notes_content.append("AI Analysis:")
                    notes_content.append("Kung Fu/Martial Arts detected in video thumbnail. Shows training forms and techniques.")
                    notes_content.append("")
                    notes_content.append(f"Detected on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                notes_content.append("")
                notes_content.append("-" * 50)
                notes_content.append("")

            # Write notes file
            with open(notes_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(notes_content))

            created_notes.append(notes_path)
            self.logger.info(f"Created mock notes file: {notes_path}")
            self.logger.info(f"  - {len(scenario['not_kungfu_videos'])} 'NOT KUNG FU' entries")
            self.logger.info(f"  - {len(scenario['videos']) - len(scenario['not_kungfu_videos'])} regular kung fu entries")

        self.logger.info(f"Created {len(created_notes)} mock notes files with 'NOT KUNG FU' entries")
        return created_notes
    
    def _get_wudan_videos(self) -> List[str]:
        """Get list of videos in Wudan folder"""
        videos = []
        if os.path.exists(self.wudan_path):
            for root, dirs, files in os.walk(self.wudan_path):
                for file in files:
                    if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                        videos.append(os.path.join(root, file))
        return videos
    
    def _get_regular_videos(self) -> List[str]:
        """Get list of videos in regular video folders (excluding Wudan)"""
        videos = []
        if os.path.exists(self.videos_path):
            for root, dirs, files in os.walk(self.videos_path):
                # Skip Wudan subfolder
                if 'Wudan' in root:
                    continue
                for file in files:
                    if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                        videos.append(os.path.join(root, file))
        return videos
    
    def generate_test_report(self, results: Dict[str, Any]) -> None:
        """Generate detailed test setup report"""
        print(f"\n📋 Test Environment Setup Report")
        print("=" * 60)
        print(f"Scenario: {results['scenario']}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        print(f"📊 Video Distribution:")
        print(f"  Total videos found: {len(results['videos_found'])}")
        print(f"  Wudan videos: {len(results['wudan_videos'])}")
        print(f"  Regular videos: {len(results['regular_videos'])}")
        print()
        
        print(f"🗑️  Notes Files Removed: {len(results['notes_removed'])}")
        if results['notes_removed']:
            print("  Files removed:")
            for file_path in results['notes_removed'][:10]:  # Show first 10
                print(f"    - {os.path.basename(file_path)}")
            if len(results['notes_removed']) > 10:
                print(f"    ... and {len(results['notes_removed']) - 10} more")

        # Show created notes files for mock scenarios
        if 'notes_created' in results and results['notes_created']:
            print(f"📝 Mock Notes Files Created: {len(results['notes_created'])}")
            print("  Files created:")
            for file_path in results['notes_created']:
                print(f"    - {os.path.basename(file_path)}")

        print()
        
        print("🎯 Expected Test Results:")
        print(f"  - Videos to be analyzed: {len(results['notes_removed'])}")
        print(f"  - Videos with existing notes: {len(results['videos_found']) - len(results['notes_removed'])}")
        print()
        
        print("🚀 Ready for Testing!")
        print("Run: ./venv/Scripts/python.exe VideoProcessor/phone_sync.py --config config.yaml --verbose")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Setup test environment for PhoneSync + VideoProcessor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Scenarios:
  clean           - Remove all notes files (force complete reprocessing)
  partial         - Remove 30% of notes files randomly
  wudan_only      - Remove notes from Wudan folder only
  mixed           - Mixed conditions (40% regular, 60% Wudan notes removed)
  mock_not_kungfu - Create mock "NOT KUNG FU" notes files for testing cleanup

Examples:
  python setup_test_environment.py --scenario clean
  python setup_test_environment.py --scenario wudan_only --reset-state
  python setup_test_environment.py --scenario mock_not_kungfu
        """
    )
    
    parser.add_argument(
        '--scenario', '-s',
        choices=['clean', 'partial', 'wudan_only', 'mixed', 'mock_not_kungfu'],
        default='mixed',
        help='Test scenario to create (default: mixed)'
    )
    
    parser.add_argument(
        '--reset-state',
        action='store_true',
        help='Reset processing state before creating test conditions'
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
    setup_logging(args.verbose)
    
    print("🧪 Test Environment Setup")
    print("=" * 40)
    
    try:
        # Initialize setup utility
        setup = TestEnvironmentSetup(args.config)
        
        # Reset processing state if requested
        if args.reset_state:
            setup.reset_processing_state()
        
        # Create test conditions
        results = setup.create_test_conditions(args.scenario)
        
        # Generate report
        setup.generate_test_report(results)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️  Setup interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Setup failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
