#!/usr/bin/env python3
"""
Production Dry Run Test Script
Tests file organization and folder creation with production configuration
without AI analysis for faster testing with limited file scope.

This script:
1. Temporarily switches to production environment
2. Disables AI analysis for speed
3. Limits processing to specified number of days
4. Runs in dry-run mode (no actual file operations)
5. Provides detailed preview of what would be processed
6. Restores original configuration when complete
"""

import os
import sys
import argparse
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import tempfile

# Add the parent directory to the path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logging
from modules.file_scanner import FileScanner
from modules.file_organizer import FileOrganizer
from modules.target_path_resolver import TargetPathResolver
from modules.wudan_rules import WudanRulesEngine
from modules.deduplication import DeduplicationManager

class ProductionDryRunTester:
    """Production dry run testing with limited scope"""
    
    def __init__(self, max_days: int = 20):
        """
        Initialize the tester

        Args:
            max_days: Maximum number of days worth of files to process
        """
        self.max_days = max_days
        self.original_config_content = None
        self.temp_config_path = None
        
    def create_test_config(self):
        """Create temporary production config with AI analysis disabled"""
        print("📝 Creating temporary production configuration...")
        
        # Read original config
        with open("config.yaml", 'r', encoding='utf-8') as f:
            self.original_config_content = f.read()
        
        # Modify for production dry run test
        test_config = self.original_config_content
        
        # Switch to production environment
        test_config = test_config.replace('environment: "DEVELOPMENT"', 'environment: "PRODUCTION"')
        
        # Disable AI analysis for speed
        test_config = test_config.replace('enable_video_analysis: true', 'enable_video_analysis: false')

        # Disable deduplication for faster testing
        test_config = test_config.replace('enable_deduplication: true', 'enable_deduplication: false')
        
        # Create temporary config file
        temp_fd, self.temp_config_path = tempfile.mkstemp(suffix='.yaml', prefix='prod_test_')
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            f.write(test_config)
        
        print(f"✅ Temporary config created: {self.temp_config_path}")
        return self.temp_config_path
    
    def cleanup_test_config(self):
        """Remove temporary config file"""
        if self.temp_config_path and os.path.exists(self.temp_config_path):
            os.unlink(self.temp_config_path)
            print("🧹 Temporary config file cleaned up")
    
    def filter_files_by_days(self, files: list) -> list:
        """
        Filter files to only include recent days up to max_days limit
        
        Args:
            files: List of file info dictionaries
            
        Returns:
            Filtered list of files
        """
        if not files:
            return files
        
        # Sort files by date (newest first)
        sorted_files = sorted(files, key=lambda x: x['date'], reverse=True)
        
        # Get unique dates
        unique_dates = set()
        filtered_files = []
        
        for file_info in sorted_files:
            file_date = file_info['date'].date()
            
            if len(unique_dates) < self.max_days:
                unique_dates.add(file_date)
                filtered_files.append(file_info)
            elif file_date in unique_dates:
                # Include files from already selected dates
                filtered_files.append(file_info)
        
        # Sort back to chronological order
        filtered_files.sort(key=lambda x: x['date'])
        
        print(f"📅 Filtered to {len(filtered_files)} files from {len(unique_dates)} days")
        print(f"   Date range: {min(unique_dates)} to {max(unique_dates)}")
        
        return filtered_files

    def calculate_statistics(self, organization_plan: list) -> dict:
        """Calculate statistics from organization plan"""
        stats = {
            'files_to_copy': 0,
            'files_to_skip': 0,
            'total_size_mb': 0.0
        }

        for item in organization_plan:
            if item.get('would_skip', False):
                stats['files_to_skip'] += 1
            else:
                stats['files_to_copy'] += 1

            stats['total_size_mb'] += item.get('size_mb', 0)

        return stats

    def display_detailed_transfer_report(self, organization_plan: list):
        """Display detailed file transfer report showing exactly where each file would go"""
        print(f"\n📋 Detailed File Transfer Report")
        print("=" * 80)
        print("Format: filename --> target_path (folder_status) [routing_reason]")
        print("-" * 80)

        # Deduplicate files by filename (since they appear in both Internal_dmc and SDCard_DMC)
        unique_files = {}
        for item in organization_plan:
            filename = Path(item['source']).name
            if filename not in unique_files:
                unique_files[filename] = item

        # Sort files by target folder for better organization
        sorted_items = sorted(unique_files.values(), key=lambda x: (
            x.get('target_folder', ''),
            x.get('final_filename', '')
        ))

        for item in sorted_items:
            if item.get('error'):
                print(f"❌ {Path(item['source']).name} --> ERROR: {item['error']}")
                continue

            source_filename = Path(item['source']).name
            target_folder = item.get('target_folder', '')
            final_filename = item.get('final_filename', source_filename)
            would_skip = item.get('would_skip', False)
            file_type = item.get('file_type', 'unknown')

            if would_skip:
                print(f"⏭️  {source_filename} --> SKIP (duplicate)")
                continue

            # Determine folder status
            folder_exists = os.path.exists(target_folder) if target_folder else False
            folder_status = "Existing Folder" if folder_exists else "New Folder Created"

            # Get relative target path for display
            if target_folder:
                # Extract the meaningful part of the path
                target_parts = Path(target_folder).parts

                # Find the base target directory (My Pictures, My Videos, etc.)
                base_found = False
                display_path = ""

                for i, part in enumerate(target_parts):
                    if part in ['My Pictures', 'My Videos']:
                        # Include this part and everything after
                        display_path = str(Path(*target_parts[i:]))
                        base_found = True
                        break

                if not base_found:
                    # Fallback to just the folder name
                    display_path = Path(target_folder).name

                # Determine routing reason
                routing_reason = self._get_routing_reason(source_filename, target_folder, file_type)

                # Handle filename changes
                if final_filename != source_filename:
                    filename_note = f" (renamed from {source_filename})"
                else:
                    filename_note = ""

                print(f"📁 {source_filename} --> {display_path}/{final_filename}{filename_note} ({folder_status}) [{routing_reason}]")
            else:
                print(f"❌ {source_filename} --> ERROR: Could not determine target")

        print("-" * 80)
        print(f"📊 Total unique files to transfer: {len([item for item in sorted_items if not item.get('would_skip', False) and not item.get('error')])}")

    def _get_routing_reason(self, filename: str, target_folder: str, file_type: str) -> str:
        """Determine why a file was routed to a specific folder"""
        if file_type == 'picture':
            return "Picture file"
        elif file_type == 'video':
            if 'Wudan' in target_folder:
                return "Video - Wudan time rules matched"
            else:
                return "Video - Regular time"
        else:
            return f"{file_type} file"

    def run_dry_run_test(self) -> dict:
        """
        Run the production dry run test
        
        Returns:
            Dictionary with test results
        """
        results = {
            'success': False,
            'files_found': 0,
            'files_filtered': 0,
            'days_processed': 0,
            'organization_plan': [],
            'errors': []
        }
        
        try:
            # Create test configuration
            config_path = self.create_test_config()
            
            # Load configuration
            config_manager = ConfigManager(config_path)
            config = config_manager.load_config()
            
            # Setup logging
            logger = setup_logging(config)
            logger.info("=== Production Dry Run Test Started ===")
            
            print(f"🏭 Production Environment Test")
            print(f"📂 Source folders: {len(config['source_folders'])}")
            for folder in config['source_folders']:
                print(f"   - {folder}")
            
            print(f"🎯 Target paths:")
            for key, path in config['target_paths'].items():
                print(f"   - {key}: {path}")
            
            # Initialize components
            file_scanner = FileScanner(config, logger)
            wudan_engine = WudanRulesEngine(config, logger)
            dedup_manager = DeduplicationManager(config, logger)
            target_resolver = TargetPathResolver(config, logger, wudan_engine, dedup_manager)
            file_organizer = FileOrganizer(config, logger, target_resolver, dedup_manager)
            
            # Build deduplication cache (only if enabled)
            if config['options']['enable_deduplication']:
                print("\n🔍 Building deduplication cache...")
                dedup_manager.build_cache()
            else:
                print("\n⚡ Deduplication disabled for faster testing")
            
            # Scan for files
            print(f"\n📁 Scanning source folders...")
            all_files = []
            for source_folder in config['source_folders']:
                if os.path.exists(source_folder):
                    files = file_scanner.scan_folder(source_folder)
                    all_files.extend(files)
                    print(f"   Found {len(files)} files in {source_folder}")
                else:
                    print(f"   ⚠️  Source folder not found: {source_folder}")
            
            results['files_found'] = len(all_files)
            
            if not all_files:
                print("❌ No files found to process")
                return results
            
            # Filter files by days
            print(f"\n📅 Filtering to {self.max_days} days worth of files...")
            filtered_files = self.filter_files_by_days(all_files)
            results['files_filtered'] = len(filtered_files)
            
            # Get unique dates for day count
            unique_dates = set(f['date'].date() for f in filtered_files)
            results['days_processed'] = len(unique_dates)
            
            # Generate organization plan
            print(f"\n📋 Generating organization plan...")
            organization_preview = file_organizer.get_organization_preview(filtered_files)
            results['organization_plan'] = organization_preview['organization_plan']

            # Calculate statistics
            organization_preview['statistics'] = self.calculate_statistics(organization_preview['organization_plan'])

            # Display summary
            self.display_test_summary(results, organization_preview)
            
            results['success'] = True
            logger.info("=== Production Dry Run Test Completed Successfully ===")
            
        except Exception as e:
            error_msg = f"Test failed: {e}"
            results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
            
        finally:
            self.cleanup_test_config()
        
        return results
    
    def display_test_summary(self, results: dict, preview: dict):
        """Display detailed test summary"""
        print(f"\n📊 Production Dry Run Test Summary")
        print("=" * 50)
        print(f"📁 Files found: {results['files_found']}")
        print(f"🔍 Files filtered: {results['files_filtered']}")
        print(f"📅 Days processed: {results['days_processed']}")
        print(f"📋 Organization plan items: {len(results['organization_plan'])}")

        # File type breakdown
        file_types = {}
        for item in results['organization_plan']:
            file_type = item.get('file_type', 'unknown')
            file_types[file_type] = file_types.get(file_type, 0) + 1

        print(f"\n📊 File Type Breakdown:")
        for file_type, count in file_types.items():
            print(f"   - {file_type}: {count} files")

        # Target folder breakdown
        target_folders = {}
        for item in results['organization_plan']:
            if item.get('target_folder'):
                folder_name = Path(item['target_folder']).name
                target_folders[folder_name] = target_folders.get(folder_name, 0) + 1

        print(f"\n📂 Target Folder Breakdown:")
        for folder, count in sorted(target_folders.items()):
            print(f"   - {folder}: {count} files")

        # Detailed file transfer report
        self.display_detailed_transfer_report(results['organization_plan'])

        # Potential issues
        if preview.get('potential_issues'):
            print(f"\n⚠️  Potential Issues ({len(preview['potential_issues'])}):")
            for issue in preview['potential_issues'][:10]:  # Show first 10
                print(f"   - {issue}")
            if len(preview['potential_issues']) > 10:
                print(f"   ... and {len(preview['potential_issues']) - 10} more")

        # Statistics
        stats = preview.get('statistics', {})
        print(f"\n📈 Processing Statistics:")
        print(f"   - Would copy: {stats.get('files_to_copy', 0)} files")
        print(f"   - Would skip (duplicates): {stats.get('files_to_skip', 0)} files")
        print(f"   - Total size: {stats.get('total_size_mb', 0):.1f} MB")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Production Dry Run Test - Test file organization with production config"
    )
    parser.add_argument(
        '--days', '-d',
        type=int,
        default=20,
        help='Maximum number of days worth of files to process (default: 20)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    print("🧪 Production Dry Run Test")
    print("=" * 50)
    print(f"📅 Processing up to {args.days} days worth of files")
    print(f"🚫 AI analysis disabled for speed")
    print(f"🔍 Dry run mode - no files will be moved")
    print()

    try:
        tester = ProductionDryRunTester(max_days=args.days)
        results = tester.run_dry_run_test()
        
        if results['success']:
            print("\n✅ Production dry run test completed successfully!")
            print(f"📊 Processed {results['files_filtered']} files from {results['days_processed']} days")
            return 0
        else:
            print("\n❌ Production dry run test failed!")
            for error in results['errors']:
                print(f"   - {error}")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
