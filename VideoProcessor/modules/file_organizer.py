"""
File Organizer for PhoneSync + VideoProcessor
Handles file operations with collision handling and progress tracking
Converted from PowerShell Copy-FileToTarget and Process-Directory functions
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List

class FileOrganizer:
    """
    Organizes files by copying them to appropriate target locations
    Converted from PowerShell file organization logic
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger, 
                 target_resolver, dedup_manager):
        """
        Initialize file organizer
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
            target_resolver: TargetPathResolver instance
            dedup_manager: DeduplicationManager instance
        """
        self.config = config
        self.logger = logger
        self.target_resolver = target_resolver
        self.dedup_manager = dedup_manager
        
        # Statistics tracking
        self.stats = {
            'files_processed': 0,
            'files_copied': 0,
            'files_skipped': 0,
            'files_failed': 0,
            'bytes_copied': 0,
            'directories_created': 0,
            'duplicates_found': 0
        }
    
    def organize_file(self, file_info: Dict[str, Any], dry_run: bool = False, skip_dedup_check: bool = False, quiet: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Organize a single file by copying it to the appropriate target location
        Converted from PowerShell Copy-FileToTarget function

        Args:
            file_info: Dictionary containing file information
            dry_run: If True, don't actually copy files
            skip_dedup_check: If True, skip deduplication check (already done in batch filtering)

        Returns:
            Tuple of (success, target_path)
        """
        source_path = file_info['path']
        filename = file_info['name']
        file_size = file_info['size']
        file_date = file_info['date']

        try:
            # Get target folder path
            target_folder = self.target_resolver.get_target_folder_path(file_info, quiet=quiet)

            if not target_folder:
                self.logger.warning(f"Could not determine target folder for {source_path}")
                self.stats['files_failed'] += 1
                return False, None

            # Check if file already exists using deduplication (only if not already batch-filtered)
            if not skip_dedup_check and self.dedup_manager.file_exists_in_target(filename, file_size, file_date, target_folder):
                self.logger.info(f"Skipping duplicate file: {filename}")
                self.stats['files_skipped'] += 1
                self.stats['duplicates_found'] += 1
                return True, target_folder  # Consider this a success (file already exists)
            
            # Ensure target directory exists
            if not self.target_resolver.ensure_target_directory(target_folder):
                self.logger.error(f"Could not create target directory: {target_folder}")
                self.stats['files_failed'] += 1
                return False, None
            
            # Get target file path (handles name collisions)
            target_file_path, final_filename = self.target_resolver.get_target_file_path(
                file_info, target_folder
            )
            
            # Perform the copy operation
            success = self._copy_file(source_path, target_file_path, file_info, dry_run)
            
            if success:
                self.stats['files_copied'] += 1
                self.stats['bytes_copied'] += file_size
                
                # Update deduplication cache with newly copied file
                if not dry_run:
                    self.dedup_manager.update_cache_with_new_file(
                        final_filename, file_size, target_file_path, file_date
                    )
                
                return True, target_file_path
            else:
                self.stats['files_failed'] += 1
                return False, None
                
        except Exception as e:
            self.logger.error(f"Error organizing file {source_path}: {e}")
            self.stats['files_failed'] += 1
            return False, None
        finally:
            self.stats['files_processed'] += 1
    
    def _copy_file(self, source_path: str, target_path: str, 
                  file_info: Dict[str, Any], dry_run: bool) -> bool:
        """
        Copy file from source to target with error handling
        
        Args:
            source_path: Source file path
            target_path: Target file path
            file_info: File information dictionary
            dry_run: If True, don't actually copy
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if dry_run:
                self.logger.info(f"[DRY RUN] Would copy: {source_path} -> {target_path}")
                return True
            
            # Check if we should actually copy files (vs move)
            if not self.config['options']['copy_files']:
                self.logger.info(f"[COPY DISABLED] Would copy: {source_path} -> {target_path}")
                return True
            
            # Perform the actual copy
            shutil.copy2(source_path, target_path)  # copy2 preserves metadata
            
            self.logger.info(f"Copied: {source_path} -> {target_path}")
            
            # Verify the copy was successful
            if os.path.exists(target_path):
                target_size = os.path.getsize(target_path)
                source_size = file_info['size']
                
                if target_size == source_size:
                    return True
                else:
                    self.logger.error(f"Copy verification failed: size mismatch for {target_path}")
                    # Clean up incomplete copy
                    try:
                        os.remove(target_path)
                    except Exception:
                        pass
                    return False
            else:
                self.logger.error(f"Copy failed: target file does not exist {target_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to copy file {source_path} to {target_path}: {e}")
            return False
    
    def organize_files_batch(self, files: List[Dict[str, Any]], 
                           dry_run: bool = False, 
                           progress_callback=None) -> Dict[str, Any]:
        """
        Organize multiple files with progress reporting
        
        Args:
            files: List of file information dictionaries
            dry_run: If True, don't actually copy files
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dictionary with batch processing results
        """
        self.logger.info(f"Starting batch organization of {len(files)} files")
        
        # Reset statistics
        self.stats = {
            'files_processed': 0,
            'files_copied': 0,
            'files_skipped': 0,
            'files_failed': 0,
            'bytes_copied': 0,
            'directories_created': 0,
            'duplicates_found': 0
        }
        
        successful_files = []
        failed_files = []
        
        for i, file_info in enumerate(files):
            try:
                success, target_path = self.organize_file(file_info, dry_run)
                
                if success:
                    successful_files.append({
                        'source': file_info['path'],
                        'target': target_path,
                        'filename': file_info['name']
                    })
                else:
                    failed_files.append({
                        'source': file_info['path'],
                        'filename': file_info['name'],
                        'error': 'Organization failed'
                    })
                
                # Progress reporting
                if progress_callback and (i + 1) % 10 == 0:
                    progress_callback(i + 1, len(files), self.stats)
                
                # Log progress periodically
                if (i + 1) % 100 == 0:
                    progress_pct = ((i + 1) / len(files)) * 100
                    self.logger.info(f"Progress: {progress_pct:.1f}% ({i + 1}/{len(files)})")
                
            except Exception as e:
                self.logger.error(f"Unexpected error processing {file_info.get('path', 'unknown')}: {e}")
                failed_files.append({
                    'source': file_info.get('path', 'unknown'),
                    'filename': file_info.get('name', 'unknown'),
                    'error': str(e)
                })
        
        # Final progress report
        if progress_callback:
            progress_callback(len(files), len(files), self.stats)
        
        results = {
            'total_files': len(files),
            'successful_files': successful_files,
            'failed_files': failed_files,
            'statistics': self.stats.copy(),
            'success_rate': (len(successful_files) / len(files)) * 100 if files else 0
        }
        
        self.logger.info(f"Batch organization complete: {len(successful_files)} successful, "
                        f"{len(failed_files)} failed, {self.stats['files_skipped']} skipped")
        
        return results
    
    def get_organization_preview(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Preview where files would be organized without actually copying them
        
        Args:
            files: List of file information dictionaries
            
        Returns:
            Dictionary with organization preview
        """
        preview = {
            'total_files': len(files),
            'organization_plan': [],
            'target_analysis': None,
            'potential_issues': []
        }
        
        for file_info in files:
            try:
                target_folder = self.target_resolver.get_target_folder_path(file_info)
                
                if target_folder:
                    # Check if file would be skipped due to duplication
                    would_skip = self.dedup_manager.file_exists_in_target(
                        file_info['name'], file_info['size'], 
                        file_info['date'], target_folder
                    )
                    
                    target_file_path, final_filename = self.target_resolver.get_target_file_path(
                        file_info, target_folder
                    )
                    
                    plan_item = {
                        'source': file_info['path'],
                        'target_folder': target_folder,
                        'target_file': target_file_path,
                        'final_filename': final_filename,
                        'would_skip': would_skip,
                        'file_type': file_info['type'],
                        'date': file_info['date'].strftime('%Y-%m-%d'),
                        'size_mb': round(file_info['size'] / (1024 * 1024), 2)
                    }
                    
                    # Check for potential issues
                    if final_filename != file_info['name']:
                        preview['potential_issues'].append(
                            f"Name collision: {file_info['name']} -> {final_filename}"
                        )
                    
                    if not os.path.exists(target_folder):
                        if not self.config['options']['create_missing_folders']:
                            preview['potential_issues'].append(
                                f"Target folder does not exist and creation disabled: {target_folder}"
                            )
                else:
                    plan_item = {
                        'source': file_info['path'],
                        'target_folder': None,
                        'error': 'Unsupported file type or could not determine target'
                    }
                    preview['potential_issues'].append(
                        f"Cannot organize: {file_info['path']} - unsupported file type"
                    )
                
                preview['organization_plan'].append(plan_item)
                
            except Exception as e:
                preview['potential_issues'].append(
                    f"Error analyzing {file_info.get('path', 'unknown')}: {e}"
                )
        
        # Get target analysis
        preview['target_analysis'] = self.target_resolver.analyze_target_structure(files)
        
        return preview
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        stats = self.stats.copy()
        
        # Add calculated fields
        if stats['files_processed'] > 0:
            stats['success_rate'] = (stats['files_copied'] / stats['files_processed']) * 100
            stats['skip_rate'] = (stats['files_skipped'] / stats['files_processed']) * 100
            stats['failure_rate'] = (stats['files_failed'] / stats['files_processed']) * 100
        else:
            stats['success_rate'] = 0
            stats['skip_rate'] = 0
            stats['failure_rate'] = 0
        
        # Convert bytes to human readable
        stats['bytes_copied_mb'] = round(stats['bytes_copied'] / (1024 * 1024), 2)
        stats['bytes_copied_gb'] = round(stats['bytes_copied'] / (1024 * 1024 * 1024), 3)

        return stats

    def get_organization_statistics(self) -> Dict[str, Any]:
        """Get file organization statistics"""
        return {
            'files_organized': self.stats.get('files_copied', 0),
            'folders_created': self.stats.get('directories_created', 0),
            'collisions_resolved': self.stats.get('duplicates_found', 0),
            'errors': self.stats.get('files_failed', 0)
        }
