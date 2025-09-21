#!/usr/bin/env python3
"""
Test script to verify LM Studio API connectivity
"""

import requests
import json
import base64
from pathlib import Path

def test_lm_studio_connection():
    """Test basic connection to LM Studio API"""
    url = "http://localhost:1234/v1/chat/completions"
    
    # Simple test message
    payload = {
        "model": "mimo-vl-7b-rl@q8_k_xl",
        "messages": [
            {
                "role": "user",
                "content": "Hello! Can you see this message? Please respond with 'Connection successful!'"
            }
        ],
        "temperature": 0.4,
        "max_tokens": 50
    }
    
    try:
        print("Testing LM Studio connection...")
        print(f"URL: {url}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"✅ LM Studio connection successful!")
            print(f"Response: {message}")
            return True
        else:
            print(f"❌ LM Studio connection failed!")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to LM Studio")
        print("Make sure LM Studio is running on localhost:1234")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: LM Studio took too long to respond")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_image_analysis():
    """Test image analysis capability with a simple test image"""
    url = "http://localhost:1234/v1/chat/completions"
    
    # Create a simple test image (1x1 pixel PNG)
    # This is a minimal PNG file in base64
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
    
    payload = {
        "model": "mimo-vl-7b-rl@q8_k_xl",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Can you analyze this test image? Just confirm you can see it."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{test_image_b64}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.4,
        "max_tokens": 100
    }
    
    try:
        print("\nTesting image analysis capability...")
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"✅ Image analysis successful!")
            print(f"Response: {message}")
            return True
        else:
            print(f"❌ Image analysis failed!")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Image analysis error: {e}")
        return False

if __name__ == "__main__":
    print("=== LM Studio API Test ===")
    
    # Test basic connection
    basic_success = test_lm_studio_connection()
    
    # Test image analysis if basic connection works
    if basic_success:
        image_success = test_image_analysis()
        
        if basic_success and image_success:
            print("\n🎉 All tests passed! LM Studio is ready for video analysis.")
        else:
            print("\n⚠️  Basic connection works but image analysis failed.")
    else:
        print("\n❌ LM Studio connection failed. Please check your setup.")
