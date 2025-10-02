#!/usr/bin/env python3
"""
Advanced async examples for PIXXIO Python client library.
Demonstrates concurrent operations and async job tracking.
"""

import asyncio
import tempfile
import os
import time
from typing import List

from pixxio_client import Client
from pixxio_client.files import File
from pixxio_client.collections import Collection
from pixxio_client.exceptions import PIXXIOException, JobTimeoutException

# Test environment configuration
TEST_HOST = "hoerl-demo.px.media"
TEST_API_KEY = "uDP9XwmExpcR6TTDobtu8qVWYs99WmDou8PTTXM22IdoWZhtO4dh5q2SMZO90F0h"

def create_test_file(content: str, suffix: str = '.txt') -> str:
    """Create a temporary test file with given content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
        f.write(content)
        return f.name

async def example_1_async_file_upload():
    """Example 1: Asynchronous file upload with job tracking."""
    print("\n⚡ Example 1: Async File Upload")
    print("-" * 40)
    
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    files = File(client)
    
    # Create test file
    test_content = f"Async upload test at {time.time()}\n" + "X" * (10 * 1024)
    test_file = create_test_file(test_content)
    
    try:
        print("🚀 Starting async upload with job tracking...")
        
        start_time = time.time()
        result = await files.async_upload_and_wait(
            test_file,
            title="Async Upload Example",
            timeout=60,
            poll_interval=2.0
        )
        duration = time.time() - start_time
        
        result_id = getattr(result, 'id')
        print(f"✅ Async upload completed in {duration:.1f}s! File ID: {result_id}")
        
        return result_id
        
    except JobTimeoutException:
        print("⏰ Upload timed out but may still be processing")
        return None
    except Exception as e:
        print(f"❌ Async upload failed: {e}")
        return None
    finally:
        os.unlink(test_file)

async def example_2_concurrent_uploads():
    """Example 2: Multiple concurrent file uploads."""
    print("\n📤 Example 2: Concurrent Uploads")
    print("-" * 40)
    
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    files = File(client)
    
    # Create multiple test files
    test_files = []
    for i in range(3):
        content = f"Concurrent upload test file {i+1}\n" + f"Content: {'X' * (5 * 1024)}"
        test_file = create_test_file(content, f'_file_{i+1}.txt')
        test_files.append(test_file)
    
    try:
        print(f"🚀 Starting {len(test_files)} concurrent uploads...")
        
        # Create upload tasks
        tasks = [
            files.async_upload_and_wait(
                file_path,
                title=f"Concurrent Upload {i+1}",
                timeout=60,
                poll_interval=2.0
            )
            for i, file_path in enumerate(test_files)
        ]
        
        start_time = time.time()
        
        # Wait for all uploads to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        duration = time.time() - start_time
        
        # Process results
        successful = []
        failed = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed.append((i+1, str(result)))
            else:
                result_id = getattr(result, 'id', 'Unknown')
                successful.append((i+1, result_id))
        
        print(f"✅ Concurrent uploads completed in {duration:.1f}s")
        print(f"   Successful: {len(successful)}")
        print(f"   Failed: {len(failed)}")
        
        for file_num, file_id in successful:
            print(f"   📄 File {file_num}: ID {file_id}")
        
        for file_num, error in failed:
            print(f"   ❌ File {file_num}: {error}")
        
        return [file_id for _, file_id in successful]
        
    except Exception as e:
        print(f"❌ Concurrent uploads failed: {e}")
        return []
    finally:
        # Clean up test files
        for test_file in test_files:
            os.unlink(test_file)

async def example_3_async_batch_operations():
    """Example 3: Batch operations with async processing."""
    print("\n📦 Example 3: Async Batch Operations")
    print("-" * 40)
    
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    collections = Collection(client)
    
    collection_names = [
        "Async Collection 1",
        "Async Collection 2", 
        "Async Collection 3"
    ]
    
    try:
        print(f"🚀 Creating {len(collection_names)} collections concurrently...")
        
        # Create collection creation tasks
        tasks = [
            asyncio.to_thread(
                collections.post,
                json_data={
                    'name': name,
                    'description': f'Created by async batch operation'
                }
            )
            for name in collection_names
        ]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time
        
        # Process results
        successful_collections = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"   ❌ Collection '{collection_names[i]}' failed: {result}")
            else:
                collection_id = getattr(result, 'id')
                successful_collections.append((collection_names[i], collection_id))
                print(f"   ✅ Collection '{collection_names[i]}': ID {collection_id}")
        
        print(f"✅ Batch operations completed in {duration:.1f}s")
        return successful_collections
        
    except Exception as e:
        print(f"❌ Batch operations failed: {e}")
        return []

async def example_4_async_with_progress_monitoring():
    """Example 4: Async operation with custom progress monitoring."""
    print("\n📊 Example 4: Async Progress Monitoring")
    print("-" * 40)
    
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    files = File(client)
    
    # Create a larger test file to show progress
    test_content = f"Progress monitoring test\n" + "X" * (20 * 1024)
    test_file = create_test_file(test_content)
    
    try:
        print("📊 Starting upload with progress monitoring...")
        
        async def upload_with_progress():
            """Upload with simulated progress updates."""
            # Start the upload
            upload_task = asyncio.create_task(
                files.async_upload_and_wait(
                    test_file,
                    title="Progress Monitoring Example",
                    timeout=90,
                    poll_interval=1.0
                )
            )
            
            # Monitor progress (simulated)
            progress_dots = 0
            while not upload_task.done():
                progress_dots = (progress_dots + 1) % 4
                dots = "." * progress_dots + " " * (3 - progress_dots)
                print(f"\r   Processing{dots}", end="", flush=True)
                await asyncio.sleep(1)
            
            print("\r   Processing complete!   ")
            return await upload_task
        
        result = await upload_with_progress()
        result_id = getattr(result, 'id')
        print(f"✅ Upload with progress monitoring completed! File ID: {result_id}")
        
        return result_id
        
    except Exception as e:
        print(f"❌ Progress monitoring upload failed: {e}")
        return None
    finally:
        os.unlink(test_file)

async def example_5_async_error_handling():
    """Example 5: Error handling in async operations."""
    print("\n🛡️ Example 5: Async Error Handling")
    print("-" * 40)
    
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    files = File(client)
    
    # Test scenarios with different error conditions
    test_scenarios = [
        ("valid_upload", lambda: files.async_upload_and_wait(
            create_test_file("Valid content"), 
            title="Valid Upload",
            timeout=30
        )),
        ("invalid_file", lambda: files.async_upload_and_wait(
            "/this/file/does/not/exist.txt",
            title="Invalid Upload",
            timeout=30
        )),
        ("timeout_test", lambda: files.async_upload_and_wait(
            create_test_file("Timeout test"),
            title="Timeout Test", 
            timeout=1  # Very short timeout (1 second)
        ))
    ]
    
    results = {}
    
    for scenario_name, scenario_func in test_scenarios:
        try:
            print(f"🧪 Testing scenario: {scenario_name}")
            
            if scenario_name == "valid_upload":
                temp_file = create_test_file("Valid test content")
                result = await files.async_upload_and_wait(
                    temp_file,
                    title="Valid Upload",
                    timeout=30
                )
                os.unlink(temp_file)
                results[scenario_name] = "✅ Success"
                
            elif scenario_name == "invalid_file":
                try:
                    await files.async_upload_and_wait(
                        "/this/file/does/not/exist.txt",
                        title="Invalid Upload"
                    )
                    results[scenario_name] = "❌ Should have failed"
                except FileNotFoundError:
                    results[scenario_name] = "✅ FileNotFoundError handled"
                except Exception as e:
                    results[scenario_name] = f"❓ Unexpected: {e}"
                    
            elif scenario_name == "timeout_test":
                temp_file = create_test_file("Timeout test content")
                try:
                    await files.async_upload_and_wait(
                        temp_file,
                        title="Timeout Test",
                        timeout=1  # Very short timeout (1 second)
                    )
                    results[scenario_name] = "❌ Should have timed out"
                except (JobTimeoutException, asyncio.TimeoutError):
                    results[scenario_name] = "✅ Timeout handled"
                except Exception as e:
                    results[scenario_name] = f"❓ Unexpected: {e}"
                finally:
                    os.unlink(temp_file)
                    
        except Exception as e:
            results[scenario_name] = f"❌ Error: {e}"
    
    # Report results
    print("\n📋 Error handling test results:")
    for scenario, result in results.items():
        print(f"   {scenario}: {result}")

async def example_6_mixed_async_sync():
    """Example 6: Mixing async and sync operations efficiently."""
    print("\n🔄 Example 6: Mixed Async/Sync Operations")
    print("-" * 40)
    
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    files = File(client)
    collections = Collection(client)
    
    try:
        print("🔄 Demonstrating mixed async/sync patterns...")
        
        # Sync operation (quick API calls)
        print("   📋 Sync: Getting file list...")
        file_list = files.get()
        print("   ✅ File list retrieved synchronously")
        
        # Async operation (potentially long-running)
        print("   ⚡ Async: Starting upload...")
        temp_file = create_test_file("Mixed operations test")
        
        async_upload_task = asyncio.create_task(
            files.async_upload_and_wait(
                temp_file,
                title="Mixed Operations Test",
                timeout=60
            )
        )
        
        # While upload is happening, do other sync work
        print("   📂 Sync: Working with collections while upload processes...")
        collection_list = collections.get()
        print("   ✅ Collection operations completed while upload in progress")
        
        # Wait for async operation to complete
        print("   ⏳ Waiting for async upload to complete...")
        upload_result = await async_upload_task
        
        upload_id = getattr(upload_result, 'id')
        print(f"   ✅ Async upload completed: File ID {upload_id}")
        
        os.unlink(temp_file)
        
        print("✅ Mixed async/sync operations completed successfully")
        
    except Exception as e:
        print(f"❌ Mixed operations failed: {e}")

async def main():
    """Run all async examples."""
    print("⚡ PIXXIO Python Client - Advanced Async Examples")
    print("=" * 60)
    print("Demonstrating concurrent operations and async job tracking.")
    
    try:
        # Run examples
        await example_1_async_file_upload()
        
        await example_2_concurrent_uploads()
        
        await example_3_async_batch_operations()
        
        await example_4_async_with_progress_monitoring()
        
        await example_5_async_error_handling()
        
        await example_6_mixed_async_sync()
        
        print("\n🎉 All async examples completed successfully!")
        print("=" * 60)
        print("Summary of what was demonstrated:")
        print("  ⚡ Async file uploads with job tracking")
        print("  📤 Concurrent file uploads for better performance")
        print("  📦 Batch operations with async processing")
        print("  📊 Progress monitoring for long operations")
        print("  🛡️ Error handling in async contexts")
        print("  🔄 Mixing async and sync operations efficiently")
        
        print("\nKey benefits of async operations:")
        print("  • Non-blocking I/O for better responsiveness")
        print("  • Concurrent operations for improved throughput") 
        print("  • Better resource utilization")
        print("  • Scalable for high-volume operations")
        
    except Exception as e:
        print(f"\n💥 Async examples failed: {e}")
        print("Check your connection and API credentials.")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())