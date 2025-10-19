#!/usr/bin/env python3
"""
File Existence Validation Script for PhoneSync + VideoProcessor
Validates which source files already exist in target folder structure
Provides comprehensive report before running full processing
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

# Add the parent directory to the path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logging

class FileExistenceValidator:
    """Validates which source files already exist in target folders"""
    
    def __init__(self, config):
        self.config = config
        self.logger = setup_logging(config)
        
        # File extensions to process
        self.picture_extensions = set(config['file_extensions']['pictures'])
        self.video_extensions = set(config['file_extensions']['videos'])
        self.all_extensions = self.picture_extensions | self.video_extensions
        
        # Results storage
        self.source_files = []
        self.target_inventory = {}
        self.matches = []
        self.missing_files = []
        
    def scan_source_folders(self):
        """Scan all source folders and build comprehensive file list"""
        print("🔍 Scanning source folders...")
        
        source_folders = self.config.get('source_folders', [])
        if not source_folders:
            print("❌ No source folders configured")
            return
            
        for source_folder in source_folders:
            if not os.path.exists(source_folder):
                print(f"⚠️  Source folder not found: {source_folder}")
                continue
                
            print(f"   📁 Scanning: {source_folder}")
            self._scan_folder_recursive(source_folder)
        
        print(f"✅ Found {len(self.source_files)} files in source folders")
        
        # Group by file type
        pictures = [f for f in self.source_files if f['extension'].lower() in self.picture_extensions]
        videos = [f for f in self.source_files if f['extension'].lower() in self.video_extensions]
        
        print(f"   📸 Pictures: {len(pictures)}")
        print(f"   🎬 Videos: {len(videos)}")
        
    def _scan_folder_recursive(self, folder_path):
        """Recursively scan a folder for files"""
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = Path(file).suffix.lower()
                    
                    if file_ext in self.all_extensions:
                        try:
                            stat = os.stat(file_path)
                            file_info = {
                                'name': file,
                                'path': file_path,
                                'extension': file_ext,
                                'size': stat.st_size,
                                'modified': datetime.fromtimestamp(stat.st_mtime),
                                'relative_path': os.path.relpath(file_path, folder_path)
                            }
                            self.source_files.append(file_info)
                        except Exception as e:
                            print(f"⚠️  Error processing {file_path}: {e}")
                            
        except Exception as e:
            print(f"❌ Error scanning {folder_path}: {e}")
    
    def build_target_inventory(self):
        """Build comprehensive inventory of all files in target folders"""
        print("\n📋 Building target folder inventory...")
        
        target_paths = self.config.get('target_paths', {})
        
        for path_type, target_path in target_paths.items():
            if not os.path.exists(target_path):
                print(f"⚠️  Target path not found: {target_path}")
                continue
                
            print(f"   📁 Scanning {path_type}: {target_path}")
            self.target_inventory[path_type] = self._build_folder_inventory(target_path)
            
        total_target_files = sum(len(files) for files in self.target_inventory.values())
        print(f"✅ Found {total_target_files} files in target folders")
        
    def _build_folder_inventory(self, folder_path):
        """Build inventory of files in a target folder"""
        inventory = {}
        
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = Path(file).suffix.lower()
                    
                    if file_ext in self.all_extensions:
                        try:
                            stat = os.stat(file_path)
                            
                            # Create lookup key (filename + size for matching)
                            lookup_key = f"{file}|{stat.st_size}"
                            
                            inventory[lookup_key] = {
                                'name': file,
                                'path': file_path,
                                'size': stat.st_size,
                                'modified': datetime.fromtimestamp(stat.st_mtime),
                                'folder': os.path.basename(root)
                            }
                        except Exception as e:
                            print(f"⚠️  Error processing target file {file_path}: {e}")
                            
        except Exception as e:
            print(f"❌ Error scanning target folder {folder_path}: {e}")
            
        return inventory
    
    def match_files(self):
        """Match source files against target inventory"""
        print("\n🔍 Matching source files against target inventory...")
        
        for source_file in self.source_files:
            # Create lookup key (filename + size)
            lookup_key = f"{source_file['name']}|{source_file['size']}"
            
            # Search across all target inventories
            found = False
            for path_type, inventory in self.target_inventory.items():
                if lookup_key in inventory:
                    target_file = inventory[lookup_key]
                    
                    match_info = {
                        'source_file': source_file,
                        'target_file': target_file,
                        'target_type': path_type,
                        'match_method': 'name_size'
                    }
                    self.matches.append(match_info)
                    found = True
                    break
            
            if not found:
                self.missing_files.append(source_file)
        
        print(f"✅ Matching complete:")
        print(f"   ✅ Found: {len(self.matches)} files")
        print(f"   ❌ Missing: {len(self.missing_files)} files")
    
    def analyze_results(self):
        """Analyze matching results and provide insights"""
        print("\n📊 Analysis Results:")
        print("=" * 60)

        # Overall statistics
        total_source = len(self.source_files)
        total_found = len(self.matches)
        total_missing = len(self.missing_files)

        print(f"📁 Total source files: {total_source}")
        print(f"✅ Files already processed: {total_found} ({total_found/total_source*100:.1f}%)")
        print(f"❌ Files needing processing: {total_missing} ({total_missing/total_source*100:.1f}%)")

        # Break down by file type
        missing_pictures = [f for f in self.missing_files if f['extension'].lower() in self.picture_extensions]
        missing_videos = [f for f in self.missing_files if f['extension'].lower() in self.video_extensions]

        print(f"\n📸 Missing Pictures: {len(missing_pictures)}")
        print(f"🎬 Missing Videos: {len(missing_videos)}")

        # Estimate processing time for videos
        if missing_videos:
            estimated_seconds = len(missing_videos) * 5  # Assume 5 seconds per video
            estimated_hours = estimated_seconds / 3600
            print(f"⏱️  Estimated video processing time: {estimated_hours:.1f} hours ({estimated_seconds/60:.0f} minutes)")

        # Date analysis of missing files
        if self.missing_files:
            missing_dates = [f['modified'] for f in self.missing_files]
            oldest_missing = min(missing_dates)
            newest_missing = max(missing_dates)

            print(f"\n📅 Missing file date range:")
            print(f"   Oldest: {oldest_missing.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Newest: {newest_missing.strftime('%Y-%m-%d %H:%M:%S')}")

        # Date analysis of found files
        if self.matches:
            found_dates = [f['source_file']['modified'] for f in self.matches]
            oldest_found = min(found_dates)
            newest_found = max(found_dates)

            print(f"\n📅 Last processed file date range:")
            print(f"   Oldest: {oldest_found.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Newest: {newest_found.strftime('%Y-%m-%d %H:%M:%S')}")

        # Incremental processing recommendation
        if self.matches and self.missing_files:
            print(f"\n💡 Incremental Processing Recommendation:")
            print(f"   The system should automatically process only the {total_missing} missing files")
            print(f"   on the next run, skipping the {total_found} already processed files.")

        # Show sample of most recent missing files
        if self.missing_files:
            print(f"\n📋 Sample of most recent missing files (last 10):")
            recent_missing = sorted(self.missing_files, key=lambda x: x['modified'], reverse=True)[:10]
            for i, file_info in enumerate(recent_missing, 1):
                print(f"   {i:2d}. {file_info['name']} ({file_info['modified'].strftime('%Y-%m-%d %H:%M')})")

        # Show target folder distribution
        if self.matches:
            print(f"\n📁 Target folder distribution:")
            folder_counts = defaultdict(int)
            for match in self.matches:
                folder_counts[match['target_type']] += 1

            for folder_type, count in folder_counts.items():
                print(f"   {folder_type}: {count} files")
    
    def generate_report(self, output_file="file_existence_report.json"):
        """Generate detailed JSON report"""
        print(f"\n📄 Generating detailed report: {output_file}")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_source_files': len(self.source_files),
                'files_found': len(self.matches),
                'files_missing': len(self.missing_files),
                'completion_percentage': len(self.matches) / len(self.source_files) * 100 if self.source_files else 0
            },
            'missing_files': [
                {
                    'name': f['name'],
                    'path': f['path'],
                    'size': f['size'],
                    'modified': f['modified'].isoformat(),
                    'extension': f['extension']
                }
                for f in self.missing_files
            ],
            'found_files': [
                {
                    'source_name': m['source_file']['name'],
                    'source_path': m['source_file']['path'],
                    'target_path': m['target_file']['path'],
                    'target_folder': m['target_file']['folder'],
                    'target_type': m['target_type']
                }
                for m in self.matches
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Report saved to: {output_file}")

def main():
    """Main execution function"""
    print("🔍 File Existence Validation for PhoneSync + VideoProcessor")
    print("=" * 60)

    # Load configuration - look for config.yaml in the project root
    try:
        # Get the project root directory (two levels up from Scripts folder)
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent
        config_path = project_root / "config.yaml"

        print(f"📁 Looking for config file: {config_path}")

        if not config_path.exists():
            print(f"❌ Configuration file not found: {config_path}")
            print(f"   Current working directory: {os.getcwd()}")
            print(f"   Script directory: {script_dir}")
            print(f"   Project root: {project_root}")
            return 1

        config_manager = ConfigManager(str(config_path))
        config = config_manager.load_config()
        print(f"✅ Configuration loaded successfully")

    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return 1
    
    # Initialize validator
    validator = FileExistenceValidator(config)
    
    # Run validation process
    try:
        validator.scan_source_folders()
        validator.build_target_inventory()
        validator.match_files()
        validator.analyze_results()
        validator.generate_report()
        
        print("\n🎯 Validation complete! Review the report before running full processing.")
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
