#!/usr/bin/env python3
"""
Processing State Management Utility
Provides commands to view, reset, and manage the incremental processing state
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path so we can import modules
sys.path.append(str(Path(__file__).parent))

from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logging
from modules.processing_state_manager import ProcessingStateManager

def show_state():
    """Display current processing state"""
    print("📊 Current Processing State")
    print("=" * 40)
    
    config_manager = ConfigManager("config.yaml")
    config = config_manager.load_config()
    logger = setup_logging(config)
    
    state_manager = ProcessingStateManager(config, logger)
    state_info = state_manager.get_state_info()
    filter_info = state_manager.get_incremental_filter_info()
    
    if state_info['first_run']:
        print("🆕 Status: First run - no previous processing state")
        print(f"📁 Tracked files: {state_info['processed_files_count']}")
    else:
        print("🔄 Status: Incremental processing enabled")
        print(f"📅 Last run: {state_info['last_run']}")
        print(f"📄 Last processed file: {state_info['last_processed_file']}")
        print(f"📊 Total files processed: {state_info['total_files_processed']}")
        print(f"🎬 Total videos analyzed: {state_info['total_videos_analyzed']}")
        print(f"📁 Tracked files: {state_info['processed_files_count']}")
    
    print(f"\n🔍 Processing mode: {filter_info['mode']}")
    print(f"💡 Reason: {filter_info['reason']}")
    
    # Show state files
    state_dir = Path("VideoProcessor/state")
    if state_dir.exists():
        print(f"\n📂 State directory: {state_dir}")
        
        state_file = state_dir / "processing_state.json"
        processed_file = state_dir / "processed_files.json"
        
        if state_file.exists():
            size = state_file.stat().st_size
            print(f"   📄 processing_state.json ({size} bytes)")
        
        if processed_file.exists():
            size = processed_file.stat().st_size
            print(f"   📄 processed_files.json ({size} bytes)")
    else:
        print("\n📂 No state directory found")

def reset_state():
    """Reset all processing state"""
    print("⚠️  Resetting Processing State")
    print("=" * 40)
    
    response = input("This will delete all processing history. Continue? (y/N): ")
    if response.lower() != 'y':
        print("❌ Reset cancelled")
        return
    
    config_manager = ConfigManager("config.yaml")
    config = config_manager.load_config()
    logger = setup_logging(config)
    
    state_manager = ProcessingStateManager(config, logger)
    state_manager.reset_state()
    
    print("✅ Processing state reset successfully")
    print("Next run will process all files as if it's the first run")

def show_processed_files(limit=10):
    """Show list of processed files"""
    print(f"📋 Recently Processed Files (showing {limit})")
    print("=" * 50)
    
    state_dir = Path("VideoProcessor/state")
    processed_file = state_dir / "processed_files.json"
    
    if not processed_file.exists():
        print("❌ No processed files database found")
        return
    
    try:
        with open(processed_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        processed_files = data.get('processed_files', [])
        total_count = data.get('total_count', len(processed_files))
        last_updated = data.get('last_updated', 'Unknown')
        
        print(f"📊 Total tracked files: {total_count}")
        print(f"🕒 Last updated: {last_updated}")
        print(f"\n📄 Recent files:")
        
        for i, file_id in enumerate(processed_files[-limit:], 1):
            # Parse file ID: path|size|date
            parts = file_id.split('|')
            if len(parts) >= 3:
                path = parts[0]
                size = parts[1]
                date = parts[2]
                filename = Path(path).name
                print(f"   {i:2d}. {filename} ({size} bytes, {date[:19]})")
            else:
                print(f"   {i:2d}. {file_id}")
                
    except Exception as e:
        print(f"❌ Error reading processed files: {e}")

def show_stats():
    """Show detailed processing statistics"""
    print("📈 Processing Statistics")
    print("=" * 40)
    
    state_dir = Path("VideoProcessor/state")
    
    # Main state file
    state_file = state_dir / "processing_state.json"
    if state_file.exists():
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            print("📊 Last Run Statistics:")
            print(f"   🕒 Timestamp: {state_data.get('last_run_timestamp', 'N/A')}")
            print(f"   📄 Last file: {state_data.get('last_processed_file', 'N/A')}")
            print(f"   📅 Date: {state_data.get('last_processed_date', 'N/A')}")
            print(f"   📁 Files processed: {state_data.get('total_files_processed', 0)}")
            print(f"   🎬 Videos analyzed: {state_data.get('total_videos_analyzed', 0)}")
            print(f"   🔧 Version: {state_data.get('processing_version', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Error reading state file: {e}")
    else:
        print("❌ No state file found")
    
    # Processed files database
    processed_file = state_dir / "processed_files.json"
    if processed_file.exists():
        try:
            with open(processed_file, 'r', encoding='utf-8') as f:
                processed_data = json.load(f)
            
            processed_files = processed_data.get('processed_files', [])
            
            print(f"\n📋 Processed Files Database:")
            print(f"   📊 Total files: {len(processed_files)}")
            print(f"   🕒 Last updated: {processed_data.get('last_updated', 'N/A')}")
            
            # Analyze file types
            video_count = sum(1 for f in processed_files if '.mp4' in f.lower() or '.avi' in f.lower() or '.mov' in f.lower())
            photo_count = len(processed_files) - video_count
            
            print(f"   🎬 Videos: {video_count}")
            print(f"   📷 Photos: {photo_count}")
            
        except Exception as e:
            print(f"❌ Error reading processed files: {e}")
    else:
        print("\n❌ No processed files database found")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Processing State Management Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_processing_state.py show          # Show current state
  python manage_processing_state.py reset         # Reset all state
  python manage_processing_state.py files         # Show processed files
  python manage_processing_state.py files --limit 20  # Show 20 recent files
  python manage_processing_state.py stats         # Show detailed statistics
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show current processing state')
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset all processing state')
    
    # Files command
    files_parser = subparsers.add_parser('files', help='Show processed files')
    files_parser.add_argument('--limit', type=int, default=10, help='Number of files to show (default: 10)')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show detailed statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'show':
            show_state()
        elif args.command == 'reset':
            reset_state()
        elif args.command == 'files':
            show_processed_files(args.limit)
        elif args.command == 'stats':
            show_stats()
        else:
            parser.print_help()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
