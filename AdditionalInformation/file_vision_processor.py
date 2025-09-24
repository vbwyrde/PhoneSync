#!/usr/bin/env python3
"""
File-Based Vision Processor for N8N
Monitors shared folder for vision analysis requests and processes them
Final solution for N8N 1.109.2 HTTP Request node limitations
"""

import json
import requests
import time
import os
import base64
from datetime import datetime
import logging
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_vision_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
SHARED_FOLDER = "C:/Docker_Share/N8N/vision_requests"
RESULTS_FOLDER = "C:/Docker_Share/N8N/vision_results"
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
DEFAULT_MODEL = "mimo-vl-7b-rl@q8_k_xl"
POLL_INTERVAL = 1  # seconds - fast polling for real-time feel

# Statistics
stats = {
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'start_time': datetime.now()
}

# Ensure folders exist
os.makedirs(SHARED_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

def get_thumbnail_from_ffmpeg_results(filename):
    """Get thumbnail base64 data from FFmpeg results folder"""
    ffmpeg_results_folder = "C:/Docker_Share/N8N/ffmpeg_results"

    try:
        # Look for FFmpeg result files
        for result_file in os.listdir(ffmpeg_results_folder):
            if result_file.endswith('.json'):
                result_path = os.path.join(ffmpeg_results_folder, result_file)
                with open(result_path, 'r', encoding='utf-8') as f:
                    result_data = json.load(f)

                # Check if this result is for our filename
                if result_data.get('filename') == filename and result_data.get('success'):
                    thumbnail_base64 = result_data.get('thumbnail_base64', '')
                    if thumbnail_base64:
                        logger.info(f"Found thumbnail for {filename} in {result_file}")
                        return thumbnail_base64

        logger.warning(f"No FFmpeg result found for {filename}")
        return None

    except Exception as e:
        logger.error(f"Error getting thumbnail from FFmpeg results for {filename}: {str(e)}")
        return None

def process_vision_request(request_file):
    """Process a single vision analysis request"""
    try:
        # Read request data
        with open(request_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        filename = data.get('filename', 'unknown.mp4')
        thumbnail_base64 = data.get('thumbnailBase64', '')
        needs_thumbnail_from_ffmpeg = data.get('needs_thumbnail_from_ffmpeg', False)
        custom_prompt = data.get('prompt', '')
        request_id = data.get('request_id', str(uuid.uuid4()))

        logger.info(f"Processing vision request: {filename} (ID: {request_id})")
        stats['total_requests'] += 1

        # Get thumbnail from FFmpeg results if needed
        if not thumbnail_base64 and needs_thumbnail_from_ffmpeg:
            logger.info(f"Getting thumbnail from FFmpeg results for {filename}")
            thumbnail_base64 = get_thumbnail_from_ffmpeg_results(filename)
            if not thumbnail_base64:
                raise ValueError(f"thumbnailBase64 is required and could not be obtained from FFmpeg results for {filename}")
        elif not thumbnail_base64:
            raise ValueError("thumbnailBase64 is required")
        
        # Enhanced kung fu detection prompt - more specific and encouraging
        default_prompt = """Analyze this video thumbnail for kung fu or martial arts content. Look for:
- Martial arts poses, stances, or movements
- Fighting techniques or combat training
- Traditional Chinese martial arts (kung fu, wushu, tai chi)
- Training equipment (wooden dummies, weapons, mats)
- Text mentioning martial arts terms (kung fu, wushu, bagua, tai chi, etc.)
- People in martial arts uniforms or practicing forms

If you see ANY of these elements, respond with YES. Only respond with NO if there are clearly no martial arts elements present. Be more inclusive rather than restrictive in your analysis."""
        
        text_prompt = custom_prompt if custom_prompt else default_prompt
        
        # Validate and prepare base64 image
        try:
            # Remove data URL prefix if present
            clean_base64 = thumbnail_base64
            if thumbnail_base64.startswith('data:image'):
                clean_base64 = thumbnail_base64.split(',')[1]

            # Debug: Check the format of the base64 data
            logger.info(f"Original base64 length: {len(thumbnail_base64)} characters")
            logger.info(f"Base64 starts with: {thumbnail_base64[:50]}...")

            # Fix corrupted base64 data - remove leading invalid characters
            # Valid PNG base64 should start with 'iVBORw0KGgo'
            if not clean_base64.startswith('iVBORw0KGgo'):
                logger.warning(f"Base64 doesn't start with PNG signature, attempting to fix...")
                # Try to find the actual PNG start
                png_start = clean_base64.find('iVBORw0KGgo')
                if png_start > 0:
                    logger.info(f"Found PNG signature at position {png_start}, removing {png_start} leading characters")
                    clean_base64 = clean_base64[png_start:]
                elif clean_base64.startswith('/'):
                    # Common issue: leading slash character
                    logger.info("Removing leading slash character")
                    clean_base64 = clean_base64[1:]

            logger.info(f"Clean base64 length: {len(clean_base64)} characters")
            logger.info(f"Clean base64 starts with: {clean_base64[:50]}...")

            # Test decode to validate
            decoded_data = base64.b64decode(clean_base64)
            logger.info(f"Decoded data length: {len(decoded_data)} bytes")
            logger.info(f"Decoded data starts with: {decoded_data[:20].hex()}")

            # Check if it's a valid PNG (should start with PNG signature)
            if decoded_data[:8] == b'\x89PNG\r\n\x1a\n':
                logger.info("Valid PNG signature detected")
            else:
                logger.warning(f"Invalid PNG signature. First 8 bytes: {decoded_data[:8].hex()}")
                # Try one more fix - sometimes there are extra bytes at the start
                if len(decoded_data) > 8:
                    for i in range(1, min(10, len(decoded_data))):
                        if decoded_data[i:i+8] == b'\x89PNG\r\n\x1a\n':
                            logger.info(f"Found PNG signature at byte offset {i}, adjusting base64")
                            # Re-encode without the leading bytes
                            fixed_data = decoded_data[i:]
                            clean_base64 = base64.b64encode(fixed_data).decode('utf-8')
                            logger.info(f"Fixed base64 length: {len(clean_base64)} characters")
                            break

            # Ensure we have the clean base64 for LM Studio
            thumbnail_base64 = clean_base64

        except Exception as e:
            raise ValueError(f"Invalid base64 image: {str(e)}")
        
        # Prepare LM Studio vision request
        lm_studio_payload = {
            "model": DEFAULT_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{thumbnail_base64}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.4,
            "max_tokens": 150,
            "stream": False
        }
        
        logger.info(f"Sending vision request to LM Studio for {filename}")
        
        # Make request to LM Studio
        response = requests.post(
            LM_STUDIO_URL,
            json=lm_studio_payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Extract YES/NO from response
            analysis_result = "NO"
            content_upper = content.upper()
            if "YES" in content_upper:
                analysis_result = "YES"
            
            logger.info(f"Analysis result for {filename}: {analysis_result}")
            stats['successful_requests'] += 1
            
            # Prepare result
            result_data = {
                "success": True,
                "request_id": request_id,
                "filename": filename,
                "analysis_result": analysis_result,
                "full_response": content,
                "contains_kung_fu": analysis_result == "YES",
                "model_used": DEFAULT_MODEL,
                "processed_at": datetime.now().isoformat(),
                "prompt_used": text_prompt[:100] + "..." if len(text_prompt) > 100 else text_prompt
            }
            
        else:
            logger.error(f"LM Studio error: {response.status_code} - {response.text}")
            stats['failed_requests'] += 1
            result_data = {
                "success": False,
                "request_id": request_id,
                "filename": filename,
                "error": f"LM Studio error: {response.status_code}",
                "error_type": "lm_studio_api_failed",
                "error_step": "vision_analysis",
                "status_code": response.status_code,
                "details": response.text,
                "processed_at": datetime.now().isoformat(),
                "skip_reason": f"LM Studio API call failed with status {response.status_code}"
            }
        
        # Write result file
        result_file = os.path.join(RESULTS_FOLDER, f"result_{request_id}.json")
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2)
        
        logger.info(f"Result written to: {result_file}")
        
        # Remove processed request file
        os.remove(request_file)
        logger.info(f"Processed request file removed: {request_file}")
        
    except Exception as e:
        logger.error(f"Error processing {request_file}: {str(e)}")
        stats['failed_requests'] += 1
        
        # Write error result
        try:
            error_result = {
                "success": False,
                "request_id": data.get('request_id', str(uuid.uuid4())) if 'data' in locals() else str(uuid.uuid4()),
                "filename": data.get('filename', 'unknown') if 'data' in locals() else 'unknown',
                "error": f"Processing error: {str(e)}",
                "error_type": "vision_processing_exception",
                "error_step": "vision_analysis",
                "processed_at": datetime.now().isoformat(),
                "skip_reason": f"Vision processing failed with exception: {str(e)}"
            }
            
            result_file = os.path.join(RESULTS_FOLDER, f"error_{int(time.time())}.json")
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(error_result, f, indent=2)
            
            # Remove failed request file
            if os.path.exists(request_file):
                os.remove(request_file)
                
        except Exception as write_error:
            logger.error(f"Failed to write error result: {str(write_error)}")

def monitor_requests():
    """Monitor the shared folder for new vision requests"""
    logger.info(f"Monitoring folder: {SHARED_FOLDER}")
    logger.info(f"Results folder: {RESULTS_FOLDER}")
    logger.info(f"Poll interval: {POLL_INTERVAL} seconds")
    
    while True:
        try:
            # Check for new request files
            if os.path.exists(SHARED_FOLDER):
                request_files = [f for f in os.listdir(SHARED_FOLDER) if f.endswith('.json')]
                
                if request_files:
                    logger.info(f"Found {len(request_files)} request(s) to process")
                    
                    for request_file in request_files:
                        full_path = os.path.join(SHARED_FOLDER, request_file)
                        process_vision_request(full_path)
            
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("Shutting down file-based vision processor...")
            break
        except Exception as e:
            logger.error(f"Error in monitoring loop: {str(e)}")
            time.sleep(POLL_INTERVAL)

if __name__ == '__main__':
    print("Starting File-Based Vision Processor")
    print(f"LM Studio URL: {LM_STUDIO_URL}")
    print(f"Model: {DEFAULT_MODEL}")
    print(f"Request Folder: {SHARED_FOLDER}")
    print(f"Results Folder: {RESULTS_FOLDER}")
    print(f"Poll Interval: {POLL_INTERVAL} seconds")
    print("\nThis processor monitors the shared folder for vision analysis requests")
    print("and processes them using LM Studio, writing results back to the results folder.")
    print("\nPress Ctrl+C to stop...")
    
    # Display statistics
    def print_stats():
        uptime = datetime.now() - stats['start_time']
        print(f"\n📊 Statistics:")
        print(f"   Uptime: {int(uptime.total_seconds())} seconds")
        print(f"   Total Requests: {stats['total_requests']}")
        print(f"   Successful: {stats['successful_requests']}")
        print(f"   Failed: {stats['failed_requests']}")
    
    try:
        monitor_requests()
    finally:
        print_stats()
