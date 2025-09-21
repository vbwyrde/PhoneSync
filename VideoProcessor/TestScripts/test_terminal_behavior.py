#!/usr/bin/env python3
"""
Diagnostic test to understand terminal vs subprocess behavior
"""

import subprocess
import sys
import os
from pathlib import Path

def test_subprocess_behavior():
    """Test various subprocess approaches"""
    print("=== Subprocess Behavior Diagnostic ===")
    
    commands_to_test = [
        ['ffmpeg', '-version'],
        ['python', '--version'],
        ['echo', 'Hello World'],
        ['ls', '-la']  # bash command
    ]
    
    for cmd in commands_to_test:
        print(f"\nTesting command: {' '.join(cmd)}")
        
        try:
            # Method 1: Basic subprocess.run
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            print(f"  Return code: {result.returncode}")
            if result.returncode == 0:
                output_preview = result.stdout[:100].replace('\n', ' ') if result.stdout else "No output"
                print(f"  Output preview: {output_preview}")
            else:
                error_preview = result.stderr[:100].replace('\n', ' ') if result.stderr else "No error message"
                print(f"  Error preview: {error_preview}")
                
        except subprocess.TimeoutExpired:
            print("  ❌ Command timed out")
        except FileNotFoundError:
            print("  ❌ Command not found")
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")

def test_ffmpeg_specific():
    """Test FFmpeg-specific functionality"""
    print("\n=== FFmpeg Specific Tests ===")
    
    # Test 1: Version check
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg version: {version_line}")
        else:
            print(f"❌ FFmpeg version check failed: {result.returncode}")
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"❌ FFmpeg version test error: {e}")
    
    # Test 2: Simple format list (quick command)
    try:
        result = subprocess.run(['ffmpeg', '-formats'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            format_count = len([line for line in result.stdout.split('\n') if 'E' in line or 'D' in line])
            print(f"✅ FFmpeg formats available: ~{format_count} formats")
        else:
            print(f"❌ FFmpeg formats check failed: {result.returncode}")
    except Exception as e:
        print(f"❌ FFmpeg formats test error: {e}")
    
    # Test 3: Codec list (another quick command)
    try:
        result = subprocess.run(['ffmpeg', '-codecs'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            codec_count = len([line for line in result.stdout.split('\n') if 'DEV' in line or 'D.V' in line])
            print(f"✅ FFmpeg codecs available: ~{codec_count} codecs")
        else:
            print(f"❌ FFmpeg codecs check failed: {result.returncode}")
    except Exception as e:
        print(f"❌ FFmpeg codecs test error: {e}")

def test_environment_info():
    """Test environment information"""
    print("\n=== Environment Information ===")
    
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"PATH environment variable:")
    
    path_env = os.environ.get('PATH', '')
    path_parts = path_env.split(os.pathsep)
    
    # Look for FFmpeg in PATH
    ffmpeg_paths = [p for p in path_parts if 'ffmpeg' in p.lower()]
    if ffmpeg_paths:
        print(f"  FFmpeg paths found in PATH: {ffmpeg_paths}")
    else:
        print("  No obvious FFmpeg paths in PATH")
    
    # Check if ffmpeg executable exists in common locations
    common_ffmpeg_paths = [
        'C:/ffmpeg/bin/ffmpeg.exe',
        'C:/Program Files/ffmpeg/bin/ffmpeg.exe',
        '/usr/bin/ffmpeg',
        '/usr/local/bin/ffmpeg'
    ]
    
    for path in common_ffmpeg_paths:
        if Path(path).exists():
            print(f"  Found FFmpeg at: {path}")
            break
    else:
        print("  FFmpeg not found in common locations")

def test_shell_vs_subprocess():
    """Compare shell execution vs subprocess"""
    print("\n=== Shell vs Subprocess Comparison ===")
    
    # Test with shell=True
    try:
        result = subprocess.run('ffmpeg -version', 
                              shell=True, capture_output=True, text=True, timeout=10)
        print(f"Shell=True result: Return code {result.returncode}")
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0] if result.stdout else "No output"
            print(f"  Output: {version_line}")
    except Exception as e:
        print(f"Shell=True error: {e}")
    
    # Test with shell=False (list format)
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              shell=False, capture_output=True, text=True, timeout=10)
        print(f"Shell=False result: Return code {result.returncode}")
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0] if result.stdout else "No output"
            print(f"  Output: {version_line}")
    except Exception as e:
        print(f"Shell=False error: {e}")

def main():
    """Main diagnostic function"""
    print("=== Terminal Behavior Diagnostic Suite ===")
    print("This will help us understand why direct commands fail but subprocess works")
    
    test_environment_info()
    test_subprocess_behavior()
    test_shell_vs_subprocess()
    test_ffmpeg_specific()
    
    print("\n=== Diagnostic Complete ===")
    print("This information will help us understand the terminal behavior patterns.")

if __name__ == "__main__":
    main()
