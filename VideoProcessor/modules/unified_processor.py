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
        self.target_resolver = TargetPathResolver(config, logger)
        self.file_organizer = FileOrganizer(config, logger)
        self.video_analyzer = VideoAnalyzer(config, logger)
        
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
            # Build deduplication cache first
            self.logger.info("Building deduplication cache...")
            cached_files = self.deduplication.build_cache()
            self.logger.info(f"Cache built: {cached_files} existing files indexed")
            
            # Process each source folder
            all_results = []
            total_files_processed = 0
            
            for source_folder in self.config['source_folders']:
                if not os.path.exists(source_folder):
                    self.logger.warning(f"Source folder not found: {source_folder}")
                    continue
                
                self.logger.info(f"Processing source folder: {source_folder}")
                
                # Scan for files
                files = self.file_scanner.scan_folder(source_folder)
                self.stats['files_scanned'] += len(files)
                
                if not files:
                    self.logger.info(f"No supported files found in {source_folder}")
                    continue
                
                self.logger.info(f"Found {len(files)} files to process")
                
                # Process files in batches
                batch_results = self._process_file_batch(files, source_folder)
                all_results.extend(batch_results)
                total_files_processed += len(batch_results)
            
            # Final statistics
            self.stats['end_time'] = datetime.now()
            self.stats['files_processed'] = total_files_processed
            
            # Combine statistics from all modules
            self._update_final_statistics()
            
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
    
    def _process_file_batch(self, files: List[Dict[str, Any]], source_folder: str) -> List[Dict[str, Any]]:
        """
        Process a batch of files from a source folder
        
        Args:
            files: List of file information dictionaries
            source_folder: Source folder path
            
        Returns:
            List of processing results
        """
        results = []
        
        for file_info in files:
            try:
                result = self._process_single_file(file_info, source_folder)
                results.append(result)
                
                # Update statistics
                if result['success']:
                    if result['action'] == 'copied':
                        self.stats['files_copied'] += 1
                    elif result['action'] == 'skipped':
                        self.stats['files_skipped'] += 1
                else:
                    self.stats['errors'] += 1
                
            except Exception as e:
                self.logger.error(f"Error processing file {file_info.get('name', 'unknown')}: {e}")
                self.stats['errors'] += 1
                results.append({
                    'file': file_info.get('name', 'unknown'),
                    'success': False,
                    'error': str(e),
                    'action': 'error'
                })
        
        return results
    
    def _process_single_file(self, file_info: Dict[str, Any], source_folder: str) -> Dict[str, Any]:
        """
        Process a single file through the complete workflow
        
        Args:
            file_info: File information dictionary
            source_folder: Source folder path
            
        Returns:
            Processing result dictionary
        """
        filename = file_info['name']
        source_path = os.path.join(source_folder, filename)
        
        self.logger.debug(f"Processing file: {filename}")
        
        # Step 1: Determine target folder
        target_folder = self.target_resolver.get_target_folder_path(file_info)
        if not target_folder:
            return {
                'file': filename,
                'success': False,
                'error': 'Could not determine target folder',
                'action': 'error'
            }
        
        # Step 2: Check for duplicates
        file_exists = self.deduplication.file_exists_in_target(
            filename,
            file_info['size'],
            file_info['date'],
            target_folder
        )
        
        if file_exists:
            self.logger.info(f"File already exists, skipping: {filename}")
            return {
                'file': filename,
                'success': True,
                'action': 'skipped',
                'reason': 'File already exists in target',
                'target_folder': target_folder
            }
        
        # Step 3: Analyze video if enabled and applicable
        analysis_result = None
        if file_info['type'] == 'video' and self.video_analyzer.video_analysis_enabled:
            self.logger.info(f"Analyzing video: {filename}")
            analysis_result = self.video_analyzer.analyze_video(source_path, file_info)
            
            if analysis_result.get('analyzed'):
                self.stats['videos_analyzed'] += 1
                if analysis_result.get('is_kung_fu'):
                    self.stats['kung_fu_detected'] += 1
        
        # Step 4: Copy/move file
        copy_result = self.file_organizer.organize_single_file(
            source_path,
            target_folder,
            file_info
        )
        
        if not copy_result['success']:
            return {
                'file': filename,
                'success': False,
                'error': copy_result.get('error', 'File operation failed'),
                'action': 'error'
            }
        
        # Step 5: Generate note file if kung fu detected
        note_path = None
        if analysis_result and analysis_result.get('is_kung_fu') and analysis_result.get('note_content'):
            note_path = self.video_analyzer.generate_note_file(
                source_path,
                analysis_result,
                target_folder
            )
            if note_path:
                self.stats['notes_generated'] += 1
        
        # Success result
        result = {
            'file': filename,
            'success': True,
            'action': 'copied',
            'source_path': source_path,
            'target_folder': target_folder,
            'target_path': copy_result.get('target_path'),
            'file_type': file_info['type'],
            'file_size': file_info['size'],
            'file_date': file_info['date'].isoformat()
        }
        
        # Add analysis results if available
        if analysis_result:
            result['analysis'] = {
                'analyzed': analysis_result.get('analyzed', False),
                'is_kung_fu': analysis_result.get('is_kung_fu', False),
                'confidence': analysis_result.get('confidence', 0),
                'description': analysis_result.get('description', ''),
                'note_generated': bool(note_path)
            }
            
            if note_path:
                result['note_path'] = note_path
        
        return result
    
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
