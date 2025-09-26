# PhoneSync + VideoProcessor - Complete Process Flow

## 🚀 **Application Entry Points**

### **Option 1: File Organization Only**
- **Command**: `./venv/Scripts/python.exe VideoProcessor/phone_sync.py`
- **Purpose**: Organize files without AI video analysis
- **Use Case**: Quick file organization, AI not needed

### **Option 2: Video Analysis Only** 
- **Command**: `./venv/Scripts/python.exe VideoProcessor/main.py`
- **Purpose**: AI analysis of videos without file organization
- **Use Case**: Analyze videos already in target locations

### **Option 3: Unified Processing (Recommended)**
- **Command**: `./venv/Scripts/python.exe VideoProcessor/modules/unified_processor.py`
- **Purpose**: Complete workflow - organize files + analyze videos
- **Use Case**: Full daily automation workflow

---

## 📋 **Phase 1: Initialization & Configuration**

### **1.1 Configuration Loading**
- Load `config.yaml` from specified path (default: project root)
- Validate required sections:
  - `source_folders` - Where to scan for files
  - `target_paths` - Where to organize files (pictures, videos, wudan, notes)
  - `file_extensions` - Supported file types
  - `wudan_rules` - Time-based routing rules
  - `ai_settings` - LM Studio configuration
  - `logging` - Log configuration
  - `options` - System behavior settings

### **1.2 Component Initialization**
- **Logger Setup**: Configure rotating logs with retention
- **FileScanner**: Initialize file discovery engine
- **WudanRulesEngine**: Load time-based classification rules
- **DeduplicationManager**: Prepare duplicate detection system
- **TargetPathResolver**: Initialize path resolution logic
- **FileOrganizer**: Setup file operation handler
- **VideoAnalyzer**: Initialize AI analysis system (if enabled)

### **1.3 System Validation**
- Verify source folders exist and are accessible
- Validate target paths and create missing directories
- Test FFmpeg availability (for video processing)
- Check LM Studio connection (if AI enabled)
- Initialize processing statistics tracking

---

## 📁 **Phase 2: Deduplication Cache Building**

### **2.1 Cache Initialization** (if `enable_deduplication: true`)
- Scan all target directories:
  - `target_paths.pictures`
  - `target_paths.videos` 
  - `target_paths.wudan`
- Build comprehensive file cache with:
  - **Filename**: Original filename
  - **Size**: File size in bytes
  - **Path**: Full target path
  - **Base Pattern**: Extracted base filename (for flexible matching)

### **2.2 Flexible Filename Pattern Extraction**
- **Date-named files**: `20250412_110016_1.mp4` → `20250412_110016_1`
- **Non-date files**: `M4H01890.MP4` → `M4H01890`
- **Handle appended text**: Match base patterns with variations
  - `20250412_110016_1.mp4` matches `20250412_110016_1_KungFu_GimStyle.mp4`
  - `M4H01890.MP4` matches `M4H01890_CameraFootage.MP4`

### **2.3 Cache Statistics**
- Log total files found in target directories
- Report cache building success/failure
- Prepare for efficient duplicate detection

---

## 🔍 **Phase 3: Source File Discovery**

### **3.1 File Scanning**
- **For each source folder** in `source_folders`:
  - Recursively scan for supported file types
  - Extract file metadata:
    - **Path**: Full source path
    - **Name**: Filename with extension
    - **Size**: File size in bytes
    - **Extension**: File extension (normalized to lowercase)
    - **Date**: File creation/modification date
    - **Type**: 'picture' or 'video' based on extension

### **3.2 Date Extraction Logic**
- **Priority 1 - Filename Date**: Parse date from filename patterns
  - `20250412_110016_1.mp4` → April 12, 2025, 11:00:16
  - `IMG_20250412_110016.jpg` → April 12, 2025, 11:00:16
- **Priority 2 - File Metadata**: Use file modification date if no filename date
- **Priority 3 - Current Date**: Fallback to current date (rare)

### **3.3 File Classification**
- **Pictures**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`
- **Videos**: `.mp4`, `.avi`, `.mov`, `.wmv`, `.mkv`, `.flv`, `.webm`
- **Unsupported**: Log and skip files with unsupported extensions

---

## 🎯 **Phase 4: Target Path Resolution**

### **4.1 Base Path Determination**
- **For Pictures**:
  - Always route to `target_paths.pictures`
- **For Videos**:
  - **Step 1**: Apply Wudan time-based rules
  - **Step 2**: Route to `target_paths.wudan` or `target_paths.videos`

### **4.2 Wudan Rules Engine** (for videos only)
- **Before 2021 Rules**:
  - **Days**: Monday, Tuesday, Wednesday, Thursday, Saturday
  - **Times**: 5:00-8:00 AM OR 6:00-10:00 PM
- **After 2021 Rules** (day-specific):
  - **Sunday**: 8:00 AM - 1:00 PM
  - **Monday**: 5:00-8:00 AM OR 6:00-9:00 PM
  - **Tuesday**: 5:00-8:00 AM OR 6:00-9:00 PM
  - **Wednesday**: 6:00-10:00 PM
  - **Thursday**: 5:00-8:00 AM OR 6:00-9:00 PM
  - **Saturday**: 8:00 AM - 4:00 PM

### **4.3 Date Folder Resolution**
- **Create date pattern**: `YYYY_MM_DD` (e.g., `2025_04_12`)
- **Check for existing custom folders**:
  - Look for folders matching `YYYY_MM_DD*` pattern
  - **Examples**:
    - `2025_04_12_KungFuClass` (custom suffix)
    - `2025_06_15_BirthdayParty` (custom suffix)
    - `2025_08_30` (standard format)
- **Folder Selection Priority**:
  - **Priority 1**: Use existing custom folder if found
  - **Priority 2**: Create new standard `YYYY_MM_DD` folder

### **4.4 Final Target Path Construction**
- **Pictures**: `{target_paths.pictures}/{date_folder}/{filename}`
- **Regular Videos**: `{target_paths.videos}/{date_folder}/{filename}`
- **Wudan Videos**: `{target_paths.wudan}/{date_folder}/{filename}`

---

## 🔄 **Phase 5: Deduplication Check**

### **5.1 Duplicate Detection Logic**
- **For each source file**:
  - Extract base filename pattern
  - Check cache for matching patterns in target date folder
  - **Match Criteria**:
    - **Base filename match** (flexible pattern matching)
    - **File size match** (exact byte comparison)
    - **Target folder match** (same date-based folder)

### **5.2 Flexible Matching Examples**
- **Source**: `20250412_110016_1.mp4` (1,000,000 bytes)
- **Target**: `20250412_110016_1_KungFu_GimStyle.mp4` (1,000,000 bytes)
- **Result**: DUPLICATE DETECTED → Skip processing

### **5.3 Duplicate Handling**
- **If duplicate found**:
  - Log: "File already exists in target"
  - Skip file processing (no copy, no AI analysis)
  - Update statistics: `files_skipped++`
- **If not duplicate**:
  - Proceed to file organization phase

---

## 📦 **Phase 6: File Organization**

### **6.1 Directory Creation**
- **Check target directory exists**:
  - Create missing date folders as needed
  - Set appropriate permissions
  - Log directory creation

### **6.2 File Operation**
- **Copy Mode** (default: `copy_files: true`):
  - Copy source file to target location
  - Preserve original file in source
- **Move Mode** (`copy_files: false`):
  - Move source file to target location
  - Remove from source after successful transfer

### **6.3 Collision Handling**
- **If target file exists with same name**:
  - **Size comparison**: If sizes match, skip (duplicate)
  - **Size mismatch**: Generate unique filename with suffix
  - **Force recopy**: If `force_recopy_if_newer: true` and source is newer

### **6.4 Operation Validation**
- **Verify successful copy/move**:
  - Check target file exists
  - Validate file size matches source
  - Update statistics: `files_processed++`
- **Handle failures**:
  - Log error details
  - Update statistics: `errors++`
  - Continue processing other files

---

## 🤖 **Phase 7: AI Video Analysis** (if enabled)

### **7.1 Analysis Eligibility Check**
- **Skip analysis if**:
  - File is not a video
  - `enable_video_analysis: false`
  - File was skipped due to duplication
  - AI system unavailable

### **7.2 Dynamic Midpoint Thumbnail Extraction**
- **Get video duration** using FFmpeg:
  - `ffprobe -v quiet -show_entries format=duration`
- **Calculate midpoint**: `midpoint_seconds = duration / 2.0`
- **Extract thumbnail** using FFmpeg:
  - `ffmpeg -ss {midpoint} -i {video} -vframes 1 -f image2pipe -`
- **Convert to base64** for AI analysis

### **7.3 LM Studio AI Analysis**
- **Prepare API request**:
  - **URL**: `http://localhost:1234/v1/chat/completions`
  - **Model**: `mimo-vl-7b-rl@q8_k_xl`
  - **Prompt**: Kung fu/martial arts detection prompt
  - **Image**: Base64 encoded thumbnail
- **Send request** with timeout handling
- **Parse response**:
  - Extract YES/NO kung fu detection
  - Extract confidence level
  - Extract descriptive text

### **7.4 Analysis Result Processing**
- **Update statistics**:
  - `videos_analyzed++`
  - `kung_fu_detected++` (if applicable)
- **Generate notes** (if kung fu detected):
  - Create descriptive note file
  - Save to `target_paths.notes` directory
  - Include analysis details and confidence

---

## 📊 **Phase 8: Statistics & Reporting**

### **8.1 Processing Statistics**
- **File Counts**:
  - `files_found`: Total files discovered
  - `files_processed`: Successfully organized
  - `files_skipped`: Duplicates skipped
  - `files_copied`: Actually transferred
- **Video Analysis**:
  - `videos_analyzed`: Videos processed by AI
  - `kung_fu_detected`: Martial arts content found
  - `notes_generated`: Analysis notes created
- **Performance**:
  - `start_time` / `end_time`: Processing duration
  - `errors`: Failed operations

### **8.2 Final Reporting**
- **Log summary statistics**:
  - Success rate percentage
  - Processing time
  - Error count and details
- **Console output** (if verbose):
  - Detailed operation log
  - File-by-file processing results
- **Return status**:
  - `True`: Successful completion
  - `False`: Errors occurred

---

## 🔧 **Phase 9: Cleanup & Finalization**

### **9.1 Resource Cleanup**
- Close file handles
- Clear memory caches
- Disconnect from AI services

### **9.2 Log Rotation**
- **If log file exceeds size limit**:
  - Rotate to backup file
  - Create new log file
  - Clean old logs based on retention policy

### **9.3 Exit Handling**
- **Success**: Exit code 0
- **Errors**: Exit code 1
- **User interruption**: Graceful shutdown

---

## ⚙️ **Configuration-Driven Behavior**

### **Dry Run Mode** (`--dry-run`)
- **File Organization**: Log what would be done, don't copy files
- **AI Analysis**: Skip actual analysis, simulate results
- **Directory Creation**: Create directories but don't copy files

### **Verbose Mode** (`--verbose`)
- **Enhanced Logging**: DEBUG level messages
- **Console Output**: Real-time processing updates
- **Detailed Statistics**: Extended reporting

### **Performance Tuning**
- **Concurrent Operations**: `max_concurrent_operations`
- **Progress Reporting**: `progress_reporting_interval`
- **Cache Management**: `cache_existing_files`

---

## 🎯 **Key Success Factors**

1. **✅ Flexible Deduplication**: Handles appended text in filenames
2. **✅ Sophisticated Time Rules**: Accurate Wudan classification
3. **✅ Custom Folder Support**: Uses existing custom-named folders
4. **✅ Robust Error Handling**: Continues processing despite individual failures
5. **✅ Performance Optimization**: Only processes missing files
6. **✅ Comprehensive Logging**: Full audit trail of operations
7. **✅ AI Integration**: Optional but powerful video analysis
8. **✅ Cross-Platform**: Works on Windows with proper path handling
