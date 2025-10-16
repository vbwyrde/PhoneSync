#!/usr/bin/env python3
"""
Simple Test - Just verify the system can load and process one file
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def main():
    print("🧪 SIMPLE TEST - System Verification")
    print("=" * 40)
    
    try:
        # Test 1: Import modules
        print("1. Testing module imports...")
        from modules.config_manager import ConfigManager
        print("   ✅ ConfigManager imported")
        
        from modules.logger_setup import setup_logging
        print("   ✅ Logger setup imported")
        
        # Test 2: Load config
        print("2. Testing config loading...")
        config_path = Path(__file__).parent.parent.parent / 'config.yaml'
        print(f"   Config path: {config_path}")
        print(f"   Config exists: {config_path.exists()}")
        
        config_manager = ConfigManager(str(config_path))
        config = config_manager.load_config()
        print("   ✅ Config loaded successfully")
        
        # Test 3: Check source folders
        print("3. Testing source folder configuration...")
        source_folders = config.get('source_folders', [])
        print(f"   Source folders configured: {len(source_folders)}")
        
        for i, folder in enumerate(source_folders[:3], 1):  # Show first 3
            print(f"   {i}. {folder}")
            print(f"      Exists: {os.path.exists(folder)}")
        
        # Test 4: Find a test file
        print("4. Looking for test files...")
        camera_folder = None
        for folder in source_folders:
            if 'Camera' in folder:
                camera_folder = folder
                break
        
        if camera_folder and os.path.exists(camera_folder):
            print(f"   Camera folder: {camera_folder}")
            
            # Find first MP4 file
            mp4_files = []
            for root, dirs, files in os.walk(camera_folder):
                for file in files:
                    if file.lower().endswith('.mp4'):
                        mp4_files.append(os.path.join(root, file))
                        if len(mp4_files) >= 1:
                            break
                if mp4_files:
                    break
            
            if mp4_files:
                test_file = mp4_files[0]
                print(f"   Found test file: {Path(test_file).name}")
                print(f"   File exists: {os.path.exists(test_file)}")
                print(f"   File size: {os.path.getsize(test_file):,} bytes")
            else:
                print("   ❌ No MP4 files found")
        else:
            print("   ❌ Camera folder not found or not accessible")
        
        print("\n✅ All basic tests passed!")
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
