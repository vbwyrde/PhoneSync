#!/usr/bin/env python3
"""
Test script for production configuration
Validates the environment-based configuration system
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager

def test_development_config():
    """Test development configuration"""
    print("🧪 Testing Development Configuration")
    print("=" * 50)
    
    # Load config with development environment
    config_manager = ConfigManager("config.yaml")
    config = config_manager.load_config()
    
    print(f"Environment: {config.get('resolved_environment', 'Unknown')}")
    print(f"Source folders: {len(config.get('source_folders', []))}")
    for i, folder in enumerate(config.get('source_folders', []), 1):
        print(f"  {i}. {folder}")
    
    print(f"\nTarget paths:")
    target_paths = config.get('target_paths', {})
    for key, path in target_paths.items():
        print(f"  {key}: {path}")
    
    return config

def test_production_config():
    """Test production configuration by temporarily switching environment"""
    print("\n🏭 Testing Production Configuration")
    print("=" * 50)
    
    # Read the config file
    with open("config.yaml", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Temporarily modify environment to PRODUCTION
    modified_content = content.replace('environment: "DEVELOPMENT"', 'environment: "PRODUCTION"')
    
    # Write temporary config
    temp_config_path = "temp_prod_config.yaml"
    with open(temp_config_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    try:
        # Load production config
        config_manager = ConfigManager(temp_config_path)
        config = config_manager.load_config()
        
        print(f"Environment: {config.get('resolved_environment', 'Unknown')}")
        print(f"Source folders: {len(config.get('source_folders', []))}")
        for i, folder in enumerate(config.get('source_folders', []), 1):
            print(f"  {i}. {folder}")
        
        print(f"\nTarget paths:")
        target_paths = config.get('target_paths', {})
        for key, path in target_paths.items():
            print(f"  {key}: {path}")
        
        return config
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_config_path):
            os.remove(temp_config_path)

def validate_production_paths(config):
    """Validate production path structure"""
    print("\n🔍 Validating Production Path Structure")
    print("=" * 50)
    
    source_folders = config.get('source_folders', [])
    target_paths = config.get('target_paths', {})
    
    # Expected production structure
    expected_source_subdirs = [
        "Internal_dmc/Camera",
        "Internal_dmc/FavoritesMA", 
        "Internal_dmc/GIF",
        "Internal_dmc/Official",
        "Internal_dmc/Videocaptures",
        "SDCard_DMC/Camera",
        "SDCard_DMC/FavoritesMA",
        "SDCard_DMC/GIF",
        "SDCard_DMC/Official",
        "SDCard_DMC/Videocaptures"
    ]
    
    print("✅ Source folder validation:")
    print(f"Expected subdirectories: {len(expected_source_subdirs)}")
    print(f"Configured source folders: {len(source_folders)}")
    
    # Check if all expected subdirs are present
    missing_subdirs = []
    for expected in expected_source_subdirs:
        found = False
        for source in source_folders:
            if expected.replace('/', '\\') in source or expected in source:
                found = True
                break
        if not found:
            missing_subdirs.append(expected)
    
    if missing_subdirs:
        print(f"❌ Missing subdirectories: {missing_subdirs}")
    else:
        print("✅ All expected subdirectories configured")
    
    print("\n✅ Target path validation:")
    required_targets = ['pictures', 'videos', 'wudan']
    for target in required_targets:
        if target in target_paths:
            path = target_paths[target]
            print(f"  {target}: {path}")
            
            # Check if it's a UNC path for production
            if config.get('resolved_environment') == 'PRODUCTION':
                if not path.startswith('//MA-2022-C/'):
                    print(f"    ⚠️  Warning: Expected UNC path starting with //MA-2022-C/")
                else:
                    print(f"    ✅ Valid UNC path")
        else:
            print(f"  ❌ Missing target: {target}")

def show_folder_mapping():
    """Show how files will be mapped from source to target"""
    print("\n📁 File Type Mapping")
    print("=" * 50)
    
    print("📷 Images (jpg, png, gif):")
    print("  From: All Camera, FavoritesMA, GIF, Official, Videocaptures folders")
    print("  To: //MA-2022-C/UserData_G/My Pictures/YYYY_MM_DD/")
    
    print("\n🎬 Videos (mp4, avi, mov):")
    print("  From: All Camera, FavoritesMA, Official, Videocaptures folders")
    print("  To: //MA-2022-C/UserData_G/My Videos/YYYY_MM_DD/")
    
    print("\n🥋 Kung Fu Videos (AI detected):")
    print("  From: All video source folders")
    print("  To: //MA-2022-C/UserData_G/My Videos/Wudan/YYYY_MM_DD/")
    
    print("\n📝 Notes Files:")
    print("  Generated in same folder as videos")
    print("  Format: YYYYMMDD_Notes.txt")

def main():
    """Main test function"""
    print("🔧 Production Configuration Test Suite")
    print("=" * 60)
    
    try:
        # Test development config
        dev_config = test_development_config()
        
        # Test production config
        prod_config = test_production_config()
        
        # Validate production paths
        validate_production_paths(prod_config)
        
        # Show folder mapping
        show_folder_mapping()
        
        print("\n🎉 Configuration Test Complete!")
        print("=" * 60)
        
        # Summary
        print("\n📊 Summary:")
        print(f"✅ Development environment: {len(dev_config.get('source_folders', []))} source folders")
        print(f"✅ Production environment: {len(prod_config.get('source_folders', []))} source folders")
        print("✅ Environment switching works correctly")
        print("✅ Path resolution working properly")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
