import os
import re
import subprocess
import time
import argparse
from datetime import datetime
from pathlib import Path

def parse_date_from_folder_name(folder_name):
    """
    Parse date from folder name in format YYYY_MM_DD or YYYY_MM_DD_Something
    Returns datetime object if valid date found, None otherwise
    """
    # Match pattern: YYYY_MM_DD at the start of the folder name
    pattern = r'^(\d{4})_(\d{2})_(\d{2})'
    match = re.match(pattern, folder_name)
    
    if match:
        year, month, day = match.groups()
        try:
            # Validate that it's a real date
            date_obj = datetime(int(year), int(month), int(day))
            return date_obj
        except ValueError:
            # Invalid date (e.g., month 13, day 32)
            return None
    return None

def get_date_stamped_folders(base_path):
    """
    Get all folders with valid date stamps and return sorted list of (date, folder_name) tuples
    """
    folders_with_dates = []
    
    try:
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path):
                date_obj = parse_date_from_folder_name(item)
                if date_obj:
                    folders_with_dates.append((date_obj, item))
    except FileNotFoundError:
        print(f"Error: Directory not found: {base_path}")
        return []
    except PermissionError:
        print(f"Error: Permission denied accessing: {base_path}")
        return []
    
    # Sort by date
    folders_with_dates.sort(key=lambda x: x[0])
    return folders_with_dates

def run_command(date_str):
    """
    Run the generate_ai_notes.py command with the given date
    """
    command = ["python", "VideoProcessor/Scripts/generate_ai_notes.py", "--date", date_str]
    
    try:
        print(f"Running command for date: {date_str}")
        
        # Set environment variables to handle Unicode properly
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True,
            env=env,
            encoding='utf-8',
            errors='replace'  # Replace problematic characters instead of failing
        )
        
        print(f"✓ Success for {date_str}")
        if result.stdout:
            # Handle Unicode output safely
            try:
                print(f"Output: {result.stdout.strip()}")
            except UnicodeEncodeError:
                print(f"Output: [Unicode output - displayed safely]")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error for {date_str}: {e}")
        if e.stderr:
            try:
                print(f"Error output: {e.stderr.strip()}")
            except UnicodeEncodeError:
                print(f"Error output: [Unicode error - displayed safely]")
        return False
    except FileNotFoundError:
        print("Error: Could not find the python script or python executable")
        return False

def main():
    parser = argparse.ArgumentParser(description="Process video folders in batches")
    parser.add_argument("--start-date", type=str, help="Start date in YYYY-MM-DD format")
    args = parser.parse_args()
    
    # Base path to scan for folders
    base_path = r"Z:\My Videos\Wudan"
    
    print(f"Scanning folders in: {base_path}")
    
    # Get all date-stamped folders
    folders_with_dates = get_date_stamped_folders(base_path)
    
    if not folders_with_dates:
        print("No date-stamped folders found.")
        return
    
    print(f"Found {len(folders_with_dates)} date-stamped folders")
    
    # Filter by start date if provided
    if args.start_date:
        try:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
            folders_with_dates = [(date_obj, folder) for date_obj, folder in folders_with_dates 
                                 if date_obj >= start_date]
            print(f"Filtered to {len(folders_with_dates)} folders from {args.start_date} onwards")
        except ValueError:
            print("Error: Invalid start date format. Use YYYY-MM-DD")
            return
    
    if not folders_with_dates:
        print("No folders found matching the start date criteria.")
        return
    
    # Process in batches of 50
    batch_size = 50
    total_folders = len(folders_with_dates)
    
    for i in range(0, total_folders, batch_size):
        batch = folders_with_dates[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_folders + batch_size - 1) // batch_size
        
        print(f"\n--- Processing Batch {batch_num}/{total_batches} ---")
        print(f"Processing folders {i+1} to {min(i+batch_size, total_folders)} of {total_folders}")
        
        success_count = 0
        for date_obj, folder_name in batch:
            date_str = date_obj.strftime("%Y-%m-%d")
            print(f"\nProcessing folder: {folder_name} (Date: {date_str})")
            
            if run_command(date_str):
                success_count += 1
        
        print(f"\nBatch {batch_num} completed: {success_count}/{len(batch)} successful")
        
        # Pause for 10 minutes between batches (except for the last batch)
        if i + batch_size < total_folders:
            print("Pausing for 10 minutes before next batch...")
            for remaining in range(600, 0, -10):
                minutes = remaining // 60
                seconds = remaining % 60
                print(f"\rTime remaining: {minutes:02d}:{seconds:02d}", end="", flush=True)
                time.sleep(10)
            print("\nResuming...")
    
    print(f"\n--- All batches completed! ---")
    print(f"Processed {total_folders} folders in total")

if __name__ == "__main__":
    main()