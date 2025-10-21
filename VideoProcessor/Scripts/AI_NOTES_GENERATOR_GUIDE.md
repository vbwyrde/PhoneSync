# AI Notes Generator - Standalone Script

## Overview

The AI Notes Generator is a standalone script that can analyze existing video files in your target folder structure and generate AI-powered notes files independently of the main processing workflow.

## Features

- ✅ **Standalone Operation**: Run independently without reprocessing files
- ✅ **Smart Detection**: Automatically finds video files in date-organized folders
- ✅ **Selective Processing**: Target specific dates or folders
- ✅ **Duplicate Prevention**: Skips folders that already have notes (unless forced)
- ✅ **Dry Run Mode**: Preview what would be analyzed before making changes
- ✅ **Force Regeneration**: Recreate existing notes files when needed

## Usage Examples

### Basic Usage

```bash
# Analyze all videos in target folders
python VideoProcessor/Scripts/generate_ai_notes.py

# Preview what would be analyzed (dry run)
python VideoProcessor/Scripts/generate_ai_notes.py --dry-run

# Force regeneration of existing notes files
python VideoProcessor/Scripts/generate_ai_notes.py --force
```

### Selective Processing

```bash
# Analyze only videos from a specific date
python VideoProcessor/Scripts/generate_ai_notes.py --date 2024-04-12

# Analyze only a specific folder
python VideoProcessor/Scripts/generate_ai_notes.py --folder "2024_04_12_Sat"

# Combine with dry run to preview specific folder
python VideoProcessor/Scripts/generate_ai_notes.py --folder "2024_04_12_Sat" --dry-run
```

### Advanced Usage

```bash
# Use custom config file
python VideoProcessor/Scripts/generate_ai_notes.py --config custom_config.yaml

# Force regenerate notes for specific date
python VideoProcessor/Scripts/generate_ai_notes.py --date 2024-04-12 --force

# Dry run with force to see what would be regenerated
python VideoProcessor/Scripts/generate_ai_notes.py --dry-run --force
```

## Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--config` | `-c` | Path to configuration file (default: config.yaml) |
| `--dry-run` | `-d` | Preview mode - show what would be analyzed |
| `--force` | `-f` | Regenerate existing notes files |
| `--date` | | Analyze only folders matching date (YYYY-MM-DD) |
| `--folder` | | Analyze only this specific folder name |
| `--help` | `-h` | Show help message |

## How It Works

1. **Folder Scanning**: Scans all target paths for date-organized folders (YYYY_MM_DD format)
2. **Video Detection**: Finds video files (.mp4, .avi, .mov, etc.) in each folder
3. **Notes Check**: Checks if Notes_YYYYMMDD.txt already exists (skips unless --force)
4. **AI Analysis**: Analyzes each video using the same AI system as main processing
5. **Notes Generation**: Creates Notes_YYYYMMDD.txt files with analysis results

## Output Format

The script generates notes files in the same format as the main system:

```
Video Analysis Notes - 2024_04_12
==================================================

video1.mp4 - Kung Fu/Martial Arts: Detailed analysis of martial arts content...
video2.mp4 - NOT KUNG FU: Analysis shows this is not martial arts content...
```

## Prerequisites

- LM Studio running and accessible (for AI analysis)
- Proper configuration in config.yaml
- Target folders with video files organized in date folders

## Use Cases

### 1. Retroactive Analysis
Generate notes for videos that were processed before AI analysis was implemented:
```bash
python VideoProcessor/Scripts/generate_ai_notes.py --dry-run
# Review what would be processed, then:
python VideoProcessor/Scripts/generate_ai_notes.py
```

### 2. Regenerate Specific Notes
Update analysis for a specific date after improving AI prompts:
```bash
python VideoProcessor/Scripts/generate_ai_notes.py --date 2024-04-12 --force
```

### 3. Spot Check Analysis
Verify AI analysis for a specific folder:
```bash
python VideoProcessor/Scripts/generate_ai_notes.py --folder "2024_04_12_Sat" --dry-run
```

### 4. Batch Regeneration
Regenerate all notes files (useful after AI model updates):
```bash
python VideoProcessor/Scripts/generate_ai_notes.py --force --dry-run
# Review the scope, then:
python VideoProcessor/Scripts/generate_ai_notes.py --force
```

## Performance Notes

- The script processes videos sequentially (not batch optimized)
- Each video analysis takes 2-3 seconds depending on AI response time
- Use `--date` or `--folder` filters for faster processing of specific content
- Dry run mode is very fast as it only scans folders without AI analysis

## Error Handling

- Gracefully handles missing folders or inaccessible files
- Continues processing other videos if one fails
- Provides detailed error reporting and statistics
- Logs all activities for troubleshooting

## Integration with Main System

This script is completely independent but uses the same:
- Configuration files
- AI analysis engine
- Notes file format
- Logging system

This ensures consistency between standalone analysis and main processing workflow.
