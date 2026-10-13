#!/usr/bin/env python3
"""
Test file upload parameters to understand what the API accepts
"""

import tempfile
import os
import traceback
from pixxio_client import Client
from pixxio_client.files import File

# Test environment configuration
try:  # direct execution: python tests/<script>.py
    from credentials import require_api_key, test_host
except ImportError:  # module execution: python -m tests.<module>
    from tests.credentials import require_api_key, test_host

TEST_HOST = test_host()
TEST_API_KEY = require_api_key()

print("🧪 Testing File Upload Parameters")
print("=" * 40)

client = Client.create_client(TEST_API_KEY, TEST_HOST)
files = File(client)

# Create test file
test_content = "Test file for parameter testing"
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    f.write(test_content)
    test_file_path = f.name

try:
    # Test 1: Upload with no parameters
    print("1. Testing upload with no parameters...")
    try:
        result1 = files.upload(test_file_path)
        print(f"   ✅ Basic upload worked: {getattr(result1, 'id', 'No ID')}")
    except Exception as e:
        print(f"   ❌ Basic upload failed: {e}")
    
    # Test 2: Upload with title parameter
    print("2. Testing upload with title parameter...")
    try:
        result2 = files.upload(test_file_path, title="Test Title")
        print(f"   ✅ Title upload worked: {getattr(result2, 'id', 'No ID')}")
    except Exception as e:
        print(f"   ❌ Title upload failed: {e}")
    
    # Test 3: Upload with different common parameters
    print("3. Testing upload with other parameters...")
    try:
        result3 = files.upload(test_file_path, description="Test description")
        print(f"   ✅ Description upload worked: {getattr(result3, 'id', 'No ID')}")
    except Exception as e:
        print(f"   ❌ Description upload failed: {e}")
        
    # Test 4: Upload with keywords
    print("4. Testing upload with keywords...")
    try:
        result4 = files.upload(test_file_path, keywords="test,api")
        print(f"   ✅ Keywords upload worked: {getattr(result4, 'id', 'No ID')}")
    except Exception as e:
        print(f"   ❌ Keywords upload failed: {e}")

finally:
    os.unlink(test_file_path)

print("\nTest completed.")