# Comprehensive Test Cases for PhoneSync + VideoProcessor

## 🎯 Test Case Categories

### 1. **File Naming Convention Tests**

#### 1.1 Standard Date-Named Files
- **Test Case**: `20250412_110016_1.mp4` (standard phone format)
- **Expected**: Route to `2025_04_12/` folder
- **Validation**: Correct date parsing and folder creation

#### 1.2 Non-Date-Named Files  
- **Test Case**: `M4H01890.MP4` (camera format)
- **Expected**: Route based on file modification date
- **Validation**: Fallback to metadata-based dating

#### 1.3 Files with Spaces
- **Test Case**: `20250615_102535 (1).mp4` (duplicate naming)
- **Expected**: Handle spaces and parentheses correctly
- **Validation**: Proper filename parsing

#### 1.4 Mixed Case Extensions
- **Test Case**: `video.Mp4`, `photo.JPG`, `file.jpeg`
- **Expected**: Case-insensitive extension matching
- **Validation**: All variations recognized

#### 1.5 Unusual Formats
- **Test Case**: `IMG_20250412_110016.jpg`, `VID_20250412_110016.mp4`
- **Expected**: Extract date from filename if possible
- **Validation**: Flexible date extraction

### 2. **Deduplication & Existing File Tests**

#### 2.1 Exact Duplicate Detection
- **Setup**: File `20250412_110016_1.mp4` already exists in target
- **Test**: Process same file again
- **Expected**: Skip processing, no AI analysis
- **Validation**: Log shows "File already exists", no LLM call

#### 2.2 Flexible Filename Matching
- **Setup**: `20250412_292993_1_KungFu_GimStyle.mp4` exists in target
- **Test**: Process `20250412_292993_1.mp4` (base filename)
- **Expected**: Detect as duplicate, skip processing
- **Validation**: Flexible matching works correctly

#### 2.3 Size Mismatch Handling
- **Setup**: `20250412_110016_1.mp4` exists but different size
- **Test**: Process file with same name but different size
- **Expected**: Process as new file (not duplicate)
- **Validation**: Size validation prevents false positives

#### 2.4 Appended Text Variations
- **Setup**: Test multiple appended text patterns
- **Test Cases**:
  - `M4H01890.MP4` vs `M4H01890_CameraFootage.MP4`
  - `20250412_110016_1.mp4` vs `20250412_110016_1_MorningPractice.mp4`
- **Expected**: All variations detected as duplicates
- **Validation**: Flexible base filename extraction

### 3. **Wudan Time Rules Tests**

#### 3.1 Before 2021 Rules
- **Test Cases**:
  - `20200615_070000_1.mp4` (Monday 7:00 AM) → Wudan
  - `20200615_120000_1.mp4` (Monday 12:00 PM) → Regular Videos
  - `20200617_190000_1.mp4` (Wednesday 7:00 PM) → Wudan
- **Expected**: Correct routing based on pre-2021 rules
- **Validation**: Time range and day-of-week logic

#### 3.2 After 2021 Rules (Day-Specific)
- **Test Cases**:
  - `20250406_100000_1.mp4` (Sunday 10:00 AM) → Wudan
  - `20250407_070000_1.mp4` (Monday 7:00 AM) → Wudan  
  - `20250409_200000_1.mp4` (Wednesday 8:00 PM) → Wudan
  - `20250410_120000_1.mp4` (Thursday 12:00 PM) → Regular Videos
- **Expected**: Day-specific time rules applied correctly
- **Validation**: Complex after-2021 logic

#### 3.3 Edge Cases
- **Test Cases**:
  - `20210101_080000_1.mp4` (Boundary date - exactly 2021)
  - `20201231_235959_1.mp4` (Last day of 2020)
- **Expected**: Correct rule set applied
- **Validation**: Boundary condition handling

### 4. **AI Video Analysis Tests**

#### 4.1 Skip Analysis for Existing Files
- **Setup**: Video already exists in target folder
- **Test**: Run unified processor
- **Expected**: No AI analysis performed, no LLM API call
- **Validation**: Check logs for "skipping analysis" message

#### 4.2 AI Analysis for New Videos
- **Setup**: New video file not in target
- **Test**: Process with AI enabled
- **Expected**: Thumbnail extraction + AI analysis
- **Validation**: LLM API call logged, analysis results stored

#### 4.3 AI Analysis Failure Handling
- **Setup**: LM Studio not running or model not loaded
- **Test**: Process video with AI enabled
- **Expected**: Graceful failure, file still organized
- **Validation**: Error logged, file processing continues

#### 4.4 Dynamic Midpoint Extraction
- **Test Cases**:
  - Short video (10 seconds) → Extract at 5 seconds
  - Medium video (60 seconds) → Extract at 30 seconds  
  - Long video (300 seconds) → Extract at 150 seconds
- **Expected**: Midpoint calculation adapts to video length
- **Validation**: Correct timestamp calculation

### 5. **Folder Structure Tests**

#### 5.1 Custom Folder Matching
- **Setup**: Existing folders with suffixes
  - `2025_04_12_KungFuClass/`
  - `2025_06_15_BirthdayParty/`
- **Test**: Process files from those dates
- **Expected**: Files go to custom folders, not new standard folders
- **Validation**: Flexible folder matching works

#### 5.2 Missing Folder Creation
- **Setup**: Target date folder doesn't exist
- **Test**: Process file requiring new folder
- **Expected**: Create `YYYY_MM_DD/` folder automatically
- **Validation**: Folder creation with correct permissions

#### 5.3 Nested Folder Handling
- **Test**: Wudan videos in nested structure
- **Expected**: Correct routing to `Videos/Wudan/YYYY_MM_DD/`
- **Validation**: Nested path creation and organization

### 6. **Performance & Edge Cases**

#### 6.1 Large File Handling
- **Test**: Process very large video files (>100MB)
- **Expected**: Efficient processing without memory issues
- **Validation**: Memory usage monitoring, no crashes

#### 6.2 Corrupted File Handling
- **Test**: Process corrupted or incomplete video files
- **Expected**: Graceful error handling, continue processing
- **Validation**: Error logged, other files processed normally

#### 6.3 Network Drive Issues
- **Test**: Target on network drive that becomes unavailable
- **Expected**: Appropriate error handling and retry logic
- **Validation**: Network error detection and user notification

#### 6.4 Concurrent Processing
- **Test**: Multiple files processed simultaneously
- **Expected**: No file conflicts or race conditions
- **Validation**: Thread safety and file locking

### 7. **Configuration Tests**

#### 7.1 Invalid Configuration
- **Test**: Malformed YAML, missing required fields
- **Expected**: Clear error messages, graceful failure
- **Validation**: Configuration validation works

#### 7.2 Path Validation
- **Test**: Non-existent source/target paths
- **Expected**: Early detection and user notification
- **Validation**: Path existence checking

#### 7.3 Permission Issues
- **Test**: Read-only target directories
- **Expected**: Permission error detection and reporting
- **Validation**: File system permission handling

## 🧪 Test Execution Plan

### Phase 1: Setup Test Environment
1. Create test source directory with sample files
2. Set up target directory structure
3. Configure test-specific config.yaml
4. Prepare LM Studio with test model

### Phase 2: Execute Test Categories
1. Run each test category systematically
2. Document results and any failures
3. Identify logic issues requiring fixes
4. Validate expected vs actual behavior

### Phase 3: Fix and Retest
1. Address any identified issues
2. Refactor logic as needed
3. Re-run failed test cases
4. Ensure all tests pass

### Phase 4: Performance Validation
1. Test with realistic file volumes
2. Measure processing times
3. Validate memory usage
4. Confirm system stability

## 📊 Success Criteria

- ✅ All file naming conventions handled correctly
- ✅ Deduplication prevents unnecessary processing
- ✅ Wudan rules route videos accurately
- ✅ AI analysis only runs on new files
- ✅ Error conditions handled gracefully
- ✅ Performance meets expectations
- ✅ Configuration validation works
- ✅ Edge cases don't crash system
