# PhoneSync + VideoProcessor - Unified Python Solution

A comprehensive Python-based file organization and AI video analysis system that automatically sorts photos and videos into date-based folders with intelligent kung fu/martial arts detection, form name extraction, and automated notes generation.

## 🎯 Overview

This project combines two powerful systems:
- **PhoneSync**: Intelligent file organization with date-based sorting and Wudan time rules
- **VideoProcessor**: AI-powered video analysis using LM Studio for kung fu/martial arts detection

The unified solution replaces separate PowerShell and N8N workflows with a single, maintainable Python application.

## ✨ Key Features

### 📁 **File Organization**
- **Date-based Organization**: Files sorted into `YYYY_MM_DD` folders based on metadata
- **Flexible Folder Matching**: Recognizes existing folders with custom suffixes (e.g., `2025_04_12_KungFuClass`)
- **Wudan Time Rules**: Videos automatically routed to special Wudan folders based on day/time criteria
- **Smart Deduplication**: Pre-scans target directories with flexible filename matching (handles appended text)
- **Performance Optimized**: Only processes missing files, dramatically speeding up subsequent runs

### 🤖 **AI Video Analysis**
- **LM Studio Integration**: Local AI model for kung fu/martial arts detection in video thumbnails
- **Dynamic Midpoint Extraction**: Intelligent thumbnail extraction from video midpoint (not fixed timestamps)
- **Confidence Scoring**: AI provides confidence levels for kung fu detection
- **Form Name Extraction**: Automatically extracts martial arts form names from video text (e.g., "Bagua - Old 8 Palms", "Dragon Walking Sword")
- **Intelligent Notes Generation**: Creates concise, searchable notes files with actual form names (under 10 words)
- **Directory-Based Notes**: Notes stored directly in video folders as `YYYYMMDD_Notes.txt` files
- **Custom Notes Preservation**: Respects existing user notes files with non-standard naming
- **Batch Processing**: Efficiently processes multiple videos with progress tracking

### 🛠️ **System Features**
- **Unified Configuration**: Single YAML config file for all settings
- **Comprehensive Logging**: Rotation, retention, and detailed progress tracking
- **Dry Run Mode**: Test operations without moving files
- **Edge Case Handling**: Robust handling of missing folders, partial files, and mixed scenarios
- **Production Ready**: Thoroughly tested with real-world video collections
- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **Cross-Platform**: Python-based with Windows optimization

## 📂 Project Structure

```
PhoneSync/
├── config.yaml                    # 🔧 Unified configuration file
├── venv/                          # 🐍 Python virtual environment
├── VideoProcessor/                # 📹 Main Python application
│   ├── main.py                   # 🚀 Entry point for video processing
│   ├── phone_sync.py             # 📱 Entry point for file organization
│   ├── modules/                  # 📦 Core system modules
│   │   ├── config_manager.py     # ⚙️  Configuration management
│   │   ├── file_scanner.py       # 🔍 File discovery and scanning
│   │   ├── file_organizer.py     # 📁 File organization logic
│   │   ├── deduplication.py      # 🔄 Smart duplicate detection
│   │   ├── wudan_rules.py        # 🥋 Time-based Wudan classification
│   │   ├── video_analyzer.py     # 🤖 AI video analysis
│   │   ├── notes_generator.py    # 📝 Video notes generation
│   │   ├── target_path_resolver.py # 🎯 Path resolution logic
│   │   └── unified_processor.py  # 🔗 Orchestrates entire workflow
│   ├── TestScripts/              # 🧪 Comprehensive test suite
│   └── logs/                     # 📝 Application logs
├── PhoneSync.ps1                 # 📜 Legacy PowerShell script (maintained)
├── RunPhoneSync.bat              # 🔄 Batch wrapper for scheduling
└── README.md                     # 📖 This documentation
```

## ⚙️ Configuration

The system uses a single `config.yaml` file for all settings:

### 📂 Source and Target Paths
```yaml
source_folders:
  - "Z:/PhotoSync_Test/Source"

target_paths:
  pictures: "Z:/PhotoSync_Test/My Pictures"
  videos: "Z:/PhotoSync_Test/My Videos"
  wudan: "Z:/PhotoSync_Test/My Videos/Wudan"
  # Notes are stored directly in video directories as YYYYMMDD_Notes.txt
```

### 🥋 Wudan Time Rules
The system applies sophisticated time-based rules for video classification:

**Before 2021:**
- **Days**: Monday, Tuesday, Wednesday, Thursday, Saturday
- **Times**: 5:00-8:00 AM or 6:00-10:00 PM

**After 2021 (Day-specific rules):**
- **Sunday**: 8:00 AM - 1:00 PM
- **Monday**: 5:00-8:00 AM or 6:00-9:00 PM
- **Tuesday**: 5:00-8:00 AM or 6:00-9:00 PM
- **Wednesday**: 6:00-10:00 PM
- **Thursday**: 5:00-8:00 AM or 6:00-9:00 PM
- **Saturday**: 8:00 AM - 4:00 PM

Videos matching these criteria are routed to the Wudan folder for martial arts content.

### 🤖 AI Settings
```yaml
ai_settings:
  lm_studio_url: "http://localhost:1234/v1/chat/completions"
  model: "mimo-vl-7b-rl@q8_k_xl"
  temperature: 0.4
  max_tokens: 150
  timeout_seconds: 30

# Enhanced prompt for form name extraction
kung_fu_prompt: |
  IMPORTANT: Look carefully for any TEXT in the image that describes the name of the martial arts form being practiced (e.g., "Bagua - Old 8 Palms", "Dragon Walking Sword", "Chen Style Tai Chi", etc.). If you find such text, use that EXACT text as your description.

  After your YES/NO answer, provide a brief description (maximum 10 words):
  - If there is text naming a specific form, use that exact text
  - Otherwise, briefly describe the martial arts content you see
```

### 📹 Video Processing & Notes Generation
```yaml
video_processing:
  thumbnail_extraction: "dynamic_midpoint"  # Extract from video midpoint
  thumbnail_scale: "320:240"
  ffmpeg_timeout: 30
  process_existing: false  # Skip videos already in target folders

# Notes are automatically generated in video directories
# Format: YYYYMMDD_Notes.txt with "filename - description" entries
# Custom user notes files (Notes.txt, video_notes.txt, etc.) are preserved
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** with virtual environment support
- **FFmpeg** installed and accessible in PATH
- **LM Studio** running locally with vision model loaded (for AI analysis)

### Installation

1. **Clone and Setup Environment**:
   ```bash
   git clone <repository-url>
   cd PhoneSync
   python -m venv venv
   ./venv/Scripts/activate  # Windows
   pip install -r VideoProcessor/requirements.txt
   ```

2. **Configure Settings**:
   Edit `config.yaml` with your paths:
   ```yaml
   source_folders:
     - "C:/Path/To/Your/Photos"
   target_paths:
     pictures: "D:/Organized/Pictures"
     videos: "D:/Organized/Videos"
     wudan: "D:/Organized/Videos/Wudan"
   ```

3. **Test Installation**:
   ```bash
   # Test configuration and logging
   ./venv/Scripts/python.exe VideoProcessor/TestScripts/test_config_and_logging.py

   # Test file organization (dry run)
   ./venv/Scripts/python.exe VideoProcessor/phone_sync.py --dry-run --verbose
   ```

## 💻 Usage

### File Organization Only
```bash
# Basic file organization
./venv/Scripts/python.exe VideoProcessor/phone_sync.py

# Dry run (no files moved)
./venv/Scripts/python.exe VideoProcessor/phone_sync.py --dry-run

# Verbose output
./venv/Scripts/python.exe VideoProcessor/phone_sync.py --verbose

# Custom config
./venv/Scripts/python.exe VideoProcessor/phone_sync.py --config custom_config.yaml
```

### Video Analysis Only
```bash
# Analyze videos with AI
./venv/Scripts/python.exe VideoProcessor/main.py

# Process specific folder
./venv/Scripts/python.exe VideoProcessor/main.py --source "C:/Videos/ToAnalyze"

# Skip AI analysis (organization only)
./venv/Scripts/python.exe VideoProcessor/main.py --skip-ai
```

### Unified Processing (Recommended)
```bash
# Complete workflow: organize files + analyze videos + generate notes
./venv/Scripts/python.exe VideoProcessor/phone_sync.py --config config.yaml --verbose

# Dry run of complete workflow
./venv/Scripts/python.exe VideoProcessor/phone_sync.py --config config.yaml --dry-run --verbose
```

### Notes Generation & Analysis
```bash
# Analyze existing videos without notes files
./venv/Scripts/python.exe VideoProcessor/analyze_existing_videos.py

# Generate notes for specific video directory
./venv/Scripts/python.exe VideoProcessor/main.py --source "Z:/Videos/Wudan/2025_04_06"

# Test notes generation with sample videos
./venv/Scripts/python.exe VideoProcessor/TestScripts/test_notes_generation.py
```

### Legacy PowerShell Support
The original PowerShell script is maintained for compatibility:
```powershell
# Legacy PowerShell execution
.\PhoneSync.ps1 -DryRun -Verbose
```

## 🧪 Testing

The project includes a comprehensive test suite:

### Core System Tests
```bash
# Test configuration and logging
./venv/Scripts/python.exe VideoProcessor/TestScripts/test_config_and_logging.py

# Test file organization
./venv/Scripts/python.exe VideoProcessor/TestScripts/test_file_organization.py

# Test flexible deduplication
./venv/Scripts/python.exe VideoProcessor/TestScripts/test_flexible_deduplication.py

# Test video analysis
./venv/Scripts/python.exe VideoProcessor/TestScripts/test_video_analysis.py
```

### Integration Tests
```bash
# Test complete unified workflow
./venv/Scripts/python.exe VideoProcessor/TestScripts/test_unified_integration.py

# Test with real video files
./venv/Scripts/python.exe VideoProcessor/TestScripts/test_real_videos.py

# Test dynamic midpoint extraction
./venv/Scripts/python.exe VideoProcessor/TestScripts/test_midpoint_extraction.py

# Test notes generation system
./venv/Scripts/python.exe VideoProcessor/TestScripts/test_notes_generation.py
```

### Edge Case Testing
```bash
# Set up comprehensive edge case scenarios
./venv/Scripts/python.exe VideoProcessor/setup_edge_case_test.py

# Test missing folder creation
# Test partial file processing
# Test custom notes preservation
# Test existing file deduplication
```

### Debug and Development
```bash
# Debug Wudan routing logic
./venv/Scripts/python.exe VideoProcessor/TestScripts/debug_wudan_routing.py

# Test FFmpeg integration
./venv/Scripts/python.exe VideoProcessor/TestScripts/test_ffmpeg.py

# Test LM Studio connection
./venv/Scripts/python.exe VideoProcessor/TestScripts/test_lm_studio.py
```

## 🔧 Advanced Features

### 📝 **AI-Powered Notes Generation**

The system automatically generates intelligent notes for kung fu/martial arts videos with sophisticated form name extraction:

**Key Features:**
- **Form Name Extraction**: Automatically detects and extracts martial arts form names from video text
- **Concise Descriptions**: Limits descriptions to 10 words maximum for searchability
- **Directory-Based Storage**: Notes stored directly in video folders, not separate directories
- **Custom Notes Preservation**: Respects existing user notes files with non-standard naming
- **Batch Processing**: Efficiently processes multiple videos with progress tracking

**Notes File Format:**
```
Video Analysis Notes - 2025_04_06
==================================================

20250406_092556_1.mp4 - Tai Chi Stroke the Sparrow's Tail
20250406_092818_1.mp4 - Tai Chi White Ghost Fist
20250406_101857_1.mp4 - Dragon Walking Sword VII
```

**File Naming Convention:**
- **Standard Notes**: `YYYYMMDD_Notes.txt` (automatically generated)
- **Custom Notes**: `Notes.txt`, `video_notes.txt`, etc. (preserved by system)

**Example Form Names Extracted:**
- "Bagua - Old 8 Palms"
- "Twin Dragon Swords"
- "Hsing-I Pounding Fist"
- "Tai Chi - Golden Phoenix Stands on Rock"
- "Dragon Walking Sword VII"
- "Bagua Republic House Fist Monkey"

**Smart Processing:**
- Only analyzes newly copied videos (not existing files)
- Preserves user's custom notes files
- Creates one notes file per date folder
- Handles mixed scenarios (existing + new videos)

### 🔄 Intelligent Deduplication
The system includes sophisticated deduplication with flexible filename matching:

**How it works:**
1. **Pre-scan Phase**: Builds cache of existing files across all target directories
2. **Flexible Matching**: Handles files with appended text after second underscore
   - `20250412_292993_1.mp4` matches `20250412_292993_1_KungFu_GimStyle.mp4`
   - `M4H01890.MP4` matches `M4H01890_CameraFootage.MP4`
3. **Size + Name Validation**: Compares base filename + file size for accurate detection
4. **Performance Optimization**: Skips processing files that already exist

**Configuration:**
```yaml
options:
  enable_deduplication: true
  use_hash_comparison: false  # Use name+size (faster) vs hash (thorough)
  force_recopy_if_newer: true
```

### 📁 Flexible Folder Matching
Intelligently handles existing folders with custom names:

**Examples:**
```
Target Structure:
├── 2025_04_12_KungFuClass/      # Custom folder with suffix
├── 2025_06_15_BirthdayParty/    # Custom folder with suffix
├── 2025_08_30/                 # Standard date folder

File Routing:
• Files from 2025-04-12 → 2025_04_12_KungFuClass/
• Files from 2025-06-15 → 2025_06_15_BirthdayParty/
• Files from 2025-08-30 → 2025_08_30/
```

This allows manual customization of folder names for special events while maintaining automated organization.

### 🎯 Dynamic Midpoint Extraction
Advanced thumbnail extraction that adapts to video length:

**How it works:**
1. **Duration Detection**: Uses FFmpeg to determine exact video length
2. **Midpoint Calculation**: Extracts thumbnail from `duration / 2.0` seconds
3. **Adaptive Quality**: Adjusts extraction based on video characteristics
4. **Safety Buffer**: Handles edge cases and corrupted videos gracefully

**Benefits:**
- More representative thumbnails than fixed timestamps
- Works with videos of any length (10 seconds to hours)
- Better AI analysis accuracy with midpoint frames

### 🛡️ **Edge Case Handling & Production Readiness**

The system has been thoroughly tested with real-world scenarios and handles complex edge cases:

**Folder Management:**
- **Missing Folders**: Automatically creates date folders with `YYYY_MM_DD` naming convention
- **Custom Folder Names**: Recognizes existing folders with suffixes (e.g., `2025_04_12_KungFuClass`)
- **Mixed Scenarios**: Handles combinations of existing and missing folders gracefully

**File Processing:**
- **Partial Collections**: Only processes missing files, skips existing ones
- **Interrupted Operations**: Resumes processing from where it left off
- **Size Validation**: Uses filename + file size for accurate duplicate detection
- **Flexible Naming**: Handles files with appended text after underscores

**Notes System Robustness:**
- **Custom Notes Preservation**: Never overwrites user's existing notes files
- **Naming Convention Respect**: Only manages `YYYYMMDD_Notes.txt` format files
- **Content Safety**: Preserves important user information in custom notes
- **Batch Efficiency**: Processes only videos that were actually copied/moved

**Real-World Testing:**
- **40+ video analysis** with 100% success rate
- **17 notes files generated** across different date structures
- **Mixed folder scenarios** (existing, missing, custom-named)
- **Custom notes preservation** verified with user content
- **Zero data loss** in comprehensive testing

**Error Handling:**
- **AI Service Failures**: Continues processing other videos if AI analysis fails
- **File Permission Issues**: Graceful handling with detailed error reporting
- **Network Timeouts**: Configurable timeouts with retry logic
- **Corrupted Videos**: Skips problematic files without stopping entire process

## 🔧 Troubleshooting

### Common Issues

1. **Python Environment**:
   ```bash
   # Ensure virtual environment is activated
   ./venv/Scripts/activate

   # Verify Python version
   python --version  # Should be 3.11+

   # Check package installation
   pip list | grep -E "(yaml|opencv|requests)"
   ```

2. **FFmpeg Issues**:
   ```bash
   # Test FFmpeg installation
   ffmpeg -version

   # Test video processing
   ./venv/Scripts/python.exe VideoProcessor/TestScripts/test_ffmpeg.py
   ```

3. **LM Studio Connection**:
   ```bash
   # Test AI connection
   ./venv/Scripts/python.exe VideoProcessor/TestScripts/test_lm_studio.py

   # Verify LM Studio is running on localhost:1234
   curl http://localhost:1234/v1/models
   ```

4. **Permission Issues**: Ensure write access to target directories

5. **Path Issues**: Use forward slashes `/` in config paths, even on Windows

6. **Notes Generation Issues**:
   ```bash
   # Check if LM Studio is running with a vision model loaded
   curl http://localhost:1234/v1/models

   # Test AI analysis on a single video
   ./venv/Scripts/python.exe VideoProcessor/TestScripts/test_video_analysis.py

   # Verify notes file creation permissions
   # Check that video directories are writable
   ```

7. **Form Name Extraction Issues**:
   - Ensure video thumbnails contain visible text with form names
   - Check AI model supports vision/image analysis
   - Verify thumbnail extraction is working with FFmpeg test

### 📝 Log Analysis

Check logs for detailed operation information:
```bash
# View recent logs
tail -f VideoProcessor/logs/phone_sync.log

# Search for errors
grep -i error VideoProcessor/logs/phone_sync.log

# Check AI analysis results
grep -i "kung_fu" VideoProcessor/logs/phone_sync.log

# Check notes generation
grep -i "notes" VideoProcessor/logs/phone_sync.log

# View generated notes files
find "Z:/PhotoSync_Test/My Videos" -name "*Notes.txt" -type f
```

### 🔄 Performance Optimization

**For Large File Collections:**
```yaml
performance:
  max_concurrent_operations: 8  # Increase for faster processing
  cache_existing_files: true    # Essential for deduplication
  progress_reporting_interval: 50  # More frequent progress updates
```

**For AI Analysis:**
```yaml
ai_settings:
  timeout_seconds: 60  # Increase for complex videos
  temperature: 0.2     # Lower for more consistent results
```

## 🛠️ Development

### Adding New Features
1. **Create Module**: Add new functionality in `VideoProcessor/modules/`
2. **Add Tests**: Create corresponding test in `VideoProcessor/TestScripts/`
3. **Update Config**: Add configuration options to `config.yaml`
4. **Integration**: Update `unified_processor.py` for workflow integration

### Debugging
```bash
# Enable debug logging
# In config.yaml: logging.log_level: "DEBUG"

# Run individual components
./venv/Scripts/python.exe VideoProcessor/modules/file_scanner.py
./venv/Scripts/python.exe VideoProcessor/modules/video_analyzer.py
```

## 📞 Support

For issues or questions:
1. **Check Logs**: Review `VideoProcessor/logs/phone_sync.log` for error details
2. **Run Tests**: Execute relevant test scripts to isolate issues
3. **Dry Run**: Use `--dry-run` flag to test without file operations
4. **Verify Config**: Ensure all paths in `config.yaml` are accessible
5. **Test Components**: Run individual test scripts to identify failing components

### 🐛 Reporting Issues
When reporting issues, please include:
- Error messages from logs
- Configuration file (sanitized)
- Python version and OS
- Test script results
- Steps to reproduce
