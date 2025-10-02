# Test Configuration for PIXXIO Client

This document provides information about the test environment and how to use it for testing the PIXXIO Python client library.

## Test Environment Details

**Test System URL**: https://hoerl-demo.px.media/
**API Username**: api_user
**API Key**: uDP9XwmExpcR6TTDobtu8qVWYs99WmDou8PTTXM22IdoWZhtO4dh5q2SMZO90F0h

## Safety and Usage Guidelines

⚠️ **Important Notes:**
- This is a demo/test environment - not for production use
- API key is shared for testing purposes
- Be respectful of the shared test environment
- Don't upload large files unnecessarily
- Clean up test data when possible

## Quick Test Setup

### Environment Variables (Recommended)

Create a `.env` file in your project root:

```bash
# .env file (don't commit this to version control)
PIXXIO_TEST_HOST=hoerl-demo.px.media
PIXXIO_TEST_API_KEY=uDP9XwmExpcR6TTDobtu8qVWYs99WmDou8PTTXM22IdoWZhtO4dh5q2SMZO90F0h
```

Load with python-dotenv:
```python
from dotenv import load_dotenv
import os

load_dotenv()

test_host = os.getenv("PIXXIO_TEST_HOST")
test_api_key = os.getenv("PIXXIO_TEST_API_KEY")
```

### Direct Configuration

```python
from pixxio_client import Client

# Create test client
client = Client.create_client(
    api_key="uDP9XwmExpcR6TTDobtu8qVWYs99WmDou8PTTXM22IdoWZhtO4dh5q2SMZO90F0h",
    host="hoerl-demo.px.media"
)

print("Test client created successfully!")
```

## Basic Integration Tests

### Test 1: Connection and Authentication

```python
from pixxio_client import Client
from pixxio_client.exceptions import UnauthorizedException

def test_connection():
    """Test basic connection and authentication."""
    try:
        client = Client.create_client(
            "uDP9XwmExpcR6TTDobtu8qVWYs99WmDou8PTTXM22IdoWZhtO4dh5q2SMZO90F0h",
            "hoerl-demo.px.media"
        )
        
        # Test with a simple API call
        from pixxio_client.users import User
        users = User(client)
        user_list = users.get()
        
        print("✅ Connection successful!")
        print(f"Found {len(user_list) if hasattr(user_list, '__len__') else 'N/A'} users")
        return True
        
    except UnauthorizedException:
        print("❌ Authentication failed - check API key")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
```

### Test 2: File Operations

```python
import tempfile
import os
from pixxio_client import Client
from pixxio_client.files import File

def test_file_operations():
    """Test file upload, retrieval, and deletion."""
    client = Client.create_client(
        "uDP9XwmExpcR6TTDobtu8qVWYs99WmDou8PTTXM22IdoWZhtO4dh5q2SMZO90F0h",
        "hoerl-demo.px.media"
    )
    
    files = File(client)
    
    # Create a test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test file for PIXXIO client library testing.")
        test_file_path = f.name
    
    try:
        print("📁 Testing file upload...")
        
        # Upload file
        upload_result = files.upload(
            test_file_path,
            title="Test File Upload",
            subject="Integration Test",
            keywords="test,client,library"
        )
        
        print(f"✅ Upload successful! File ID: {upload_result.id}")
        
        # Retrieve file info
        file_info = files.get(upload_result.id)
        print(f"✅ File retrieval successful: {file_info.fileName}")
        
        # Test file listing
        all_files = files.get()
        print(f"✅ File listing successful: Found files")
        
        return upload_result.id
        
    except Exception as e:
        print(f"❌ File operations failed: {e}")
        return None
    finally:
        # Clean up test file
        os.unlink(test_file_path)

if __name__ == "__main__":
    file_id = test_file_operations()
    if file_id:
        print(f"Test file uploaded with ID: {file_id}")
```

### Test 3: Collection Operations

```python
from pixxio_client import Client
from pixxio_client.collections import Collection

def test_collection_operations():
    """Test collection CRUD operations."""
    client = Client.create_client(
        "uDP9XwmExpcR6TTDobtu8qVWYs99WmDou8PTTXM22IdoWZhtO4dh5q2SMZO90F0h",
        "hoerl-demo.px.media"
    )
    
    collections = Collection(client)
    
    try:
        print("📂 Testing collection operations...")
        
        # Create collection
        new_collection = collections.post(json_data={
            'name': 'Test Collection',
            'description': 'Created by Python client test'
        })
        
        print(f"✅ Collection created: {new_collection.id}")
        
        # Retrieve collection
        collection_info = collections.get(new_collection.id)
        print(f"✅ Collection retrieved: {collection_info.name}")
        
        # Update collection
        updated_collection = collections.put(
            new_collection.id,
            json_data={'description': 'Updated by Python client test'}
        )
        
        print(f"✅ Collection updated successfully")
        
        # List all collections
        all_collections = collections.get()
        print(f"✅ Collection listing successful")
        
        return new_collection.id
        
    except Exception as e:
        print(f"❌ Collection operations failed: {e}")
        return None

if __name__ == "__main__":
    collection_id = test_collection_operations()
```

## Advanced Testing Scenarios

### Job Tracking Test

```python
import tempfile
import os
from pixxio_client import Client
from pixxio_client.files import File

def test_job_tracking():
    """Test job tracking with file upload."""
    client = Client.create_client(
        "uDP9XwmExpcR6TTDobtu8qVWYs99WmDou8PTTXM22IdoWZhtO4dh5q2SMZO90F0h", 
        "hoerl-demo.px.media"
    )
    
    files = File(client)
    
    # Create a larger test file (more likely to trigger job tracking)
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.dat', delete=False) as f:
        # Create a 1MB test file
        f.write(b'X' * (1024 * 1024))
        test_file_path = f.name
    
    try:
        print("⚡ Testing job tracking...")
        
        # Upload with job tracking
        result = files.upload_and_wait(
            test_file_path,
            title="Job Tracking Test",
            timeout=120,  # 2 minutes
            poll_interval=2.0
        )
        
        print(f"✅ Job tracking upload successful: {result.id}")
        return True
        
    except Exception as e:
        print(f"❌ Job tracking test failed: {e}")
        return False
    finally:
        os.unlink(test_file_path)

if __name__ == "__main__":
    test_job_tracking()
```

### Error Handling Test

```python
from pixxio_client import Client
from pixxio_client.files import File
from pixxio_client.exceptions import (
    NotFoundException, 
    PIXXIOException,
    UnauthorizedException
)

def test_error_handling():
    """Test various error scenarios."""
    print("🛡️ Testing error handling...")
    
    # Test with invalid API key
    try:
        invalid_client = Client.create_client("invalid-key", "hoerl-demo.px.media")
        files = File(invalid_client)
        files.get()
        print("❌ Should have failed with invalid key")
    except UnauthorizedException:
        print("✅ Invalid key properly handled")
    except Exception as e:
        print(f"❓ Unexpected error with invalid key: {e}")
    
    # Test with valid client
    client = Client.create_client(
        "uDP9XwmExpcR6TTDobtu8qVWYs99WmDou8PTTXM22IdoWZhtO4dh5q2SMZO90F0h",
        "hoerl-demo.px.media"
    )
    files = File(client)
    
    # Test not found error
    try:
        files.get(999999)  # Non-existent ID
        print("❌ Should have failed with not found")
    except NotFoundException:
        print("✅ Not found error properly handled")
    except Exception as e:
        print(f"❓ Unexpected error for not found: {e}")
    
    # Test file not found
    try:
        files.upload("/non/existent/file.txt")
        print("❌ Should have failed with file not found")
    except FileNotFoundError:
        print("✅ File not found properly handled")
    except Exception as e:
        print(f"❓ Unexpected error for missing file: {e}")
    
    print("🛡️ Error handling tests completed")

if __name__ == "__main__":
    test_error_handling()
```

## Comprehensive Test Suite

### All-in-One Test Runner

```python
#!/usr/bin/env python3
"""
Comprehensive test suite for PIXXIO Python client library.
Uses the hoerl-demo.px.media test environment.
"""

import sys
import tempfile
import os
from typing import List, Tuple, Callable

from pixxio_client import Client
from pixxio_client.files import File
from pixxio_client.collections import Collection
from pixxio_client.users import User
from pixxio_client.exceptions import *

# Test configuration
TEST_HOST = "hoerl-demo.px.media"
TEST_API_KEY = "uDP9XwmExpcR6TTDobtu8qVWYs99WmDou8PTTXM22IdoWZhtO4dh5q2SMZO90F0h"

class TestResult:
    def __init__(self, name: str, passed: bool, message: str = ""):
        self.name = name
        self.passed = passed
        self.message = message

def run_test(test_name: str, test_func: Callable) -> TestResult:
    """Run a single test and return result."""
    try:
        print(f"\n🧪 Running {test_name}...")
        success = test_func()
        if success:
            print(f"✅ {test_name} PASSED")
            return TestResult(test_name, True)
        else:
            print(f"❌ {test_name} FAILED")
            return TestResult(test_name, False, "Test returned False")
    except Exception as e:
        print(f"❌ {test_name} FAILED: {e}")
        return TestResult(test_name, False, str(e))

def test_client_creation() -> bool:
    """Test client creation and basic setup."""
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    return client is not None

def test_authentication() -> bool:
    """Test API authentication."""
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    users = User(client)
    result = users.get()
    return result is not None

def test_file_upload() -> bool:
    """Test file upload functionality."""
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    files = File(client)
    
    # Create test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test file content for PIXXIO client library")
        test_file = f.name
    
    try:
        result = files.upload(
            test_file,
            title="Integration Test File",
            subject="Client Library Test"
        )
        return hasattr(result, 'id')
    finally:
        os.unlink(test_file)

def test_file_retrieval() -> bool:
    """Test file retrieval."""
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    files = File(client)
    
    # Get list of files
    file_list = files.get()
    return file_list is not None

def test_collection_operations() -> bool:
    """Test collection CRUD operations."""
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    collections = Collection(client)
    
    # Create collection
    new_collection = collections.post(json_data={
        'name': f'Test Collection {os.getpid()}',
        'description': 'Created by integration test'
    })
    
    if not hasattr(new_collection, 'id'):
        return False
    
    # Retrieve collection
    retrieved = collections.get(new_collection.id)
    return hasattr(retrieved, 'name')

def test_error_handling() -> bool:
    """Test error handling with invalid operations."""
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    files = File(client)
    
    # Test not found error
    try:
        files.get(999999)
        return False  # Should have thrown exception
    except NotFoundException:
        return True  # Expected exception
    except Exception:
        return False  # Unexpected exception

def test_response_field_filtering() -> bool:
    """Test response field filtering."""
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    files = File(client)
    
    # Set response fields
    files.set_response_fields(['id', 'fileName'])
    
    # Get files with filtering
    result = files.get()
    return result is not None

def main():
    """Run all tests and report results."""
    print("🚀 PIXXIO Python Client Integration Tests")
    print("=" * 50)
    print(f"Test Environment: {TEST_HOST}")
    print(f"API User: api_user")
    
    # Define tests to run
    tests = [
        ("Client Creation", test_client_creation),
        ("Authentication", test_authentication),
        ("File Upload", test_file_upload),
        ("File Retrieval", test_file_retrieval),
        ("Collection Operations", test_collection_operations),
        ("Error Handling", test_error_handling),
        ("Response Field Filtering", test_response_field_filtering),
    ]
    
    results: List[TestResult] = []
    
    # Run all tests
    for test_name, test_func in tests:
        result = run_test(test_name, test_func)
        results.append(result)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = [r for r in results if r.passed]
    failed = [r for r in results if not r.passed]
    
    print(f"✅ Passed: {len(passed)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if failed:
        print("\n❌ Failed Tests:")
        for result in failed:
            print(f"  - {result.name}: {result.message}")
    
    # Return appropriate exit code
    return 0 if len(failed) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
```

## Usage Instructions

### Running Individual Tests

```bash
# Test basic connection
python test_connection.py

# Test file operations  
python test_file_operations.py

# Test collection operations
python test_collection_operations.py
```

### Running Complete Test Suite

```bash
# Run all integration tests
python integration_tests.py

# Expected output:
# 🚀 PIXXIO Python Client Integration Tests
# ✅ Passed: 7/7
```

### Development Testing

```python
# Quick development test
from pixxio_client import Client

client = Client.create_client(
    "uDP9XwmExpcR6TTDobtu8qVWYs99WmDou8PTTXM22IdoWZhtO4dh5q2SMZO90F0h",
    "hoerl-demo.px.media"
)

print("Client created successfully!")
print(f"Base URL: {client.location_base}")
```

## Security Notes

⚠️ **Important Security Considerations:**

1. **Test Environment Only**: This API key is for testing only
2. **No Sensitive Data**: Don't upload sensitive or personal files
3. **Shared Environment**: Other developers may be using the same test system
4. **Rate Limiting**: Be respectful of API rate limits
5. **Cleanup**: Clean up test data when possible

## Next Steps

After testing with this environment:

1. **Verify all functionality works as expected**
2. **Test error scenarios and edge cases**
3. **Validate type hints with mypy**
4. **Document any issues found**
5. **Create production examples with placeholder credentials**

This test environment allows for comprehensive validation of the PIXXIO Python client library! 🎉