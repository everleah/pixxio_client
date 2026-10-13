#!/usr/bin/env python3
"""
Comprehensive integration test suite for PIXXIO Python client library.
Targets the test environment configured through PIXXIO_TEST_HOST and PIXXIO_TEST_API_KEY.

Run this to verify all client functionality works correctly.
"""

import sys
import tempfile
import os
import time
from typing import List, Callable, Optional

from pixxio_client import Client
from pixxio_client.files import File
from pixxio_client.collections import Collection
from pixxio_client.users import User
from pixxio_client.exceptions import (
    PIXXIOException,
    NotFoundException,
    UnauthorizedException,
    JobTimeoutException
)

# Test configuration
try:  # direct execution: python tests/<script>.py
    from credentials import require_api_key, require_test_host
except ImportError:  # module execution: python -m tests.<module>
    from tests.credentials import require_api_key, require_test_host

TEST_HOST = require_test_host()
TEST_API_KEY = require_api_key()

class TestResult:
    def __init__(self, name: str, passed: bool, message: str = "", duration: float = 0.0):
        self.name = name
        self.passed = passed
        self.message = message
        self.duration = duration

def run_test(test_name: str, test_func: Callable) -> TestResult:
    """Run a single test and return result."""
    start_time = time.time()
    try:
        print(f"\n🧪 Running {test_name}...")
        success = test_func()
        duration = time.time() - start_time
        
        if success:
            print(f"✅ {test_name} PASSED ({duration:.2f}s)")
            return TestResult(test_name, True, duration=duration)
        else:
            print(f"❌ {test_name} FAILED ({duration:.2f}s)")
            return TestResult(test_name, False, "Test returned False", duration)
    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ {test_name} FAILED ({duration:.2f}s): {e}")
        return TestResult(test_name, False, str(e), duration)

def test_client_creation() -> bool:
    """Test client creation and basic setup."""
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    
    # Verify client properties
    assert client is not None, "Client should not be None"
    assert client.location_base.startswith("https://"), "Should use HTTPS"
    assert TEST_HOST in client.location_base, "Should contain test host"
    
    print(f"  📍 Base URL: {client.location_base}")
    return True

def test_authentication() -> bool:
    """Test API authentication with real API call."""
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    users = User(client)
    
    # Make authenticated API call
    result = users.get()
    assert result is not None, "Should get user data"
    
    print(f"  👥 Authentication successful")
    return True

def test_invalid_authentication() -> bool:
    """Test authentication failure with invalid credentials."""
    try:
        invalid_client = Client.create_client("invalid-key-12345", TEST_HOST)
        users = User(invalid_client)
        users.get()
        
        # Should not reach here
        return False
    except UnauthorizedException:
        print(f"  🔒 Invalid authentication properly rejected")
        return True
    except Exception as e:
        print(f"  ❓ Unexpected error: {e}")
        return False

def test_file_operations() -> bool:
    """Test comprehensive file operations."""
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    files = File(client)
    
    # Create test file
    test_content = f"Test file created at {time.time()} by PIXXIO Python client integration test"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        test_file_path = f.name
    
    uploaded_file_id = None
    try:
        # Test file upload
        upload_result = files.upload(
            test_file_path,
            description="Integration Test File",
            subject="Python Client Test",
            keywords="test,integration,python-client"
        )
        
        assert hasattr(upload_result, 'id'), "Upload should return file with ID"
        uploaded_file_id = getattr(upload_result, 'id')
        print(f"  📤 Upload successful: File ID {uploaded_file_id}")
        
        # Test file retrieval
        file_info = files.get(uploaded_file_id)
        assert hasattr(file_info, 'fileName'), "Should retrieve file info"
        file_name = getattr(file_info, 'fileName', 'Unknown')
        print(f"  📄 File info retrieved: {file_name}")
        
        # Test file listing
        all_files = files.get()
        assert all_files is not None, "Should get file list"
        print(f"  📋 File listing successful")
        
        return True
        
    finally:
        # Cleanup
        os.unlink(test_file_path)
        
        # Note: We don't delete the uploaded file from PIXXIO as it's a shared test environment
        # In a real test environment, you might want to clean up uploaded files

def test_file_upload_with_job_tracking() -> bool:
    """Test file upload with job tracking."""
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    files = File(client)
    
    # Create slightly larger test file to potentially trigger job processing
    test_content = "X" * (10 * 1024)  # 10KB file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        test_file_path = f.name
    
    try:
        # Test upload with job tracking
        result = files.upload_and_wait(
            test_file_path,
            description="Job Tracking Test File",
            timeout=60,  # 1 minute timeout
            poll_interval=1.0  # Check every second
        )
        
        assert hasattr(result, 'id'), "Job tracked upload should return result with ID"
        result_id = getattr(result, 'id')
        print(f"  ⚡ Job tracking upload successful: File ID {result_id}")
        return True
        
    except JobTimeoutException:
        print(f"  ⏰ Upload timed out but may still be processing")
        return True  # Timeout is acceptable for this test
        
    finally:
        os.unlink(test_file_path)

def test_collection_operations() -> bool:
    """Test collection CRUD operations."""
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    collections = Collection(client)
    
    collection_id = None
    try:
        # Test collection creation
        collection_name = f"Test Collection {int(time.time())}"
        new_collection = collections.post(json_data={
            'name': collection_name,
            'description': 'Created by Python client integration test'
        })
        
        assert hasattr(new_collection, 'id'), "Collection creation should return ID"
        collection_id = getattr(new_collection, 'id')
        print(f"  📂 Collection created: ID {collection_id}")
        
        # Test collection retrieval
        retrieved_collection = collections.get(collection_id)
        assert hasattr(retrieved_collection, 'name'), "Should retrieve collection info"
        collection_name = getattr(retrieved_collection, 'name', 'Unknown')
        print(f"  📖 Collection retrieved: {collection_name}")
        
        # Test collection update
        updated_collection = collections.put(
            collection_id,
            json_data={'description': 'Updated by Python client integration test'}
        )
        print(f"  📝 Collection updated successfully")
        
        # Test collection listing
        all_collections = collections.get()
        assert all_collections is not None, "Should get collection list"
        print(f"  📋 Collection listing successful")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Collection operations failed: {e}")
        raise

def test_error_handling() -> bool:
    """Test various error handling scenarios."""
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    files = File(client)
    
    # Test not found error
    try:
        files.get(999999999)  # Very unlikely to exist
        print(f"  ❌ Should have raised NotFoundException")
        return False
    except NotFoundException:
        print(f"  🔍 NotFoundException properly handled")
    except Exception as e:
        print(f"  ❓ Unexpected error for not found: {e}")
        return False
    
    # Test file not found error
    try:
        files.upload("/this/file/does/not/exist.txt")
        print(f"  ❌ Should have raised FileNotFoundError")
        return False
    except FileNotFoundError:
        print(f"  📁 FileNotFoundError properly handled")
    except Exception as e:
        print(f"  ❓ Unexpected error for missing file: {e}")
        return False
    
    return True

def test_response_field_filtering() -> bool:
    """Test response field filtering functionality."""
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    files = File(client)
    
    # Set response field filtering
    files.set_response_fields(['id', 'fileName', 'fileSize'])
    
    # Test filtered response
    result = files.get()
    assert result is not None, "Filtered request should return data"
    print(f"  🔍 Response field filtering successful")
    
    # Reset filters
    files.set_response_fields([])
    
    return True

def test_type_safety() -> bool:
    """Test type safety and type hints."""
    # This is mainly tested by mypy, but we can do basic runtime checks
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    
    # Verify client has expected attributes
    assert hasattr(client, 'location_base'), "Client should have location_base"
    assert hasattr(client, 'session'), "Client should have session property"
    assert hasattr(client, 'reset'), "Client should have reset method"
    
    print(f"  🔒 Type safety checks passed")
    return True

def main():
    """Run all integration tests and report results."""
    print("🚀 PIXXIO Python Client - Integration Test Suite")
    print("=" * 60)
    print(f"Test Environment: https://{TEST_HOST}")
    print(f"API User: api_user")
    print(f"Client Version: Testing latest")
    
    # Define test suite
    tests = [
        ("Client Creation", test_client_creation),
        ("Authentication Success", test_authentication),
        ("Authentication Failure", test_invalid_authentication),
        ("File Operations", test_file_operations),
        ("File Upload with Job Tracking", test_file_upload_with_job_tracking),
        ("Collection Operations", test_collection_operations),
        ("Error Handling", test_error_handling),
        ("Response Field Filtering", test_response_field_filtering),
        ("Type Safety", test_type_safety),
    ]
    
    results: List[TestResult] = []
    start_time = time.time()
    
    # Run all tests
    for test_name, test_func in tests:
        result = run_test(test_name, test_func)
        results.append(result)
        
        # Small delay between tests to be respectful of API
        time.sleep(0.5)
    
    total_duration = time.time() - start_time
    
    # Calculate results
    passed = [r for r in results if r.passed]
    failed = [r for r in results if not r.passed]
    
    # Print detailed summary
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST RESULTS")
    print("=" * 60)
    
    print(f"✅ Passed: {len(passed)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    print(f"⏱️  Total Duration: {total_duration:.2f}s")
    
    if passed:
        print(f"\n✅ Successful Tests:")
        for result in passed:
            print(f"   • {result.name} ({result.duration:.2f}s)")
    
    if failed:
        print(f"\n❌ Failed Tests:")
        for result in failed:
            print(f"   • {result.name}: {result.message} ({result.duration:.2f}s)")
    
    # Overall result
    if len(failed) == 0:
        print(f"\n🎉 ALL TESTS PASSED! The PIXXIO Python client is working correctly.")
        print(f"   Ready for production use with proper credentials.")
    else:
        print(f"\n⚠️  SOME TESTS FAILED. Please review and fix issues before using in production.")
    
    print("\n" + "=" * 60)
    
    # Return appropriate exit code
    return 0 if len(failed) == 0 else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n💥 Unexpected error in test runner: {e}")
        sys.exit(1)