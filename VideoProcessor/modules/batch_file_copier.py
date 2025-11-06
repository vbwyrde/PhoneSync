import os
import time
import subprocess
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta


class BatchFileCopier:
    """High-performance batch file copier using system commands and progress tracking"""
    
    def __init__(self, config: Dict[str, Any], logger):
        self.config = config
        self.logger = logger
        self.start_time = None
        self.total_files = 0
        self.processed_files = 0
        self.failed_files = 0
        self.copied_files = 0
        
    def copy_files_batch(self, files_to_process: List[Dict[str, Any]], 
                        target_path_resolver, file_organizer, 
                        processing_state_manager) -> Dict[str, Any]:
        """
        Copy files using optimized batch operations with progress tracking
        
        Args:
            files_to_process: List of file info dictionaries
            target_path_resolver: Module to resolve target paths
            file_organizer: Module to organize files
            processing_state_manager: Module to track processed files
            
        Returns:
            Dictionary with processing statistics
        """
        self.start_time = time.time()
        self.total_files = len(files_to_process)
        self.processed_files = 0
        self.failed_files = 0
        self.copied_files = 0
        
        self.logger.info(f"=== Starting Batch File Copy Operation ===")
        self.logger.info(f"Total files to process: {self.total_files}")
        
        # Group files by target directory for batch operations
        files_by_target_dir = self._group_files_by_target_directory(
            files_to_process, target_path_resolver
        )
        
        # Process each target directory in batches
        for target_dir, file_list in files_by_target_dir.items():
            self._process_directory_batch(
                target_dir, file_list, file_organizer, processing_state_manager
            )
        
        # Final statistics
        elapsed_time = time.time() - self.start_time
        stats = {
            'total_files': self.total_files,
            'copied_files': self.copied_files,
            'failed_files': self.failed_files,
            'elapsed_time': elapsed_time,
            'files_per_second': self.copied_files / elapsed_time if elapsed_time > 0 else 0
        }
        
        self.logger.info(f"=== Batch Copy Operation Complete ===")
        self.logger.info(f"Copied: {self.copied_files} files")
        self.logger.info(f"Failed: {self.failed_files} files")
        self.logger.info(f"Total time: {elapsed_time:.2f} seconds")
        self.logger.info(f"Speed: {stats['files_per_second']:.2f} files/second")
        
        return stats

    def copy_files_batch_with_paths(self, files_to_process: List[Dict[str, Any]],
                                   target_paths: Dict[str, str],
                                   file_organizer, processing_state_manager) -> Dict[str, Any]:
        """
        Copy files using pre-resolved target paths (optimized version)

        Args:
            files_to_process: List of file info dictionaries
            target_paths: Pre-resolved target paths (file_key -> target_path)
            file_organizer: FileOrganizer instance
            processing_state_manager: ProcessingStateManager instance

        Returns:
            Copy operation statistics
        """
        self.logger.info(f"Starting optimized batch copy with pre-resolved paths for {len(files_to_process)} files")

        # Initialize counters
        self.total_files = len(files_to_process)
        self.processed_files = 0
        self.copied_files = 0
        self.failed_files = 0
        self.start_time = time.time()

        # Group files by target directory using pre-resolved paths
        files_by_dir = self._group_files_by_resolved_paths(files_to_process, target_paths)

        self.logger.info(f"Grouped files into {len(files_by_dir)} target directories")

        # Process each directory
        for target_dir, files in files_by_dir.items():
            self._process_directory_batch(target_dir, files, file_organizer, processing_state_manager)

        return self._get_final_stats()

    def _group_files_by_resolved_paths(self, files_to_process: List[Dict[str, Any]],
                                     target_paths: Dict[str, str]) -> Dict[str, List[Dict[str, Any]]]:
        """Group files by target directory using pre-resolved paths"""
        files_by_dir = {}

        for file_info in files_to_process:
            file_key = f"{file_info['name']}|{file_info['size']}"

            if file_key in target_paths:
                target_path = target_paths[file_key]
                target_dir = os.path.dirname(target_path)

                if target_dir not in files_by_dir:
                    files_by_dir[target_dir] = []

                # Add the resolved target path to file_info for later use
                file_info_with_path = file_info.copy()
                file_info_with_path['resolved_target_path'] = target_path
                files_by_dir[target_dir].append(file_info_with_path)
            else:
                self.logger.error(f"No target path resolved for file: {file_info.get('name', 'unknown')}")
                self.failed_files += 1

        return files_by_dir

    def _group_files_by_target_directory(self, files_to_process: List[Dict[str, Any]],
                                       target_path_resolver) -> Dict[str, List[Dict[str, Any]]]:
        """Group files by their target directory for batch processing"""
        files_by_dir = {}
        
        for file_info in files_to_process:
            try:
                # Get target folder path for this file
                target_folder = target_path_resolver.get_target_folder_path(file_info)
                if not target_folder:
                    self.logger.error(f"Could not determine target folder for file: {file_info.get('name', 'unknown')}")
                    self.failed_files += 1
                    continue

                # Get full target file path with collision handling
                target_path, final_filename = target_path_resolver.get_target_file_path(file_info, target_folder)
                target_dir = os.path.dirname(target_path)
                
                if target_dir not in files_by_dir:
                    files_by_dir[target_dir] = []
                
                # Add both source and target info
                file_info['target_path'] = target_path
                file_info['target_dir'] = target_dir
                files_by_dir[target_dir].append(file_info)
                
            except Exception as e:
                self.logger.error(f"Error resolving target path for {file_info.get('filename', 'unknown')}: {e}")
                self.failed_files += 1
        
        self.logger.info(f"Grouped files into {len(files_by_dir)} target directories")
        return files_by_dir
    
    def _process_directory_batch(self, target_dir: str, file_list: List[Dict[str, Any]], 
                               file_organizer, processing_state_manager):
        """Process all files for a specific target directory in batch"""
        
        # Ensure target directory exists
        os.makedirs(target_dir, exist_ok=True)
        
        self.logger.info(f"Processing {len(file_list)} files for directory: {target_dir}")
        
        # Process files individually but with optimized operations
        for i, file_info in enumerate(file_list):
            self._process_single_file_optimized(
                file_info, file_organizer, processing_state_manager
            )
            
            # Update progress every 10 files or at the end
            if (i + 1) % 10 == 0 or (i + 1) == len(file_list):
                self._log_progress()
    
    def _process_single_file_optimized(self, file_info: Dict[str, Any],
                                     file_organizer, processing_state_manager):
        """Process a single file with optimized operations"""
        try:
            # Check if file_info is actually a tuple instead of a dictionary
            if isinstance(file_info, tuple):
                self.logger.error(f"ERROR: file_info is a tuple instead of dictionary: {file_info}")
                self.failed_files += 1
                return

            if not isinstance(file_info, dict):
                self.logger.error(f"ERROR: file_info is not a dictionary: {type(file_info)} - {file_info}")
                self.failed_files += 1
                return

            source_path = file_info.get('path', file_info.get('full_path'))
            # Handle both resolved_target_path (new) and target_path (old) for compatibility
            target_path = file_info.get('resolved_target_path', file_info.get('target_path'))
            filename = file_info.get('name', file_info.get('filename'))
            
            # Use file organizer to handle the copy (it has collision detection)
            # Note: organize_file returns (success, target_path) tuple, not a dictionary
            success, target_path = file_organizer.organize_file(file_info, skip_dedup_check=True)

            if success:
                # Mark as processed in state manager
                ## processing_state_manager.mark_file_processed(
                ##     filename, file_info.get('size', file_info.get('file_size', 0)),
                ##     file_info.get('type', file_info.get('file_type', 'unknown'))
                ## )

                processing_state_manager.mark_file_processed(file_info)
                self.copied_files += 1
                self.logger.debug(f"Successfully copied: {filename}")
            else:
                self.failed_files += 1
                self.logger.error(f"Failed to copy: {filename}")
                
        except Exception as e:
            self.failed_files += 1
            # Handle both dictionary and tuple cases for file_info
            if isinstance(file_info, dict):
                filename = file_info.get('name', file_info.get('filename', 'unknown'))
            else:
                filename = 'unknown'
            self.logger.error(f"Error processing file {filename}: {e}")
        
        finally:
            self.processed_files += 1
    
    def _log_progress(self):
        """Log current progress with percentage and ETA"""
        if self.total_files == 0:
            return
            
        start_time = self.start_time if self.start_time is not None else time.time()

        elapsed_time = time.time() - start_time
        percent_complete = (self.processed_files / self.total_files) * 100
        
        # Calculate ETA
        if self.processed_files > 0:
            avg_time_per_file = elapsed_time / self.processed_files
            remaining_files = self.total_files - self.processed_files
            eta_seconds = remaining_files * avg_time_per_file
            eta = timedelta(seconds=int(eta_seconds))
        else:
            eta = "Unknown"
        
        # Calculate current speed
        files_per_second = self.processed_files / elapsed_time if elapsed_time > 0 else 0
        
        self.logger.info(
            f"Progress: {self.processed_files}/{self.total_files} ({percent_complete:.1f}%) | "
            f"Copied: {self.copied_files} | Failed: {self.failed_files} | "
            f"Speed: {files_per_second:.1f} files/sec | ETA: {eta}"
        )

    def _get_final_stats(self) -> Dict[str, Any]:
        """Get final statistics for the batch copy operation"""
        elapsed_time = time.time() - self.start_time if hasattr(self, 'start_time') and self.start_time is not None else 0

        stats = {
            'copied_files': self.copied_files,
            'failed_files': self.failed_files,
            'total_files': self.total_files,
            'processed_files': self.processed_files,
            'elapsed_time': elapsed_time,
            'files_per_second': self.processed_files / elapsed_time if elapsed_time > 0 else 0
        }

        self.logger.info(f"=== Batch Copy Operation Complete ===")
        self.logger.info(f"Copied: {stats['copied_files']} files")
        self.logger.info(f"Failed: {stats['failed_files']} files")
        self.logger.info(f"Total time: {elapsed_time:.2f} seconds")
        self.logger.info(f"Speed: {stats['files_per_second']:.2f} files/second")

        return stats
