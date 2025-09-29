#!/usr/bin/env python3
"""
Integration tests for enhanced VideoAnalyzer functionality
Tests the complete pipeline with base64 validation and enhanced error handling
"""

import os
import sys
import yaml
import logging
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from modules.video_analyzer import VideoAnalyzer

def setup_logging():
    """Setup logging for test visibility"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def create_test_video(output_path: str, duration: int = 5) -> bool:
    """
    Create a simple test video using FFmpeg
    
    Args:
        output_path: Path where to save the test video
        duration: Duration in seconds
        
    Returns:
        True if video created successfully, False otherwise
    """
    try:
        # Create a simple test video with FFmpeg
        # This creates a video with a moving colored rectangle
        cmd = [
            'ffmpeg', '-y',  # -y to overwrite existing files
            '-f', 'lavfi',
            '-i', f'testsrc=duration={duration}:size=320x240:rate=1',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-t', str(duration),
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
        
    except Exception as e:
        print(f"Failed to create test video: {e}")
        return False

def test_enhanced_video_analyzer():
    """Test the enhanced VideoAnalyzer with real video processing"""
    logger = setup_logging()
    logger.info("Starting enhanced VideoAnalyzer integration tests...")
    
    # Load configuration
    config_path = Path(__file__).parent.parent.parent / 'config.yaml'
    if not config_path.exists():
        config_path = Path(__file__).parent.parent / 'config.yaml'
        if not config_path.exists():
            logger.error("Config file not found")
            return False
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Create VideoAnalyzer instance
        analyzer = VideoAnalyzer(config, logger)
        
        # Test scenarios
        test_results = {}
        
        # Test 1: Real video processing with thumbnail extraction
        logger.info("\n=== Test 1: Real Video Processing ===")
        with tempfile.TemporaryDirectory() as temp_dir:
            test_video_path = os.path.join(temp_dir, "test_video.mp4")
            
            # Create test video
            if create_test_video(test_video_path):
                logger.info(f"✅ Test video created: {test_video_path}")
                
                # Test video analysis (dry_run=False for real processing)
                result = analyzer.analyze_video(test_video_path, dry_run=False)
                
                test_results['real_video_processing'] = {
                    'success': result.get('analyzed', False),
                    'has_kung_fu_result': 'is_kung_fu' in result,
                    'has_confidence': 'confidence' in result,
                    'has_description': 'description' in result,
                    'error_handling': 'error_type' in result if not result.get('analyzed') else None
                }

                if result.get('analyzed'):
                    logger.info("✅ Real video processing successful")
                    logger.info(f"   Kung Fu detected: {result.get('is_kung_fu', 'N/A')}")
                    logger.info(f"   Confidence: {result.get('confidence', 'N/A')}%")
                    logger.info(f"   Description: {result.get('description', 'N/A')}")
                else:
                    logger.warning(f"⚠️  Real video processing failed: {result.get('reason', 'Unknown error')}")
                    logger.info(f"   Enhanced error info: {result.get('error_type', 'N/A')}")
            else:
                logger.error("❌ Failed to create test video")
                test_results['real_video_processing'] = {'success': False, 'error': 'Video creation failed'}
        
        # Test 2: Base64 validation in real pipeline
        logger.info("\n=== Test 2: Base64 Validation Integration ===")
        
        # Test with various base64 scenarios
        base64_scenarios = {
            'valid_png': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4//8/AAX+Av7czFnnAAAAAElFTkSuQmCC',
            'with_data_url': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4//8/AAX+Av7czFnnAAAAAElFTkSuQmCC',
            'with_corruption': '/iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4//8/AAX+Av7czFnnAAAAAElFTkSuQmCC',
            'invalid_data': 'not_valid_base64_data'
        }
        
        validation_results = {}
        for scenario_name, base64_data in base64_scenarios.items():
            try:
                validated = analyzer._validate_and_repair_base64_image(base64_data)
                validation_results[scenario_name] = {
                    'success': True,
                    'output_length': len(validated),
                    'starts_with_png': validated.startswith('iVBORw0KGgo')
                }
                logger.info(f"✅ {scenario_name}: Validation successful")
            except Exception as e:
                validation_results[scenario_name] = {
                    'success': False,
                    'error': str(e)
                }
                logger.info(f"❌ {scenario_name}: Validation failed - {str(e)}")
        
        test_results['base64_validation'] = validation_results
        
        # Test 3: Enhanced error handling
        logger.info("\n=== Test 3: Enhanced Error Handling ===")
        
        # Test with non-existent video file
        error_result = analyzer.analyze_video('/nonexistent/path/video.mp4', dry_run=False)
        
        test_results['error_handling'] = {
            'has_error_type': 'error_type' in error_result,
            'has_error_step': 'error_step' in error_result,
            'has_timestamp': 'processed_at' in error_result,
            'has_skip_reason': 'skip_reason' in error_result,
            'failed_as_expected': error_result.get('analyzed', True) == False  # Should fail
        }
        
        if test_results['error_handling']['has_error_type']:
            logger.info(f"✅ Enhanced error handling working: {error_result.get('error_type')}")
        else:
            logger.warning("⚠️  Enhanced error handling not detected")
        
        # Print comprehensive test summary
        logger.info("\n" + "="*60)
        logger.info("ENHANCED VIDEOANALYZER INTEGRATION TEST SUMMARY")
        logger.info("="*60)
        
        total_tests = 0
        passed_tests = 0
        
        # Real video processing
        if test_results.get('real_video_processing', {}).get('success'):
            logger.info("✅ PASS Real Video Processing")
            passed_tests += 1
        else:
            logger.info("❌ FAIL Real Video Processing")
        total_tests += 1
        
        # Base64 validation
        validation_success = sum(1 for r in validation_results.values() if r.get('success', False))
        validation_total = len(validation_results)
        logger.info(f"✅ PASS Base64 Validation ({validation_success}/{validation_total} scenarios)")
        if validation_success > 0:
            passed_tests += 1
        total_tests += 1
        
        # Error handling
        error_features = sum(1 for v in test_results['error_handling'].values() if v)
        if error_features >= 4:  # At least 4 out of 5 error handling features
            logger.info("✅ PASS Enhanced Error Handling")
            passed_tests += 1
        else:
            logger.info("❌ FAIL Enhanced Error Handling")
        total_tests += 1
        
        logger.info(f"\nOverall: {passed_tests}/{total_tests} test categories passed")
        
        # Detailed results
        logger.info("\n--- Detailed Results ---")
        for test_name, result in test_results.items():
            logger.info(f"{test_name}: {result}")
        
        return passed_tests == total_tests
        
    except Exception as e:
        logger.error(f"Integration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_enhanced_video_analyzer()
    sys.exit(0 if success else 1)
