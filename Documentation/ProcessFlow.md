# PhoneSync + VideoProcessor - Technical Process Flow

**Detailed technical documentation of the system's processing workflow**

## Overview

The PhoneSync + VideoProcessor system follows a multi-phase approach to organize files and analyze videos with AI. This document provides a detailed technical breakdown of each phase and component interaction.

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   File Scanner  │───▶│  State Manager   │───▶│ File Organizer  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Date Extraction │    │ Incremental      │    │ Target Path     │
│ & Metadata      │    │ Processing       │    │ Resolution      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                    ┌──────────────────┐    ┌─────────────────┐
                    │ Video Analyzer   │    │ Wudan Rules     │
                    │ (AI Analysis)    │    │ Engine          │
                    └──────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                    ┌──────────────────┐    ┌─────────────────┐
                    │ Notes Generator  │    │ Deduplication   │
                    │                  │    │ Manager         │
                    └──────────────────┘    └─────────────────┘
```

## Phase-by-Phase Process Flow

### Phase 0: Initialization & State Management

**Purpose**: Initialize system components and determine processing mode

**Components**: 
- `ProcessingStateManager`
- `ConfigManager`
- `Logger`

**Process**:
1. Load configuration from `config.yaml`
2. Initialize logging system
3. Load processing state from `VideoProcessor/state/`
4. Determine processing mode (full vs incremental)
5. Initialize all system components

**Key Files**:
- `processing_state.json` - Main state tracking
- `processed_files.json` - Database of processed files

**Decision Logic**:
```python
if first_run:
    mode = "full_processing"
    reason = "First run - processing all files"
else:
    mode = "incremental_processing" 
    reason = f"Processing files newer than {last_run_timestamp}"
```

### Phase 1: Deduplication Cache Building

**Purpose**: Build cache of existing files to avoid duplicate processing

**Components**: 
- `DeduplicationManager`

**Process**:
1. Scan all target directories recursively
2. Build cache with file metadata (name, size, date)
3. Create lookup structures for fast duplicate detection

**Cache Structure**:
```python
{
    "filename.mp4": [
        {
            "size": 12345678,
            "path": "/target/2024_01_15/filename.mp4",
            "date": "2024-01-15"
        }
    ]
}
```

### Phase 2: File Discovery & Scanning

**Purpose**: Discover all supported files in source directories

**Components**: 
- `FileScanner`

**Process**:
1. Recursively scan each source folder
2. Filter files by supported extensions
3. Extract file metadata and creation dates
4. Apply date extraction patterns

**Date Extraction Patterns** (in priority order):
1. `YYYYMMDD_HHMMSS_X.ext` - Primary phone format
2. `YYYY_MM_DD` - Legacy format
3. `YYYY-MM-DD` - Alternative format
4. File modification time - Fallback

**File Info Structure**:
```python
{
    'path': '/source/20240115_143022_1.mp4',
    'name': '20240115_143022_1.mp4',
    'extension': '.mp4',
    'type': 'video',
    'size': 12345678,
    'date': datetime(2024, 1, 15, 14, 30, 22),
    'modification_time': datetime(...),
    'creation_time': datetime(...)
}
```

### Phase 2.5: Incremental Processing Filter

**Purpose**: Filter files based on processing state for efficiency

**Components**: 
- `ProcessingStateManager`

**Filter Logic**:
```python
def should_process_file(file_info):
    file_id = f"{path}|{size}|{date.isoformat()}"
    
    # Skip if already processed
    if file_id in processed_files:
        return False
    
    # Skip if older than last run (incremental mode)
    if not first_run and file_date <= last_run_time:
        return False
        
    return True
```

### Phase 3: File Organization

**Purpose**: Copy/move files to appropriate target directories

**Components**: 
- `FileOrganizer`
- `TargetPathResolver` 
- `WudanRulesEngine`
- `DeduplicationManager`

**Process Flow**:
1. **Target Path Resolution**:
   - Determine file type (picture/video)
   - Apply Wudan rules for videos
   - Generate date-based folder path (`YYYY_MM_DD`)

2. **Wudan Rules Evaluation**:
   ```python
   if file_type == 'video':
       if wudan_engine.should_go_to_wudan_folder(file_date):
           base_path = target_paths['wudan']
       else:
           base_path = target_paths['videos']
   ```

3. **Duplication Check**:
   - Check if file already exists in target
   - Compare by name, size, and date
   - Skip if duplicate found

4. **File Copy Operation**:
   - Create target directory if needed
   - Handle filename conflicts with numbering
   - Copy file with progress tracking
   - Update deduplication cache

**Target Structure**:
```
My Videos/
├── 2024_01_15/
│   ├── 20240115_143022_1.mp4
│   └── 20240115_Notes.txt
└── Wudan/
    └── 2024_01_16/
        ├── 20240116_090000_1.mp4
        └── 20240116_Notes.txt
```

### Phase 4: Video Analysis (AI Processing)

**Purpose**: Analyze video content for martial arts detection using AI

**Components**:
- `VideoAnalyzer`
- LM Studio API integration
- FFmpeg for thumbnail extraction

**Process Flow**:
1. **Thumbnail Extraction**:
   ```bash
   ffmpeg -i video.mp4 -ss 00:00:01 -vframes 1 -f image2pipe -vcodec png -
   ```

2. **AI Analysis**:
   - Send thumbnail to LM Studio vision model
   - Use specialized prompt for kung fu detection
   - Parse AI response for confidence and description

3. **Analysis Result Processing**:
   ```python
   {
       'analyzed': True,
       'is_kung_fu': True,
       'confidence': 0.85,
       'description': 'Martial arts form detected - appears to be Tai Chi',
       'analysis_timestamp': '2024-01-15T14:30:22'
   }
   ```

**AI Prompt Template**:
```
Analyze this video thumbnail for martial arts or kung fu content.
Look for:
- Martial arts stances or poses
- Traditional kung fu movements
- Training equipment
- Martial arts uniforms

Respond with:
1. Is this kung fu/martial arts? (YES/NO)
2. Confidence level (0-100%)
3. Brief description of what you see
```

### Phase 5: Notes Generation

**Purpose**: Create searchable notes files with video descriptions

**Components**:
- `NotesGenerator`

**Process**:
1. **Note Collection**:
   - Collect analysis results by date
   - Group videos by target directory
   - Format descriptions for readability

2. **File Generation**:
   - Create `YYYYMMDD_Notes.txt` per date folder
   - Use format: `filename - description`
   - Preserve existing user notes

**Notes File Format**:
```
Video Analysis Notes - 2024_01_15
==================================================

20240115_143022_1.mp4 - Martial arts form detected - appears to be Tai Chi
20240115_150000_1.mp4 - Regular video content - no martial arts detected
```

### Phase 6: State Finalization

**Purpose**: Update processing state for next incremental run

**Components**:
- `ProcessingStateManager`

**Process**:
1. Update processing statistics
2. Save processed file database
3. Record run timestamp and metadata
4. Log final statistics

**State Update**:
```python
ProcessingState(
    last_run_timestamp=current_time.isoformat(),
    last_processed_file=stats['last_processed_file'],
    last_processed_date=current_time.strftime('%Y-%m-%d'),
    total_files_processed=stats['files_processed'],
    total_videos_analyzed=stats['videos_analyzed']
)
```

## Component Interactions

### Wudan Rules Engine

**Purpose**: Time-based routing for martial arts videos

**Rules Logic**:
- **Before 2021**: Specific days and time ranges
- **After 2021**: Day-specific time ranges with different patterns

**Implementation**:
```python
def should_go_to_wudan_folder(file_date):
    year = file_date.year
    day_of_week = file_date.weekday()
    file_time = file_date.time()

    if year < 2021:
        return check_before_2021_rules(day_of_week, file_time)
    else:
        return check_after_2021_rules(day_of_week, file_time)
```

### Deduplication Manager

**Purpose**: Prevent duplicate file processing and storage

**Strategies**:
1. **Filename + Size Matching**: Primary deduplication
2. **Date Validation**: Secondary verification
3. **Path Tracking**: Avoid re-processing moved files

**Cache Structure**:
```python
{
    "cache_by_name": {
        "video.mp4": [file_entries...]
    },
    "cache_by_size": {
        12345678: [file_entries...]
    }
}
```

## Error Handling & Recovery

### File Processing Errors
- **Missing Source Files**: Log warning, continue processing
- **Permission Errors**: Log error, skip file
- **Disk Space Issues**: Fail gracefully with clear error message

### AI Analysis Errors
- **LM Studio Unavailable**: Skip analysis, continue file organization
- **Thumbnail Extraction Failure**: Log error, mark as unanalyzed
- **API Timeout**: Retry with exponential backoff

### State Management Errors
- **Corrupted State Files**: Reset to clean state, log warning
- **Permission Issues**: Create backup state location

## Performance Optimizations

### Incremental Processing
- Only process files newer than last run
- Skip files already in processed database
- Maintain persistent state across runs

### Deduplication
- Build target cache once per run
- Use efficient lookup structures
- Skip expensive operations for duplicates

### Parallel Processing
- Thumbnail extraction can be parallelized
- File operations use efficient copy methods
- AI analysis batching for multiple videos

## Configuration Dependencies

### Required Settings
```yaml
environment: "DEVELOPMENT" | "PRODUCTION"
source_folders: [list of source paths]
target_paths:
  pictures: "path/to/pictures"
  videos: "path/to/videos"
  wudan: "path/to/wudan"
```

### Optional Features
```yaml
options:
  enable_deduplication: true
  create_missing_folders: true
  enable_video_analysis: true
  enable_notes_generation: true
```

## Logging & Monitoring

### Log Levels
- **INFO**: Major phase transitions, statistics
- **DEBUG**: Detailed file processing steps
- **WARNING**: Non-fatal issues, skipped files
- **ERROR**: Processing failures, system errors

### Key Metrics
- Files discovered vs processed
- Videos analyzed vs total videos
- Duplicates detected and skipped
- Processing time per phase
- AI analysis success rate

---

*This document reflects the current implementation as of the system architecture. For usage instructions, see README.md.*
