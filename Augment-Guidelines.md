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

### **Python Bytecode Cache Management**
- **Cache Issues**: Python creates `.pyc` files and `__pycache__` directories that can cause outdated code to run
- **Symptoms**: Code changes not taking effect, old methods being called, import errors after updates
- **Solution**: Clear cache when code changes don't take effect:
  ```bash
  # Clear all Python cache files
  find VideoProcessor -name "*.pyc" -delete
  find VideoProcessor -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

  # Alternative single command
  rm -rf VideoProcessor/modules/__pycache__ && find VideoProcessor -name "*.pyc" -delete
  ```
- **When to Clear Cache**:
  - After major code changes or refactoring
  - When seeing "method not found" errors for recently added methods
  - When system appears to use old code despite file updates
  - Before running critical production processes after code changes
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

### **Unicode Character Usage**
- **Avoid Unicode characters** (emojis, special symbols) in documentation and scripts unless logically required
- **Use ASCII alternatives**: Replace emojis with descriptive text or simple symbols
- **Reason**: Unicode characters can cause encoding issues, display problems across different systems, and compatibility issues
- **Exception**: Only use Unicode when functionally necessary (e.g., processing international text data)

**Examples:**
```markdown
# Good - ASCII only
## Key Features
- Smart File Organization
- AI Video Analysis

# Avoid - Unicode characters
## 🔧 Key Features
- 📁 Smart File Organization
- 🤖 AI Video Analysis
```

### **Change Documentation**
- **Update guidelines** when new patterns are established
- **Document workarounds** and their reasons
- **Maintain version history** of major changes

---

## 🛡️ **Code Enhancement & Replacement Safety**

### **Before Replacing or "Enhancing" Existing Code**

**Critical Rule**: Existing production code may be more sophisticated than it initially appears. Always fully understand what you're replacing before making changes.

#### **1. Read ALL Existing Code Completely**
- **Don't make assumptions** based on partial reading or similar-looking code elsewhere
- **Use `view` with full file ranges** or search patterns to see complete implementations
- **Pay special attention** to multi-line configurations, prompts, and complex logic
- **Read to the end** - important details are often at the end of functions/configurations

#### **2. Understand Current Implementation Sophistication**
- **Newer/current code may be more advanced** than older code you're comparing it to
- **Check git history or file dates** when possible to understand code evolution
- **Look for signs of production refinement**: detailed error handling, specific edge cases, comprehensive instructions
- **Production code often has hidden complexity** developed through real-world usage

#### **3. Perform Thorough Comparison Analysis**
- **Don't assume "enhancement" code is actually better**
- **List specific features/capabilities of BOTH versions** side by side
- **Identify what would be gained vs. lost** in any replacement
- **Consider that production code may have been refined** through user feedback and edge case handling

#### **4. Validate the Improvement Hypothesis**
Before proceeding with changes:
- **Clearly articulate what specific problem** the change solves
- **Confirm the "enhancement" actually adds value** rather than removing sophisticated features
- **Get user confirmation** when replacing sophisticated existing implementations
- **Question whether the change is truly an improvement**

#### **5. When in Doubt, Ask First**
If you're unsure whether existing code is sophisticated or needs improvement:
- **Present your analysis to the user** before making changes
- **Explain what you found** and ask for guidance
- **Don't assume older-looking code is inferior**
- **Admit uncertainty** rather than making potentially harmful changes

**Example of Near-Miss**: Almost replacing a sophisticated AI prompt with detailed text extraction instructions, structured response format, and fallback handling with a basic generic prompt, which would have significantly degraded application performance.

---

## 🧪 **Testing and Dry-Run Guidelines**

### **CRITICAL: No Fake Results in Tests**

**Never create dummy/fake results in dry-run or test modes that make tests pass without actually validating functionality.**

#### **Prohibited Practices**
- ❌ **Hardcoded Success Results**: Returning `success: True` with fake data in dry-run mode
- ❌ **Dummy Data**: Providing fake confidence scores, descriptions, or analysis results
- ❌ **Simulated Success**: Making tests pass without exercising the actual code paths
- ❌ **Fake Validations**: Returning positive results without performing real validation

#### **Correct Approaches**
- ✅ **Skip with Clear Reason**: Return `analyzed: False, reason: 'Dry run mode - analysis skipped'`
- ✅ **Caller Control**: Let the calling code decide whether to invoke the function or not
- ✅ **Real Testing**: Use actual test data and real function calls when testing functionality
- ✅ **Honest Results**: Always return truthful results about what was actually performed

#### **Why This Matters**
Fake results in tests create a false sense of security and hide real bugs that only surface in production. Tests should validate actual functionality, not just code paths.

**Example of Bad Practice**:
```python
if dry_run:
    return {'analyzed': True, 'is_kung_fu': False, 'confidence': 0.5}  # FAKE!
```

**Example of Good Practice**:
```python
if dry_run:
    return {'analyzed': False, 'reason': 'Dry run mode - analysis skipped'}
```

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

*Last Updated: 2025-09-26*
*Version: 1.1*
