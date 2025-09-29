"""
Video Analyzer for PhoneSync + VideoProcessor
Integrates FFmpeg video processing with LM Studio AI analysis
Handles thumbnail extraction, kung fu detection, and automated note generation
"""

import os
import base64
import logging
import subprocess
import tempfile
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
import json

class VideoAnalyzer:
    """
    Analyzes videos using FFmpeg for thumbnail extraction and LM Studio for AI analysis
    Detects kung fu/martial arts content and generates automated notes
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        Initialize video analyzer
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        
        # AI settings
        self.ai_settings = config['ai_settings']
        self.lm_studio_url = self.ai_settings['lm_studio_url']
        self.model = self.ai_settings['model']
        self.kung_fu_prompt = self.ai_settings['kung_fu_prompt']
        
        # Video analysis settings
        self.video_analysis_enabled = config['options']['enable_video_analysis']
        # Dynamic thumbnail extraction - will calculate midpoint of each video
        
        # Statistics
        self.stats = {
            'videos_analyzed': 0,
            'kung_fu_detected': 0,
            'notes_generated': 0,
            'analysis_failures': 0,
            'thumbnails_extracted': 0
        }

    def should_analyze_video(self, video_path: str) -> bool:
        """
        Determine if a video should be analyzed

        Args:
            video_path: Path to the video file

        Returns:
            True if video should be analyzed, False otherwise
        """
        if not self.video_analysis_enabled:
            return False

        # Check if video file exists
        if not os.path.exists(video_path):
            self.logger.warning(f"Video file does not exist: {video_path}")
            return False

        # Check if it's actually a video file
        video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv', '.webm'}
        file_ext = Path(video_path).suffix.lower()
        if file_ext not in video_extensions:
            self.logger.debug(f"Skipping non-video file: {video_path}")
            return False

        # Additional checks could be added here:
        # - File size limits
        # - Already analyzed check
        # - Blacklist/whitelist patterns

        return True

    def analyze_video(self, video_path: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Analyze a video file for kung fu/martial arts content

        Args:
            video_path: Path to the video file
            dry_run: If True, simulate analysis without making API calls

        Returns:
            Analysis results dictionary
        """
        if not self.video_analysis_enabled:
            return {
                'analyzed': False,
                'reason': 'Video analysis disabled in configuration'
            }

        if dry_run:
            self.logger.info(f"[DRY RUN] Would analyze video: {video_path}")
            return {
                'analyzed': True,
                'is_kung_fu': False,
                'confidence': 0.5,
                'description': '[DRY RUN] Simulated analysis - no actual AI processing performed',
                'dry_run': True
            }

        self.logger.info(f"Analyzing video: {video_path}")

        try:
            # Extract thumbnail from video
            thumbnail_data = self._extract_thumbnail(video_path)
            if not thumbnail_data:
                self.stats['analysis_failures'] += 1
                return {
                    'analyzed': False,
                    'reason': 'Failed to extract thumbnail'
                }

            self.stats['thumbnails_extracted'] += 1

            # Create file_info from video_path for AI analysis
            file_info = {
                'filename': Path(video_path).name,
                'path': video_path,
                'date': datetime.now()
            }

            # Analyze thumbnail with LM Studio
            analysis_result = self._analyze_thumbnail_with_ai(thumbnail_data, file_info)
            
            if analysis_result['success']:
                self.stats['videos_analyzed'] += 1
                
                if analysis_result['is_kung_fu']:
                    self.stats['kung_fu_detected'] += 1
                
                if analysis_result.get('note_generated'):
                    self.stats['notes_generated'] += 1
                
                return {
                    'analyzed': True,
                    'is_kung_fu': analysis_result['is_kung_fu'],
                    'confidence': analysis_result.get('confidence', 0),
                    'description': analysis_result.get('description', ''),
                    'note_content': analysis_result.get('note_content', ''),
                    'analysis_timestamp': datetime.now().isoformat()
                }
            else:
                self.stats['analysis_failures'] += 1
                return {
                    'analyzed': False,
                    'reason': f"AI analysis failed: {analysis_result.get('error', 'Unknown error')}"
                }
                
        except Exception as e:
            self.logger.error(f"Error analyzing video {video_path}: {e}")
            self.stats['analysis_failures'] += 1
            return {
                'analyzed': False,
                'reason': f"Analysis error: {str(e)}"
            }
    
    def _get_video_duration(self, video_path: str) -> Optional[float]:
        """
        Get video duration in seconds using FFmpeg

        Args:
            video_path: Path to the video file

        Returns:
            Duration in seconds or None if failed
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                video_path
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=10)

            if result.returncode == 0:
                import json
                probe_data = json.loads(result.stdout.decode())
                duration = float(probe_data['format']['duration'])
                self.logger.debug(f"Video duration: {duration:.2f} seconds")
                return duration
            else:
                self.logger.warning(f"FFprobe failed for {video_path}: {result.stderr.decode()}")
                return None

        except Exception as e:
            self.logger.error(f"Error getting video duration for {video_path}: {e}")
            return None

    def _extract_thumbnail(self, video_path: str) -> Optional[str]:
        """
        Extract thumbnail from video midpoint using FFmpeg and return as base64

        Args:
            video_path: Path to the video file

        Returns:
            Base64 encoded thumbnail data or None if failed
        """
        try:
            # Get video duration to calculate midpoint
            duration = self._get_video_duration(video_path)

            if duration is None:
                self.logger.warning(f"Could not determine video duration, using 5 second fallback")
                thumbnail_time = "00:00:05"
            else:
                # Calculate midpoint timestamp
                midpoint_seconds = duration / 2.0

                # Ensure we don't go beyond video bounds (leave 1 second buffer)
                if midpoint_seconds > (duration - 1):
                    midpoint_seconds = max(1.0, duration - 1)

                # Format as HH:MM:SS.mmm
                hours = int(midpoint_seconds // 3600)
                minutes = int((midpoint_seconds % 3600) // 60)
                seconds = midpoint_seconds % 60
                thumbnail_time = f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

                self.logger.debug(f"Extracting thumbnail at midpoint: {thumbnail_time} (duration: {duration:.2f}s)")

            # Use FFmpeg to extract thumbnail and pipe to stdout
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-ss', thumbnail_time,  # Seek to calculated timestamp
                '-vframes', '1',  # Extract 1 frame
                '-f', 'image2pipe',  # Output to pipe
                '-vcodec', 'png',  # PNG format
                '-'  # Output to stdout
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30  # 30 second timeout
            )
            
            if result.returncode == 0 and result.stdout:
                # Encode thumbnail data as base64
                thumbnail_base64 = base64.b64encode(result.stdout).decode('utf-8')
                self.logger.debug(f"Extracted thumbnail: {len(thumbnail_base64)} bytes (base64)")
                return thumbnail_base64
            else:
                self.logger.warning(f"FFmpeg failed for {video_path}: {result.stderr.decode() if result.stderr else 'No error output'}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.warning(f"FFmpeg timeout for {video_path}")
            return None
        except Exception as e:
            self.logger.error(f"Error extracting thumbnail from {video_path}: {e}")
            return None
    
    def _validate_and_repair_base64_image(self, thumbnail_base64: str) -> str:
        """
        Validate and repair base64 image data for robust AI analysis

        Extracted and enhanced from legacy N8N processor for improved reliability.
        Handles common base64 corruption issues and validates PNG signatures.

        Args:
            thumbnail_base64: Base64 encoded thumbnail data

        Returns:
            Validated and repaired base64 string

        Raises:
            ValueError: If base64 data cannot be validated or repaired
        """
        try:
            # Remove data URL prefix if present
            clean_base64 = thumbnail_base64
            if thumbnail_base64.startswith('data:image'):
                clean_base64 = thumbnail_base64.split(',')[1]

            # Debug logging for troubleshooting
            self.logger.debug(f"Original base64 length: {len(thumbnail_base64)} characters")
            self.logger.debug(f"Base64 starts with: {thumbnail_base64[:50]}...")

            # Fix corrupted base64 data - remove leading invalid characters
            # Valid PNG base64 should start with 'iVBORw0KGgo'
            if not clean_base64.startswith('iVBORw0KGgo'):
                self.logger.warning(f"Base64 doesn't start with PNG signature, attempting to fix...")
                # Try to find the actual PNG start
                png_start = clean_base64.find('iVBORw0KGgo')
                if png_start > 0:
                    self.logger.info(f"Found PNG signature at position {png_start}, removing {png_start} leading characters")
                    clean_base64 = clean_base64[png_start:]
                elif clean_base64.startswith('/'):
                    # Common issue: leading slash character
                    self.logger.info("Removing leading slash character")
                    clean_base64 = clean_base64[1:]

            self.logger.debug(f"Clean base64 length: {len(clean_base64)} characters")
            self.logger.debug(f"Clean base64 starts with: {clean_base64[:50]}...")

            # Test decode to validate
            decoded_data = base64.b64decode(clean_base64)
            self.logger.debug(f"Decoded data length: {len(decoded_data)} bytes")
            self.logger.debug(f"Decoded data starts with: {decoded_data[:20].hex()}")

            # Check if it's a valid PNG (should start with PNG signature)
            if decoded_data[:8] == b'\x89PNG\r\n\x1a\n':
                self.logger.debug("Valid PNG signature detected")
            else:
                self.logger.warning(f"Invalid PNG signature. First 8 bytes: {decoded_data[:8].hex()}")
                # Try one more fix - sometimes there are extra bytes at the start
                if len(decoded_data) > 8:
                    for i in range(1, min(10, len(decoded_data))):
                        if decoded_data[i:i+8] == b'\x89PNG\r\n\x1a\n':
                            self.logger.info(f"Found PNG signature at byte offset {i}, adjusting base64")
                            # Re-encode without the leading bytes
                            fixed_data = decoded_data[i:]
                            clean_base64 = base64.b64encode(fixed_data).decode('utf-8')
                            self.logger.info(f"Fixed base64 length: {len(clean_base64)} characters")
                            break

            return clean_base64

        except Exception as e:
            raise ValueError(f"Invalid base64 image data: {str(e)}")

    def _analyze_thumbnail_with_ai(self, thumbnail_base64: str, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze thumbnail using LM Studio AI

        Args:
            thumbnail_base64: Base64 encoded thumbnail data
            file_info: File information dictionary

        Returns:
            Analysis results dictionary
        """
        try:
            # Validate and repair base64 data before AI analysis
            validated_base64 = self._validate_and_repair_base64_image(thumbnail_base64)
            # Prepare the prompt with file context
            filename = file_info.get('name', 'unknown')
            file_date = file_info.get('date', datetime.now())

            context_prompt = f"""
File: {filename}
Date: {file_date.strftime('%Y-%m-%d %H:%M:%S')}

{self.kung_fu_prompt}
"""

            # Prepare request payload using validated base64
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": context_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{validated_base64}"
                                }
                            }
                        ]
                    }
                ],
                "temperature": self.ai_settings['temperature'],
                "max_tokens": self.ai_settings['max_tokens']
            }
            
            # Make request to LM Studio
            response = requests.post(
                self.lm_studio_url,
                json=payload,
                timeout=self.ai_settings['timeout_seconds']
            )
            
            if response.status_code == 200:
                response_data = response.json()
                ai_response = response_data['choices'][0]['message']['content']
                
                # Extract YES/NO from response (proven N8N approach)
                content_upper = ai_response.upper()
                is_kung_fu = "YES" in content_upper

                # Extract confidence based on language used
                confidence = 75 if is_kung_fu else 25  # Default confidence levels

                # Try to extract more nuanced confidence from response
                if "definitely" in ai_response.lower() or "clearly" in ai_response.lower():
                    confidence = 90 if is_kung_fu else 10
                elif "possibly" in ai_response.lower() or "might" in ai_response.lower():
                    confidence = 60 if is_kung_fu else 40
                elif "probably" in ai_response.lower() or "likely" in ai_response.lower():
                    confidence = 80 if is_kung_fu else 20

                # Clean the AI response for notes (remove <think> tags and extract clean description)
                clean_description = self._clean_ai_response(ai_response)

                # Generate note content for both kung fu and non-kung fu videos
                note_content = ""
                if is_kung_fu:
                    note_content = f"Kung Fu/Martial Arts detected in video thumbnail.\n\nAI Analysis:\n{clean_description}\n\nDetected on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                else:
                    # Generate "NOT KUNG FU" note for videos routed to Wudan folder but not containing martial arts
                    note_content = f"NOT KUNG FU - Video does not contain martial arts content.\n\nAI Analysis:\n{clean_description}\n\nAnalyzed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nNote: This video was routed to Wudan folder based on time rules but AI analysis indicates it does not contain kung fu/martial arts content."

                analysis_result = {
                    'success': True,
                    'is_kung_fu': is_kung_fu,
                    'confidence': confidence,
                    'description': clean_description,
                    'note_content': note_content,
                    'full_response': ai_response,
                    'note_generated': bool(note_content.strip())
                }

                self.logger.info(f"AI analysis complete: kung_fu={is_kung_fu}, confidence={confidence}%")
                self.logger.debug(f"Full AI response: {ai_response}")

                return analysis_result
            else:
                # Enhanced error handling with categorization
                return {
                    'success': False,
                    'error': f"LM Studio request failed: {response.status_code} - {response.text}",
                    'error_type': 'lm_studio_api_failed',
                    'error_step': 'vision_analysis',
                    'status_code': response.status_code,
                    'details': response.text,
                    'processed_at': datetime.now().isoformat(),
                    'skip_reason': f"LM Studio API call failed with status {response.status_code}"
                }

        except requests.Timeout:
            return {
                'success': False,
                'error': "LM Studio request timeout",
                'error_type': 'lm_studio_timeout',
                'error_step': 'vision_analysis',
                'processed_at': datetime.now().isoformat(),
                'skip_reason': "LM Studio API request timed out"
            }
        except ValueError as e:
            # Base64 validation errors
            return {
                'success': False,
                'error': f"Base64 validation error: {str(e)}",
                'error_type': 'base64_validation_failed',
                'error_step': 'thumbnail_validation',
                'processed_at': datetime.now().isoformat(),
                'skip_reason': f"Thumbnail data validation failed: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"AI analysis error: {str(e)}",
                'error_type': 'vision_processing_exception',
                'error_step': 'vision_analysis',
                'processed_at': datetime.now().isoformat(),
                'skip_reason': f"Vision processing failed with exception: {str(e)}"
            }

    def _clean_ai_response(self, ai_response: str) -> str:
        """
        Clean AI response by removing <think> tags and extracting useful description

        Args:
            ai_response: Raw AI response text

        Returns:
            Cleaned description text
        """
        try:
            import re

            # Remove <think> tags and their content (handle both closed and unclosed tags)
            cleaned = re.sub(r'<think>.*?</think>', '', ai_response, flags=re.DOTALL)
            # Handle unclosed <think> tags by removing everything from <think> to end
            cleaned = re.sub(r'<think>.*', '', cleaned, flags=re.DOTALL)

            # Split by lines and find the actual description (after YES/NO)
            lines = cleaned.strip().split('\n')
            description_lines = []
            found_answer = False

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Skip the YES/NO line
                if line.upper() in ['YES', 'NO']:
                    found_answer = True
                    continue

                # Collect description lines after YES/NO
                if found_answer and line:
                    description_lines.append(line)

            # Join description lines
            if description_lines:
                result = ' '.join(description_lines)
                # Ensure it's under 10 words as requested
                words = result.split()
                if len(words) > 10:
                    result = ' '.join(words[:10])
                return result
            else:
                # Fallback: return cleaned response without <think> tags
                fallback = cleaned.strip()
                # Ensure fallback is also under 10 words
                words = fallback.split()
                if len(words) > 10:
                    fallback = ' '.join(words[:10])
                return fallback

        except Exception as e:
            self.logger.warning(f"Error cleaning AI response: {e}")
            # Fallback: return original response (truncated to 10 words)
            words = ai_response.split()
            return ' '.join(words[:10]) if len(words) > 10 else ai_response

    def generate_note_file(self, video_path: str, analysis_result: Dict[str, Any],
                          target_directory: str) -> Optional[str]:
        """
        Generate a note file for analyzed videos (both kung fu and non-kung fu)

        Args:
            video_path: Path to the video file
            analysis_result: Analysis results from analyze_video
            target_directory: Directory where the video will be stored

        Returns:
            Path to generated note file or None if not generated
        """
        if not analysis_result.get('note_content'):
            return None
        
        try:
            # Create note filename based on video filename
            video_filename = Path(video_path).stem
            note_filename = f"{video_filename}_analysis.txt"
            note_path = os.path.join(target_directory, note_filename)
            
            # Prepare note content
            note_content = f"""Video Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Video File: {Path(video_path).name}
Analysis Confidence: {analysis_result.get('confidence', 0)}%

Description:
{analysis_result.get('description', 'No description available')}

Detailed Analysis:
{analysis_result.get('note_content', 'No detailed analysis available')}

---
Generated by PhoneSync + VideoProcessor AI Analysis
"""
            
            # Write note file
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(note_content)
            
            self.logger.info(f"Generated note file: {note_path}")
            return note_path
            
        except Exception as e:
            self.logger.error(f"Error generating note file for {video_path}: {e}")
            return None
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get video analysis statistics"""
        stats = self.stats.copy()
        
        # Add calculated fields
        if stats['videos_analyzed'] > 0:
            stats['kung_fu_detection_rate'] = (stats['kung_fu_detected'] / stats['videos_analyzed']) * 100
            stats['success_rate'] = ((stats['videos_analyzed']) / 
                                   (stats['videos_analyzed'] + stats['analysis_failures'])) * 100
        else:
            stats['kung_fu_detection_rate'] = 0
            stats['success_rate'] = 0
        
        stats['analysis_enabled'] = self.video_analysis_enabled
        
        return stats
    
    def test_ai_connection(self) -> Dict[str, Any]:
        """
        Test connection to LM Studio AI service
        
        Returns:
            Test results dictionary
        """
        try:
            # Simple test request
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": "Please respond with 'Connection successful!' to confirm you can see this message."
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 50
            }
            
            response = requests.post(
                self.lm_studio_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                response_data = response.json()
                ai_response = response_data['choices'][0]['message']['content']
                
                return {
                    'success': True,
                    'response': ai_response,
                    'status_code': response.status_code
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'status_code': response.status_code
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': None
            }
