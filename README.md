# PhoneSync + VideoProcessor

**Automated file organization and AI video analysis for phone content**

Organizes photos and videos from phone sync folders into date-based directories, with intelligent detection and categorization of martial arts videos.

## Key Features

- **Smart File Organization**: Automatically sorts files into `YYYY_MM_DD` folders
- **AI Video Analysis**: Detects kung fu videos and extracts form names using local AI
- **Incremental Processing**: Only processes new files on subsequent runs (perfect for daily sync)
- **Automated Notes**: Generates searchable notes files with video descriptions
- **Environment Support**: Separate development and production configurations
- **High Performance**: Handles hundreds/thousands of files efficiently

## How It Works

1. **File Discovery**: Scans source folders for photos and videos and checks to see if they need to be processed by date
2. **Date Extraction**: Gets creation date from file name, or file metadata when file name does not contain date
3. **Folder Creation**: Creates `YYYY_MM_DD` folders in target directories if they do not exist
4. **File Organization**: Moves files to appropriate date folders
5. **AI Analysis**: Analyzes videos to detect kung fu/martial arts content
6. **Smart Routing**: Kung fu videos go to special Wudan folder
7. **Notes Generation**: Creates searchable notes files with form names
8. **State Tracking**: Remembers processed files for incremental runs

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

- **Incremental Processing**: Only processes new files on subsequent runs
- **Smart Deduplication**: Avoids processing duplicate files
- **Environment Switching**: Easy development/production configuration switching
- **Wudan Time Rules**: Automatically routes martial arts videos based on time/day
- **Custom Notes Preservation**: Respects existing user notes files
- **Edge Case Handling**: Robust handling of missing folders and partial files

## Support

For issues:
1. Check logs in `VideoProcessor/logs/`
2. Run with `--dry-run` flag to test safely
3. Use test scripts to isolate problems
4. Verify paths in `config.yaml` are accessible

---

**Ready to organize your phone content with AI-powered video analysis!**
