#!/usr/bin/env python3
"""
Fast Batch Processor - Efficient file comparison using set operations
Instead of individual file loops, this uses flat lists and set operations for speed
"""

import os
import logging
import re
from typing import Dict, List, Set, Tuple, Any, Optional
from pathlib import Path
from datetime import datetime
import time

class FastBatchProcessor:
    """
    High-performance batch file processor using set operations instead of loops
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger

        # Date extraction patterns (copied from FileScanner)
        self.date_patterns = [
            # Primary pattern: YYYYMMDD_HHMMSS_X.ext or YYYYMMDD_HHMMSS.ext
            r'^(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})(?:_\d+)?\.',

            # Legacy patterns for backward compatibility
            r'(\d{4})_(\d{2})_(\d{2})',  # YYYY_MM_DD
            r'(\d{4})(\d{2})(\d{2})',    # YYYYMMDD
            r'(\d{2})_(\d{2})_(\d{4})',  # MM_DD_YYYY
            r'(\d{2})(\d{2})(\d{4})',    # MMDDYYYY

            # Screenshot patterns: Screenshot_YYYYMMDD-HHMMSS_App.jpg
            r'Screenshot_(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})',

            # WeChat patterns: wx_camera_timestamp.ext
            r'wx_camera_(\d{10,13})',  # Unix timestamp (10-13 digits)
        ]
        
    def build_source_inventory(self, source_folders: List[str]) -> Set[str]:
        """
        Build a flat set of source files using format: filename|size
        This is much faster than individual file processing
        """
        source_files = set()
        total_files = 0

        self.logger.info("Building source file inventory...")
        start_time = time.time()

        for folder_path in source_folders:
            # Use path as-is since ConfigManager now preserves proper UNC syntax
            if not os.path.exists(folder_path):
                self.logger.warning(f"Source folder not found: {folder_path}")
                continue
                
            self.logger.info(f"Scanning source: {folder_path}")
            folder_files = 0
            
            try:
                # Use os.walk for efficient directory traversal
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        # Filter by supported extensions
                        ext = Path(file).suffix.lower()
                        if ext not in ['.jpg', '.jpeg', '.mp4', '.mov', '.avi']:
                            continue
                            
                        try:
                            # Get file size efficiently
                            file_size = os.path.getsize(file_path)
                            
                            # Create unique key: filename|size
                            file_key = f"{file}|{file_size}"
                            source_files.add(file_key)
                            folder_files += 1
                            total_files += 1
                            
                        except (OSError, PermissionError) as e:
                            self.logger.warning(f"Cannot access {file_path}: {e}")
                            
            except Exception as e:
                self.logger.error(f"Error scanning {folder_path}: {e}")
                
            self.logger.info(f"Found {folder_files} files in {os.path.basename(folder_path)}")
        
        elapsed = time.time() - start_time
        self.logger.info(f"Source inventory complete: {total_files} files in {elapsed:.2f} seconds")
        return source_files
    
    def build_target_inventory(self, target_paths: Dict[str, str]) -> Set[str]:
        """
        Build a flat set of target files using format: filename|size
        This replaces the slow deduplication cache building
        """
        target_files = set()
        total_files = 0
        
        self.logger.info("Building target file inventory...")
        start_time = time.time()
        
        for path_type, base_path in target_paths.items():
            if not base_path or not os.path.exists(base_path):
                continue
                
            self.logger.info(f"Scanning target: {base_path}")
            path_files = 0
            
            try:
                # Use os.walk for efficient directory traversal
                for root, dirs, files in os.walk(base_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        # Filter by supported extensions
                        ext = Path(file).suffix.lower()
                        if ext not in ['.jpg', '.jpeg', '.mp4', '.mov', '.avi']:
                            continue
                            
                        try:
                            # Get file size efficiently
                            file_size = os.path.getsize(file_path)
                            
                            # Create unique key: filename|size
                            file_key = f"{file}|{file_size}"
                            target_files.add(file_key)
                            path_files += 1
                            total_files += 1
                            
                        except (OSError, PermissionError) as e:
                            self.logger.warning(f"Cannot access {file_path}: {e}")
                            
            except Exception as e:
                self.logger.error(f"Error scanning {base_path}: {e}")
                
            self.logger.info(f"Found {path_files} files in {path_type}")
        
        elapsed = time.time() - start_time
        self.logger.info(f"Target inventory complete: {total_files} files in {elapsed:.2f} seconds")
        return target_files
    
    def find_files_needing_processing(self, source_files: Set[str], target_files: Set[str]) -> Set[str]:
        """
        Use set difference operation to find files that need processing
        This is MUCH faster than individual file loops
        """
        self.logger.info("Computing files needing processing...")
        start_time = time.time()
        
        # Set difference: files in source but not in target
        files_to_process = source_files - target_files
        
        elapsed = time.time() - start_time
        self.logger.info(f"Set comparison complete in {elapsed:.3f} seconds")
        self.logger.info(f"Result: {len(files_to_process)} files need processing out of {len(source_files)} total")
        self.logger.info(f"Already processed: {len(source_files) - len(files_to_process)} files ({((len(source_files) - len(files_to_process)) / len(source_files) * 100):.1f}%)")
        
        return files_to_process
    
    def convert_keys_to_file_info(self, file_keys: Set[str], source_folders: List[str]) -> List[Dict[str, Any]]:
        """
        Convert the file keys back to full file info dictionaries for processing
        Only do this for files that actually need processing
        """
        file_info_list = []

        self.logger.info(f"Converting {len(file_keys)} file keys to file info...")
        start_time = time.time()

        # Build a lookup map of filename|size -> full path
        file_lookup = {}

        for folder_path in source_folders:
            # Use path as-is since ConfigManager now preserves proper UNC syntax
            if not os.path.exists(folder_path):
                continue
                
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    ext = Path(file).suffix.lower()
                    
                    if ext not in ['.jpg', '.jpeg', '.mp4', '.mov', '.avi']:
                        continue
                        
                    try:
                        file_size = os.path.getsize(file_path)
                        file_key = f"{file}|{file_size}"
                        
                        if file_key in file_keys:
                            # Extract date from filename using FileScanner's logic
                            file_date = self._extract_date_from_filename(file)
                            if not file_date:
                                # Fallback to file modification time
                                file_date = datetime.fromtimestamp(os.path.getmtime(file_path))

                            # Determine file type
                            file_type = 'picture' if ext in ['.jpg', '.jpeg'] else 'video'

                            file_info = {
                                'name': file,
                                'path': file_path,
                                'size': file_size,
                                'type': file_type,
                                'extension': ext,
                                'date': file_date,  # Use 'date' field like FileScanner
                                'source_folder': os.path.basename(folder_path)
                            }

                            file_info_list.append(file_info)
                            
                    except (OSError, PermissionError):
                        continue
        
        elapsed = time.time() - start_time
        self.logger.info(f"File info conversion complete: {len(file_info_list)} files in {elapsed:.2f} seconds")
        
        return file_info_list
    
    def get_processing_statistics(self, source_files: Set[str], target_files: Set[str], files_to_process: Set[str]) -> Dict[str, Any]:
        """
        Generate processing statistics
        """
        total_source = len(source_files)
        total_target = len(target_files)
        need_processing = len(files_to_process)
        already_processed = total_source - need_processing
        
        return {
            'total_source_files': total_source,
            'total_target_files': total_target,
            'files_needing_processing': need_processing,
            'files_already_processed': already_processed,
            'completion_percentage': (already_processed / total_source * 100) if total_source > 0 else 0
        }

    def _extract_date_from_filename(self, filename: str) -> Optional[datetime]:
        """
        Extract date from filename using various patterns

        Args:
            filename: Name of the file

        Returns:
            Datetime object if date found, None otherwise
        """
        for pattern in self.date_patterns:
            match = re.search(pattern, filename)
            if match:
                try:
                    groups = match.groups()

                    # Handle Unix timestamp (WeChat files)
                    if 'wx_camera_' in filename and len(groups) == 1:
                        timestamp = int(groups[0])
                        # Convert milliseconds to seconds if needed
                        if timestamp > 10**10:  # Milliseconds
                            timestamp = timestamp / 1000
                        return datetime.fromtimestamp(timestamp)

                    # Handle regular date formats
                    if len(groups) >= 3:
                        # Determine if this is YYYY-MM-DD or MM-DD-YYYY format
                        if len(groups[0]) == 4:  # YYYY format
                            year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                        else:  # MM format (MM-DD-YYYY)
                            month, day, year = int(groups[0]), int(groups[1]), int(groups[2])

                        # Validate date ranges
                        if not (1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31):
                            continue

                        # Extract time if available (for YYYYMMDD_HHMMSS patterns)
                        if len(groups) >= 6:
                            hour = int(groups[3])
                            minute = int(groups[4])
                            second = int(groups[5])

                            # Validate time ranges
                            if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
                                continue
                        else:
                            hour = minute = second = 0

                        return datetime(year, month, day, hour, minute, second)

                except (ValueError, TypeError, OSError):
                    continue

        return None
