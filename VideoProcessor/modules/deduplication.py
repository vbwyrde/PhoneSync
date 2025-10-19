"""
Deduplication Manager for PhoneSync + VideoProcessor
Hash-based duplicate detection with caching and flexible folder matching
Converted from PowerShell Build-ExistingFilesCache and Test-FileExistsInTarget functions
"""

import os
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import re

class DeduplicationManager:
    """
    Manages file deduplication using name+size caching with flexible date folder matching
    Converted from PowerShell deduplication logic
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """Initialize deduplication manager"""
        self.config = config
        self.logger = logger
        self.existing_files_cache = {}  # Key: "filename|size", Value: list of file info
        
        # Get target paths from config
        self.target_paths = [
            config['target_paths']['pictures'],
            config['target_paths']['videos'],
            config['target_paths']['wudan']
        ]
    
    def build_cache(self) -> int:
        """
        Build cache of existing files in target directories
        Converted from PowerShell Build-ExistingFilesCache function
        
        Returns:
            Number of files cached
        """
        self.logger.info("Building cache of existing files in target directories...")
        
        self.existing_files_cache = {}
        total_files = 0
        
        for target_path in self.target_paths:
            if not os.path.exists(target_path):
                self.logger.info(f"Target path does not exist, will be created: {target_path}")
                continue
            
            self.logger.info(f"Scanning existing files in: {target_path}")
            
            try:
                # Recursively scan target directory
                for root, dirs, files in os.walk(target_path):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        
                        try:
                            file_stat = os.stat(file_path)
                            file_key = f"{filename}|{file_stat.st_size}"
                            
                            # Initialize list if key doesn't exist
                            if file_key not in self.existing_files_cache:
                                self.existing_files_cache[file_key] = []
                            
                            # Extract date pattern from directory name for flexible matching
                            directory_name = os.path.basename(root)
                            date_pattern = self._extract_date_pattern(directory_name)
                            
                            file_info = {
                                'path': file_path,
                                'last_write_time': datetime.fromtimestamp(file_stat.st_mtime),
                                'directory': root,
                                'date_pattern': date_pattern,
                                'full_directory_name': directory_name,
                                'size': file_stat.st_size
                            }
                            
                            self.existing_files_cache[file_key].append(file_info)
                            total_files += 1
                            
                        except (OSError, IOError) as e:
                            self.logger.warning(f"Error processing file {file_path}: {e}")
                            continue
                            
            except Exception as e:
                self.logger.warning(f"Error scanning {target_path}: {e}")
        
        self.logger.info(f"Cache built successfully. Found {total_files} existing files across all target directories.")
        return total_files
    
    def _extract_date_pattern(self, directory_name: str) -> Optional[str]:
        """
        Extract YYYY_MM_DD date pattern from directory name
        Converted from PowerShell date pattern extraction logic
        
        Args:
            directory_name: Name of the directory
            
        Returns:
            Date pattern string (YYYY_MM_DD) or None if not found
        """
        # Look for YYYY_MM_DD pattern at the beginning of directory name
        match = re.match(r'^(\d{4}_\d{2}_\d{2})', directory_name)
        if match:
            return match.group(1)
        return None
    
    def file_exists_in_target(self, filename: str, file_size: int,
                            file_date: datetime, target_directory: str, quiet: bool = False) -> bool:
        """
        Check if file already exists in target using deduplication cache
        Handles flexible filename matching for files with appended text

        Example: Source '20250412_292993_1.mp4' matches target '20250412_292993_1_KungFu_GimStyle.mp4'

        Args:
            filename: Name of the file
            file_size: Size of the file in bytes
            file_date: Date/time of the file
            target_directory: Target directory path

        Returns:
            True if file already exists, False otherwise
        """
        if not self.config['options']['enable_deduplication']:
            return False

        # First try exact filename match
        file_key = f"{filename}|{file_size}"
        exact_matches = self.existing_files_cache.get(file_key, [])

        # Then try flexible filename matching (base filename + size validation)
        flexible_matches = self._find_flexible_filename_matches(filename, file_size)

        # Combine both types of matches
        all_matches = exact_matches + flexible_matches

        if not all_matches:
            return False

        # Extract expected date pattern from target directory
        target_directory_name = os.path.basename(target_directory)
        expected_date_pattern = self._extract_date_pattern(target_directory_name)

        for existing_file in all_matches:
            match_found = False

            # Check if file is in directory with same date pattern (flexible matching)
            if expected_date_pattern and existing_file['date_pattern']:
                if existing_file['date_pattern'] == expected_date_pattern:
                    match_found = True
                    if not quiet:
                        existing_filename = os.path.basename(existing_file['path'])
                        self.logger.info(f"Found existing file in date-matched folder: {filename} "
                                       f"matches {existing_filename} in {existing_file['full_directory_name']}")
            elif existing_file['directory'] == target_directory:
                # Exact directory match (fallback)
                match_found = True

            if match_found:
                # Check if forceRecopyIfNewer is enabled
                if self.config['options']['force_recopy_if_newer']:
                    if file_date > existing_file['last_write_time']:
                        if not quiet:
                            self.logger.info(f"File exists but source is newer: {filename}")
                        return False  # File exists but source is newer, so copy it

                if not quiet:
                    self.logger.info(f"File already exists in target: {filename} (Size: {file_size} bytes)")
                return True

        return False

    def _find_flexible_filename_matches(self, source_filename: str, file_size: int) -> List[Dict[str, Any]]:
        """
        Find files that match the base filename pattern with potential appended text

        Example: '20250412_292993_1.mp4' should match '20250412_292993_1_KungFu_GimStyle.mp4'

        Args:
            source_filename: Source filename to match
            file_size: Expected file size for validation

        Returns:
            List of matching file info dictionaries
        """
        matches = []

        # Extract base filename (up to second underscore for date-named files)
        base_pattern = self._extract_base_filename_pattern(source_filename)
        if not base_pattern:
            return matches

        # Search through all cached files for potential matches
        for file_key, file_list in self.existing_files_cache.items():
            cached_filename, cached_size = file_key.split('|', 1)
            cached_size = int(cached_size)

            # Skip if sizes don't match (primary validation)
            if cached_size != file_size:
                continue

            # Check if cached filename matches the base pattern
            if self._filenames_match_flexible(source_filename, cached_filename, base_pattern):
                matches.extend(file_list)
                self.logger.debug(f"Flexible match found: {source_filename} matches {cached_filename} (size: {file_size})")

        return matches

    def _extract_base_filename_pattern(self, filename: str) -> Optional[str]:
        """
        Extract base filename pattern for flexible matching

        For date-named files like '20250412_292993_1.mp4', returns '20250412_292993_1'
        For other files, returns the full filename without extension

        Args:
            filename: Filename to extract pattern from

        Returns:
            Base pattern string or None if not extractable
        """
        import re
        from pathlib import Path

        # Remove extension
        name_without_ext = Path(filename).stem

        # Check if this is a date-named file (YYYYMMDD_HHMMSS_X pattern)
        date_pattern = r'^(\d{4}\d{2}\d{2}_\d{6}_\d+)'
        match = re.match(date_pattern, name_without_ext)

        if match:
            # Return the base pattern (YYYYMMDD_HHMMSS_X)
            return match.group(1)
        else:
            # For non-date-named files, return the full name without extension
            return name_without_ext

    def _filenames_match_flexible(self, source_filename: str, target_filename: str, base_pattern: str) -> bool:
        """
        Check if two filenames match using flexible matching rules

        Args:
            source_filename: Source filename
            target_filename: Target filename to compare against
            base_pattern: Base pattern extracted from source filename

        Returns:
            True if filenames match flexibly, False otherwise
        """
        from pathlib import Path

        # Remove extensions for comparison
        source_stem = Path(source_filename).stem
        target_stem = Path(target_filename).stem

        # Exact match
        if source_stem == target_stem:
            return True

        # Check if target starts with base pattern and has additional text
        if target_stem.startswith(base_pattern):
            # Ensure there's a separator (underscore) before additional text
            remaining = target_stem[len(base_pattern):]
            if remaining.startswith('_') or remaining == '':
                return True

        return False

    def find_existing_date_folder(self, base_path: str, date_pattern: str, quiet: bool = False) -> Optional[str]:
        """
        Find existing folder with date pattern (allows suffixes like _PaulArt)
        Converted from PowerShell Find-ExistingDateFolder function
        
        Args:
            base_path: Base directory to search in
            date_pattern: Date pattern to match (YYYY_MM_DD)
            
        Returns:
            Full path to existing folder or None if not found
        """
        if not os.path.exists(base_path):
            return None
        
        try:
            # Look for folders that start with the date pattern
            for item in os.listdir(base_path):
                item_path = os.path.join(base_path, item)
                if os.path.isdir(item_path):
                    # Check if folder name starts with date pattern (allows suffixes)
                    escaped_pattern = re.escape(date_pattern)
                    if re.match(f"^{escaped_pattern}(_.*)?$", item):
                        if not quiet:
                            self.logger.info(f"Found existing date folder: {item} for pattern {date_pattern}")
                        return item_path
                        
        except Exception as e:
            self.logger.warning(f"Error searching for existing date folders in {base_path}: {e}")
        
        return None
    
    def get_file_hash_quick(self, file_path: str) -> Optional[str]:
        """
        Get quick hash of file for comparison (first 1KB + last 1KB + size for large files)
        Converted from PowerShell Get-FileHashQuick function
        
        Args:
            file_path: Path to file
            
        Returns:
            Hash string or None if error
        """
        try:
            file_size = os.path.getsize(file_path)
            
            if file_size > 2048:
                # For large files, hash first 1KB + last 1KB + file size
                with open(file_path, 'rb') as f:
                    # Read first 1KB
                    first_bytes = f.read(1024)
                    
                    # Seek to last 1KB
                    f.seek(-1024, 2)
                    last_bytes = f.read(1024)
                    
                    # Combine with file size
                    combined_data = first_bytes + last_bytes + str(file_size).encode('utf-8')
                    
                    hash_obj = hashlib.sha256()
                    hash_obj.update(combined_data)
                    return hash_obj.hexdigest()
            else:
                # For small files, hash the entire file
                hash_obj = hashlib.sha256()
                with open(file_path, 'rb') as f:
                    hash_obj.update(f.read())
                return hash_obj.hexdigest()
                
        except Exception as e:
            self.logger.warning(f"Error computing hash for {file_path}: {e}")
            return None
    
    def update_cache_with_new_file(self, filename: str, file_size: int, 
                                 target_path: str, file_date: datetime):
        """
        Update cache with newly copied file
        
        Args:
            filename: Name of the file
            file_size: Size of the file
            target_path: Full path where file was copied
            file_date: Date/time of the file
        """
        file_key = f"{filename}|{file_size}"
        
        if file_key not in self.existing_files_cache:
            self.existing_files_cache[file_key] = []
        
        directory = os.path.dirname(target_path)
        directory_name = os.path.basename(directory)
        date_pattern = self._extract_date_pattern(directory_name)
        
        file_info = {
            'path': target_path,
            'last_write_time': file_date,
            'directory': directory,
            'date_pattern': date_pattern,
            'full_directory_name': directory_name,
            'size': file_size
        }
        
        self.existing_files_cache[file_key].append(file_info)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the deduplication cache"""
        total_entries = len(self.existing_files_cache)
        total_files = sum(len(files) for files in self.existing_files_cache.values())
        
        # Count files by target path
        path_counts = {}
        for target_path in self.target_paths:
            path_counts[target_path] = 0
        
        for file_list in self.existing_files_cache.values():
            for file_info in file_list:
                for target_path in self.target_paths:
                    if file_info['directory'].startswith(target_path):
                        path_counts[target_path] += 1
                        break
        
        return {
            'cache_entries': total_entries,
            'total_files': total_files,
            'files_by_target': path_counts,
            'cache_enabled': self.config['options']['enable_deduplication']
        }
