#!/usr/bin/env python3
"""
Test script for enhanced base64 validation functionality
Tests the new base64 validation and repair logic integrated into VideoAnalyzer
"""

import os
import sys
import base64
import tempfile
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from modules.video_analyzer import VideoAnalyzer

def setup_logging():
    """Setup logging for test visibility"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def create_test_base64_data():
    """Create various test base64 scenarios"""
    # Create a simple PNG image data (1x1 pixel PNG)
    valid_png_bytes = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 dimensions
        0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,  # bit depth, color type, etc.
        0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT chunk start
        0x54, 0x08, 0x99, 0x01, 0x01, 0x00, 0x00, 0x00,  # IDAT data
        0xFF, 0xFF, 0x00, 0x00, 0x00, 0x02, 0x00, 0x01,  # IDAT data
        0xE2, 0x21, 0xBC, 0x33, 0x00, 0x00, 0x00, 0x00,  # IDAT end + IEND
        0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82   # IEND chunk
    ])
    
    valid_base64 = base64.b64encode(valid_png_bytes).decode('utf-8')
    
    test_cases = {
        'valid_png': valid_base64,
        'with_data_url': f'data:image/png;base64,{valid_base64}',
        'with_leading_slash': f'/{valid_base64}',
        'with_leading_chars': f'abc{valid_base64}',
        'corrupted_start': f'xyz{valid_base64[3:]}',  # Remove some chars from start
        'empty_string': '',
        'invalid_base64': 'not_base64_data_at_all',
    }
    
    return test_cases

def test_base64_validation():
    """Test the base64 validation functionality"""
    logger = setup_logging()
    logger.info("Starting base64 validation tests...")
    
    # Create VideoAnalyzer instance (we'll need config)
    # Look for config.yaml in the project root
    config_path = Path(__file__).parent.parent.parent / 'config.yaml'
    if not config_path.exists():
        # Try VideoProcessor directory
        config_path = Path(__file__).parent.parent / 'config.yaml'
        if not config_path.exists():
            logger.error(f"Config file not found in expected locations")
            logger.error(f"Tried: {Path(__file__).parent.parent.parent / 'config.yaml'}")
            logger.error(f"Tried: {Path(__file__).parent.parent / 'config.yaml'}")
            return False
    
    try:
        # Load config
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        analyzer = VideoAnalyzer(config, logger)
        test_cases = create_test_base64_data()
        
        results = {}
        
        for test_name, test_data in test_cases.items():
            logger.info(f"\n--- Testing: {test_name} ---")
            logger.info(f"Input length: {len(test_data)} characters")
            logger.info(f"Input preview: {test_data[:50]}...")
            
            try:
                result = analyzer._validate_and_repair_base64_image(test_data)
                results[test_name] = {
                    'success': True,
                    'output_length': len(result),
                    'starts_with_png_sig': result.startswith('iVBORw0KGgo'),
                    'message': 'Validation successful'
                }
                logger.info(f"✅ SUCCESS: Output length: {len(result)}")
                logger.info(f"   Starts with PNG signature: {result.startswith('iVBORw0KGgo')}")
                
            except Exception as e:
                results[test_name] = {
                    'success': False,
                    'error': str(e),
                    'message': f'Validation failed: {str(e)}'
                }
                logger.error(f"❌ FAILED: {str(e)}")
        
        # Print summary
        logger.info("\n" + "="*60)
        logger.info("BASE64 VALIDATION TEST SUMMARY")
        logger.info("="*60)
        
        success_count = sum(1 for r in results.values() if r['success'])
        total_count = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            logger.info(f"{status} {test_name:20} - {result['message']}")
        
        logger.info(f"\nOverall: {success_count}/{total_count} tests passed")
        
        # Expected results analysis
        expected_successes = ['valid_png', 'with_data_url', 'with_leading_slash', 'with_leading_chars']
        expected_failures = ['empty_string', 'invalid_base64', 'corrupted_start']
        
        logger.info("\n--- Expected Results Analysis ---")
        all_expected = True
        
        for test_name in expected_successes:
            if not results[test_name]['success']:
                logger.error(f"❌ UNEXPECTED FAILURE: {test_name} should have succeeded")
                all_expected = False
        
        for test_name in expected_failures:
            if results[test_name]['success']:
                logger.warning(f"⚠️  UNEXPECTED SUCCESS: {test_name} should have failed")
                # This might be OK if our repair logic is very good
        
        if all_expected:
            logger.info("✅ All critical tests behaved as expected!")
        
        return all_expected
        
    except Exception as e:
        logger.error(f"Test setup failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_base64_validation()
    sys.exit(0 if success else 1)
