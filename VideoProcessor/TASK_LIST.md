# PhoneSync + VideoProcessor - Unified Python Solution Task List

## 🎯 **PROJECT GOAL**
Create a unified Python application that combines file organization (PhoneSync) with video analysis (VideoProcessor) into a single, maintainable daily automation system.

**Core Functions:**
1. **File Organization**: Scan folders, organize JPG/MP4 files by date with Wudan rules
2. **Video Analysis**: Extract thumbnails, AI analysis for kung fu detection, generate notes
3. **Daily Automation**: Single scheduled task for complete file management

**Input**: Source folders with mixed JPG/MP4 files
**Output**: Organized date folders + AI-generated video description notes

---

## 📋 **TASK BREAKDOWN**

### **Phase 1: Environment Setup & Core Infrastructure**
- [ ] Create Python virtual environment in VideoProcessor folder
- [ ] Install required dependencies (requests, pillow, python-dateutil, pyyaml, hashlib)
- [ ] Test FFmpeg availability and basic thumbnail extraction
- [ ] Test LM Studio API connectivity (localhost:1234/v1/chat/completions)
- [ ] Create unified YAML configuration file structure that combines PhoneSync and VideoProcessor settings
- [ ] Create initial unified script structure with modular components
- [ ] Implement comprehensive logging system with 14 day rotation
- [ ] Ensure that logging goes into one file and records both: 1. Process flow, 2. Errors
- [ ] Implement end-to-end Test integration folders with test files that have sample data
- [ ] Implement unit tests for critical components (thumbnail extraction, AI analysis, logging)

### **Phase 2: File Organization System (PhoneSync Conversion)**
- [ ] **File Scanner**: Scan source folders for JPG/MP4 files recursively
- [ ] **Date Extraction**: Extract dates from filenames or file modification times
- [ ] **Wudan Rules Engine**: Implement time-based rules for video categorization
- [ ] **Target Path Resolution**: Determine correct destination folders (Pictures/Videos/Wudan) - rules are in the PhoneSync.ps1 file.
- [ ] **Deduplication System**: Hash-based duplicate detection with caching
- [ ] **File Operations**: Copy files with collision handling and progress tracking
- [ ] **Integration Testing**: Validate file organization with test data
- [ ] **Unit Testing**: Comprehensive unit tests for all components
- [ ] **Note1**: This step should be taken before the Video Analysis step so we know which files need to be processed for AI analysis.
- [ ] **Note2**: The PhoneSync.ps1 file has the logic for the Wudan rules.  This needs to be converted to Python.

### **Phase 3: Video Analysis System (AI Integration)**
- [ ] **Video Detection**: Identify MP4 files that need AI analysis
- [ ] **Detection Rule**: Extractions are only done for mp4 files that do not yet exist in the target folder structure
- [ ] **Thumbnail Extractor**: Use FFmpeg to extract frame at 10-second mark
- [ ] **AI Analyzer**: Send thumbnail to LM Studio for kung fu detection + description
- [ ] **Notes Generator**: Create YYYYMMDD_Notes.txt files with "filename - description"
- [ ] **Results Integration**: Combine file organization with AI analysis results

### **Phase 4: Unified System Integration**
- [ ] **Main Orchestrator**: Single entry point that runs both file organization and video analysis
- [ ] **Configuration Management**: Unified YAML config for all settings
- [ ] **Error Handling**: Robust error recovery with detailed logging
- [ ] **Progress Reporting**: Comprehensive status reporting and statistics
- [ ] **Dry Run Mode**: Test mode for validation without actual file operations

### **Phase 5: Scheduling & Production Deployment**
- [ ] **Windows Task Scheduler**: Create scheduled task for daily execution
- [ ] **Batch Wrapper**: Create .bat file for easy Task Scheduler integration
- [ ] **Testing**: End-to-end testing with Test source and Target folders
- [ ] **Documentation**: Complete README with setup and usage instructions
- [ ] **Monitoring**: Log analysis and error alerting setup

---

## 🔧 **TECHNICAL SPECIFICATIONS**

### **Dependencies**
```
requests>=2.31.0          # LM Studio API calls
pillow>=10.0.0           # Image processing and base64 handling
python-dateutil>=2.8.2   # Date parsing and manipulation
pyyaml>=6.0              # YAML configuration file support
hashlib                  # File hashing for deduplication (built-in)
pathlib                  # Modern path handling (built-in)
logging                  # Comprehensive logging (built-in)
subprocess               # FFmpeg integration (built-in)
```

### **Configuration Requirements**
- **Source Folders**: Multiple configurable source directories to scan
- **Target Paths**: Pictures, Videos, and Wudan video destinations
- **File Extensions**: Configurable JPG/MP4 file type support
- **Wudan Rules**: Time-based categorization rules (before/after 2021)
- **LM Studio Integration**: http://localhost:1234/v1/chat/completions
- **AI Model**: mimo-vl-7b-rl@q8_k_xl with optimized settings
- **Logging**: Configurable log levels, rotation, and retention
- **Deduplication**: Hash-based duplicate detection settings

### **File Structure**
```
VideoProcessor/
├── venv/                    # Virtual environment
├── config.yaml             # Unified configuration file
├── phone_sync.py           # Main unified script
├── requirements.txt        # Python dependencies
├── run_phone_sync.bat      # Windows Task Scheduler wrapper
├── README.md              # Complete documentation
├── logs/                  # Log files with rotation
├── tests/                 # Unit tests for components
└── TASK_LIST.md          # This file
```

---

## 🎯 **SUCCESS CRITERIA**

### **Functional Requirements**
1. **File Organization**: Scan source folders and organize JPG/MP4 files by date
2. **Wudan Rules**: Apply time-based rules to categorize videos into Wudan folder
3. **Deduplication**: Detect and skip duplicate files using hash comparison
4. **Video Analysis**: Extract thumbnails and perform AI analysis for MP4 files
5. **AI Integration**: Call LM Studio API for kung fu detection and descriptions
6. **Notes Generation**: Create date-grouped text files with video descriptions
7. **Error Handling**: Robust error recovery with comprehensive logging
8. **Configuration**: Single YAML file for all settings and paths

### **Performance Requirements**
- **File Organization**: Process thousands of files efficiently with deduplication
- **Video Analysis**: ~4 seconds per video for thumbnail + AI analysis
- **Memory Usage**: Minimal - process files individually, not batch loading
- **Reliability**: 100% success rate with graceful error recovery
- **Scalability**: Handle large source folders with progress reporting

### **Output Structure**
```
Target Folders:
├── My Pictures/
│   └── 2025_09_19/          # Date-organized JPG files
├── My Videos/
│   └── 2025_09_19/          # Regular MP4 files
└── My Videos/Wudan/
    └── 2025_09_19/          # Wudan-time MP4 files

Notes Files:
├── 20250406_Notes.txt:
│   20250406_110016_1.mp4 - Dragon Walking Sword VII martial arts training
├── 20250504_Notes.txt:
│   20250504_113836_1.mp4 - Bagua martial arts practice with traditional forms
└── 20120125_Notes.txt:
    M4H01890.MP4 - Tortoise in natural habitat, no martial arts content
    M4H01892.MP4 - Wildlife footage of tortoise behavior
```

---

## 🚀 **ADVANTAGES OVER SEPARATE SYSTEMS**

### **Unified Solution Benefits**
- ✅ **Single Application** - One script handles file organization + video analysis
- ✅ **Unified Configuration** - Single YAML file for all settings
- ✅ **Consolidated Logging** - All operations logged to same system
- ✅ **Single Scheduled Task** - One daily automation instead of multiple
- ✅ **Shared Deduplication** - File organization and video analysis share duplicate detection

### **Python vs PowerShell Benefits**
- ✅ **Better LLM Integration** - Native HTTP requests and JSON handling
- ✅ **Superior Error Handling** - Try/catch with detailed stack traces
- ✅ **Cross-Platform Compatibility** - Works on Windows/Linux if needed
- ✅ **Easier Testing** - Unit tests for individual components
- ✅ **Modern Libraries** - Rich ecosystem for file processing and AI integration

### **Maintainability Improvements**
- ✅ **Single Codebase** - One language, one set of dependencies
- ✅ **Standard Debugging** - Python debugging tools and practices
- ✅ **Version Control Friendly** - Clean diffs and change tracking
- ✅ **Extensible Architecture** - Easy to add new AI features or file types

---

## 📝 **IMPLEMENTATION NOTES**

### **Key Lessons from Previous Implementations**
1. **N8N Complexity**: Workflow engines add unnecessary complexity for local file processing
2. **FFmpeg Reliability**: Direct FFmpeg commands work better than workflow node wrappers
3. **LM Studio Integration**: Simple HTTP requests are more reliable than complex workflows
4. **Error Logging**: Comprehensive logging is essential for debugging and monitoring
5. **Configuration Management**: YAML files are more maintainable than JSON workflows

### **Proven Components to Reuse**
- **PhoneSync Logic**: File organization, deduplication, and Wudan rules (from PowerShell)
- **FFmpeg Command**: `ffmpeg -i {video} -ss 00:00:10 -vframes 1 -vf scale=320:240 -f image2pipe -vcodec png -`
- **AI Prompt**: Optimized kung fu detection prompt with inclusive analysis
- **Date Extraction**: Regex patterns for YYYYMMDD extraction from filenames
- **Base64 Handling**: PNG signature validation and corruption detection
- **Logging System**: Comprehensive logging with rotation and retention

---

## 🎯 **IMPLEMENTATION STRATEGY**

### **Development Approach**
1. **Start new agent conversation** with this comprehensive task list
2. **Phase-by-phase development** - complete each phase before moving to next
3. **Test incrementally** - validate each component individually
4. **Reuse proven patterns** - leverage existing PhoneSync and N8N learnings
5. **Keep it simple** - avoid over-engineering, focus on reliability

### **Success Metrics**
- **File Organization**: Successfully organize mixed JPG/MP4 files by date
- **Wudan Categorization**: Correctly apply time-based rules for video placement
- **AI Analysis**: Generate accurate kung fu detection and descriptions
- **Error Handling**: Graceful recovery from file access and API errors
- **Performance**: Process large folders efficiently with progress reporting
- **Scheduling**: Reliable daily automation via Windows Task Scheduler

**Estimated completion time**: 4-6 hours for complete unified solution

---

## 📋 **CONFIGURATION TEMPLATE**

### **Sample config.yaml Structure**
```yaml
# Source and target paths
source_folders:
  - "Z:/PhotoSync_Test/Source"
  - "C:/Users/Username/Phone_Backup"

target_paths:
  pictures: "Z:/PhotoSync_Test/My Pictures"
  videos: "Z:/PhotoSync_Test/My Videos"
  wudan_videos: "Z:/PhotoSync_Test/My Videos/Wudan"
  notes: "Z:/PhotoSync_Test/Video_Notes"

# File type configuration
file_extensions:
  pictures: [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"]
  videos: [".mp4", ".avi", ".mov", ".wmv", ".mkv", ".flv", ".webm"]

# Wudan time-based rules
wudan_rules:
  before_2021:
    days_of_week: [1, 2, 3, 4, 6]  # Mon-Thu, Sat
    time_ranges:
      - {start: "05:00", end: "08:00"}
      - {start: "18:00", end: "22:00"}
  after_2021:
    days_of_week: [0, 1, 2, 3, 4, 6]  # Sun-Thu, Sat
    time_ranges:
      0: [{start: "08:00", end: "13:00"}]  # Sunday
      1: [{start: "05:00", end: "08:00"}, {start: "18:00", end: "21:00"}]  # Monday
      # ... etc

# AI and processing settings
ai_settings:
  lm_studio_url: "http://localhost:1234/v1/chat/completions"
  model: "mimo-vl-7b-rl@q8_k_xl"
  temperature: 0.4
  max_tokens: 150
  kung_fu_prompt: "Analyze this video thumbnail for kung fu or martial arts content..."

# System options
options:
  enable_deduplication: true
  use_hash_comparison: false
  create_missing_folders: true
  dry_run: false
  verbose_logging: false
  force_recopy_if_newer: true

# Logging configuration
logging:
  enabled: true
  log_path: "logs/phone_sync.log"
  max_log_size_mb: 10
  keep_log_days: 30
  log_level: "INFO"
```

---

## 🧹 **CLEANUP COMPLETED**

✅ **N8N file processors stopped** - No more runaway error generation
✅ **Shared folders cleaned** - Kept only 4 most recent files for reference
✅ **PhoneSync/VideoProcessor directory created** - Ready for unified Python implementation
✅ **Guidelines updated** - Added N8N evaluation framework to prevent future rabbit holes
✅ **Task list updated** - Comprehensive roadmap for unified PhoneSync + VideoProcessor solution

**Ready to start fresh with a unified, reliable Python solution that combines file organization with AI-powered video analysis!**
