#!/usr/bin/env python3
"""
Debug script for target path resolution issues
"""

import sys
import os
import tempfile
from pathlib import Path
from datetime import datetime

# Add the parent directory to Python path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logging
from modules.file_scanner import FileScanner
from modules.wudan_rules import WudanRulesEngine
from modules.deduplication import DeduplicationManager
from modules.target_path_resolver import TargetPathResolver

def main():
    """Debug target path resolution"""
    print("=== Target Path Resolution Debug ===")
    
    # Change to the correct directory
    os.chdir(Path(__file__).parent.parent)
    
    try:
        # Load configuration
        config_manager = ConfigManager("config.yaml")
        config = config_manager.load_config()
        logger = setup_logging(config)
        
        # Create temporary test environment
        temp_dir = Path(tempfile.mkdtemp())
        target_paths = {
            'pictures': str(temp_dir / "Pictures"),
            'videos': str(temp_dir / "Videos"),
            'wudan_videos': str(temp_dir / "Videos" / "Wudan"),
            'notes': str(temp_dir / "Notes")
        }
        
        # Update config with test paths
        test_config = config.copy()
        test_config['target_paths'] = target_paths
        
        # Initialize components
        wudan_engine = WudanRulesEngine(test_config, logger)
        dedup_manager = DeduplicationManager(test_config, logger)
        target_resolver = TargetPathResolver(test_config, logger, wudan_engine, dedup_manager)
        
        # Test the specific files that should match Wudan rules
        test_files = [
            {
                'path': '/test/WUDAN_20210307_100000.mp4',
                'name': 'WUDAN_20210307_100000.mp4',
                'extension': '.mp4',
                'type': 'video',
                'size': 1000,
                'date': datetime(2021, 3, 7, 10, 0, 0)
            },
            {
                'path': '/test/TRAINING_20200615_070000.mp4',
                'name': 'TRAINING_20200615_070000.mp4',
                'extension': '.mp4',
                'type': 'video',
                'size': 1000,
                'date': datetime(2020, 6, 15, 7, 0, 0)
            },
            {
                'path': '/test/VID_20230615_120000.mp4',
                'name': 'VID_20230615_120000.mp4',
                'extension': '.mp4',
                'type': 'video',
                'size': 1000,
                'date': datetime(2023, 6, 15, 12, 0, 0)
            }
        ]
        
        print(f"\nTarget paths configured:")
        print(f"  Pictures: {target_paths['pictures']}")
        print(f"  Videos: {target_paths['videos']}")
        print(f"  Wudan Videos: {target_paths['wudan_videos']}")
        
        for file_info in test_files:
            print(f"\n--- Testing {file_info['name']} ---")
            print(f"Date: {file_info['date']}")
            
            # Test Wudan rules first
            should_match_wudan = wudan_engine.should_go_to_wudan_folder(file_info['date'])
            print(f"Should match Wudan rules: {should_match_wudan}")
            
            # Test base path determination
            base_path = target_resolver._determine_base_path(
                file_info['type'], file_info['extension'], file_info['date']
            )
            print(f"Determined base path: {base_path}")
            
            # Test full target folder path
            target_folder = target_resolver.get_target_folder_path(file_info)
            print(f"Target folder: {target_folder}")
            
            # Check if it's going to the right place
            if should_match_wudan:
                if target_paths['wudan_videos'] in target_folder:
                    print("✅ CORRECT: Going to Wudan folder")
                else:
                    print("❌ INCORRECT: Should go to Wudan folder but going elsewhere")
            else:
                if target_paths['videos'] in target_folder and target_paths['wudan_videos'] not in target_folder:
                    print("✅ CORRECT: Going to regular Videos folder")
                else:
                    print("❌ INCORRECT: Should go to regular Videos folder but going elsewhere")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
    except Exception as e:
        print(f"❌ Debug failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
