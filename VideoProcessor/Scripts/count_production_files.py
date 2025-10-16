#!/usr/bin/env python3
"""
Production File Counter - Accurate MP4 count for time estimation
Scans all production source folders to count files and estimate processing time
"""

import os
import sys
import yaml
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

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

def scan_folder_for_files(folder_path, video_extensions=None, collect_file_details=False):
    """
    Scan a folder for files and categorize them

    Args:
        folder_path: Path to scan
        video_extensions: List of video extensions to count
        collect_file_details: If True, collect detailed file information for duplicate analysis

    Returns:
        dict: File counts by category and optionally file details
    """
    if video_extensions is None:
        video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv', '.webm']

    results = {
        'total_files': 0,
        'video_files': 0,
        'mp4_files': 0,
        'other_videos': 0,
        'picture_files': 0,
        'other_files': 0,
        'total_size_bytes': 0,
        'video_size_bytes': 0,
        'mp4_size_bytes': 0,
        'scan_time_seconds': 0,
        'accessible': True,
        'error': None,
        'file_details': [] if collect_file_details else None
    }
    
    start_time = time.time()
    
    try:
        if not os.path.exists(folder_path):
            results['accessible'] = False
            results['error'] = f"Path does not exist: {folder_path}"
            return results
        
        if not os.access(folder_path, os.R_OK):
            results['accessible'] = False
            results['error'] = f"No read access to: {folder_path}"
            return results
        
        print(f"📁 Scanning: {folder_path}")
        
        # Scan all files in folder
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = Path(file).suffix.lower()

                try:
                    file_size = os.path.getsize(file_path)
                    file_mtime = os.path.getmtime(file_path)

                    results['total_files'] += 1
                    results['total_size_bytes'] += file_size

                    # Collect detailed file information if requested
                    if collect_file_details:
                        relative_path = os.path.relpath(file_path, folder_path)
                        results['file_details'].append({
                            'name': file,
                            'relative_path': relative_path,
                            'full_path': file_path,
                            'size': file_size,
                            'mtime': file_mtime,
                            'extension': file_ext
                        })

                    if file_ext in video_extensions:
                        results['video_files'] += 1
                        results['video_size_bytes'] += file_size

                        if file_ext == '.mp4':
                            results['mp4_files'] += 1
                            results['mp4_size_bytes'] += file_size
                        else:
                            results['other_videos'] += 1

                    elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
                        results['picture_files'] += 1

                    else:
                        results['other_files'] += 1

                except (OSError, PermissionError) as e:
                    # Skip files we can't access
                    continue
        
        results['scan_time_seconds'] = time.time() - start_time
        print(f"   ✅ Found {results['total_files']} files ({results['video_files']} videos, {results['mp4_files']} MP4s)")
        
    except Exception as e:
        results['accessible'] = False
        results['error'] = str(e)
        results['scan_time_seconds'] = time.time() - start_time
        print(f"   ❌ Error scanning folder: {e}")
    
    return results

def analyze_duplicates_between_folders(internal_results, sdcard_results):
    """
    Analyze duplicates between Internal_dmc and SDCard_DMC folder structures

    Args:
        internal_results: Dict of scan results for Internal_dmc folders
        sdcard_results: Dict of scan results for SDCard_DMC folders

    Returns:
        dict: Duplicate analysis results
    """
    print(f"\n🔍 DUPLICATE ANALYSIS - Comparing Internal_dmc vs SDCard_DMC")
    print("=" * 70)

    duplicate_analysis = {
        'total_duplicates': 0,
        'duplicate_size_bytes': 0,
        'folder_comparisons': {},
        'duplicate_files': []
    }

    # Compare corresponding folders
    folder_pairs = [
        ('Camera', 'Camera'),
        ('FavoritesMA', 'FavoritesMA'),
        ('GIF', 'GIF'),
        ('Official', 'Official'),
        ('Videocaptures', 'Videocaptures')
    ]

    for internal_folder, sdcard_folder in folder_pairs:
        print(f"\n📁 Comparing {internal_folder}:")

        internal_files = internal_results.get(internal_folder, {}).get('file_details', [])
        sdcard_files = sdcard_results.get(sdcard_folder, {}).get('file_details', [])

        if not internal_files or not sdcard_files:
            print(f"   ⚠️  No detailed file data available for comparison")
            continue

        # Create lookup dictionaries for comparison
        internal_lookup = {}
        for file_info in internal_files:
            key = (file_info['name'], file_info['size'])
            internal_lookup[key] = file_info

        sdcard_lookup = {}
        for file_info in sdcard_files:
            key = (file_info['name'], file_info['size'])
            sdcard_lookup[key] = file_info

        # Find duplicates (same name and size)
        duplicates = []
        for key in internal_lookup:
            if key in sdcard_lookup:
                duplicates.append({
                    'name': key[0],
                    'size': key[1],
                    'internal_path': internal_lookup[key]['full_path'],
                    'sdcard_path': sdcard_lookup[key]['full_path']
                })

        folder_comparison = {
            'internal_files': len(internal_files),
            'sdcard_files': len(sdcard_files),
            'duplicates': len(duplicates),
            'duplicate_percentage': (len(duplicates) / max(len(internal_files), 1)) * 100,
            'duplicate_size_bytes': sum(d['size'] for d in duplicates)
        }

        duplicate_analysis['folder_comparisons'][internal_folder] = folder_comparison
        duplicate_analysis['total_duplicates'] += len(duplicates)
        duplicate_analysis['duplicate_size_bytes'] += folder_comparison['duplicate_size_bytes']
        duplicate_analysis['duplicate_files'].extend(duplicates)

        print(f"   📊 Internal_dmc/{internal_folder}: {len(internal_files)} files")
        print(f"   📊 SDCard_DMC/{sdcard_folder}: {len(sdcard_files)} files")
        print(f"   🔄 Duplicates found: {len(duplicates)} ({folder_comparison['duplicate_percentage']:.1f}%)")
        print(f"   💾 Duplicate data size: {format_size(folder_comparison['duplicate_size_bytes'])}")

        if len(duplicates) > 0:
            print(f"   ⚠️  HIGH DUPLICATION - Possible sync misconfiguration!")

    return duplicate_analysis

def format_size(bytes_size):
    """Format bytes as human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"

def estimate_processing_time(mp4_count, total_files):
    """
    Estimate processing time based on file counts
    
    Args:
        mp4_count: Number of MP4 files requiring AI analysis
        total_files: Total number of files to organize
        
    Returns:
        dict: Time estimates
    """
    # Performance assumptions (based on documentation and testing)
    file_organization_seconds_per_file = 1.5  # File copy + metadata + deduplication
    ai_analysis_seconds_per_video = 32  # LM Studio + thumbnail extraction + base64 validation
    notes_generation_seconds_per_video = 1  # Notes file creation
    
    # Calculate components
    organization_time = total_files * file_organization_seconds_per_file
    ai_analysis_time = mp4_count * ai_analysis_seconds_per_video
    notes_time = mp4_count * notes_generation_seconds_per_video
    
    total_seconds = organization_time + ai_analysis_time + notes_time
    
    return {
        'file_organization_hours': organization_time / 3600,
        'ai_analysis_hours': ai_analysis_time / 3600,
        'notes_generation_hours': notes_time / 3600,
        'total_hours': total_seconds / 3600,
        'total_days': total_seconds / (3600 * 24),
        'breakdown': {
            'organization_percent': (organization_time / total_seconds) * 100,
            'ai_analysis_percent': (ai_analysis_time / total_seconds) * 100,
            'notes_percent': (notes_time / total_seconds) * 100
        }
    }

def main():
    """Main execution function"""
    print("🔍 Production File Counter - Accurate MP4 Analysis")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    if not config:
        return 1
    
    # Get production source folders
    source_folders = resolve_production_paths(config)
    if not source_folders:
        return 1
    
    print(f"📂 Scanning {len(source_folders)} production source folders:")
    for folder in source_folders:
        print(f"   • {folder}")
    print()
    
    # Scan all folders with detailed file collection for duplicate analysis
    total_results = defaultdict(int)
    folder_results = {}
    internal_results = {}
    sdcard_results = {}
    scan_start_time = time.time()

    for folder in source_folders:
        folder_name = Path(folder).name
        folder_type = 'Internal_dmc' if 'Internal_dmc' in folder else 'SDCard_DMC'

        # Collect detailed file information for duplicate analysis
        results = scan_folder_for_files(folder, collect_file_details=True)
        folder_results[folder_name] = results

        # Separate results by folder type for duplicate analysis
        if folder_type == 'Internal_dmc':
            internal_results[folder_name] = results
        else:
            sdcard_results[folder_name] = results

        # Accumulate totals
        for key, value in results.items():
            if isinstance(value, (int, float)) and key != 'scan_time_seconds':
                total_results[key] += value
    
    total_scan_time = time.time() - scan_start_time
    
    # Display detailed results by folder type
    print(f"\n📊 Detailed Results by Folder:")
    print("-" * 90)
    print(f"{'Folder':<20} {'Type':<12} {'Total':<8} {'Videos':<8} {'MP4s':<8} {'Size':<12} {'Status'}")
    print("-" * 90)

    for folder_name, results in folder_results.items():
        folder_type = 'Internal_dmc' if folder_name in internal_results else 'SDCard_DMC'

        if results['accessible']:
            status = "✅ OK"
            size_str = format_size(results['total_size_bytes'])
        else:
            status = f"❌ {results['error'][:20]}..."
            size_str = "N/A"

        print(f"{folder_name:<20} {folder_type:<12} {results['total_files']:<8} {results['video_files']:<8} "
              f"{results['mp4_files']:<8} {size_str:<12} {status}")

    # Analyze duplicates between Internal_dmc and SDCard_DMC
    duplicate_analysis = analyze_duplicates_between_folders(internal_results, sdcard_results)
    
    # Display summary with duplicate analysis
    print(f"\n🎯 PRODUCTION SCALE SUMMARY")
    print("=" * 50)
    print(f"📁 Total files found: {total_results['total_files']:,}")
    print(f"🎬 Total video files: {total_results['video_files']:,}")
    print(f"📹 MP4 files (AI analysis): {total_results['mp4_files']:,}")
    print(f"📸 Picture files: {total_results['picture_files']:,}")
    print(f"📄 Other files: {total_results['other_files']:,}")
    print(f"💾 Total data size: {format_size(total_results['total_size_bytes'])}")
    print(f"🎬 Video data size: {format_size(total_results['video_size_bytes'])}")
    print(f"⏱️  Scan completed in: {total_scan_time:.1f} seconds")

    # Display duplicate analysis summary
    if duplicate_analysis['total_duplicates'] > 0:
        print(f"\n⚠️  DUPLICATE ANALYSIS SUMMARY")
        print("=" * 50)
        print(f"🔄 Total duplicate files: {duplicate_analysis['total_duplicates']:,}")
        print(f"💾 Duplicate data size: {format_size(duplicate_analysis['duplicate_size_bytes'])}")
        duplicate_percentage = (duplicate_analysis['total_duplicates'] / total_results['total_files']) * 100
        print(f"📊 Duplication rate: {duplicate_percentage:.1f}% of all files")

        # Adjusted estimates accounting for duplicates
        unique_files = total_results['total_files'] - duplicate_analysis['total_duplicates']
        duplicate_mp4_count = len([d for d in duplicate_analysis['duplicate_files'] if d['name'].lower().endswith('.mp4')])
        unique_mp4s = total_results['mp4_files'] - duplicate_mp4_count

        print(f"\n📋 ADJUSTED COUNTS (removing duplicates):")
        print(f"📁 Unique files to process: {unique_files:,}")
        print(f"📹 Unique MP4s for AI analysis: {unique_mp4s:,}")

        if duplicate_percentage > 50:
            print(f"\n🚨 HIGH DUPLICATION DETECTED!")
            print(f"   • {duplicate_percentage:.1f}% of files appear to be duplicates")
            print(f"   • This suggests a phone sync misconfiguration")
            print(f"   • Internal_dmc and SDCard_DMC may be syncing the same content")
            print(f"   • Consider reviewing your phone sync setup")
    else:
        print(f"\n✅ No significant duplicates detected between Internal_dmc and SDCard_DMC")
    
    # Calculate time estimates (use adjusted counts if duplicates found)
    if total_results['mp4_files'] > 0:
        # Use adjusted counts if significant duplicates found
        if duplicate_analysis['total_duplicates'] > 0:
            unique_files = total_results['total_files'] - duplicate_analysis['total_duplicates']
            duplicate_mp4_count = len([d for d in duplicate_analysis['duplicate_files'] if d['name'].lower().endswith('.mp4')])
            unique_mp4s = total_results['mp4_files'] - duplicate_mp4_count
            estimates = estimate_processing_time(unique_mp4s, unique_files)
            estimate_note = f" (adjusted for {duplicate_analysis['total_duplicates']:,} duplicates)"
        else:
            estimates = estimate_processing_time(total_results['mp4_files'], total_results['total_files'])
            estimate_note = ""
        
        print(f"\n⏱️  FIRST RUN TIME ESTIMATE{estimate_note}")
        print("=" * 50)
        print(f"📁 File organization: {estimates['file_organization_hours']:.1f} hours")
        print(f"🤖 AI video analysis: {estimates['ai_analysis_hours']:.1f} hours")
        print(f"📝 Notes generation: {estimates['notes_generation_hours']:.1f} hours")
        print(f"⏰ TOTAL TIME: {estimates['total_hours']:.1f} hours ({estimates['total_days']:.1f} days)")
        
        print(f"\n📊 Time Breakdown:")
        print(f"   • File organization: {estimates['breakdown']['organization_percent']:.1f}%")
        print(f"   • AI analysis: {estimates['breakdown']['ai_analysis_percent']:.1f}%")
        print(f"   • Notes generation: {estimates['breakdown']['notes_percent']:.1f}%")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if estimates['total_hours'] > 48:
            print("   🔥 LARGE DATASET - Consider batch processing over multiple days")
            print("   📅 Suggested: Process 20-30 days at a time using production dry run script")
        elif estimates['total_hours'] > 24:
            print("   ⏰ MEDIUM DATASET - Plan for weekend processing")
            print("   📅 Suggested: Start Friday evening, complete by Monday")
        else:
            print("   ✅ MANAGEABLE DATASET - Can complete in single session")
        
        print(f"   🚀 After first run: Daily processing will take 2-5 minutes for new files")
    
    print(f"\n✅ File count analysis complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
