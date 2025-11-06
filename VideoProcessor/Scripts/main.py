#!/usr/bin/env python3
"""
PhoneSync + VideoProcessor Unified System
Main entry point for the unified file organization and AI video analysis system

Usage:
    python main.py                    # Run full processing
    python main.py --test             # Test all systems
    python main.py --dry-run          # Preview what would be processed
    python main.py --config custom.yaml  # Use custom config file
"""

import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add modules directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logging
from modules.unified_processor import UnifiedProcessor

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="PhoneSync + VideoProcessor Unified System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                       # Run full processing
  python main.py --test                # Test all systems
  python main.py --dry-run             # Preview without copying files
  python main.py --config custom.yaml  # Use custom configuration
  python main.py --verbose             # Enable verbose logging
        """
    )
    
    print("Current working directory:", os.getcwd())

    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Configuration file path (default: config.yaml)'
    )
    
    parser.add_argument(
        '--test', '-t',
        action='store_true',
        help='Test all system components without processing files'
    )
    
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Preview what would be processed without copying files'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging output'
    )
    
    parser.add_argument(
        '--output-json',
        help='Save results to JSON file'
    )
    
    return parser.parse_args()

def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("PhoneSync + VideoProcessor Unified System")
    print("File Organization + AI Video Analysis")
    print("=" * 60)

def print_test_results(test_results):
    """Print system test results"""
    print("\n=== System Test Results ===")
    
    # Configuration
    config_result = test_results['configuration']
    print(f"[OK] Configuration: {config_result['source_folders']} sources, "
          f"{config_result['target_paths']} targets, {config_result['wudan_rules']} rules")

    # AI Connection
    ai_result = test_results['ai_connection']
    if ai_result['success']:
        print(f"[OK] AI Connection: Connected to LM Studio")
    else:
        print(f"[ERROR] AI Connection: {ai_result['error']}")

    # Deduplication
    dedup_result = test_results['deduplication']
    if dedup_result['success']:
        print(f"[OK] Deduplication: Cache built with {dedup_result['cache_size']} files")
    else:
        print(f"[ERROR] Deduplication: {dedup_result['error']}")

    # Modules
    modules = test_results['modules']
    module_status = "[OK]" if all(modules.values()) else "[ERROR]"
    print(f"{module_status} Modules: All {len(modules)} modules initialized")

    # Overall
    overall = "[OK] READY" if test_results['overall_success'] else "[ERROR] ISSUES DETECTED"
    print(f"\nSystem Status: {overall}")

    if not test_results['overall_success']:
        print("\n[WARNING] Please resolve the issues above before running full processing.")

def print_processing_results(results):
    """Print processing results summary"""
    print("\n=== Processing Results ===")
    
    stats = results['statistics']
    
    print(f"Files scanned: {stats['files_scanned']}")
    print(f"Files processed: {stats['files_processed']}")
    print(f"Files copied: {stats['files_copied']}")
    print(f"Files skipped: {stats['files_skipped']}")
    print(f"Errors: {stats['errors']}")
    
    if stats['videos_analyzed'] > 0:
        print(f"\nVideo Analysis:")
        print(f"   Videos analyzed: {stats['videos_analyzed']}")
        print(f"   Kung fu detected: {stats['kung_fu_detected']}")
        print(f"   Notes generated: {stats['notes_generated']}")

        if stats['videos_analyzed'] > 0:
            detection_rate = (stats['kung_fu_detected'] / stats['videos_analyzed']) * 100
            print(f"   Detection rate: {detection_rate:.1f}%")

    if stats.get('processing_time_formatted'):
        print(f"\nProcessing time: {stats['processing_time_formatted']}")

    # Success/failure summary
    if results['success']:
        print(f"\nProcessing completed successfully!")
    else:
        print(f"\nProcessing failed: {results.get('error', 'Unknown error')}")

def save_results_to_json(results, output_path):
    """Save results to JSON file"""
    try:
        # Convert datetime objects to strings for JSON serialization
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=json_serializer)

        print(f"Results saved to: {output_path}")

    except Exception as e:
        print(f"Failed to save results to JSON: {e}")

def main():
    """Main application entry point"""
    args = parse_arguments()
    
    print_banner()
    
    try:
        # Load configuration
        print(f"Loading configuration: {args.config}")

        if not os.path.exists(args.config):
            print(f"Configuration file not found: {args.config}")
            return 1
        
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        
        # Override config options based on arguments
        if args.dry_run:
            config['options']['dry_run'] = True
            print("Dry run mode enabled - no files will be copied")

        if args.verbose:
            config['options']['verbose_logging'] = True
            print("Verbose logging enabled")

        # Setup logging
        logger = setup_logging(config)
        logger.info("=== PhoneSync + VideoProcessor Started ===")

        # Initialize unified processor
        print("Initializing unified processor...")
        processor = UnifiedProcessor(config, logger)

        # Run tests or full processing
        if args.test:
            print("Running system tests...")
            test_results = processor.test_all_systems()
            print_test_results(test_results)
            
            if args.output_json:
                save_results_to_json({'test_results': test_results}, args.output_json)
            
            return 0 if test_results['overall_success'] else 1
        
        else:
            print("Starting file processing...")
            results = processor.process_all_sources()
            print_processing_results(results)
            
            if args.output_json:
                save_results_to_json(results, args.output_json)
            
            logger.info("=== PhoneSync + VideoProcessor Completed ===")
            return 0 if results['success'] else 1
    
    except KeyboardInterrupt:
        print("\n\n[WARNING] Processing interrupted by user")
        return 130

    except Exception as e:
        print(f"\n[ERROR] Application error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
