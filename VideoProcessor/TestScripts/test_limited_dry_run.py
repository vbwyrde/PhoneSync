#!/usr/bin/env python3
"""
Limited Test Dry Run - Test processing on one folder with first 4 MP4 files
Shows exactly what the system would do without making any changes
"""

import os
import sys
import yaml
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent.parent.parent / 'config.yaml'
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return None
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return None

def resolve_production_paths(config):
    """Resolve production source folder paths"""
    if not config:
        return []
    
    prod_vars = config.get('PROD_VARS', {})
    source_root = prod_vars.get('source_root', '')
    source_subdirs = prod_vars.get('source_subdirs', [])
    
    if not source_root or not source_subdirs:
        print("❌ Production paths not configured in config.yaml")
        return []
    
    # Build full paths
    source_folders = []
    for subdir in source_subdirs:
        full_path = os.path.join(source_root, subdir).replace('/', '\\')
        source_folders.append(full_path)
    
    return source_folders

def get_first_mp4_files(folder_path, limit=4):
    """
    Get the first N MP4 files from a folder
    
    Args:
        folder_path: Path to scan
        limit: Maximum number of MP4 files to return
        
    Returns:
        list: List of MP4 file paths
    """
    mp4_files = []
    
    try:
        if not os.path.exists(folder_path):
            print(f"❌ Folder does not exist: {folder_path}")
            return []
        
        print(f"📁 Scanning for MP4 files in: {folder_path}")
        
        # Walk through folder and find MP4 files
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.mp4'):
                    file_path = os.path.join(root, file)
                    mp4_files.append(file_path)
                    
                    if len(mp4_files) >= limit:
                        break
            
            if len(mp4_files) >= limit:
                break
        
        print(f"   ✅ Found {len(mp4_files)} MP4 files (limit: {limit})")
        return mp4_files[:limit]
        
    except Exception as e:
        print(f"❌ Error scanning folder: {e}")
        return []

def extract_date_from_filename(filename):
    """Extract date from filename using common patterns"""
    # Handle files that start with . (hidden files)
    clean_filename = filename.lstrip('.')

    # Primary pattern: YYYYMMDD_HHMMSS_X.ext or YYYYMMDD_HHMMSS.ext
    pattern = r'^(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})(?:_\d+)?\..*'
    match = re.match(pattern, clean_filename)

    if match:
        year, month, day, hour, minute, second = match.groups()
        try:
            return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        except ValueError:
            pass

    # Fallback: try to extract just date
    date_pattern = r'^(\d{4})(\d{2})(\d{2})'
    match = re.match(date_pattern, clean_filename)
    if match:
        year, month, day = match.groups()
        try:
            return datetime(int(year), int(month), int(day))
        except ValueError:
            pass

    return None

def check_wudan_time_rules(file_datetime, config):
    """Simplified Wudan time rules check"""
    if not file_datetime:
        return False

    wudan_rules = config.get('wudan_rules', {})

    # Check before_2021 rules
    if file_datetime.year < 2021:
        before_2021 = wudan_rules.get('before_2021', {})
        days_of_week = before_2021.get('days_of_week', [])
        time_ranges = before_2021.get('time_ranges', [])

        # Check day of week (0=Monday, 6=Sunday)
        if file_datetime.weekday() in days_of_week:
            # Check time ranges
            file_time = file_datetime.time()
            for time_range in time_ranges:
                start_time = datetime.strptime(time_range['start'], '%H:%M').time()
                end_time = datetime.strptime(time_range['end'], '%H:%M').time()
                if start_time <= file_time <= end_time:
                    return True

    # Check after_2021 rules
    else:
        rules_2021 = wudan_rules.get('after_2021', {})
        days_of_week = rules_2021.get('days_of_week', [])
        time_ranges = rules_2021.get('time_ranges', {})

        # Check day of week
        weekday = file_datetime.weekday()
        if weekday in days_of_week:
            # Get time ranges for this specific day
            day_ranges = time_ranges.get(weekday, [])
            file_time = file_datetime.time()

            for time_range in day_ranges:
                start_time = datetime.strptime(time_range['start'], '%H:%M').time()
                end_time = datetime.strptime(time_range['end'], '%H:%M').time()
                if start_time <= file_time <= end_time:
                    return True

    return False

def analyze_file_processing_plan(config, mp4_files):
    """
    Analyze what would happen to each MP4 file during processing

    Args:
        config: Configuration dictionary
        mp4_files: List of MP4 file paths to analyze

    Returns:
        list: Processing plan for each file
    """
    print(f"\n🔍 ANALYZING PROCESSING PLAN FOR {len(mp4_files)} MP4 FILES")
    print("=" * 70)

    processing_plan = []

    # Get target paths from config
    target_paths = config.get('PROD_VARS', {}).get('target_paths', {})
    videos_path = target_paths.get('videos', '')
    wudan_path = target_paths.get('wudan', '')

    for i, file_path in enumerate(mp4_files, 1):
        filename = Path(file_path).name
        print(f"\n📹 File {i}/{len(mp4_files)}: {filename}")
        print("-" * 50)

        try:
            # Get file size
            file_size = os.path.getsize(file_path)
            print(f"   📏 File size: {file_size:,} bytes")

            # Extract date from filename
            file_datetime = extract_date_from_filename(filename)
            if file_datetime:
                print(f"   📅 Date extracted: {file_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"   📅 Date extracted: Could not parse date from filename")

            # Check Wudan rules
            is_wudan = check_wudan_time_rules(file_datetime, config) if file_datetime else False
            print(f"   🥋 Wudan routing: {'YES' if is_wudan else 'NO'}")

            # Determine target folder
            if is_wudan:
                base_target_folder = wudan_path
                folder_type = "Wudan"
            else:
                base_target_folder = videos_path
                folder_type = "Videos"

            # Create date-based subfolder
            if file_datetime:
                date_folder = file_datetime.strftime('%Y_%m_%d')
                target_folder = os.path.join(base_target_folder, date_folder)
            else:
                target_folder = base_target_folder
                date_folder = "Unknown_Date"

            print(f"   📂 Target folder: {target_folder}")
            print(f"   📄 Target filename: {filename}")

            # Check if target folder exists
            folder_exists = os.path.exists(target_folder)
            print(f"   📁 Target folder exists: {'YES' if folder_exists else 'NO (will be created)'}")

            # Check for potential duplicates (simplified - just check if file exists)
            full_target_path = os.path.join(target_folder, filename)
            file_exists = os.path.exists(full_target_path)

            if file_exists:
                print(f"   🔄 Duplicate status: DUPLICATE - Would be SKIPPED")
                skip_reason = "File already exists in target folder"
                would_skip = True
            else:
                print(f"   🔄 Duplicate status: UNIQUE - Would be PROCESSED")
                skip_reason = None
                would_skip = False

            # Determine if AI analysis would be performed
            would_analyze = not would_skip and filename.lower().endswith('.mp4')
            print(f"   🤖 AI analysis: {'YES' if would_analyze else 'NO'}")

            # Build processing plan entry
            plan_entry = {
                'source_file': file_path,
                'source_filename': filename,
                'file_size_bytes': file_size,
                'extracted_date': file_datetime.strftime('%Y-%m-%d %H:%M:%S') if file_datetime else 'Unknown',
                'is_wudan': is_wudan,
                'target_folder': target_folder,
                'target_filename': filename,
                'full_target_path': full_target_path,
                'folder_exists': folder_exists,
                'file_exists': file_exists,
                'would_skip': would_skip,
                'skip_reason': skip_reason,
                'would_analyze_ai': would_analyze,
                'folder_type': folder_type,
                'date_folder': date_folder,
                'wudan_reason': 'Time-based routing matched Wudan schedule' if is_wudan else 'Time does not match Wudan schedule'
            }

            processing_plan.append(plan_entry)

        except Exception as e:
            print(f"   ❌ Error analyzing file: {e}")
            continue

    return processing_plan

def display_processing_summary(processing_plan):
    """Display a comprehensive summary of the processing plan"""
    print(f"\n📊 PROCESSING PLAN SUMMARY")
    print("=" * 70)
    
    total_files = len(processing_plan)
    files_to_process = len([p for p in processing_plan if not p['would_skip']])
    files_to_skip = len([p for p in processing_plan if p['would_skip']])
    files_for_ai = len([p for p in processing_plan if p['would_analyze_ai']])
    wudan_files = len([p for p in processing_plan if p['is_wudan']])
    
    print(f"📁 Total files analyzed: {total_files}")
    print(f"✅ Files to process: {files_to_process}")
    print(f"⏭️  Files to skip: {files_to_skip}")
    print(f"🤖 Files for AI analysis: {files_for_ai}")
    print(f"🥋 Files routed to Wudan: {wudan_files}")
    
    # Detailed file-by-file plan
    print(f"\n📋 DETAILED PROCESSING PLAN")
    print("=" * 70)
    print("Format: filename → target_path [ACTION] (reason)")
    print("-" * 70)
    
    for i, plan in enumerate(processing_plan, 1):
        filename = plan['source_filename']
        target_path = plan['full_target_path']
        
        if plan['would_skip']:
            action = "SKIP"
            reason = plan['skip_reason']
            icon = "⏭️ "
        else:
            action = "COPY"
            if plan['would_analyze_ai']:
                action += " + AI ANALYSIS"
            reason = plan['wudan_reason']
            icon = "✅"
        
        print(f"{icon} {filename}")
        print(f"   → {target_path}")
        print(f"   [{action}] ({reason})")
        
        if plan['would_analyze_ai']:
            print(f"   🤖 Will extract thumbnail and analyze for kung fu content")
            print(f"   📝 Will generate notes file if kung fu detected")
        
        print()
    
    # Time estimate for this test
    if files_for_ai > 0:
        estimated_time_minutes = (files_to_process * 1.5 + files_for_ai * 32) / 60
        print(f"⏱️  Estimated processing time: {estimated_time_minutes:.1f} minutes")
    else:
        estimated_time_seconds = files_to_process * 1.5
        print(f"⏱️  Estimated processing time: {estimated_time_seconds:.1f} seconds")

def main():
    """Main execution function"""
    print("🧪 LIMITED TEST DRY RUN - First 4 MP4 Files Analysis")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    if not config:
        return 1
    
    # Get production source folders
    source_folders = resolve_production_paths(config)
    if not source_folders:
        return 1
    
    print(f"📂 Available source folders:")
    for i, folder in enumerate(source_folders, 1):
        folder_name = Path(folder).name
        print(f"   {i}. {folder_name}")
    
    # For this test, let's use the first folder (Camera)
    test_folder = source_folders[0]  # SDCard_DCIM/Camera
    folder_name = Path(test_folder).name
    
    print(f"\n🎯 Testing with folder: {folder_name}")
    print(f"📁 Full path: {test_folder}")
    
    # Get first 4 MP4 files
    mp4_files = get_first_mp4_files(test_folder, limit=4)
    
    if not mp4_files:
        print("❌ No MP4 files found in test folder")
        return 1
    
    # Analyze processing plan
    processing_plan = analyze_file_processing_plan(config, mp4_files)
    
    if not processing_plan:
        print("❌ Could not create processing plan")
        return 1
    
    # Display summary
    display_processing_summary(processing_plan)
    
    print(f"\n✅ Test dry run analysis complete!")
    print(f"💡 This shows exactly what would happen during actual processing")
    print(f"🚀 Ready to proceed with full processing when you're satisfied with the plan")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
