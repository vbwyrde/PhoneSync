#!/usr/bin/env python3
"""
Environment Switching Utility
Easily switch between DEVELOPMENT and PRODUCTION environments
"""

import argparse
import sys
from pathlib import Path

def switch_environment(target_env: str):
    """
    Switch the environment in config.yaml
    
    Args:
        target_env: Either 'DEVELOPMENT' or 'PRODUCTION'
    """
    config_path = Path("config.yaml")
    
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        return False
    
    # Read current config
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find current environment
    current_env = None
    if 'environment: "DEVELOPMENT"' in content:
        current_env = "DEVELOPMENT"
    elif 'environment: "PRODUCTION"' in content:
        current_env = "PRODUCTION"
    else:
        print("❌ Could not determine current environment from config.yaml")
        return False
    
    if current_env == target_env:
        print(f"✅ Already in {target_env} environment")
        return True
    
    # Switch environment
    if target_env == "PRODUCTION":
        new_content = content.replace('environment: "DEVELOPMENT"', 'environment: "PRODUCTION"')
    else:
        new_content = content.replace('environment: "PRODUCTION"', 'environment: "DEVELOPMENT"')
    
    # Write updated config
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Switched from {current_env} to {target_env} environment")
    return True

def show_current_environment():
    """Show the current environment configuration"""
    config_path = Path("config.yaml")
    
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        return
    
    # Read current config
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find current environment
    if 'environment: "DEVELOPMENT"' in content:
        current_env = "DEVELOPMENT"
    elif 'environment: "PRODUCTION"' in content:
        current_env = "PRODUCTION"
    else:
        print("❌ Could not determine current environment from config.yaml")
        return
    
    print(f"📊 Current Environment: {current_env}")
    
    # Load and show configuration details
    try:
        sys.path.append(str(Path(__file__).parent))
        from modules.config_manager import ConfigManager
        
        config_manager = ConfigManager("config.yaml")
        config = config_manager.load_config()
        
        source_folders = config.get('source_folders', [])
        target_paths = config.get('target_paths', {})
        
        print(f"📁 Source folders: {len(source_folders)}")
        for i, folder in enumerate(source_folders[:3], 1):  # Show first 3
            print(f"   {i}. {folder}")
        if len(source_folders) > 3:
            print(f"   ... and {len(source_folders) - 3} more")
        
        print(f"🎯 Target paths:")
        for key, path in target_paths.items():
            print(f"   {key}: {path}")
            
    except Exception as e:
        print(f"⚠️  Could not load configuration details: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Environment Switching Utility for PhoneSync + VideoProcessor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python switch_environment.py show                    # Show current environment
  python switch_environment.py switch PRODUCTION       # Switch to production
  python switch_environment.py switch DEVELOPMENT      # Switch to development
  python switch_environment.py prod                    # Shortcut for production
  python switch_environment.py dev                     # Shortcut for development
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show current environment')
    
    # Switch command
    switch_parser = subparsers.add_parser('switch', help='Switch environment')
    switch_parser.add_argument('environment', choices=['PRODUCTION', 'DEVELOPMENT'], 
                              help='Target environment')
    
    # Shortcut commands
    prod_parser = subparsers.add_parser('prod', help='Switch to PRODUCTION (shortcut)')
    dev_parser = subparsers.add_parser('dev', help='Switch to DEVELOPMENT (shortcut)')
    
    args = parser.parse_args()
    
    if not args.command:
        # Default to showing current environment
        show_current_environment()
        return
    
    try:
        if args.command == 'show':
            show_current_environment()
        elif args.command == 'switch':
            success = switch_environment(args.environment)
            if success:
                print("\n📋 Updated configuration:")
                show_current_environment()
        elif args.command == 'prod':
            success = switch_environment('PRODUCTION')
            if success:
                print("\n📋 Updated configuration:")
                show_current_environment()
        elif args.command == 'dev':
            success = switch_environment('DEVELOPMENT')
            if success:
                print("\n📋 Updated configuration:")
                show_current_environment()
        else:
            parser.print_help()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
