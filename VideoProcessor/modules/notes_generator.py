"""
Notes Generator for PhoneSync + VideoProcessor
Generates and manages notes files for video analysis results
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class NotesGenerator:
    """
    Generates and manages notes files for video analysis results
    Creates organized notes files based on analysis results
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        Initialize notes generator
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        
        # Notes settings - notes go in the video directories, not separate notes directory
        self.videos_base_path = config['target_paths']['videos']
        self.wudan_base_path = config['target_paths']['wudan']
        self.notes_enabled = config['options'].get('generate_notes', True)

        # Storage for notes to be written: date -> {'notes': [...], 'directory': 'path'}
        self.pending_notes = {}
    
    def add_video_note(self, file_date: datetime, filename: str, description: str, video_directory: str, dry_run: bool = False):
        """
        Add a video analysis note

        Args:
            file_date: Date of the video file
            filename: Name of the video file
            description: Analysis description
            video_directory: Full path to the directory containing the video
            dry_run: If True, simulate adding note without writing
        """
        if not self.notes_enabled:
            return

        if dry_run:
            self.logger.info(f"[DRY RUN] Would add note for {filename}: {description[:50]}...")
            return

        # Format date for grouping
        date_key = file_date.strftime("%Y_%m_%d")

        # Create simple note entry (filename - description format)
        note_entry = {
            'filename': filename,
            'description': description
        }

        # Add to pending notes with directory information
        if date_key not in self.pending_notes:
            self.pending_notes[date_key] = {
                'notes': [],
                'directory': video_directory
            }

        self.pending_notes[date_key]['notes'].append(note_entry)

        self.logger.debug(f"Added note for {filename} on {date_key} in {video_directory}")
    
    def write_all_notes(self):
        """
        Write all pending notes to files
        """
        if not self.notes_enabled or not self.pending_notes:
            return

        notes_count = len(self.pending_notes)
        for date_key, note_data in self.pending_notes.items():
            self._write_notes_file(date_key, note_data['notes'], note_data['directory'])

        # Clear pending notes after writing
        self.pending_notes.clear()

        self.logger.info(f"Generated notes files for {notes_count} dates")
    
    def _write_notes_file(self, date_key: str, notes: List[Dict[str, Any]], video_directory: str):
        """
        Write notes for a specific date to file in the video directory
        Format: filename - description (one per line)

        Args:
            date_key: Date key (YYYY_MM_DD format)
            notes: List of note entries
            video_directory: Directory where the videos are stored
        """
        try:
            # Create notes filename: YYYYMMDD_Notes.txt
            date_compact = date_key.replace("_", "")  # Convert YYYY_MM_DD to YYYYMMDD
            notes_filename = f"{date_compact}_Notes.txt"
            notes_filepath = Path(video_directory) / notes_filename

            # Write simple text format: filename - description
            with open(notes_filepath, 'w', encoding='utf-8') as f:
                f.write(f"Video Analysis Notes - {date_key}\n")
                f.write("=" * 50 + "\n\n")

                for note in notes:
                    # Format: filename - description
                    f.write(f"{note['filename']} - {note['description']}\n")

            self.logger.info(f"Generated notes file: {notes_filepath}")

        except Exception as e:
            self.logger.error(f"Failed to write notes file for {date_key}: {e}")
    
    # NOTE: These methods are not currently used in the main workflow
    # They would need to be updated to work with directory-based notes

    # def get_existing_notes(self, date_key: str) -> Optional[List[str]]:
    #     """
    #     Get existing notes for a specific date
    #
    #     Args:
    #         date_key: Date key (YYYY_MM_DD format)
    #
    #     Returns:
    #         List of existing note lines or None if not found
    #     """
    #     # TODO: Update to work with directory-based notes if needed
    #     pass

    # def append_to_existing_notes(self, date_key: str, new_notes: List[Dict[str, Any]]):
    #     """
    #     Append new notes to existing notes file
    #
    #     Args:
    #         date_key: Date key (YYYY_MM_DD format)
    #         new_notes: List of new note entries to append
    #     """
    #     # TODO: Update to work with directory-based notes if needed
    #     pass
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get notes generation statistics
        
        Returns:
            Statistics dictionary
        """
        total_pending = sum(len(notes) for notes in self.pending_notes.values())
        
        return {
            'pending_notes': total_pending,
            'pending_dates': len(self.pending_notes),
            'notes_enabled': self.notes_enabled
        }
