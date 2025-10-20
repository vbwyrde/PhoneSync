"""
Batch Target Path Resolver for PhoneSync + VideoProcessor
High-performance batch target path resolution using vectorized operations
Replaces individual file-by-file target path resolution with bulk processing
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Set, Tuple, Optional
from collections import defaultdict
import re

class BatchTargetResolver:
    """
    High-performance batch target path resolver
    Uses vectorized operations instead of individual file loops
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        Initialize batch target resolver
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.target_paths = config['target_paths']
        self.file_extensions = config['file_extensions']
        
        # Wudan detection patterns (vectorized)
        self.wudan_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in config.get('wudan_keywords', [])
        ]
        
        # Pre-compile date patterns for performance
        self.date_patterns = [
            re.compile(r'^(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})'),  # YYYYMMDD_HHMMSS
            re.compile(r'Screenshot_(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})'),  # Screenshot
            re.compile(r'wx_camera_(\d{10,13})'),  # WeChat timestamp
        ]
        
        # Cache for performance
        self._date_cache = {}
        self._wudan_cache = {}
        
    def resolve_all_target_paths(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolve target paths for all files using batch operations
        
        Args:
            files: List of file info dictionaries
            
        Returns:
            Dictionary with resolved paths and analysis
        """
        start_time = datetime.now()
        self.logger.info(f"Starting batch target path resolution for {len(files)} files...")
        
        # Step 1: Batch classify files by type (pictures vs videos)
        pictures, videos = self._batch_classify_by_type(files)
        
        # Step 2: Batch extract dates and create date folders
        date_folders = self._batch_create_date_folders(files)
        
        # Step 3: Batch identify Wudan videos
        wudan_videos = self._batch_identify_wudan_videos(videos)
        
        # Step 4: Batch resolve target paths
        target_paths = self._batch_resolve_paths(files, pictures, videos, wudan_videos, date_folders)
        
        # Step 5: Generate analysis
        analysis = self._generate_batch_analysis(files, pictures, videos, wudan_videos, target_paths)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        self.logger.info(f"Batch target path resolution complete: {len(files)} files in {elapsed:.2f} seconds")
        
        return {
            'target_paths': target_paths,
            'analysis': analysis,
            'performance': {
                'total_files': len(files),
                'elapsed_seconds': elapsed,
                'files_per_second': len(files) / elapsed if elapsed > 0 else 0
            }
        }
    
    def _batch_classify_by_type(self, files: List[Dict[str, Any]]) -> Tuple[Set[str], Set[str]]:
        """Batch classify files into pictures and videos"""
        pictures = set()
        videos = set()
        
        picture_exts = set(self.file_extensions['pictures'])
        video_exts = set(self.file_extensions['videos'])
        
        for file_info in files:
            ext = file_info.get('extension', '').lower()
            file_key = f"{file_info['name']}|{file_info['size']}"
            
            if ext in picture_exts:
                pictures.add(file_key)
            elif ext in video_exts:
                videos.add(file_key)
        
        self.logger.debug(f"Classified: {len(pictures)} pictures, {len(videos)} videos")
        return pictures, videos
    
    def _batch_create_date_folders(self, files: List[Dict[str, Any]]) -> Dict[str, str]:
        """Batch create date folder names for all files"""
        date_folders = {}
        
        for file_info in files:
            file_key = f"{file_info['name']}|{file_info['size']}"
            file_date = file_info.get('date')
            
            if file_date:
                # Create date folder name: YYYY_MM_DD_DDD
                date_str = file_date.strftime('%Y_%m_%d')
                day_name = file_date.strftime('%a')  # Mon, Tue, Wed, etc.
                date_folder = f"{date_str}_{day_name}"
                date_folders[file_key] = date_folder
        
        self.logger.debug(f"Created date folders for {len(date_folders)} files")
        return date_folders
    
    def _batch_identify_wudan_videos(self, videos: Set[str]) -> Set[str]:
        """Batch identify Wudan videos using vectorized pattern matching"""
        wudan_videos = set()
        
        # Use cached results when possible
        for video_key in videos:
            filename = video_key.split('|')[0]
            
            if filename in self._wudan_cache:
                if self._wudan_cache[filename]:
                    wudan_videos.add(video_key)
                continue
            
            # Check Wudan patterns
            is_wudan = any(pattern.search(filename) for pattern in self.wudan_patterns)
            self._wudan_cache[filename] = is_wudan
            
            if is_wudan:
                wudan_videos.add(video_key)
        
        self.logger.debug(f"Identified {len(wudan_videos)} Wudan videos out of {len(videos)} total videos")
        return wudan_videos
    
    def _batch_resolve_paths(self, files: List[Dict[str, Any]], pictures: Set[str], 
                           videos: Set[str], wudan_videos: Set[str], 
                           date_folders: Dict[str, str]) -> Dict[str, str]:
        """Batch resolve target paths for all files"""
        target_paths = {}
        
        for file_info in files:
            file_key = f"{file_info['name']}|{file_info['size']}"
            date_folder = date_folders.get(file_key, '')
            
            if file_key in pictures:
                # Pictures go to pictures folder
                base_path = self.target_paths['pictures']
                target_path = os.path.join(base_path, date_folder)
            elif file_key in wudan_videos:
                # Wudan videos go to wudan folder
                base_path = self.target_paths['wudan']
                target_path = os.path.join(base_path, date_folder)
            elif file_key in videos:
                # Regular videos go to videos folder
                base_path = self.target_paths['videos']
                target_path = os.path.join(base_path, date_folder)
            else:
                # Unsupported file type
                continue
            
            target_paths[file_key] = os.path.normpath(target_path)
        
        self.logger.debug(f"Resolved target paths for {len(target_paths)} files")
        return target_paths
    
    def _generate_batch_analysis(self, files: List[Dict[str, Any]], pictures: Set[str], 
                               videos: Set[str], wudan_videos: Set[str], 
                               target_paths: Dict[str, str]) -> Dict[str, Any]:
        """Generate analysis of batch target path resolution"""
        
        # Count by target type
        by_target_type = {
            'pictures': len(pictures),
            'videos': len(videos) - len(wudan_videos),
            'wudan_videos': len(wudan_videos),
            'unsupported': len(files) - len(pictures) - len(videos)
        }
        
        # Get unique target folders needed
        target_folders_needed = set(target_paths.values())
        
        # Count by date
        by_date = defaultdict(lambda: {'pictures': 0, 'videos': 0, 'wudan_videos': 0})
        
        for file_info in files:
            file_key = f"{file_info['name']}|{file_info['size']}"
            file_date = file_info.get('date')
            
            if file_date:
                date_key = file_date.strftime('%Y-%m-%d')
                
                if file_key in pictures:
                    by_date[date_key]['pictures'] += 1
                elif file_key in wudan_videos:
                    by_date[date_key]['wudan_videos'] += 1
                elif file_key in videos:
                    by_date[date_key]['videos'] += 1
        
        return {
            'total_files': len(files),
            'by_target_type': by_target_type,
            'by_date': dict(by_date),
            'wudan_matches': len(wudan_videos),
            'target_folders_needed': list(target_folders_needed),
            'folders_to_create': len(target_folders_needed)
        }
    
    def get_target_path_for_file(self, file_info: Dict[str, Any]) -> Optional[str]:
        """
        Get target path for a single file (compatibility method)
        Uses cached batch results when available
        """
        file_key = f"{file_info['name']}|{file_info['size']}"
        
        # This would be called after batch resolution
        # For now, fall back to individual resolution
        return self._resolve_single_file_path(file_info)
    
    def _resolve_single_file_path(self, file_info: Dict[str, Any]) -> Optional[str]:
        """Resolve target path for a single file (fallback method)"""
        # Determine file type
        ext = file_info.get('extension', '').lower()
        
        if ext in self.file_extensions['pictures']:
            base_path = self.target_paths['pictures']
        elif ext in self.file_extensions['videos']:
            # Check if it's a Wudan video
            filename = file_info.get('name', '')
            is_wudan = any(pattern.search(filename) for pattern in self.wudan_patterns)
            
            if is_wudan:
                base_path = self.target_paths['wudan']
            else:
                base_path = self.target_paths['videos']
        else:
            return None
        
        # Create date folder
        file_date = file_info.get('date')
        if file_date:
            date_str = file_date.strftime('%Y_%m_%d')
            day_name = file_date.strftime('%a')
            date_folder = f"{date_str}_{day_name}"
            return os.path.normpath(os.path.join(base_path, date_folder))
        
        return base_path
