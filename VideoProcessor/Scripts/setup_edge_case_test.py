#!/usr/bin/env python3
"""
Script to set up edge case testing scenarios for the PhoneSync + VideoProcessor system.
This will create various test conditions to validate proper handling of:
- Existing non-standard notes files
- Missing folders that need creation
- Partial file sets in existing folders
- Mixed scenarios
"""

import os
import shutil
from pathlib import Path
import random

def setup_edge_case_test():
    """Set up comprehensive edge case test scenarios"""
    
    videos_path = Path("Z:/PhotoSync_Test/My Videos")
    wudan_path = videos_path / "Wudan"
    
    print("🧪 Setting up edge case test scenarios...")
    
    # Get list of all current folders
    all_folders = []
    for folder in videos_path.rglob("*"):
        if folder.is_dir() and folder != videos_path and "2024" in folder.name or "2025" in folder.name:
            all_folders.append(folder)
    
    print(f"Found {len(all_folders)} date folders")
    
    # Scenario 1: Delete some folders completely (to test folder creation)
    folders_to_delete = random.sample(all_folders, min(3, len(all_folders) // 4))
    print(f"\n📁 Deleting {len(folders_to_delete)} folders to test folder creation:")
    for folder in folders_to_delete:
        print(f"   - Deleting: {folder.relative_to(videos_path)}")
        shutil.rmtree(folder, ignore_errors=True)
    
    # Scenario 2: In remaining folders, delete some video files (to test partial processing)
    remaining_folders = [f for f in all_folders if f.exists()]
    folders_for_partial_deletion = random.sample(remaining_folders, min(3, len(remaining_folders) // 3))
    
    print(f"\n🎬 Removing some videos from {len(folders_for_partial_deletion)} folders:")
    for folder in folders_for_partial_deletion:
        video_files = list(folder.glob("*.mp4"))
        if video_files:
            files_to_delete = random.sample(video_files, min(2, len(video_files) // 2))
            for video_file in files_to_delete:
                print(f"   - Removing: {video_file.name} from {folder.name}")
                video_file.unlink(missing_ok=True)
    
    # Scenario 3: Create custom notes files in some folders (to test preservation)
    folders_for_custom_notes = random.sample(remaining_folders, min(4, len(remaining_folders) // 2))
    
    print(f"\n📝 Creating custom notes files in {len(folders_for_custom_notes)} folders:")
    custom_notes_types = ["Notes.txt", "video_notes.txt", "class_notes.txt", "practice_log.txt"]
    
    for i, folder in enumerate(folders_for_custom_notes):
        if folder.exists():
            notes_filename = custom_notes_types[i % len(custom_notes_types)]
            notes_path = folder / notes_filename
            
            custom_content = f"""Custom Notes for {folder.name}
=====================================

These are user-created notes that should NOT be overwritten.
Contains important information about:
- Training session details
- Personal observations
- Instructor feedback
- Progress notes

Created: {folder.name}
Type: {notes_filename}
"""
            
            with open(notes_path, 'w', encoding='utf-8') as f:
                f.write(custom_content)
            
            print(f"   - Created: {notes_filename} in {folder.name}")
    
    # Scenario 4: Delete all our standard notes files (to test regeneration)
    print(f"\n🗑️ Removing all standard YYYYMMDD_Notes.txt files:")
    notes_deleted = 0
    for notes_file in videos_path.rglob("*Notes.txt"):
        if notes_file.name.match(r'\d{8}_Notes\.txt'):
            print(f"   - Removing: {notes_file.relative_to(videos_path)}")
            notes_file.unlink(missing_ok=True)
            notes_deleted += 1
    
    print(f"   Total standard notes files removed: {notes_deleted}")
    
    # Summary
    print(f"\n✅ Edge case test setup complete!")
    print(f"📊 Test Scenarios Created:")
    print(f"   - {len(folders_to_delete)} folders deleted (test folder creation)")
    print(f"   - {len(folders_for_partial_deletion)} folders with partial video removal")
    print(f"   - {len(folders_for_custom_notes)} folders with custom notes files")
    print(f"   - {notes_deleted} standard notes files removed")
    
    print(f"\n🧪 Ready to test:")
    print(f"   1. Folder creation for missing dates")
    print(f"   2. Preservation of custom notes files")
    print(f"   3. Processing only missing/new files")
    print(f"   4. Notes generation for newly processed videos")
    
    return {
        'folders_deleted': len(folders_to_delete),
        'folders_partial': len(folders_for_partial_deletion),
        'custom_notes_created': len(folders_for_custom_notes),
        'standard_notes_removed': notes_deleted
    }

if __name__ == "__main__":
    results = setup_edge_case_test()
    print(f"\n🎯 Test setup results: {results}")
