"""
File Scanner Module for PhoneSync + VideoProcessor
Scans source folders for JPG/MP4 files recursively with file info extraction
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import re

class FileScanner:
    """Scans source directories for supported files and extracts metadata"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """Initialize file scanner with configuration"""
        self.config = config
        self.logger = logger
        
        # Get supported extensions from config
        self.picture_extensions = [ext.lower() for ext in config['file_extensions']['pictures']]
        self.video_extensions = [ext.lower() for ext in config['file_extensions']['videos']]
        self.all_extensions = self.picture_extensions + self.video_extensions
        
        # Date extraction patterns for real-world file naming
        # Updated to handle actual patterns: 20250406_110016_1.mp4, 20250622_100122.mp4, M4H01890.MP4
        self.date_patterns = [
            # Primary pattern: YYYYMMDD_HHMMSS_X.ext or YYYYMMDD_HHMMSS.ext
            r'^(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})(?:_\d+)?\.',

            # Legacy patterns for backward compatibility
            r'(\d{4})_(\d{2})_(\d{2})',  # YYYY_MM_DD
            r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
            r'^(\d{4})(\d{2})(\d{2})(?:[_-]|$)',  # YYYYMMDD (date only, no time)
            r'[A-Z]{3}_(\d{4})(\d{2})(\d{2})[_-](\d{2})(\d{2})(\d{2})',  # IMG_YYYYMMDD_HHMMSS
            r'(\d{2})(\d{2})(\d{4})',    # MMDDYYYY
            r'(\d{2})-(\d{2})-(\d{4})',  # MM-DD-YYYY
            r'(\d{2})_(\d{2})_(\d{4})',  # MM_DD_YYYY
        ]
    
    def scan_folder(self, source_path: str) -> List[Dict[str, Any]]:
        """
        Scan a source folder recursively for supported files
        
        Args:
            source_path: Path to source folder to scan
            
        Returns:
            List of file information dictionaries
        """
        source_path = Path(source_path)
        
        if not source_path.exists():
            self.logger.error(f"Source folder does not exist: {source_path}")
            return []
        
        if not source_path.is_dir():
            self.logger.error(f"Source path is not a directory: {source_path}")
            return []
        
        self.logger.info(f"Scanning folder: {source_path}")
        
        files_found = []
        
        try:
            # Recursively scan for files
            for file_path in source_path.rglob('*'):
                if file_path.is_file():
                    file_info = self._extract_file_info(file_path)
                    if file_info:
                        files_found.append(file_info)
            
            self.logger.info(f"Found {len(files_found)} supported files in {source_path}")
            
        except Exception as e:
            self.logger.error(f"Error scanning folder {source_path}: {e}")
        
        return files_found
    
    def _extract_file_info(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Extract file information and metadata
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information or None if not supported
        """
        try:
            # Check if file extension is supported
            extension = file_path.suffix.lower()
            if extension not in self.all_extensions:
                return None
            
            # Get file stats
            stat_info = file_path.stat()
            
            # Determine file type
            file_type = 'picture' if extension in self.picture_extensions else 'video'
            
            # Extract date from filename or use modification time
            file_date = self._extract_date_from_filename(file_path.name)
            if not file_date:
                file_date = datetime.fromtimestamp(stat_info.st_mtime)
            
            file_info = {
                'path': str(file_path),
                'name': file_path.name,
                'extension': extension,
                'type': file_type,
                'size': stat_info.st_size,
                'date': file_date,
                'modification_time': datetime.fromtimestamp(stat_info.st_mtime),
                'creation_time': datetime.fromtimestamp(stat_info.st_ctime),
            }
            
            return file_info
            
        except Exception as e:
            self.logger.warning(f"Error extracting info for {file_path}: {e}")
            return None
    
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

                    # Handle different date formats
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

                except (ValueError, TypeError):
                    continue
        
        return None
    
    def get_file_stats(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about scanned files
        
        Args:
            files: List of file information dictionaries
            
        Returns:
            Dictionary with statistics
        """
        if not files:
            return {
                'total_files': 0,
                'pictures': 0,
                'videos': 0,
                'total_size': 0,
                'date_range': None
            }
        
        pictures = [f for f in files if f['type'] == 'picture']
        videos = [f for f in files if f['type'] == 'video']
        total_size = sum(f['size'] for f in files)
        
        # Get date range
        dates = [f['date'] for f in files if f['date']]
        date_range = None
        if dates:
            min_date = min(dates)
            max_date = max(dates)
            date_range = {
                'earliest': min_date.strftime('%Y-%m-%d'),
                'latest': max_date.strftime('%Y-%m-%d')
            }
        
        return {
            'total_files': len(files),
            'pictures': len(pictures),
            'videos': len(videos),
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'date_range': date_range,
            'extensions': list(set(f['extension'] for f in files))
        }
    
    def filter_files_by_date_range(self, files: List[Dict[str, Any]], 
                                 start_date: datetime = None, 
                                 end_date: datetime = None) -> List[Dict[str, Any]]:
        """
        Filter files by date range
        
        Args:
            files: List of file information dictionaries
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            Filtered list of files
        """
        filtered_files = []
        
        for file_info in files:
            file_date = file_info['date']
            
            # Check date range
            if start_date and file_date < start_date:
                continue
            if end_date and file_date > end_date:
                continue
            
            filtered_files.append(file_info)
        
        return filtered_files
    
    def group_files_by_date(self, files: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group files by date (YYYY-MM-DD format)
        
        Args:
            files: List of file information dictionaries
            
        Returns:
            Dictionary with date strings as keys and file lists as values
        """
        grouped_files = {}
        
        for file_info in files:
            date_key = file_info['date'].strftime('%Y-%m-%d')
            
            if date_key not in grouped_files:
                grouped_files[date_key] = []
            
            grouped_files[date_key].append(file_info)
        
        return grouped_files

    def get_scan_statistics(self) -> Dict[str, Any]:
        """
        Get file scanning statistics

        Returns:
            Dictionary with scanning statistics
        """
        return {
            'total_files_scanned': 0,  # This would be updated during scanning
            'supported_extensions': self.all_extensions,
            'picture_extensions': self.picture_extensions,
            'video_extensions': self.video_extensions
        }
