"""
Target Path Resolver for PhoneSync + VideoProcessor
Determines correct destination folders (Pictures/Videos/Wudan) with existing folder detection
Converted from PowerShell Get-TargetFolderPath and Find-ExistingDateFolder functions
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

class TargetPathResolver:
    """
    Resolves target paths for files based on type, date, and Wudan rules
    Converted from PowerShell target path resolution logic
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger, 
                 wudan_engine, dedup_manager):
        """
        Initialize target path resolver
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
            wudan_engine: WudanRulesEngine instance
            dedup_manager: DeduplicationManager instance
        """
        self.config = config
        self.logger = logger
        self.wudan_engine = wudan_engine
        self.dedup_manager = dedup_manager
        
        # Get target paths from config
        self.target_paths = config['target_paths']
        self.file_extensions = config['file_extensions']
    
    def get_target_folder_path(self, file_info: Dict[str, Any], quiet: bool = False) -> Optional[str]:
        """
        Get target folder path for a file based on type, date, and Wudan rules
        Converted from PowerShell Get-TargetFolderPath function
        
        Args:
            file_info: Dictionary containing file information (path, type, date, etc.)
            
        Returns:
            Full path to target folder or None if unsupported file type
        """
        file_path = file_info['path']
        file_date = file_info['date']
        file_type = file_info['type']
        extension = file_info['extension']
        
        # Determine base target path based on file type and Wudan rules
        base_path = self._determine_base_path(file_type, extension, file_date)

        if not base_path:
            self.logger.warning(f"Unsupported file extension: {extension} for file {file_path}")
            return None

        # Create date pattern for folder name - add day of week for Wudan files
        if base_path == self.target_paths['wudan']:
            # For Wudan files: 2024_06_11_Wed
            day_of_week = file_date.strftime('%a')  # Mon, Tue, Wed, etc.
            date_pattern = file_date.strftime(f'%Y_%m_%d_{day_of_week}')
            self.logger.debug(f"Wudan folder date pattern with day of week: {date_pattern}")
        else:
            # For regular files: 2024_06_11
            date_pattern = file_date.strftime('%Y_%m_%d')

        # Look for existing folder with the date pattern (allows suffixes like _PaulArt)
        existing_folder = self.dedup_manager.find_existing_date_folder(base_path, date_pattern, quiet=quiet)

        if existing_folder:
            if not quiet:
                self.logger.debug(f"Using existing date folder: {existing_folder}")
            return os.path.normpath(existing_folder)
        else:
            # Return the standard date folder path if no existing folder found
            target_folder = os.path.join(base_path, date_pattern)
            if not quiet:
                self.logger.debug(f"Will create new date folder: {target_folder}")
            return os.path.normpath(target_folder)
    
    def _determine_base_path(self, file_type: str, extension: str, file_date: datetime) -> Optional[str]:
        """
        Determine base target path based on file type and Wudan rules
        
        Args:
            file_type: 'picture' or 'video'
            extension: File extension (e.g., '.jpg', '.mp4')
            file_date: Date/time of the file
            
        Returns:
            Base path string or None if unsupported
        """
        if file_type == 'picture':
            if extension in self.file_extensions['pictures']:
                return self.target_paths['pictures']
        
        elif file_type == 'video':
            if extension in self.file_extensions['videos']:
                # Check Wudan rules for videos
                if self.wudan_engine.should_go_to_wudan_folder(file_date):
                    self.logger.debug(f"Video matches Wudan rules: {file_date}")
                    return self.target_paths['wudan']
                else:
                    self.logger.debug(f"Video does not match Wudan rules: {file_date}")
                    return self.target_paths['videos']
        
        return None
    
    def ensure_target_directory(self, target_path: str) -> bool:
        """
        Ensure target directory exists, create if needed
        Converted from PowerShell Ensure-TargetDirectory function
        
        Args:
            target_path: Path to target directory
            
        Returns:
            True if directory exists or was created successfully, False otherwise
        """
        if os.path.exists(target_path):
            return True
        
        if self.config['options']['create_missing_folders']:
            try:
                os.makedirs(target_path, exist_ok=True)
                self.logger.info(f"Created directory: {target_path}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to create directory {target_path}: {e}")
                return False
        else:
            self.logger.warning(f"Target directory does not exist and creation is disabled: {target_path}")
            return False
    
    def get_target_file_path(self, file_info: Dict[str, Any], target_folder: str) -> Tuple[str, str]:
        """
        Get full target file path, handling name collisions

        Args:
            file_info: Dictionary containing file information
            target_folder: Target folder path

        Returns:
            Tuple of (target_file_path, final_filename)
        """
        original_filename = file_info['name']
        # Normalize the target folder path to use consistent separators
        normalized_target_folder = os.path.normpath(target_folder)
        target_file_path = os.path.join(normalized_target_folder, original_filename)
        
        # If file doesn't exist, use original name
        if not os.path.exists(target_file_path):
            return target_file_path, original_filename
        
        # Handle name collision by creating unique filename
        return self._create_unique_filename(normalized_target_folder, original_filename, file_info)
    
    def _create_unique_filename(self, target_folder: str, original_filename: str, 
                              file_info: Dict[str, Any]) -> Tuple[str, str]:
        """
        Create unique filename to avoid collisions
        
        Args:
            target_folder: Target folder path
            original_filename: Original filename
            file_info: File information dictionary
            
        Returns:
            Tuple of (unique_file_path, unique_filename)
        """
        base_name = Path(original_filename).stem
        extension = Path(original_filename).suffix
        counter = 1
        
        while True:
            unique_filename = f"{base_name}_{counter}{extension}"
            unique_file_path = os.path.normpath(os.path.join(target_folder, unique_filename))

            if not os.path.exists(unique_file_path):
                self.logger.info(f"Created unique filename to avoid collision: {unique_filename}")
                return unique_file_path, unique_filename
            
            counter += 1
            
            # Safety check to avoid infinite loop
            if counter > 9999:
                self.logger.error(f"Could not create unique filename after 9999 attempts for {original_filename}")
                # Fall back to timestamp-based naming
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                unique_filename = f"{base_name}_{timestamp}{extension}"
                unique_file_path = os.path.join(target_folder, unique_filename)
                return unique_file_path, unique_filename
    
    def analyze_target_structure(self, files: list) -> Dict[str, Any]:
        """
        Analyze where files would be placed in target structure
        
        Args:
            files: List of file information dictionaries
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            'total_files': len(files),
            'by_target_type': {
                'pictures': 0,
                'videos': 0,
                'wudan_videos': 0,
                'unsupported': 0
            },
            'by_date': {},
            'wudan_matches': 0,
            'target_folders_needed': set()
        }
        
        for file_info in files:
            try:
                target_folder = self.get_target_folder_path(file_info)
                
                if not target_folder:
                    analysis['by_target_type']['unsupported'] += 1
                    continue
                
                # Determine target type
                if self.target_paths['pictures'] in target_folder:
                    target_type = 'pictures'
                elif self.target_paths['wudan'] in target_folder:
                    target_type = 'wudan'
                    analysis['wudan_matches'] += 1
                elif self.target_paths['videos'] in target_folder:
                    target_type = 'videos'
                else:
                    target_type = 'unsupported'
                
                analysis['by_target_type'][target_type] += 1
                analysis['target_folders_needed'].add(target_folder)
                
                # Track by date
                date_key = file_info['date'].strftime('%Y-%m-%d')
                if date_key not in analysis['by_date']:
                    analysis['by_date'][date_key] = {
                        'pictures': 0, 'videos': 0, 'wudan_videos': 0
                    }
                analysis['by_date'][date_key][target_type] += 1
                
            except Exception as e:
                self.logger.warning(f"Error analyzing target for {file_info.get('path', 'unknown')}: {e}")
                analysis['by_target_type']['unsupported'] += 1
        
        # Convert set to list for JSON serialization
        analysis['target_folders_needed'] = list(analysis['target_folders_needed'])
        analysis['folders_to_create'] = len(analysis['target_folders_needed'])
        
        return analysis
    
    def validate_target_paths(self) -> Dict[str, Any]:
        """
        Validate that all target paths are accessible
        
        Returns:
            Dictionary with validation results
        """
        validation = {
            'all_valid': True,
            'results': {},
            'errors': []
        }
        
        for path_type, path_value in self.target_paths.items():
            try:
                path_obj = Path(path_value)
                
                result = {
                    'exists': path_obj.exists(),
                    'is_directory': path_obj.is_dir() if path_obj.exists() else None,
                    'writable': None,
                    'parent_exists': path_obj.parent.exists()
                }
                
                # Test writability if directory exists
                if result['exists'] and result['is_directory']:
                    try:
                        test_file = path_obj / '.write_test'
                        test_file.touch()
                        test_file.unlink()
                        result['writable'] = True
                    except Exception:
                        result['writable'] = False
                        validation['all_valid'] = False
                        validation['errors'].append(f"{path_type}: Not writable - {path_value}")
                
                # Check if we can create the directory if it doesn't exist
                elif not result['exists']:
                    if result['parent_exists'] and self.config['options']['create_missing_folders']:
                        result['can_create'] = True
                    else:
                        result['can_create'] = False
                        validation['all_valid'] = False
                        validation['errors'].append(f"{path_type}: Cannot create directory - {path_value}")
                
                validation['results'][path_type] = result
                
            except Exception as e:
                validation['all_valid'] = False
                validation['errors'].append(f"{path_type}: Validation error - {e}")
                validation['results'][path_type] = {'error': str(e)}
        
        return validation
