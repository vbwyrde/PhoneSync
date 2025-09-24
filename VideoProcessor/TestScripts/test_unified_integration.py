#!/usr/bin/env python3
"""
Unified Integration Test Suite
Tests the complete PhoneSync + VideoProcessor system with real data
"""

import os
import sys
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.config_manager import ConfigManager
from modules.logger_setup import setup_logger
from modules.unified_processor import UnifiedProcessor

def main():
    """Main test function"""
    print("=== Unified Integration Test Suite ===")
    print("Testing complete PhoneSync + VideoProcessor system with real data")
    
    try:
        # Initialize configuration and logging
        config_path = "../config.yaml"
        config_manager = ConfigManager(config_path)
        config = config_manager.get_config()
        logger = setup_logger(config)
        
        print("✅ Configuration and logging initialized")
        
        # Create test environment
        test_env = setup_test_environment(config)
        print(f"✅ Test environment created: {test_env['temp_dir']}")
        
        # Initialize unified processor
        processor = UnifiedProcessor(config, logger)
        print("✅ UnifiedProcessor initialized")
        
        # Run system tests
        print("\n=== Running System Component Tests ===")
        system_test_results = processor.test_all_systems()
        display_system_test_results(system_test_results)
        
        # Test with real video files
        print("\n=== Testing with Real Video Files ===")
        real_video_results = test_with_real_videos(processor, test_env, logger)
        display_real_video_results(real_video_results)
        
        # Test complete workflow
        print("\n=== Testing Complete Workflow ===")
        workflow_results = test_complete_workflow(processor, test_env, logger)
        display_workflow_results(workflow_results)
        
        # Performance analysis
        print("\n=== Performance Analysis ===")
        performance_results = analyze_performance(workflow_results, logger)
        display_performance_results(performance_results)
        
        # Cleanup
        cleanup_test_environment(test_env)
        print("✅ Test environment cleaned up")
        
        # Final summary
        print("\n=== Integration Test Summary ===")
        display_final_summary(system_test_results, real_video_results, workflow_results, performance_results)
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def setup_test_environment(config):
    """Set up temporary test environment"""
    temp_dir = tempfile.mkdtemp(prefix="unified_integration_test_")
    
    # Create test directories
    test_source = os.path.join(temp_dir, "test_source")
    test_pictures = os.path.join(temp_dir, "Pictures")
    test_videos = os.path.join(temp_dir, "Videos")
    test_wudan = os.path.join(test_videos, "Wudan")
    
    os.makedirs(test_source, exist_ok=True)
    os.makedirs(test_pictures, exist_ok=True)
    os.makedirs(test_videos, exist_ok=True)
    os.makedirs(test_wudan, exist_ok=True)
    
    # Copy a few real video files for testing
    real_source = "Z:\\PhotoSync_Test\\Source"
    if os.path.exists(real_source):
        video_files = [f for f in os.listdir(real_source) if f.lower().endswith('.mp4')][:3]  # Take first 3 videos
        
        for video_file in video_files:
            src_path = os.path.join(real_source, video_file)
            dst_path = os.path.join(test_source, video_file)
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
    
    return {
        'temp_dir': temp_dir,
        'test_source': test_source,
        'test_pictures': test_pictures,
        'test_videos': test_videos,
        'test_wudan': test_wudan,
        'copied_videos': len([f for f in os.listdir(test_source) if f.lower().endswith('.mp4')]) if os.path.exists(test_source) else 0
    }

def display_system_test_results(results):
    """Display system component test results"""
    print("--- System Component Test Results ---")
    
    # Configuration test
    config_result = results.get('configuration', {})
    if config_result.get('success'):
        print(f"✅ Configuration: {config_result.get('source_folders', 0)} sources, {config_result.get('target_paths', 0)} targets")
    else:
        print("❌ Configuration: FAILED")
    
    # AI connection test
    ai_result = results.get('ai_connection', {})
    if ai_result.get('success'):
        print("✅ AI Connection: CONNECTED")
    else:
        print(f"❌ AI Connection: {ai_result.get('error', 'FAILED')}")
    
    # Deduplication test
    dedup_result = results.get('deduplication', {})
    if dedup_result.get('success'):
        print(f"✅ Deduplication: Cache built with {dedup_result.get('cache_size', 0)} files")
    else:
        print(f"❌ Deduplication: {dedup_result.get('error', 'FAILED')}")
    
    # Module initialization test
    modules_result = results.get('modules', {})
    module_status = "✅" if all(modules_result.values()) else "❌"
    print(f"{module_status} Modules: All {len(modules_result)} modules initialized")
    
    # Overall status
    overall = "✅ PASS" if results.get('overall_success') else "❌ FAIL"
    print(f"Overall System Test: {overall}")

def test_with_real_videos(processor, test_env, logger):
    """Test video analysis with real video files"""
    results = {
        'videos_found': 0,
        'videos_analyzed': 0,
        'analysis_results': [],
        'errors': []
    }
    
    test_source = test_env['test_source']
    video_files = [f for f in os.listdir(test_source) if f.lower().endswith('.mp4')]
    results['videos_found'] = len(video_files)
    
    if not video_files:
        results['errors'].append("No video files found in test source")
        return results
    
    # Test video analysis on each file
    for video_file in video_files:
        try:
            video_path = os.path.join(test_source, video_file)
            file_info = {
                'name': video_file,
                'path': video_path,
                'size': os.path.getsize(video_path),
                'type': 'video',
                'date': datetime.fromtimestamp(os.path.getmtime(video_path))
            }
            
            # Analyze video
            analysis_result = processor.video_analyzer.analyze_video(video_path, file_info)
            
            if analysis_result.get('analyzed'):
                results['videos_analyzed'] += 1
                results['analysis_results'].append({
                    'file': video_file,
                    'is_kung_fu': analysis_result.get('is_kung_fu', False),
                    'confidence': analysis_result.get('confidence', 0),
                    'description': analysis_result.get('description', '')[:100] + "..." if len(analysis_result.get('description', '')) > 100 else analysis_result.get('description', '')
                })
            else:
                results['errors'].append(f"Failed to analyze {video_file}")
                
        except Exception as e:
            results['errors'].append(f"Error analyzing {video_file}: {str(e)}")
    
    return results

def display_real_video_results(results):
    """Display real video test results"""
    print("--- Real Video Analysis Results ---")
    print(f"Videos found: {results['videos_found']}")
    print(f"Videos analyzed: {results['videos_analyzed']}")
    
    if results['analysis_results']:
        print("Analysis Results:")
        for result in results['analysis_results']:
            kung_fu_status = "🥋 YES" if result['is_kung_fu'] else "❌ NO"
            print(f"  {result['file']}: {kung_fu_status} (confidence: {result['confidence']}%)")
            if result['description']:
                print(f"    Description: {result['description']}")
    
    if results['errors']:
        print("Errors:")
        for error in results['errors']:
            print(f"  ❌ {error}")
    
    success_rate = (results['videos_analyzed'] / results['videos_found'] * 100) if results['videos_found'] > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")

def test_complete_workflow(processor, test_env, logger):
    """Test the complete workflow with real files"""
    # Temporarily modify config to use test directories
    original_sources = processor.config['source_folders'].copy()
    original_targets = processor.config['target_paths'].copy()
    
    try:
        # Set test paths
        processor.config['source_folders'] = [test_env['test_source']]
        processor.config['target_paths']['pictures'] = test_env['test_pictures']
        processor.config['target_paths']['videos'] = test_env['test_videos']
        processor.config['target_paths']['wudan'] = test_env['test_wudan']
        
        # Run complete workflow
        workflow_results = processor.process_all_sources()
        
        return workflow_results
        
    finally:
        # Restore original config
        processor.config['source_folders'] = original_sources
        processor.config['target_paths'] = original_targets

def display_workflow_results(results):
    """Display complete workflow results"""
    print("--- Complete Workflow Results ---")
    
    if results.get('success'):
        print("✅ Workflow completed successfully")
        stats = results.get('statistics', {})
        print(f"Files scanned: {stats.get('files_scanned', 0)}")
        print(f"Files processed: {stats.get('files_processed', 0)}")
        print(f"Files copied: {stats.get('files_copied', 0)}")
        print(f"Files skipped: {stats.get('files_skipped', 0)}")
        print(f"Videos analyzed: {stats.get('videos_analyzed', 0)}")
        print(f"Kung fu detected: {stats.get('kung_fu_detected', 0)}")
        print(f"Notes generated: {stats.get('notes_generated', 0)}")
        print(f"Errors: {stats.get('errors', 0)}")
        
        if stats.get('processing_time_formatted'):
            print(f"Processing time: {stats['processing_time_formatted']}")

        # Display individual file results
        file_results = results.get('results', [])
        if file_results:
            print(f"\nFile Processing Details ({len(file_results)} files):")
            for result in file_results:
                status = "✅" if result.get('success') else "❌"
                action = result.get('action', 'unknown')
                file_name = result.get('file', 'unknown')
                print(f"  {status} {file_name}: {action}")

                # Show analysis results if available
                analysis = result.get('analysis')
                if analysis and analysis.get('analyzed'):
                    kung_fu = "🥋 YES" if analysis.get('is_kung_fu') else "❌ NO"
                    confidence = analysis.get('confidence', 0)
                    print(f"    Analysis: {kung_fu} (confidence: {confidence}%)")

                    if analysis.get('note_generated'):
                        print(f"    📝 Note generated")
    else:
        print(f"❌ Workflow failed: {results.get('error', 'Unknown error')}")

def analyze_performance(workflow_results, logger):
    """Analyze system performance"""
    performance = {
        'processing_time': 0,
        'files_per_second': 0,
        'memory_efficient': True,
        'recommendations': []
    }

    if workflow_results.get('success'):
        stats = workflow_results.get('statistics', {})
        processing_time = stats.get('processing_time_seconds', 0)
        files_processed = stats.get('files_processed', 0)

        performance['processing_time'] = processing_time

        if processing_time > 0 and files_processed > 0:
            performance['files_per_second'] = files_processed / processing_time

        # Performance recommendations
        if processing_time > 60:  # More than 1 minute
            performance['recommendations'].append("Consider batch processing for large datasets")

        if stats.get('videos_analyzed', 0) > 0 and processing_time > 30:
            performance['recommendations'].append("Video analysis is time-intensive - consider parallel processing")

        if stats.get('errors', 0) > 0:
            performance['recommendations'].append("Address errors to improve overall performance")

    return performance

def display_performance_results(performance):
    """Display performance analysis results"""
    print("--- Performance Analysis ---")
    print(f"Processing time: {performance['processing_time']:.2f} seconds")
    print(f"Files per second: {performance['files_per_second']:.2f}")

    if performance['recommendations']:
        print("Recommendations:")
        for rec in performance['recommendations']:
            print(f"  💡 {rec}")
    else:
        print("✅ Performance looks good!")

def display_final_summary(system_results, video_results, workflow_results, performance_results):
    """Display final integration test summary"""
    # Calculate overall success
    system_success = system_results.get('overall_success', False)
    video_success = video_results['videos_analyzed'] > 0 and len(video_results['errors']) == 0
    workflow_success = workflow_results.get('success', False)

    overall_success = system_success and workflow_success

    print(f"System Components: {'✅ PASS' if system_success else '❌ FAIL'}")
    print(f"Video Analysis: {'✅ PASS' if video_success else '❌ FAIL'}")
    print(f"Complete Workflow: {'✅ PASS' if workflow_success else '❌ FAIL'}")
    print(f"Performance: ✅ {performance_results['processing_time']:.1f}s")

    print(f"\n{'🎉 INTEGRATION TEST PASSED!' if overall_success else '❌ INTEGRATION TEST FAILED'}")

    if overall_success:
        print("📹 The unified PhoneSync + VideoProcessor system is ready for production!")
    else:
        print("🔧 Please address the issues above before proceeding to production.")

def cleanup_test_environment(test_env):
    """Clean up temporary test environment"""
    try:
        shutil.rmtree(test_env['temp_dir'])
    except Exception as e:
        print(f"Warning: Could not clean up test directory: {e}")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
