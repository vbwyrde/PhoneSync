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

### 4. **Enhanced AI Video Analysis Tests**

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

#### 4.5 Enhanced Base64 Validation Tests
- **Test Cases**:
  - **Valid PNG Data**: Standard base64 PNG thumbnail
  - **Data URL Prefix**: `data:image/png;base64,iVBORw0KGgo...`
  - **Leading Character Corruption**: `/iVBORw0KGgo...` (extra slash)
  - **Invalid Base64**: Completely corrupted data
- **Expected**: Automatic detection and repair of fixable corruption
- **Validation**: Only truly invalid data causes failures

#### 4.6 Enhanced Error Handling Tests
- **Test Cases**:
  - **Base64 Validation Failure**: Corrupted thumbnail data
  - **AI Analysis Failure**: LM Studio API errors
  - **FFmpeg Extraction Failure**: Video file corruption
- **Expected**: Structured error responses with categorization
- **Validation**: Error type, step, timestamp, and skip reason logged

#### 4.7 Production Reliability Tests
- **Test Cases**:
  - **Corrupted Video Files**: Files with damaged headers
  - **Network Interruption**: LM Studio connection issues
  - **Memory Pressure**: Large video file processing
- **Expected**: Graceful degradation without system crashes
- **Validation**: System continues processing other files

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

### 9. **Post-Processing Cleanup Tests** ⭐ **NEW**

#### 9.1 "NOT KUNG FU" Detection
- **Test Case**: Notes file with mixed kung fu and "NOT KUNG FU" entries
- **Expected**: Cleanup script identifies only "NOT KUNG FU" videos
- **Validation**: Correct parsing of notes file content

#### 9.2 Preview Mode Functionality
- **Test Case**: Run cleanup with `--preview` flag
- **Expected**: Shows what would be moved without making changes
- **Validation**: No actual file operations performed

#### 9.3 Cleanup Execution
- **Test Case**: Execute cleanup after preview validation
- **Expected**: Videos moved from Wudan to regular folders
- **Validation**: Files moved to correct date folders, notes updated

#### 9.4 Dry Run Mode
- **Test Case**: Run cleanup with `--execute --dry-run`
- **Expected**: Simulates operations without making changes
- **Validation**: Detailed logging without file modifications

#### 9.5 Notes File Updates
- **Test Case**: Cleanup videos with entries in date-based notes files
- **Expected**: "NOT KUNG FU" entries removed, kung fu entries preserved
- **Validation**: Notes files properly updated after cleanup

#### 9.6 Mixed Date Folders
- **Test Case**: Multiple date folders with varying numbers of "NOT KUNG FU" videos
- **Expected**: All misclassified videos identified and processed
- **Validation**: Comprehensive scanning across all Wudan date folders

### 10. **Test Environment Setup Tests** ⭐ **NEW**

#### 10.1 Mock Data Generation
- **Test Case**: `setup_test_environment.py --scenario mock_not_kungfu`
- **Expected**: Creates realistic test data with "NOT KUNG FU" notes
- **Validation**: Test files and notes created in correct format

#### 10.2 Test Scenario Variations
- **Test Case**: Different scenarios (clean, partial, mixed, mock_not_kungfu)
- **Expected**: Each scenario creates appropriate test conditions
- **Validation**: Correct files removed/created for each scenario

#### 10.3 Test Environment Isolation
- **Test Case**: Test scripts use development environment paths
- **Expected**: No impact on production data during testing
- **Validation**: All test operations confined to test directories

## 📊 Success Criteria

### Core System
- ✅ All file naming conventions handled correctly
- ✅ Deduplication prevents unnecessary processing
- ✅ Wudan rules route videos accurately
- ✅ AI analysis only runs on new files
- ✅ Error conditions handled gracefully
- ✅ Performance meets expectations
- ✅ Configuration validation works
- ✅ Edge cases don't crash system

### Post-Processing Cleanup ⭐ **NEW**
- ✅ "NOT KUNG FU" videos correctly identified in notes files
- ✅ Preview mode shows accurate cleanup plan
- ✅ Cleanup execution moves videos to correct folders
- ✅ Notes files properly updated after video movement
- ✅ Dry run mode simulates without making changes
- ✅ User validation workflow prevents accidental operations

### Test Environment ⭐ **NEW**
- ✅ Test setup scripts create realistic test conditions
- ✅ Mock data generation produces valid test scenarios
- ✅ Test environment isolation prevents production impact
- ✅ Multiple test scenarios support comprehensive validation
