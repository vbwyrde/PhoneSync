# Augment Guidelines - PhoneSync Project

## 📋 **Core Guidelines**

### 1. **Always Check Guidelines First**
Before making any major change or addition to the codebase, **ALWAYS** review this Augment-Guidelines file to ensure consistency with established patterns and avoid repeating solved problems.

### 2. **Document New Discoveries**
Whenever new information, solutions, or patterns come to light during development, **ALWAYS** add clear, concise instructions to the appropriate category in this file. This prevents future repetition of trial-and-error processes.

---

## 🖥️ **Windows Development Environment**

### **Bash Shell on Windows**
- **Environment**: The development environment uses bash shell on Windows (likely Git Bash or WSL)
- **Virtual Environment Activation**: Use `source venv/Scripts/activate` (NOT `venv\Scripts\activate.bat`)
- **Directory Creation**: Use Python commands or bash commands, avoid Windows-specific commands
- **Path Separators**: Use forward slashes `/` in bash commands, backslashes `\` in Windows paths within Python

**Example Commands:**
```bash
# Virtual environment activation
source venv/Scripts/activate

# Python directory operations
python -c "import os; os.makedirs('TestScripts', exist_ok=True)"

# File operations
python -c "import shutil; shutil.move('source.py', 'target/source.py')"
```

---

## 📁 **Project Structure Standards**

### **Test Organization**
- **All test scripts** must be placed in the `TestScripts/` folder
- **No test files** should be created in the root or main source directories
- **Test naming**: Use descriptive names like `test_lm_studio.py`, `test_ffmpeg.py`

### **Directory Structure**
```
PhoneSync/                          # Root project directory
├── Augment-Guidelines.md          # This file - project guidelines
├── PhoneSync.ps1                  # Original PowerShell script
├── config.json                    # Original configuration
├── README.md                      # Project documentation
└── VideoProcessor/                # Python implementation
    ├── venv/                      # Virtual environment
    ├── TestScripts/               # All test scripts go here
    ├── config.yaml               # Unified YAML configuration
    ├── phone_sync.py             # Main unified script
    ├── requirements.txt          # Python dependencies
    ├── logs/                     # Log files with rotation
    └── tests/                    # Unit tests for components
```

---

## 🐍 **Python Development Standards**

### **Dependency Management**
- **Always use package managers** for dependency installation
- **Never manually edit** requirements.txt - use `pip freeze > requirements.txt`
- **Virtual environment required** for all Python development

### **Code Organization**
- **Modular design**: Separate concerns into distinct modules
- **Configuration-driven**: Use YAML for all configuration
- **Comprehensive logging**: Log both process flow and errors
- **Error handling**: Graceful failure recovery with detailed logging

---

## 🔧 **Development Workflow**

### **Phase-Based Development**
1. **Environment Setup**: Virtual environment, dependencies, connectivity tests
2. **Core Logic Conversion**: Convert PowerShell logic to Python
3. **Integration**: Combine file organization with video analysis
4. **Testing**: Unit tests and end-to-end validation
5. **Deployment**: Scheduling and production setup

### **Testing Strategy**
- **Test early and often**: Create test scripts for each major component
- **Incremental validation**: Test each phase before proceeding
- **End-to-end testing**: Validate complete workflow with test data

---

## 🚀 **Deployment Standards**

### **Windows Task Scheduler Integration**
- **Batch wrapper required**: Create `.bat` file for Task Scheduler
- **Path handling**: Use absolute paths in production scripts
- **Error logging**: Ensure all errors are captured in log files

---

## 📝 **Documentation Standards**

### **Code Documentation**
- **Docstrings required** for all functions and classes
- **Inline comments** for complex logic
- **Configuration examples** in documentation

### **Change Documentation**
- **Update guidelines** when new patterns are established
- **Document workarounds** and their reasons
- **Maintain version history** of major changes

---

## ⚠️ **Common Pitfalls to Avoid**

### **Environment Issues**
- **Don't assume Windows CMD**: Environment uses bash shell
- **Don't use Windows-specific commands** without testing
- **Always activate virtual environment** before Python operations
- **Terminal interruptions**: Some commands may get interrupted (Ctrl+C behavior) - use simpler test approaches first
- **Direct vs Python subprocess**: Direct terminal commands may fail (return code 130) while Python subprocess.run() works perfectly
- **FFmpeg behavior**: FFmpeg works through Python subprocess but may not work in direct bash commands

### **Critical Terminal Display Issue - SOLUTION**
- **Return code 130 does NOT mean failure**: Commands may show return code 130 but actually execute successfully
- **ALWAYS use `read-terminal` tool**: When seeing return code 130, immediately use `read-terminal` to see actual output
- **Don't ask user for confirmation**: Use the `read-terminal` tool instead of asking user to provide terminal output
- **Terminal shows real results**: The `read-terminal` tool shows the actual execution results, not the launch-process response
- **Simple workflow**: launch-process → see code 130 → immediately call read-terminal → see real results

### **FFmpeg Issues**
- **Check FFmpeg installation**: FFmpeg may not be installed or in PATH
- **Test availability first**: Always test `ffmpeg -version` before complex operations
- **Alternative approaches**: Consider using online FFmpeg or bundled solutions if system FFmpeg unavailable

### **File Operations**
- **Test file paths** on target system before deployment
- **Handle path separators** correctly for cross-platform compatibility
- **Validate permissions** for source and target directories

---

## 🔄 **Update Process**

When adding new guidelines:
1. **Identify the category** or create a new one if needed
2. **Write clear, actionable instructions**
3. **Include examples** where helpful
4. **Test the guidance** before documenting
5. **Update table of contents** if adding new sections

---

*Last Updated: 2025-09-21*
*Version: 1.0*
