# 🏭 Production Deployment Guide

## 📋 Overview

This guide covers deploying the PhoneSync + VideoProcessor system to production with the correct folder structure and paths.

## 🌍 Environment Configuration

### Production Source Structure
The system will process files from these 10 subdirectories:
```
\\MA-2022-C\PHONESYNC\
├── Internal_dmc/
│   ├── Camera/
│   ├── FavoritesMA/
│   ├── GIF/
│   ├── Official/
│   └── Videocaptures/
└── SDCard_DMC/
    ├── Camera/
    ├── FavoritesMA/
    ├── GIF/
    ├── Official/
    └── Videocaptures/
```

### Production Target Structure
Files will be organized into:
- **📷 Images (jpg, png, gif)**: `\\MA-2022-C\UserData_G\My Pictures\YYYY_MM_DD\`
- **🎬 Videos (mp4, avi, mov)**: `\\MA-2022-C\UserData_G\My Videos\YYYY_MM_DD\`
- **🥋 Kung Fu Videos (AI detected)**: `\\MA-2022-C\UserData_G\My Videos\Wudan\YYYY_MM_DD\`

## 🚀 Deployment Steps

### 1. Environment Setup
```bash
# Clone/copy the project to production server
# Ensure Python 3.11+ and FFmpeg are installed
# Set up virtual environment (already done in development)
```

### 2. Switch to Production Environment
```bash
# Switch to production configuration
./venv/Scripts/python.exe VideoProcessor/switch_environment.py prod

# Verify production configuration
./venv/Scripts/python.exe VideoProcessor/switch_environment.py show
```

### 3. Test Production Configuration
```bash
# Test configuration without processing files
./venv/Scripts/python.exe VideoProcessor/test_production_config.py

# Dry run to verify paths (will fail if paths don't exist - that's expected)
./venv/Scripts/python.exe VideoProcessor/phone_sync.py --config config.yaml --dry-run --verbose
```

### 4. First Production Run
```bash
# IMPORTANT: First run will process ALL existing files
# This may take several hours for large collections
./venv/Scripts/python.exe VideoProcessor/phone_sync.py --config config.yaml --verbose

# Monitor progress in logs
tail -f VideoProcessor/logs/phonesync_YYYYMMDD.log
```

### 5. Daily Automation Setup
```bash
# Set up scheduled task/cron job for daily runs
# Subsequent runs will only process new files (enhanced incremental processing with validation)
./venv/Scripts/python.exe VideoProcessor/phone_sync.py --config config.yaml --verbose
```

## 📊 Production Monitoring

### Check Processing State
```bash
# View current processing state
./venv/Scripts/python.exe VideoProcessor/manage_processing_state.py show

# View recently processed files
./venv/Scripts/python.exe VideoProcessor/manage_processing_state.py files --limit 20

# View detailed statistics
./venv/Scripts/python.exe VideoProcessor/manage_processing_state.py stats
```

### Log Monitoring
```bash
# Check latest log file
ls -la VideoProcessor/logs/

# Monitor real-time processing
tail -f VideoProcessor/logs/phonesync_YYYYMMDD.log
```

## ⚠️ Important Production Notes

### First Run Considerations
- **Time**: First run may take 2-4 hours for 1000+ videos
- **Resources**: High CPU usage during AI video analysis
- **Storage**: Ensure sufficient space for organized files
- **Network**: UNC path access must be reliable

### Daily Operations
- **Speed**: Subsequent runs take 2-5 minutes for 5-10 new files
- **Automation**: Perfect for scheduled daily phone sync
- **Reliability**: Incremental processing prevents re-processing

### File Processing Rules
1. **Images**: All go to `My Pictures` with date folders
2. **Regular Videos**: Go to `My Videos` with date folders  
3. **Kung Fu Videos**: AI-detected videos go to `My Videos\Wudan` with date folders
4. **Notes**: Generated in same folder as videos (`YYYYMMDD_Notes.txt`)
5. **Custom Notes**: Existing user notes files are preserved

### Troubleshooting
```bash
# Reset processing state (forces full reprocessing)
./venv/Scripts/python.exe VideoProcessor/manage_processing_state.py reset

# Switch back to development for testing
./venv/Scripts/python.exe VideoProcessor/switch_environment.py dev

# Test individual components
./venv/Scripts/python.exe VideoProcessor/TestScripts/test_config_and_logging.py
```

## 🔧 Configuration Customization

### Modify Production Paths
Edit `config.yaml` PROD_VARS section:
```yaml
PROD_VARS:
  source_root: "\\\\YOUR-SERVER\\PHONESYNC"
  target_paths:
    pictures: "\\\\YOUR-SERVER\\UserData\\My Pictures"
    videos: "\\\\YOUR-SERVER\\UserData\\My Videos"
    wudan: "\\\\YOUR-SERVER\\UserData\\My Videos\\Wudan"
```

### AI Model Configuration
Ensure LM Studio is running with vision model:
```yaml
ai_analysis:
  api_url: "http://localhost:1234/v1/chat/completions"
  model: "your-vision-model-name"
```

## 📈 Performance Expectations

### First Run (1000 videos)
- **Processing Time**: 2-4 hours
- **AI Analysis**: ~10-15 seconds per video
- **File Organization**: ~1-2 seconds per file
- **Notes Generation**: ~5 seconds per video

### Daily Runs (10 new videos)
- **Processing Time**: 2-5 minutes
- **Incremental Detection**: Instant
- **New File Processing**: Same per-file times as first run

## ✅ Production Readiness Checklist

- [ ] Production paths accessible (`\\MA-2022-C\PHONESYNC` and `\\MA-2022-C\UserData_G`)
- [ ] Python 3.11+ installed with virtual environment
- [ ] FFmpeg installed and in PATH
- [ ] LM Studio running with vision model
- [ ] Environment switched to PRODUCTION
- [ ] Configuration tested with dry run
- [ ] First run completed successfully
- [ ] Daily automation scheduled
- [ ] Log monitoring set up
- [ ] Backup/recovery procedures in place

## 🎯 Success Metrics

After successful deployment, you should see:
- ✅ All 10 source subdirectories being scanned
- ✅ Files organized into date-based folders
- ✅ Kung Fu videos correctly identified and moved to Wudan folder
- ✅ Notes files generated with form names
- ✅ Incremental processing working (only new files processed)
- ✅ Processing state maintained between runs
- ✅ Logs showing successful operations

**Your PhoneSync + VideoProcessor system is now production-ready for handling hundreds or thousands of MP4s efficiently!** 🎉
