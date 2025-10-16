# PhoneSync + VideoProcessor

**Automated file organization and AI video analysis for phone content**

Organizes photos and videos from phone sync folders into date-based directories, with intelligent detection and categorization of martial arts videos.

## Key Features

- **Smart File Organization**: Automatically sorts files into `YYYY_MM_DD` folders
- **Enhanced AI Video Analysis**: Detects kung fu videos and extracts form names using local AI with robust thumbnail processing
- **Advanced Base64 Validation**: Automatic detection and repair of corrupted thumbnail data for reliable AI analysis
- **Enhanced Error Handling**: Comprehensive error categorization and detailed debugging information
- **Intelligent Video Routing**: Time-based routing with post-processing cleanup for misclassified videos
- **"NOT KUNG FU" Detection**: AI identifies non-martial arts videos for cleanup from Wudan folders
- **Post-Processing Cleanup**: User-controlled cleanup of misclassified videos with preview and validation
- **Incremental Processing**: Only processes new files on subsequent runs (perfect for daily sync)
- **Automated Notes**: Generates searchable notes files with video descriptions for all analyzed videos
- **Environment Support**: Separate development and production configurations
- **Test Environment Tools**: Comprehensive testing utilities for validation and development
- **High Performance**: Handles hundreds/thousands of files efficiently with production-grade reliability

## How It Works

### Main Processing Workflow
1. **File Discovery**: Scans source folders for photos and videos and checks to see if they need to be processed by date
2. **Date Extraction**: Gets creation date from file name, or file metadata when file name does not contain date
3. **Folder Creation**: Creates `YYYY_MM_DD` folders in target directories if they do not exist
4. **File Organization**: Moves files to appropriate date folders
5. **AI Analysis**: Analyzes videos to detect kung fu/martial arts content using local LM Studio
6. **Smart Routing**: Time-based routing to Wudan folder based on class schedules
7. **Comprehensive Notes**: Creates notes files for ALL analyzed videos (kung fu AND non-kung fu)
8. **"NOT KUNG FU" Marking**: Videos routed to Wudan but containing non-martial arts content are marked
9. **State Tracking**: Remembers processed files for incremental runs

### Post-Processing Cleanup Workflow
1. **Detection**: Scan Wudan folders for videos marked as "NOT KUNG FU"
2. **Preview**: Show user exactly which videos would be moved and where
3. **Validation**: User reviews AI decisions before cleanup execution
4. **Cleanup**: Move misclassified videos from Wudan to regular video folders
5. **Notes Update**: Clean up notes files to remove moved video entries

## Enhanced Technical Features

### Advanced Base64 Validation & Repair
The VideoAnalyzer now includes sophisticated thumbnail validation that automatically detects and repairs common corruption issues:

- **PNG Signature Validation**: Verifies proper PNG file headers in thumbnail data
- **Data URL Prefix Handling**: Automatically removes `data:image/png;base64,` prefixes
- **Corruption Detection**: Identifies and fixes leading character corruption in base64 data
- **Automatic Repair**: Attempts to repair corrupted thumbnails before AI analysis
- **Graceful Fallback**: Handles edge cases without crashing the analysis pipeline

### Enhanced Error Handling
Comprehensive error reporting provides detailed debugging information:

- **Error Categorization**: Structured error types (`base64_validation_failed`, `ai_analysis_failed`, etc.)
- **Processing Step Tracking**: Identifies exactly where errors occur in the pipeline
- **Detailed Context**: Includes timestamps, file paths, and specific error conditions
- **Skip Reason Logging**: Clear explanations for why files are skipped or fail processing
- **Production Monitoring**: Structured error data suitable for monitoring and alerting

### Reliability Improvements
- **Robust Thumbnail Processing**: Handles corrupted or malformed image data gracefully
- **Production-Grade Error Handling**: Comprehensive error categorization and logging
- **Comprehensive Testing**: Full integration test suite validates all enhanced features
- **Zero Regression**: All existing functionality preserved while adding new capabilities

## Quick Start

### Prerequisites
- **Python 3.11+** with virtual environment support
- **FFmpeg** installed and accessible in PATH
- **LM Studio** running locally with vision model loaded (for AI analysis)

### Setup
1. **Install Dependencies**:
   ```bash
   # Virtual environment is already set up
   # Dependencies are already installed
   ```

2. **Configure Paths**: Edit `config.yaml` to set your source and target directories
   ```yaml
   # Set environment: "DEVELOPMENT" or "PRODUCTION"
   environment: "DEVELOPMENT"
   
   # Development paths (for testing)
   DEV_VARS:
     source_folders:
       - "Z:/PhotoSync_Test/Source"
     target_paths:
       pictures: "Z:/PhotoSync_Test/My Pictures"
       videos: "Z:/PhotoSync_Test/My Videos"
       wudan: "Z:/PhotoSync_Test/My Videos/Wudan"
   ```

3. **Start LM Studio**: Launch LM Studio with a vision model for AI analysis

## Testing

### **Quick System Validation**
```bash
# Test AI analysis functionality
./venv/Scripts/python.exe VideoProcessor/TestScripts/test_ai_analysis_only.py

# Test file organization with production data
./venv/Scripts/python.exe VideoProcessor/TestScripts/test_4_files_processing.py

# Test complete workflow (dry-run)
./venv/Scripts/python.exe VideoProcessor/phone_sync.py --config config.yaml --dry-run --verbose
```

**📋 For comprehensive testing procedures, see [Documentation/TESTING_SYSTEM.md](Documentation/TESTING_SYSTEM.md)**

## Usage

### Basic Operation
```bash
# Run file organization and AI analysis
./venv/Scripts/python.exe VideoProcessor/phone_sync.py --config config.yaml --verbose

# Test run (no files moved)
./venv/Scripts/python.exe VideoProcessor/phone_sync.py --config config.yaml --dry-run --verbose
```

### Environment Management
```bash
# Switch to production environment
./venv/Scripts/python.exe VideoProcessor/switch_environment.py prod

# Switch to development environment
./venv/Scripts/python.exe VideoProcessor/switch_environment.py dev

# Show current environment
./venv/Scripts/python.exe VideoProcessor/switch_environment.py show
```

### Processing State Management
```bash
# View processing state (shows incremental vs. full processing mode)
./venv/Scripts/python.exe VideoProcessor/manage_processing_state.py show

# View recently processed files
./venv/Scripts/python.exe VideoProcessor/manage_processing_state.py files

# Reset state (force full reprocessing)
./venv/Scripts/python.exe VideoProcessor/manage_processing_state.py reset
```

### Post-Processing Cleanup (NEW!)
```bash
# Preview what videos would be moved from Wudan folders
./venv/Scripts/python.exe VideoProcessor/Scripts/cleanup_non_kungfu_videos.py --preview

# Execute cleanup after user validation
./venv/Scripts/python.exe VideoProcessor/Scripts/cleanup_non_kungfu_videos.py --execute

# Dry run mode (simulate without making changes)
./venv/Scripts/python.exe VideoProcessor/Scripts/cleanup_non_kungfu_videos.py --execute --dry-run
```

### Test Environment Management (NEW!)
```bash
# Create test conditions with mock "NOT KUNG FU" videos
./venv/Scripts/python.exe VideoProcessor/Scripts/setup_test_environment.py --scenario mock_not_kungfu

# Clean test environment (remove all notes files)
./venv/Scripts/python.exe VideoProcessor/Scripts/setup_test_environment.py --scenario clean

# Mixed test conditions
./venv/Scripts/python.exe VideoProcessor/Scripts/setup_test_environment.py --scenario mixed
```

## Configuration

The system uses environment-based configuration in `config.yaml`:

- **Development**: Uses test folders for safe development
- **Production**: Uses actual phone sync folders and target directories

Switch environments easily:
```bash
# Switch to production
./venv/Scripts/python.exe VideoProcessor/switch_environment.py prod

# Switch to development
./venv/Scripts/python.exe VideoProcessor/switch_environment.py dev
```

## Output

The system creates:
- **Organized folders**: `YYYY_MM_DD` date-based directories
- **Notes files**: `YYYYMMDD_Notes.txt` with video descriptions
- **Processing logs**: Detailed logs in `VideoProcessor/logs/`

### Example Output Structure
```
My Videos/
├── 2024_12_08/
│   ├── 20241208_094652_1.mp4
│   ├── 20241208_094944_1.mp4
│   └── 20241208_Notes.txt
└── Wudan/
    └── 2025_04_06/
        ├── 20250406_092556_1.mp4
        ├── 20250406_092818_1.mp4
        └── 20250406_Notes.txt
```

## Advanced Features

### Core Processing
- **Incremental Processing**: Only processes new files on subsequent runs
- **Smart Deduplication**: Avoids processing duplicate files
- **Environment Switching**: Easy development/production configuration switching
- **Wudan Time Rules**: Automatically routes martial arts videos based on time/day
- **Custom Notes Preservation**: Respects existing user notes files
- **Edge Case Handling**: Robust handling of missing folders and partial files

### AI Analysis & Cleanup (NEW!)
- **Comprehensive AI Analysis**: Generates notes for ALL videos, not just kung fu videos
- **"NOT KUNG FU" Detection**: Identifies non-martial arts content routed to Wudan folders
- **Post-Processing Cleanup**: User-controlled cleanup of misclassified videos
- **Preview Mode**: See exactly what would be moved before making changes
- **Dry Run Support**: Test cleanup operations without making actual changes
- **Notes File Management**: Automatically updates notes files when videos are moved

### Testing & Development Tools (NEW!)
- **Comprehensive Test Suite**: Complete testing system for all components and workflows
- **AI Analysis Testing**: Dedicated tests for LM Studio integration and video analysis
- **Production Data Testing**: Validate system with real phone sync data
- **Test Environment Setup**: Create controlled test conditions for validation
- **Mock Data Generation**: Generate realistic test scenarios with "NOT KUNG FU" videos
- **Multiple Test Scenarios**: Clean, partial, mixed, and mock test conditions
- **Reusable Test Setup**: Easily recreate test conditions for consistent validation

**📋 For complete testing procedures, see [Documentation/TESTING_SYSTEM.md](Documentation/TESTING_SYSTEM.md)**

## Optimized Workflow for Daily Use

### Phase 1: Daily Processing
```bash
# Run normal processing (handles new files automatically)
./venv/Scripts/python.exe VideoProcessor/phone_sync.py --config config.yaml --verbose
```
This processes new files, creates notes for all videos, and routes based on time rules.

### Phase 2: Periodic Cleanup (Weekly/Monthly)
```bash
# Preview what needs cleanup
./venv/Scripts/python.exe VideoProcessor/Scripts/cleanup_non_kungfu_videos.py --preview

# Review the preview, then execute cleanup
./venv/Scripts/python.exe VideoProcessor/Scripts/cleanup_non_kungfu_videos.py --execute
```
This moves any non-martial arts videos that were incorrectly routed to Wudan folders.

### Benefits of This Approach
- **Efficiency**: No disruption to daily processing workflow
- **User Control**: Manual validation before moving files
- **Safety**: Preview and dry-run modes prevent mistakes
- **Flexibility**: Run cleanup on your schedule, not during every sync

## Support

For issues:
1. Check logs in `VideoProcessor/logs/`
2. Run with `--dry-run` flag to test safely
3. Use test scripts to isolate problems
4. Verify paths in `config.yaml` are accessible
5. Test with `setup_test_environment.py` for controlled validation

---

**Ready to organize your phone content with AI-powered video analysis and intelligent cleanup!**
