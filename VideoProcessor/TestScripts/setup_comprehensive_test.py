#!/usr/bin/env python3
"""
Comprehensive Test Setup Script
Creates test files and scenarios for validating the PhoneSync + VideoProcessor system
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# Add the modules directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))

from config_manager import ConfigManager
from logger_setup import setup_logging

def create_test_video(output_path, duration_seconds=10, width=320, height=240):
    """Create a test video file using FFmpeg"""
    try:
        cmd = [
            'ffmpeg', '-y',  # Overwrite existing files
            '-f', 'lavfi',
            '-i', f'testsrc=duration={duration_seconds}:size={width}x{height}:rate=30',
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-crf', '28',
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return True
        else:
            print(f"FFmpeg error: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error creating test video: {e}")
        return False

def create_test_image(output_path, width=640, height=480):
    """Create a test image file using FFmpeg"""
    try:
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'testsrc=duration=1:size={width}x{height}:rate=1',
            '-frames:v', '1',
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        print(f"Error creating test image: {e}")
        return False

def setup_comprehensive_test_environment():
    """Set up comprehensive test environment with various file scenarios"""
    
    print("=== Comprehensive Test Environment Setup ===")
    
    # Create temporary directories
    test_root = Path(tempfile.mkdtemp(prefix="phonesync_test_"))
    source_dir = test_root / "Source"
    target_root = test_root / "Target"
    
    # Create directory structure
    source_dir.mkdir(parents=True)
    (target_root / "Pictures").mkdir(parents=True)
    (target_root / "Videos").mkdir(parents=True)
    (target_root / "Videos" / "Wudan").mkdir(parents=True)
    (target_root / "Video_Notes").mkdir(parents=True)
    
    print(f"✅ Test directories created:")
    print(f"   Source: {source_dir}")
    print(f"   Target: {target_root}")
    
    # Test Case 1: Standard Date-Named Files
    print("\n📁 Creating Test Case 1: Standard Date-Named Files")
    test_files = [
        # Standard phone format videos
        ("20250412_110016_1.mp4", 15),  # Should go to regular videos
        ("20250406_070000_1.mp4", 20),  # Sunday 7:00 AM - should go to Wudan (after 2021)
        ("20250407_070000_1.mp4", 25),  # Monday 7:00 AM - should go to Wudan
        ("20250409_200000_1.mp4", 30),  # Wednesday 8:00 PM - should go to Wudan
        ("20250410_120000_1.mp4", 18),  # Thursday 12:00 PM - should go to regular videos
        
        # Standard phone format images
        ("20250412_110016_1.jpg", None),
        ("20250406_070000_1.jpg", None),
    ]
    
    for filename, duration in test_files:
        file_path = source_dir / filename
        if filename.endswith('.mp4'):
            if create_test_video(file_path, duration or 10):
                print(f"   ✅ Created: {filename} ({duration}s)")
            else:
                print(f"   ❌ Failed: {filename}")
        else:
            if create_test_image(file_path):
                print(f"   ✅ Created: {filename}")
            else:
                print(f"   ❌ Failed: {filename}")
    
    # Test Case 2: Non-Date-Named Files
    print("\n📁 Creating Test Case 2: Non-Date-Named Files")
    non_date_files = [
        ("M4H01890.MP4", 12),
        ("IMG_1234.JPG", None),
        ("VID_5678.mp4", 8),
        ("random_video.mp4", 22),
        ("photo.jpeg", None),
    ]
    
    for filename, duration in non_date_files:
        file_path = source_dir / filename
        if filename.lower().endswith(('.mp4', '.avi', '.mov')):
            if create_test_video(file_path, duration or 10):
                print(f"   ✅ Created: {filename} ({duration}s)")
            else:
                print(f"   ❌ Failed: {filename}")
        else:
            if create_test_image(file_path):
                print(f"   ✅ Created: {filename}")
            else:
                print(f"   ❌ Failed: {filename}")
    
    # Test Case 3: Files with Special Characters
    print("\n📁 Creating Test Case 3: Files with Special Characters")
    special_files = [
        ("20250615_102535 (1).mp4", 14),  # Space and parentheses
        ("video file with spaces.mp4", 16),
        ("file-with-dashes.jpg", None),
        ("file_with_underscores.mp4", 11),
    ]
    
    for filename, duration in special_files:
        file_path = source_dir / filename
        if filename.lower().endswith(('.mp4', '.avi', '.mov')):
            if create_test_video(file_path, duration or 10):
                print(f"   ✅ Created: {filename}")
            else:
                print(f"   ❌ Failed: {filename}")
        else:
            if create_test_image(file_path):
                print(f"   ✅ Created: {filename}")
            else:
                print(f"   ❌ Failed: {filename}")
    
    # Test Case 4: Pre-existing Files in Target (for deduplication testing)
    print("\n📁 Creating Test Case 4: Pre-existing Files in Target")
    
    # Create some target folders with existing files
    existing_folders = [
        (target_root / "Videos" / "2025_04_12", [
            ("20250412_292993_1_KungFu_GimStyle.mp4", 18),  # Appended text version
            ("existing_video.mp4", 20),
        ]),
        (target_root / "Pictures" / "2025_04_12", [
            ("20250412_110016_1_PhotoEdit.jpg", None),  # Appended text version
        ]),
        (target_root / "Videos" / "Wudan" / "2025_04_07", [
            ("20250407_070000_1_MorningPractice.mp4", 25),  # Wudan with appended text
        ]),
    ]
    
    for folder_path, files in existing_folders:
        folder_path.mkdir(parents=True, exist_ok=True)
        for filename, duration in files:
            file_path = folder_path / filename
            if filename.lower().endswith(('.mp4', '.avi', '.mov')):
                if create_test_video(file_path, duration or 10):
                    print(f"   ✅ Pre-existing: {folder_path.name}/{filename}")
                else:
                    print(f"   ❌ Failed: {folder_path.name}/{filename}")
            else:
                if create_test_image(file_path):
                    print(f"   ✅ Pre-existing: {folder_path.name}/{filename}")
                else:
                    print(f"   ❌ Failed: {folder_path.name}/{filename}")
    
    # Test Case 5: Custom Folder Names (for flexible matching)
    print("\n📁 Creating Test Case 5: Custom Folder Names")
    custom_folders = [
        (target_root / "Videos" / "2025_06_15_BirthdayParty", []),
        (target_root / "Pictures" / "2025_08_30_VacationPhotos", []),
        (target_root / "Videos" / "Wudan" / "2025_04_06_SundayClass", []),
    ]
    
    for folder_path, _ in custom_folders:
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Custom folder: {folder_path.name}")
    
    # Test Case 6: Files that should match custom folders
    print("\n📁 Creating Test Case 6: Files for Custom Folders")
    custom_folder_files = [
        ("20250615_140000_1.mp4", 16),  # Should go to BirthdayParty folder
        ("20250830_120000_1.jpg", None),  # Should go to VacationPhotos folder
        ("20250406_100000_1.mp4", 28),  # Should go to SundayClass folder (Wudan time)
    ]
    
    for filename, duration in custom_folder_files:
        file_path = source_dir / filename
        if filename.lower().endswith(('.mp4', '.avi', '.mov')):
            if create_test_video(file_path, duration or 10):
                print(f"   ✅ Created: {filename} (for custom folder)")
            else:
                print(f"   ❌ Failed: {filename}")
        else:
            if create_test_image(file_path):
                print(f"   ✅ Created: {filename} (for custom folder)")
            else:
                print(f"   ❌ Failed: {filename}")
    
    # Create test configuration file
    print("\n⚙️ Creating Test Configuration")
    test_config = {
        'source_folders': [str(source_dir)],
        'target_paths': {
            'pictures': str(target_root / "Pictures"),
            'videos': str(target_root / "Videos"),
            'wudan': str(target_root / "Videos" / "Wudan"),
        },
        'file_extensions': {
            'pictures': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
            'videos': ['.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv', '.webm'],
        },
        'wudan_rules': {
            'description': 'Time ranges when video files should go to Wudan folder',
            'before_2021': {
                'days_of_week': [1, 2, 3, 4, 6],
                'time_ranges': [
                    {'start': '05:00', 'end': '08:00'},
                    {'start': '18:00', 'end': '22:00'}
                ]
            },
            'after_2021': {
                'days_of_week': [0, 1, 2, 3, 4, 6],
                'time_ranges': {
                    0: [{'start': '08:00', 'end': '13:00'}],  # Sunday
                    1: [{'start': '05:00', 'end': '08:00'}, {'start': '18:00', 'end': '21:00'}],  # Monday
                    2: [{'start': '05:00', 'end': '08:00'}, {'start': '18:00', 'end': '21:00'}],  # Tuesday
                    3: [{'start': '18:00', 'end': '22:00'}],  # Wednesday
                    4: [{'start': '05:00', 'end': '08:00'}, {'start': '18:00', 'end': '21:00'}],  # Thursday
                    6: [{'start': '08:00', 'end': '16:00'}]   # Saturday
                }
            }
        },
        'ai_settings': {
            'lm_studio_url': 'http://localhost:1234/v1/chat/completions',
            'model': 'mimo-vl-7b-rl@q8_k_xl',
            'temperature': 0.4,
            'max_tokens': 150,
            'timeout_seconds': 30,
            'kung_fu_prompt': '''Analyze this video thumbnail for kung fu or martial arts content. Look for:
- Martial arts poses, stances, or movements
- Fighting techniques or combat training
- Traditional Chinese martial arts (kung fu, wushu, tai chi)
- Training equipment (wooden dummies, weapons, mats)
- Text mentioning martial arts terms
- People in martial arts uniforms or practicing forms

If you see ANY of these elements, respond with YES. Only respond with NO if there are clearly no martial arts elements present.

After your YES/NO answer, provide a brief description of what you observed.'''
        },
        'video_processing': {
            'thumbnail_extraction': 'dynamic_midpoint',
            'thumbnail_scale': '320:240',
            'ffmpeg_timeout': 30,
            'process_existing': False,
        },
        'options': {
            'enable_deduplication': True,
            'use_hash_comparison': False,
            'create_missing_folders': True,
            'dry_run': False,
            'verbose_logging': True,
            'force_recopy_if_newer': True,
            'copy_files': True,
            'enable_video_analysis': True,
        },
        'logging': {
            'enabled': True,
            'log_path': 'logs/test_phone_sync.log',
            'max_log_size_mb': 10,
            'keep_log_days': 30,
            'log_level': 'DEBUG',
            'rotation_enabled': True,
        },
        'performance': {
            'max_concurrent_operations': 4,
            'cache_existing_files': True,
            'progress_reporting_interval': 10,
        },
        'development': {
            'test_mode': False,
            'mock_ai_responses': False,
            'skip_video_analysis': False,
        }
    }
    
    # Save test config
    import yaml
    test_config_path = test_root / "test_config.yaml"
    with open(test_config_path, 'w') as f:
        yaml.dump(test_config, f, default_flow_style=False, indent=2)
    
    print(f"   ✅ Test config saved: {test_config_path}")
    
    # Summary
    print(f"\n🎉 Test Environment Setup Complete!")
    print(f"📂 Test Root: {test_root}")
    print(f"📁 Source Files: {len(list(source_dir.glob('*')))} files created")
    print(f"📁 Target Structure: Ready with pre-existing files")
    print(f"⚙️  Config File: {test_config_path}")
    
    print(f"\n🧪 To run tests:")
    print(f"   ./venv/Scripts/python.exe VideoProcessor/phone_sync.py --config {test_config_path} --dry-run")
    print(f"   ./venv/Scripts/python.exe VideoProcessor/main.py --config {test_config_path}")
    
    return test_root, test_config_path

if __name__ == "__main__":
    test_root, config_path = setup_comprehensive_test_environment()

    print(f"\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Review the test files created")
    print("2. Run the comprehensive test validation script")
    print("3. Execute the system with test configuration")
    print("4. Validate results against expected outcomes")
    print(f"\nTest environment ready at: {test_root}")
    print(f"Config file: {config_path}")
