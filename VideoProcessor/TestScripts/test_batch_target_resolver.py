#!/usr/bin/env python3
"""
Test script for BatchTargetResolver performance optimization
Compares individual vs batch target path resolution
"""

import sys
import os
import time
from datetime import datetime

# Add the VideoProcessor modules to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'VideoProcessor'))

from VideoProcessor.modules.config_manager import ConfigManager
from VideoProcessor.modules.logger_setup import setup_logging
from VideoProcessor.modules.batch_target_resolver import BatchTargetResolver

def create_test_files(count=100):
    """Create test file data for performance testing"""
    test_files = []
    
    for i in range(count):
        # Mix of different file types and naming patterns
        if i % 3 == 0:
            # Picture file
            filename = f"20240{(i%12)+1:02d}{(i%28)+1:02d}_120000_{i}.jpg"
            file_type = 'picture'
            extension = '.jpg'
        elif i % 3 == 1:
            # Regular video
            filename = f"20240{(i%12)+1:02d}{(i%28)+1:02d}_150000_{i}.mp4"
            file_type = 'video'
            extension = '.mp4'
        else:
            # Wudan video (contains kung fu keywords)
            filename = f"20240{(i%12)+1:02d}{(i%28)+1:02d}_180000_kungfu_{i}.mp4"
            file_type = 'video'
            extension = '.mp4'
        
        # Create date from filename
        date_str = filename[:8]  # YYYYMMDD
        file_date = datetime.strptime(date_str, '%Y%m%d')
        
        test_files.append({
            'name': filename,
            'path': f"\\\\MA-2022-C\\PHONESYNC\\TestFolder\\{filename}",
            'size': 1000000 + i,
            'type': file_type,
            'extension': extension,
            'date': file_date,
            'source_folder': 'TestFolder'
        })
    
    return test_files

def test_individual_resolution_simulation(test_files):
    """Simulate individual file-by-file target path resolution"""
    print("Simulating individual target path resolution...")
    start_time = time.time()

    resolved_paths = {}
    for file_info in test_files:
        # Simulate the time it takes for individual resolution (2 seconds per file as mentioned)
        time.sleep(0.001)  # 1ms per file for simulation

        # Simple target path logic for simulation
        file_key = f"{file_info['name']}|{file_info['size']}"
        if file_info['type'] == 'picture':
            base_path = "\\\\MA-2022-C\\UserData_G\\My Pictures"
        elif 'kungfu' in file_info['name'].lower():
            base_path = "\\\\MA-2022-C\\UserData_G\\My Videos\\Wudan"
        else:
            base_path = "\\\\MA-2022-C\\UserData_G\\My Videos"

        date_folder = file_info['date'].strftime('%Y_%m_%d_%a')
        target_path = f"{base_path}\\{date_folder}"
        resolved_paths[file_key] = target_path

    elapsed = time.time() - start_time
    print(f"Individual resolution: {len(resolved_paths)} paths in {elapsed:.3f} seconds")
    print(f"Speed: {len(test_files) / elapsed:.1f} files/second")

    return resolved_paths, elapsed

def test_batch_resolution(batch_resolver, test_files):
    """Test batch target path resolution"""
    print("Testing batch target path resolution...")
    start_time = time.time()
    
    result = batch_resolver.resolve_all_target_paths(test_files)
    
    elapsed = time.time() - start_time
    print(f"Batch resolution: {len(result['target_paths'])} paths in {elapsed:.3f} seconds")
    print(f"Speed: {result['performance']['files_per_second']:.1f} files/second")
    
    return result['target_paths'], elapsed

def compare_results(individual_paths, batch_paths):
    """Compare results from individual vs batch resolution"""
    print("\nComparing results...")
    
    individual_set = set(individual_paths.items())
    batch_set = set(batch_paths.items())
    
    if individual_set == batch_set:
        print("✅ Results match perfectly!")
    else:
        print("❌ Results differ!")
        print(f"Individual paths: {len(individual_paths)}")
        print(f"Batch paths: {len(batch_paths)}")
        
        # Show differences
        only_individual = individual_set - batch_set
        only_batch = batch_set - individual_set
        
        if only_individual:
            print(f"Only in individual: {len(only_individual)}")
            for item in list(only_individual)[:3]:
                print(f"  {item}")
        
        if only_batch:
            print(f"Only in batch: {len(only_batch)}")
            for item in list(only_batch)[:3]:
                print(f"  {item}")

def main():
    """Main test function"""
    print("=== BatchTargetResolver Performance Test ===")
    
    # Setup
    config_manager = ConfigManager()
    config = config_manager.load_config()
    logger = setup_logging(config, 'test_batch_target_resolver')
    
    # Initialize batch resolver
    batch_resolver = BatchTargetResolver(config, logger)
    
    # Create test data
    test_sizes = [100, 500, 1000]
    
    for test_size in test_sizes:
        print(f"\n=== Testing with {test_size} files ===")
        test_files = create_test_files(test_size)
        
        # Test individual resolution (simulated)
        individual_paths, individual_time = test_individual_resolution_simulation(test_files)
        
        # Test batch resolution
        batch_paths, batch_time = test_batch_resolution(batch_resolver, test_files)
        
        # Compare results
        compare_results(individual_paths, batch_paths)
        
        # Calculate speedup
        if individual_time > 0:
            speedup = individual_time / batch_time
            print(f"🚀 Speedup: {speedup:.1f}x faster")
        
        print("-" * 50)

if __name__ == "__main__":
    main()
