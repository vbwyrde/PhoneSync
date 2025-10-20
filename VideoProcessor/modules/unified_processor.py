"""
Unified PhoneSync + VideoProcessor System
Main integration module that combines file organization with AI video analysis
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from .file_scanner import FileScanner
from .wudan_rules import WudanRulesEngine
from .deduplication import DeduplicationManager
from .target_path_resolver import TargetPathResolver
from .file_organizer import FileOrganizer
from .video_analyzer import VideoAnalyzer
from .processing_state_manager import ProcessingStateManager
from .fast_batch_processor import FastBatchProcessor
from .batch_file_copier import BatchFileCopier
from .batch_target_resolver import BatchTargetResolver

class UnifiedProcessor:
    """
    Main processor that combines file organization with AI video analysis
    Replaces the original PowerShell PhoneSync + N8N VideoProcessor workflow
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        Initialize the unified processor
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        
        # Initialize all modules
        self.file_scanner = FileScanner(config, logger)
        self.wudan_rules = WudanRulesEngine(config, logger)
        self.deduplication = DeduplicationManager(config, logger)
        self.target_resolver = TargetPathResolver(config, logger, self.wudan_rules, self.deduplication)
        self.file_organizer = FileOrganizer(config, logger, self.target_resolver, self.deduplication)
        self.video_analyzer = VideoAnalyzer(config, logger)
        self.state_manager = ProcessingStateManager(config, logger)
        self.fast_batch_processor = FastBatchProcessor(config, logger)
        self.batch_file_copier = BatchFileCopier(config, logger)
        self.batch_target_resolver = BatchTargetResolver(config, logger)
        
        # Processing statistics
        self.stats = {
            'files_scanned': 0,
            'files_processed': 0,
            'files_copied': 0,
            'files_skipped': 0,
            'videos_analyzed': 0,
            'kung_fu_detected': 0,
            'notes_generated': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
        
        self.logger.info("UnifiedProcessor initialized successfully")
    
    def process_all_sources(self) -> Dict[str, Any]:
        """
        Process all configured source folders
        Main entry point for the unified system
        
        Returns:
            Processing results dictionary
        """
        self.logger.info("=== Starting Unified PhoneSync + VideoProcessor ===")
        self.stats['start_time'] = datetime.now()

        try:
            # Start processing run in state manager
            self.state_manager.start_processing_run()

            # Build deduplication cache first
            self.logger.info("Building deduplication cache...")
            cached_files = self.deduplication.build_cache()
            self.logger.info(f"Cache built: {cached_files} existing files indexed")
            
            # Process each source folder
            all_results = []
            total_files_processed = 0
            
            # FAST BATCH PROCESSING: Use set operations instead of individual file loops
            self.logger.info("=== Starting Fast Batch Processing ===")

            # Step 1: Build source file inventory using fast scanning
            source_folders = self.config['source_folders']
            source_files_set = self.fast_batch_processor.build_source_inventory(source_folders)
            self.stats['files_scanned'] = len(source_files_set)

            if not source_files_set:
                self.logger.info("No supported files found in any source folder")
                return all_results

            # Step 2: Build target file inventory using fast scanning
            target_paths = self.config.get('target_paths', {})
            target_files_set = self.fast_batch_processor.build_target_inventory(target_paths)

            # Step 3: Use set operations to find files needing processing (lightning fast!)
            files_needing_processing_set = self.fast_batch_processor.find_files_needing_processing(
                source_files_set, target_files_set
            )

            if not files_needing_processing_set:
                self.logger.info("All files are already processed!")
                return all_results

            # Step 4: Convert file keys back to file info objects (only for files that need processing)
            files_to_process = self.fast_batch_processor.convert_keys_to_file_info(
                files_needing_processing_set, source_folders
            )

            self.logger.info(f"Fast batch processing identified {len(files_to_process)} files needing processing")

            # Step 5: Pre-resolve all target paths using batch operations
            if files_to_process:
                self.logger.info("=== Starting Batch Target Path Resolution ===")
                target_resolution = self.batch_target_resolver.resolve_all_target_paths(files_to_process)

                self.logger.info(f"Batch target resolution complete: {target_resolution['performance']['files_per_second']:.1f} files/sec")

                # Step 6: Use optimized batch file copier with pre-resolved paths
                self.logger.info("=== Starting Optimized Batch File Copy ===")
                copy_stats = self.batch_file_copier.copy_files_batch_with_paths(
                    files_to_process,
                    target_resolution['target_paths'],
                    self.file_organizer,
                    self.state_manager
                )

                # Update statistics from batch copier
                self.stats['files_copied'] = copy_stats['copied_files']
                self.stats['errors'] = copy_stats['failed_files']
                total_files_processed = copy_stats['copied_files']

                # Create results summary
                all_results = [{
                    'batch_operation': True,
                    'files_copied': copy_stats['copied_files'],
                    'files_failed': copy_stats['failed_files'],
                    'elapsed_time': copy_stats['elapsed_time'],
                    'files_per_second': copy_stats['files_per_second']
                }]
            
            # Final statistics
            self.stats['end_time'] = datetime.now()
            self.stats['files_processed'] = total_files_processed
            
            # Combine statistics from all modules
            self._update_final_statistics()

            # Finish processing run in state manager
            self.state_manager.finish_processing_run(self.stats)

            self.logger.info("=== Unified Processing Complete ===")
            self._log_final_summary()
            
            return {
                'success': True,
                'files_processed': total_files_processed,
                'results': all_results,
                'statistics': self.stats,
                'module_stats': self._get_all_module_statistics()
            }
            
        except Exception as e:
            self.logger.error(f"Unified processing failed: {e}")
            self.stats['errors'] += 1
            return {
                'success': False,
                'error': str(e),
                'statistics': self.stats
            }
    
    # OLD SLOW METHOD - REPLACED BY BATCH FILE COPIER
    # def _process_file_batch(self, files: List[Dict[str, Any]], source_folder: str) -> List[Dict[str, Any]]:
    
    # OLD SLOW METHOD - REPLACED BY BATCH FILE COPIER
    # def _process_single_file(self, file_info: Dict[str, Any], source_folder: str) -> Dict[str, Any]:
        # OLD SLOW METHOD - REPLACED BY BATCH FILE COPIER
        # (This method processed files one by one, taking 5-6 seconds each)
        # Now using BatchFileCopier for much faster bulk operations
    
    def _update_final_statistics(self):
        """Update final statistics from all modules"""
        # Get statistics from video analyzer
        video_stats = self.video_analyzer.get_analysis_statistics()
        self.stats['videos_analyzed'] = video_stats['videos_analyzed']
        self.stats['kung_fu_detected'] = video_stats['kung_fu_detected']
        self.stats['notes_generated'] = video_stats['notes_generated']
        
        # Calculate processing time
        if self.stats['start_time'] and self.stats['end_time']:
            duration = self.stats['end_time'] - self.stats['start_time']
            self.stats['processing_time_seconds'] = duration.total_seconds()
            self.stats['processing_time_formatted'] = str(duration).split('.')[0]  # Remove microseconds
    
    def _get_all_module_statistics(self) -> Dict[str, Any]:
        """Get statistics from all modules"""
        return {
            'file_scanner': self.file_scanner.get_scan_statistics(),
            'deduplication': {
                'cache_size': len(self.deduplication.existing_files_cache),
                'cache_enabled': self.config['options']['enable_deduplication']
            },
            'video_analyzer': self.video_analyzer.get_analysis_statistics(),
            'file_organizer': self.file_organizer.get_organization_statistics()
        }
    
    def _log_final_summary(self):
        """Log final processing summary"""
        self.logger.info("=== Processing Summary ===")
        self.logger.info(f"Files scanned: {self.stats['files_scanned']}")
        self.logger.info(f"Files processed: {self.stats['files_processed']}")
        self.logger.info(f"Files copied: {self.stats['files_copied']}")
        self.logger.info(f"Files skipped: {self.stats['files_skipped']}")
        self.logger.info(f"Videos analyzed: {self.stats['videos_analyzed']}")
        self.logger.info(f"Kung fu detected: {self.stats['kung_fu_detected']}")
        self.logger.info(f"Notes generated: {self.stats['notes_generated']}")
        self.logger.info(f"Errors: {self.stats['errors']}")
        
        if self.stats.get('processing_time_formatted'):
            self.logger.info(f"Processing time: {self.stats['processing_time_formatted']}")
    
    def test_all_systems(self) -> Dict[str, Any]:
        """
        Test all system components
        
        Returns:
            Test results dictionary
        """
        self.logger.info("=== Testing All System Components ===")
        
        test_results = {}
        
        # Test 1: Configuration
        test_results['configuration'] = {
            'success': True,
            'source_folders': len(self.config['source_folders']),
            'target_paths': len(self.config['target_paths']),
            'wudan_rules': len(self.config['wudan_rules']['before_2021']) + len(self.config['wudan_rules']['after_2021'])
        }
        
        # Test 2: AI Connection
        ai_test = self.video_analyzer.test_ai_connection()
        test_results['ai_connection'] = ai_test
        
        # Test 3: Deduplication cache
        try:
            cache_size = self.deduplication.build_cache()
            test_results['deduplication'] = {
                'success': True,
                'cache_size': cache_size
            }
        except Exception as e:
            test_results['deduplication'] = {
                'success': False,
                'error': str(e)
            }
        
        # Test 4: Module initialization
        test_results['modules'] = {
            'file_scanner': bool(self.file_scanner),
            'wudan_rules': bool(self.wudan_rules),
            'target_resolver': bool(self.target_resolver),
            'file_organizer': bool(self.file_organizer),
            'video_analyzer': bool(self.video_analyzer)
        }
        
        # Overall success
        test_results['overall_success'] = all([
            test_results['configuration']['success'],
            test_results['deduplication']['success'],
            all(test_results['modules'].values())
        ])
        
        return test_results

    # Old slow batch filtering method removed - replaced with FastBatchProcessor

    def get_processing_statistics(self) -> Dict[str, Any]:
        """
        Get current processing statistics

        Returns:
            Dictionary with processing statistics
        """
        return self.stats.copy()
