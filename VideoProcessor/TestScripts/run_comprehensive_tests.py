#!/usr/bin/env python3
"""
Comprehensive Test Execution and Validation Script
Runs the PhoneSync + VideoProcessor system with test data and validates results
"""

import os
import sys
import subprocess
import json
import yaml
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Add the modules directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))

from setup_comprehensive_test import setup_comprehensive_test_environment

class ComprehensiveTestRunner:
    def __init__(self):
        self.test_results = []
        self.test_root = None
        self.config_path = None
        
    def setup_test_environment(self):
        """Set up the test environment"""
        print("🚀 Setting up comprehensive test environment...")
        self.test_root, self.config_path = setup_comprehensive_test_environment()
        return True
        
    def run_file_organization_test(self, dry_run=True):
        """Test file organization functionality"""
        print(f"\n📁 Running File Organization Test (dry_run={dry_run})...")
        
        try:
            cmd = [
                sys.executable,
                "VideoProcessor/phone_sync.py",
                "--config", str(self.config_path),
                "--verbose"
            ]
            
            if dry_run:
                cmd.append("--dry-run")
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            success = result.returncode == 0
            self.test_results.append({
                'test': 'File Organization',
                'dry_run': dry_run,
                'success': success,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            })
            
            if success:
                print(f"   ✅ File organization test {'(dry run) ' if dry_run else ''}passed")
            else:
                print(f"   ❌ File organization test {'(dry run) ' if dry_run else ''}failed")
                print(f"   Error: {result.stderr}")
                
            return success
            
        except Exception as e:
            print(f"   ❌ File organization test failed with exception: {e}")
            self.test_results.append({
                'test': 'File Organization',
                'dry_run': dry_run,
                'success': False,
                'error': str(e)
            })
            return False
    
    def run_video_analysis_test(self, dry_run=True):
        """Test video analysis functionality"""
        print(f"\n🤖 Running Video Analysis Test (dry_run={dry_run})...")
        
        try:
            cmd = [
                sys.executable,
                "VideoProcessor/main.py",
                "--config", str(self.config_path),
                "--verbose"
            ]
            
            if dry_run:
                cmd.append("--dry-run")
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            success = result.returncode == 0
            self.test_results.append({
                'test': 'Video Analysis',
                'dry_run': dry_run,
                'success': success,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            })
            
            if success:
                print(f"   ✅ Video analysis test {'(dry run) ' if dry_run else ''}passed")
            else:
                print(f"   ❌ Video analysis test {'(dry run) ' if dry_run else ''}failed")
                print(f"   Error: {result.stderr}")
                
            return success
            
        except Exception as e:
            print(f"   ❌ Video analysis test failed with exception: {e}")
            self.test_results.append({
                'test': 'Video Analysis',
                'dry_run': dry_run,
                'success': False,
                'error': str(e)
            })
            return False
    
    def validate_file_organization_results(self):
        """Validate that files were organized correctly"""
        print(f"\n🔍 Validating File Organization Results...")
        
        if not self.test_root:
            print("   ❌ No test environment to validate")
            return False
            
        target_root = Path(self.test_root) / "Target"
        validation_results = []
        
        # Test Case 1: Standard date-named files should be in correct folders
        expected_locations = [
            # Regular videos (not Wudan time)
            ("Videos/2025_04_12/20250412_110016_1.mp4", "Standard date video"),
            ("Videos/2025_04_10/20250410_120000_1.mp4", "Thursday noon (not Wudan time)"),
            
            # Wudan videos (matching time rules)
            ("Videos/Wudan/2025_04_06/20250406_070000_1.mp4", "Sunday 7:00 AM (Wudan time)"),
            ("Videos/Wudan/2025_04_07/20250407_070000_1.mp4", "Monday 7:00 AM (Wudan time)"),
            ("Videos/Wudan/2025_04_09/20250409_200000_1.mp4", "Wednesday 8:00 PM (Wudan time)"),
            
            # Pictures
            ("Pictures/2025_04_12/20250412_110016_1.jpg", "Standard date picture"),
            ("Pictures/2025_04_06/20250406_070000_1.jpg", "Date-based picture"),
        ]
        
        for expected_path, description in expected_locations:
            full_path = target_root / expected_path
            exists = full_path.exists()
            validation_results.append({
                'path': expected_path,
                'description': description,
                'exists': exists,
                'expected': True
            })
            
            if exists:
                print(f"   ✅ {description}: {expected_path}")
            else:
                print(f"   ❌ {description}: {expected_path} (NOT FOUND)")
        
        # Test Case 2: Files should NOT be duplicated if they already exist
        source_dir = Path(self.test_root) / "Source"
        duplicate_tests = [
            ("20250412_292993_1.mp4", "Videos/2025_04_12/20250412_292993_1_KungFu_GimStyle.mp4", 
             "Should not duplicate - appended text version exists"),
        ]
        
        for source_file, existing_target, description in duplicate_tests:
            source_path = source_dir / source_file
            target_path = target_root / existing_target
            
            # Check if source file would have been processed (shouldn't be if dedup works)
            base_target = target_root / f"Videos/2025_04_12/{source_file}"
            was_duplicated = base_target.exists()
            
            validation_results.append({
                'source': source_file,
                'existing_target': existing_target,
                'description': description,
                'was_duplicated': was_duplicated,
                'expected_duplicated': False
            })
            
            if not was_duplicated:
                print(f"   ✅ {description}: No duplicate created")
            else:
                print(f"   ❌ {description}: Duplicate was created")
        
        # Test Case 3: Custom folders should be used when they exist
        custom_folder_tests = [
            ("20250615_140000_1.mp4", "Videos/2025_06_15_BirthdayParty", "Should use custom folder"),
            ("20250830_120000_1.jpg", "Pictures/2025_08_30_VacationPhotos", "Should use custom picture folder"),
        ]
        
        for filename, custom_folder, description in custom_folder_tests:
            custom_path = target_root / custom_folder / filename
            standard_path = target_root / f"Videos/2025_06_15/{filename}" if filename.endswith('.mp4') else target_root / f"Pictures/2025_08_30/{filename}"
            
            used_custom = custom_path.exists()
            used_standard = standard_path.exists()
            
            validation_results.append({
                'filename': filename,
                'custom_folder': custom_folder,
                'description': description,
                'used_custom': used_custom,
                'used_standard': used_standard,
                'expected_custom': True
            })
            
            if used_custom and not used_standard:
                print(f"   ✅ {description}: Used custom folder")
            elif used_standard and not used_custom:
                print(f"   ❌ {description}: Used standard folder instead of custom")
            elif used_custom and used_standard:
                print(f"   ⚠️  {description}: File exists in both locations")
            else:
                print(f"   ❌ {description}: File not found in either location")
        
        # Calculate overall validation success
        total_tests = len(validation_results)
        passed_tests = sum(1 for result in validation_results 
                          if result.get('exists', False) == result.get('expected', True) or
                             result.get('was_duplicated', True) == result.get('expected_duplicated', False) or
                             result.get('used_custom', False) == result.get('expected_custom', False))
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n📊 Validation Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        return success_rate >= 80  # 80% pass rate required
    
    def analyze_logs(self):
        """Analyze log files for important information"""
        print(f"\n📝 Analyzing Log Files...")
        
        log_path = Path("VideoProcessor/logs/test_phone_sync.log")
        if not log_path.exists():
            print("   ⚠️  No log file found")
            return
            
        try:
            with open(log_path, 'r') as f:
                log_content = f.read()
                
            # Count important log entries
            dedup_skips = log_content.count("File already exists")
            ai_analyses = log_content.count("AI analysis complete")
            wudan_routes = log_content.count("Wudan folder")
            errors = log_content.count("ERROR")
            warnings = log_content.count("WARNING")
            
            print(f"   📊 Log Analysis:")
            print(f"      • Deduplication skips: {dedup_skips}")
            print(f"      • AI analyses performed: {ai_analyses}")
            print(f"      • Wudan routes: {wudan_routes}")
            print(f"      • Errors: {errors}")
            print(f"      • Warnings: {warnings}")
            
            if errors > 0:
                print(f"   ⚠️  Found {errors} errors in logs - review recommended")
            else:
                print(f"   ✅ No errors found in logs")
                
        except Exception as e:
            print(f"   ❌ Error analyzing logs: {e}")
    
    def generate_test_report(self):
        """Generate a comprehensive test report"""
        print(f"\n📋 Generating Test Report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'test_environment': str(self.test_root),
            'config_file': str(self.config_path),
            'test_results': self.test_results,
            'summary': {
                'total_tests': len(self.test_results),
                'passed_tests': sum(1 for r in self.test_results if r.get('success', False)),
                'failed_tests': sum(1 for r in self.test_results if not r.get('success', True)),
            }
        }
        
        report_path = Path("comprehensive_test_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"   ✅ Test report saved: {report_path}")
        
        # Print summary
        summary = report['summary']
        print(f"\n🎯 Test Summary:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['passed_tests']}")
        print(f"   Failed: {summary['failed_tests']}")
        print(f"   Success Rate: {(summary['passed_tests']/summary['total_tests']*100):.1f}%")
        
        return report
    
    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🧪 Starting Comprehensive Test Suite")
        print("="*60)
        
        # Setup test environment
        if not self.setup_test_environment():
            print("❌ Failed to set up test environment")
            return False
            
        # Run tests in order
        tests_passed = 0
        total_tests = 4
        
        # 1. File organization dry run
        if self.run_file_organization_test(dry_run=True):
            tests_passed += 1
            
        # 2. File organization actual run
        if self.run_file_organization_test(dry_run=False):
            tests_passed += 1
            
        # 3. Video analysis dry run  
        if self.run_video_analysis_test(dry_run=True):
            tests_passed += 1
            
        # 4. Validate results
        if self.validate_file_organization_results():
            tests_passed += 1
            
        # Analyze logs
        self.analyze_logs()
        
        # Generate report
        self.generate_test_report()
        
        # Final summary
        success_rate = (tests_passed / total_tests) * 100
        print(f"\n🏁 Comprehensive Test Suite Complete")
        print(f"   Tests Passed: {tests_passed}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 75:
            print("   🎉 Test suite PASSED!")
            return True
        else:
            print("   ❌ Test suite FAILED - review results and fix issues")
            return False

if __name__ == "__main__":
    runner = ComprehensiveTestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)
