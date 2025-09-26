# VideoProcessor Scripts

**Additional utility and testing scripts for the PhoneSync + VideoProcessor system**

This folder contains supplementary scripts that are not part of the core system but provide useful functionality for testing, analysis, and system management.

## 📁 Script Descriptions

### **🧪 Testing Scripts**

#### `production_dry_run_test.py`
**Purpose**: Test file organization with production configuration without AI analysis

**Features**:
- Temporarily switches to production environment
- Disables AI analysis for faster testing
- Limits processing to specified number of days (default: 20)
- Runs in dry-run mode (no actual file operations)
- Provides detailed preview of organization plan
- Automatically restores original configuration

**Usage**:
```bash
# Test with default 20 days
./venv/Scripts/python.exe VideoProcessor/Scripts/production_dry_run_test.py

# Test with custom number of days
./venv/Scripts/python.exe VideoProcessor/Scripts/production_dry_run_test.py --days 10

# Verbose output
./venv/Scripts/python.exe VideoProcessor/Scripts/production_dry_run_test.py --verbose
```

#### `test_incremental_processing.py`
**Purpose**: Test the incremental processing functionality

**Features**:
- Tests first run vs subsequent runs
- Validates file filtering logic
- Tests state management
- Verifies reset functionality

**Usage**:
```bash
./venv/Scripts/python.exe VideoProcessor/Scripts/test_incremental_processing.py
```

#### `test_production_config.py`
**Purpose**: Validate environment-based configuration system

**Features**:
- Tests development configuration
- Tests production configuration (temporarily)
- Validates path resolution
- Checks configuration switching

**Usage**:
```bash
./venv/Scripts/python.exe VideoProcessor/Scripts/test_production_config.py
```

### **🔧 Utility Scripts**

#### `main.py`
**Purpose**: Alternative entry point with unified processing

**Features**:
- Combines file organization and video analysis
- Built-in system testing
- JSON output support
- Alternative to phone_sync.py

**Usage**:
```bash
# Run full processing
./venv/Scripts/python.exe VideoProcessor/Scripts/main.py

# Run system tests
./venv/Scripts/python.exe VideoProcessor/Scripts/main.py --test

# Dry run mode
./venv/Scripts/python.exe VideoProcessor/Scripts/main.py --dry-run
```

#### `analyze_existing_videos.py`
**Purpose**: Analyze existing videos that don't have notes files yet

**Features**:
- Finds videos without corresponding notes files
- Runs AI analysis on existing videos
- Generates missing notes files
- Useful for retroactive analysis

**Usage**:
```bash
./venv/Scripts/python.exe VideoProcessor/Scripts/analyze_existing_videos.py
```

### **🧪 Test Setup Scripts**

#### `setup_edge_case_test.py`
**Purpose**: Set up edge case testing scenarios

**Features**:
- Creates various test conditions
- Tests handling of existing non-standard notes files
- Tests missing folder creation
- Tests partial file sets in existing folders
- Creates mixed scenarios for comprehensive testing

**Usage**:
```bash
./venv/Scripts/python.exe VideoProcessor/Scripts/setup_edge_case_test.py
```

## 🚀 Quick Start Guide

### **For Production Testing**
```bash
# Quick production dry run test (20 days)
./venv/Scripts/python.exe VideoProcessor/Scripts/production_dry_run_test.py

# Extended production test (30 days)
./venv/Scripts/python.exe VideoProcessor/Scripts/production_dry_run_test.py --days 30
```

### **For Development Testing**
```bash
# Test incremental processing
./venv/Scripts/python.exe VideoProcessor/Scripts/test_incremental_processing.py

# Test configuration system
./venv/Scripts/python.exe VideoProcessor/Scripts/test_production_config.py
```

### **For Retroactive Analysis**
```bash
# Analyze existing videos without notes
./venv/Scripts/python.exe VideoProcessor/Scripts/analyze_existing_videos.py
```

## 📋 Script Dependencies

All scripts require:
- Python 3.11+
- Virtual environment activated
- Core system modules in `../modules/`
- Valid `config.yaml` in project root

### **Additional Dependencies by Script**:

- **production_dry_run_test.py**: tempfile, pathlib
- **test_incremental_processing.py**: datetime, json
- **test_production_config.py**: tempfile, yaml manipulation
- **main.py**: unified_processor module
- **analyze_existing_videos.py**: video_analyzer, notes_generator
- **setup_edge_case_test.py**: shutil, random

## ⚠️ Important Notes

### **Configuration Safety**
- `production_dry_run_test.py` creates temporary configs and restores originals
- `test_production_config.py` uses temporary files to avoid modifying main config
- Always verify your `config.yaml` after running tests

### **File System Safety**
- Most scripts run in dry-run mode by default
- `setup_edge_case_test.py` modifies test directories - use with caution
- Always backup important data before running test setup scripts

### **Production Environment**
- `production_dry_run_test.py` is specifically designed for safe production testing
- It never modifies actual files (dry-run only)
- Automatically switches back to original environment

## 🔗 Related Documentation

- **Main System**: See `../README.md` for core system usage
- **Process Flow**: See `../../Documentation/ProcessFlow.md` for technical details
- **Test Scripts**: See `../TestScripts/README.md` for comprehensive testing

---

*These scripts complement the main PhoneSync + VideoProcessor system and provide additional functionality for testing, analysis, and system management.*
