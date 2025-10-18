#!/usr/bin/env python3
"""
Processing State Manager for PhoneSync + VideoProcessor
Tracks which files have been processed to avoid re-processing large collections
Implements incremental processing for hundreds/thousands of MP4s
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict

@dataclass
class ProcessingState:
    """State information for processing runs"""
    last_run_timestamp: str
    last_processed_file: str
    last_processed_date: str
    total_files_processed: int
    total_videos_analyzed: int
    processing_version: str = "1.0"

class ProcessingStateManager:
    """
    Manages persistent state for video processing to enable incremental processing
    Tracks which files have been processed to avoid re-analysis on subsequent runs
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        Initialize processing state manager
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        
        # State file location from config
        state_config = config.get('state_management', {})
        state_dir_path = state_config.get('state_dir', 'VideoProcessor/state')

        # Handle relative paths - if running from VideoProcessor dir, adjust path
        if not os.path.exists(state_dir_path) and state_dir_path.startswith('VideoProcessor/'):
            # Try without VideoProcessor prefix (running from VideoProcessor directory)
            alt_path = state_dir_path.replace('VideoProcessor/', '', 1)
            if os.path.exists(alt_path) or os.path.exists(os.path.dirname(alt_path)):
                state_dir_path = alt_path

        self.state_dir = Path(state_dir_path)
        self.state_dir.mkdir(exist_ok=True)

        # State file names from config
        state_file_name = state_config.get('processing_state_file', 'processing_state.json')
        processed_files_name = state_config.get('processed_files_db', 'processed_files.json')

        self.state_file = self.state_dir / state_file_name
        self.processed_files_db = self.state_dir / processed_files_name
        
        # Current state
        self.current_state: Optional[ProcessingState] = None
        self.processed_files: Set[str] = set()
        
        # Load existing state
        self._load_state()
        
        self.logger.info(f"ProcessingStateManager initialized. State file: {self.state_file}")
    
    def _load_state(self):
        """Load processing state from disk"""
        try:
            # Load main state
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                    self.current_state = ProcessingState(**state_data)
                    self.logger.info(f"Loaded processing state: last run {self.current_state.last_run_timestamp}")
            else:
                self.logger.info("No previous processing state found - first run")
                
            # Load processed files database
            if self.processed_files_db.exists():
                with open(self.processed_files_db, 'r', encoding='utf-8') as f:
                    processed_data = json.load(f)
                    self.processed_files = set(processed_data.get('processed_files', []))
                    self.logger.info(f"Loaded {len(self.processed_files)} previously processed files")
            else:
                self.logger.info("No processed files database found - first run")
                
        except Exception as e:
            self.logger.warning(f"Error loading processing state: {e}")
            self.current_state = None
            self.processed_files = set()
    
    def _save_state(self):
        """Save processing state to disk"""
        try:
            # Save main state
            if self.current_state:
                with open(self.state_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(self.current_state), f, indent=2)
                    
            # Save processed files database
            processed_data = {
                'processed_files': list(self.processed_files),
                'last_updated': datetime.now().isoformat(),
                'total_count': len(self.processed_files)
            }
            
            with open(self.processed_files_db, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2)
                
            self.logger.info(f"Saved processing state: {len(self.processed_files)} processed files tracked")
            
        except Exception as e:
            self.logger.error(f"Error saving processing state: {e}")
    
    def should_process_file(self, file_info: Dict[str, Any]) -> bool:
        """
        Determine if a file should be processed based on state tracking

        Args:
            file_info: File information dictionary

        Returns:
            True if file should be processed, False if already processed
        """
        file_path = file_info['path']
        file_name = file_info['name']
        file_date = file_info['date']

        # Create unique identifier for file (path + size + date)
        file_id = f"{file_path}|{file_info['size']}|{file_date.isoformat()}"

        # Check if file was already processed
        if file_id in self.processed_files:
            self.logger.debug(f"File already processed, skipping: {file_name}")
            return False

        # Enhanced incremental processing with validation
        if self.current_state and self.config['options'].get('enable_incremental_processing', True):
            # Validate that our state corresponds to actual target folder structure
            if self._validate_last_run_against_folders():
                # State is valid, use timestamp-based filtering
                last_run_time = datetime.fromisoformat(self.current_state.last_run_timestamp)
                if file_date <= last_run_time:
                    self.logger.debug(f"File older than last run ({last_run_time}), skipping: {file_name}")
                    return False
            else:
                # State validation failed, fall back to folder-based detection
                self.logger.warning("State validation failed, falling back to folder-based last date detection")
                last_folder_date = self._determine_last_process_date_from_folders()
                if last_folder_date and file_date.date() <= last_folder_date:
                    self.logger.debug(f"File older than last folder date ({last_folder_date}), skipping: {file_name}")
                    return False
        
        return True

    def _validate_last_run_against_folders(self) -> bool:
        """
        Validate that the last_run_timestamp corresponds to actual target folder structure

        This provides a sanity check to ensure our state files are consistent with
        the actual folder structure. If validation fails, we fall back to examining
        the target folders directly.

        Returns:
            True if validation passes, False if we need folder-based fallback
        """
        if not self.current_state:
            self.logger.debug("No current state available for validation")
            return False

        try:
            # Extract date from last_run_timestamp
            last_run_datetime = datetime.fromisoformat(self.current_state.last_run_timestamp)
            last_run_date = last_run_datetime.date()
            expected_folder = last_run_date.strftime('%Y_%m_%d')

            self.logger.debug(f"Validating last run date {expected_folder} against target folders")

            # Check target directories for expected date folder
            target_paths = self.config.get('target_paths', {})
            validation_passed = False

            for path_type, base_path in target_paths.items():
                if not base_path or not os.path.exists(base_path):
                    continue

                try:
                    # Look for date folders in this target directory
                    for item in os.listdir(base_path):
                        item_path = os.path.join(base_path, item)
                        if not os.path.isdir(item_path):
                            continue

                        # Check if this folder matches our expected date or is newer
                        if path_type == 'wudan':
                            # For Wudan folders, check YYYY_MM_DD_DDD pattern
                            if item.startswith(expected_folder + '_'):
                                validation_passed = True
                                break
                        else:
                            # For regular folders, check YYYY_MM_DD pattern
                            if item == expected_folder:
                                validation_passed = True
                                break

                    if validation_passed:
                        break

                except (OSError, PermissionError) as e:
                    self.logger.warning(f"Could not access target directory {base_path}: {e}")
                    continue

            if validation_passed:
                self.logger.debug(f"State validation passed: found expected date folder {expected_folder}")
                return True
            else:
                self.logger.info(f"State validation failed: no folder found for date {expected_folder}")
                return False

        except Exception as e:
            self.logger.warning(f"Error during state validation: {e}")
            return False

    def _determine_last_process_date_from_folders(self) -> Optional[datetime.date]:
        """
        Examine target folder structure to find the most recent YYYY_MM_DD folder

        This provides a fallback when state files are missing, corrupted, or inconsistent
        with the actual folder structure.

        Returns:
            Most recent date found in target folders, or None if no valid dates found
        """
        self.logger.info("Scanning target folders to determine last process date")

        latest_date = None
        target_paths = self.config.get('target_paths', {})

        for path_type, base_path in target_paths.items():
            if not base_path or not os.path.exists(base_path):
                continue

            try:
                for item in os.listdir(base_path):
                    item_path = os.path.join(base_path, item)
                    if not os.path.isdir(item_path):
                        continue

                    # Parse date from folder name
                    folder_date = self._parse_date_from_folder_name(item, path_type)
                    if folder_date and (latest_date is None or folder_date > latest_date):
                        latest_date = folder_date

            except (OSError, PermissionError) as e:
                self.logger.warning(f"Could not access target directory {base_path}: {e}")
                continue

        if latest_date:
            self.logger.info(f"Found last process date from folders: {latest_date}")
        else:
            self.logger.info("No valid date folders found in target directories")

        return latest_date

    def _parse_date_from_folder_name(self, folder_name: str, path_type: str) -> Optional[datetime.date]:
        """
        Parse date from folder name based on expected patterns

        Args:
            folder_name: Name of the folder
            path_type: Type of target path (wudan, videos, pictures)

        Returns:
            Parsed date or None if folder name doesn't match expected pattern
        """
        try:
            if path_type == 'wudan':
                # Wudan folders: YYYY_MM_DD_DDD (with day of week)
                parts = folder_name.split('_')
                if len(parts) >= 3:
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    return datetime(year, month, day).date()
            else:
                # Regular folders: YYYY_MM_DD
                parts = folder_name.split('_')
                if len(parts) == 3:
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    return datetime(year, month, day).date()

        except (ValueError, IndexError):
            # Not a valid date folder
            pass

        return None

    def mark_file_processed(self, file_info: Dict[str, Any], analysis_result: Optional[Dict[str, Any]] = None):
        """
        Mark a file as processed
        
        Args:
            file_info: File information dictionary
            analysis_result: Optional analysis result for additional tracking
        """
        file_path = file_info['path']
        file_date = file_info['date']
        
        # Create unique identifier for file
        file_id = f"{file_path}|{file_info['size']}|{file_date.isoformat()}"
        
        # Add to processed files set
        self.processed_files.add(file_id)
        
        self.logger.debug(f"Marked file as processed: {file_info['name']}")
    
    def start_processing_run(self):
        """Start a new processing run"""
        self.logger.info("=== Starting new processing run ===")
        
        # Log previous state if exists
        if self.current_state:
            self.logger.info(f"Previous run: {self.current_state.last_run_timestamp}")
            self.logger.info(f"Previously processed: {self.current_state.total_files_processed} files, {self.current_state.total_videos_analyzed} videos")
        else:
            self.logger.info("First processing run - no previous state")
    
    def finish_processing_run(self, stats: Dict[str, Any]):
        """
        Finish processing run and update state
        
        Args:
            stats: Processing statistics from current run
        """
        current_time = datetime.now()
        
        # Update state
        self.current_state = ProcessingState(
            last_run_timestamp=current_time.isoformat(),
            last_processed_file=stats.get('last_processed_file', ''),
            last_processed_date=current_time.strftime('%Y-%m-%d'),
            total_files_processed=stats.get('files_processed', 0),
            total_videos_analyzed=stats.get('videos_analyzed', 0)
        )
        
        # Save state to disk
        self._save_state()
        
        self.logger.info("=== Processing run completed ===")
        self.logger.info(f"Files processed this run: {stats.get('files_processed', 0)}")
        self.logger.info(f"Videos analyzed this run: {stats.get('videos_analyzed', 0)}")
        self.logger.info(f"Total tracked files: {len(self.processed_files)}")
    
    def get_state_info(self) -> Dict[str, Any]:
        """
        Get current state information
        
        Returns:
            Dictionary with state information
        """
        if not self.current_state:
            return {
                'first_run': True,
                'processed_files_count': len(self.processed_files)
            }
            
        return {
            'first_run': False,
            'last_run': self.current_state.last_run_timestamp,
            'last_processed_file': self.current_state.last_processed_file,
            'total_files_processed': self.current_state.total_files_processed,
            'total_videos_analyzed': self.current_state.total_videos_analyzed,
            'processed_files_count': len(self.processed_files)
        }
    
    def reset_state(self):
        """Reset all processing state (for testing or fresh start)"""
        self.logger.warning("Resetting all processing state")
        
        self.current_state = None
        self.processed_files = set()
        
        # Remove state files
        if self.state_file.exists():
            self.state_file.unlink()
        if self.processed_files_db.exists():
            self.processed_files_db.unlink()
            
        self.logger.info("Processing state reset complete")
    
    def get_incremental_filter_info(self) -> Dict[str, Any]:
        """
        Get information about incremental filtering
        
        Returns:
            Dictionary with filter information for logging
        """
        if not self.current_state:
            return {
                'mode': 'full_processing',
                'reason': 'First run - processing all files'
            }
        
        return {
            'mode': 'incremental_processing',
            'last_run': self.current_state.last_run_timestamp,
            'filter_date': self.current_state.last_run_timestamp,
            'reason': f'Processing files newer than {self.current_state.last_run_timestamp}'
        }
