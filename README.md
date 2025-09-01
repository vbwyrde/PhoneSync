# PhoneSync - File Organization System

PhoneSync is a Windows-based file organization system that automatically sorts JPG and MP4 files into date-based folders with special rules for Wudan video classification.

## Features

- **Date-based Organization**: Files are organized into folders named `YYYY_MM_DD` based on their last modified date
- **Flexible Folder Matching**: Recognizes existing folders with custom suffixes (e.g., `2016_06_20_PaulArt`, `2016_12_29_VincentBirthday`)
- **Wudan Time Rules**: Videos are automatically sorted into special Wudan folders based on specific day/time criteria
- **Smart Deduplication**: Pre-scans target directories to skip files that already exist, dramatically speeding up processing
- **Configurable**: Easy-to-modify JSON configuration file
- **Logging**: Comprehensive logging with rotation and size management
- **Dry Run Mode**: Test the script without actually moving files
- **Duplicate Handling**: Smart handling of duplicate files with size and optional hash comparison
- **Performance Optimized**: Only processes files that don't already exist in target locations
- **Schedulable**: Can be run via Windows Task Scheduler

## File Structure

```
PhoneSync/
├── PhoneSync.ps1      # Main PowerShell script
├── RunPhoneSync.bat   # Batch wrapper for scheduling
├── config.json        # Configuration file
├── README.md          # This file
└── PhoneSync.log      # Log file (created when script runs)
```

## Configuration

Edit `config.json` to customize the behavior:

### Source Folders
```json
"sourceFolders": [
    "C:\\Users\\YourUsername\\Pictures",
    "C:\\Users\\YourUsername\\Videos"
]
```

### Target Paths
```json
"targetPaths": {
    "pictures": "G:\\UserData\\My Pictures",
    "videos": "G:\\UserData\\My Videos",
    "wudanVideos": "G:\\UserData\\My Videos\\Wudan"
}
```

### Wudan Rules
The system applies special rules for video files based on their date and time:

**Before 2021:**
- Days: Monday, Tuesday, Wednesday, Thursday, Saturday
- Times: 5:00-8:00 AM or 6:00-10:00 PM

**After 2021:**
- **Sunday**: 8:00 AM - 1:00 PM
- **Monday**: 5:00-8:00 AM or 6:00-9:00 PM
- **Tuesday**: 5:00-8:00 AM or 6:00-9:00 PM
- **Wednesday**: 6:00-10:00 PM
- **Thursday**: 5:00-8:00 AM or 6:00-9:00 PM
- **Saturday**: 8:00 AM - 4:00 PM

Videos matching these criteria go to the Wudan folder, others go to the regular videos folder.

## Setup Instructions

1. **Download Files**: Place all files in a folder on your target machine
2. **Edit Configuration**: Modify `config.json` with your actual source and target paths
3. **Test Run**: Execute a dry run first to verify behavior
4. **Schedule**: Set up Windows Task Scheduler to run automatically

### Initial Setup Steps

1. **Update Source Folders**:
   ```json
   "sourceFolders": [
       "C:\\Path\\To\\Your\\Pictures",
       "C:\\Path\\To\\Your\\Videos"
   ]
   ```

2. **Verify Target Paths**: Ensure G: drive paths are correct for your system

3. **Test with Dry Run**:
   ```cmd
   RunPhoneSync.bat
   ```
   Or directly:
   ```powershell
   .\PhoneSync.ps1 -DryRun -Verbose
   ```

## Usage

### Manual Execution

**Basic run:**
```cmd
RunPhoneSync.bat
```

**PowerShell with options:**
```powershell
# Dry run (no files copied)
.\PhoneSync.ps1 -DryRun

# Verbose output
.\PhoneSync.ps1 -Verbose

# Custom config file
.\PhoneSync.ps1 -ConfigPath "custom-config.json"

# Combination
.\PhoneSync.ps1 -DryRun -Verbose
```

### Windows Task Scheduler Setup

1. Open Task Scheduler (`taskschd.msc`)
2. Create Basic Task
3. Set trigger (daily, weekly, etc.)
4. Action: Start a program
5. Program: Full path to `RunPhoneSync.bat`
6. Start in: Directory containing the script files

**Example Task Scheduler Settings:**
- **Program**: `C:\PhoneSync\RunPhoneSync.bat`
- **Start in**: `C:\PhoneSync`
- **Run whether user is logged on or not**: Checked
- **Run with highest privileges**: Checked

## Configuration Options

### File Extensions
Customize which file types to process:
```json
"fileExtensions": {
    "pictures": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
    "videos": [".mp4", ".avi", ".mov", ".wmv", ".mkv", ".flv", ".webm"]
}
```

### Logging Options
```json
"logging": {
    "enabled": true,
    "logPath": "PhoneSync.log",
    "maxLogSizeMB": 10,
    "keepLogDays": 30
}
```

### Script Options
```json
"options": {
    "createMissingFolders": true,
    "copyFiles": true,
    "dryRun": false,
    "verboseLogging": false,
    "enableDeduplication": true,
    "useHashComparison": false,
    "forceRecopyIfNewer": true
}
```

### Deduplication Feature
The script includes intelligent deduplication to dramatically speed up processing:

**How it works:**
1. **Pre-scan Phase**: Scans all target directories and builds a cache of existing files
2. **Smart Filtering**: Only processes files that don't already exist in the target location
3. **Size + Name Comparison**: Compares files by name and size for fast duplicate detection
4. **Optional Hash Comparison**: Enable `useHashComparison` for more thorough duplicate detection
5. **Newer File Handling**: Enable `forceRecopyIfNewer` to update files when source is newer

**Performance Benefits:**
- Skips copying files that already exist
- Particularly beneficial for large MP4 files
- Shows statistics on how many files were skipped
- Can reduce processing time by 80%+ on subsequent runs

**Configuration Options:**
- `enableDeduplication`: Enable/disable the deduplication feature
- `useHashComparison`: Use file hashes for more accurate duplicate detection (slower but more thorough)
- `forceRecopyIfNewer`: Re-copy files when source file is newer than target

### Flexible Folder Matching
The script intelligently handles existing folders with custom names:

**How it works:**
- **Standard folders**: Creates `YYYY_MM_DD` folders (e.g., `2016_06_20`)
- **Custom folders**: Recognizes existing folders with suffixes (e.g., `2016_06_20_PaulArt`, `2016_12_29_VincentBirthday`)
- **Smart matching**: Files for `2016-06-20` will go into `2016_06_20_PaulArt` if it exists
- **Deduplication aware**: Correctly identifies files in custom-named folders during deduplication

**Examples:**
```
Target folder structure:
├── 2016_06_20_PaulArt/          # Custom folder with suffix
├── 2016_12_29_VincentBirthday/  # Custom folder with suffix
├── 2017_01_01/                 # Standard date folder
└── 2017_02_14_ValentinesDay/    # Custom folder with suffix

Files dated 2016-06-20 → go to 2016_06_20_PaulArt/
Files dated 2016-12-29 → go to 2016_12_29_VincentBirthday/
Files dated 2017-01-01 → go to 2017_01_01/
Files dated 2017-02-14 → go to 2017_02_14_ValentinesDay/
```

This allows you to manually customize folder names for special events while maintaining automated organization.

## Troubleshooting

### Common Issues

1. **PowerShell Execution Policy**:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Permission Issues**: Run as Administrator or ensure user has write access to target folders

3. **G: Drive Not Available**: Verify network drive is mapped and accessible

4. **Large Log Files**: Logs auto-rotate when they exceed the configured size

### Log Analysis

Check `PhoneSync.log` for detailed operation information:
- File processing status
- Error messages
- Performance statistics
- Wudan rule applications

## Maintenance

### Regular Tasks
- Review log files for errors
- Update source folders in config as needed
- Verify target drive space availability
- Test dry runs after configuration changes

### Updating Wudan Rules
Modify the `wudanRules` section in `config.json`:
```json
"wudanRules": {
    "before2021": {
        "daysOfWeek": [1, 2, 3, 4, 6],  // 0=Sunday, 1=Monday, etc.
        "timeRanges": [
            {"start": "05:00", "end": "08:00"},
            {"start": "18:00", "end": "22:00"}
        ]
    }
}
```

## Support

For issues or questions:
1. Check the log file for error details
2. Run with `-Verbose` flag for detailed output
3. Test with `-DryRun` to verify behavior without file operations
4. Verify all paths in configuration are accessible
