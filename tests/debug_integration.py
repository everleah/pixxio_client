#!/usr/bin/env python3
"""
Debug version of integration tests to see response structure
"""

import traceback
from pixxio_client import Client
from pixxio_client.files import File
from pixxio_client.collections import Collection

# Test environment configuration
try:  # direct execution: python tests/<script>.py
    from credentials import require_api_key, test_host
except ImportError:  # module execution: python -m tests.<module>
    from tests.credentials import require_api_key, test_host

TEST_HOST = test_host()
TEST_API_KEY = require_api_key()

print("🔍 Debug Integration Test")
print("=" * 40)

# Test 1: Check Collections.get() 
try:
    print("1. Testing collections.get()...")
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    collections = Collection(client)
    
    print("   Making request...")
    result = collections.get()
    print(f"   ✅ Success: {type(result)}")
    print(f"   Result attributes: {dir(result)}")
    print(f"   Result: {result}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("   Full traceback:")
    traceback.print_exc()

# Test 2: Check invalid request - let's intercept the response
try:
    print("\n2. Testing invalid request...")
    files = File(client)
    
    # Test individual file request via our method
    try:
        result = files.get(id=999999999)
        print(f"   Unexpected success: {result}")
    except Exception as individual_error:
        print(f"   Individual file error: {individual_error}")
        
    # Let's manually make the request to see what we get without pagination
    response = client.session.get(f"{client.location_base}/files/999999999")
    print(f"   Raw response status: {response.status_code}")
    print(f"   Raw response text: {response.text[:200]}...")
    
    # Now try the parsed version
    if response.text:
        from pixxio_client._base import Objectifier
        response_obj = Objectifier.from_json_str(response.text)
        print(f"   Parsed response: {response_obj}")
        print(f"   Response attributes: {dir(response_obj)}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("   Full traceback:")
    traceback.print_exc()

# Test 3: Check collections post
try:
    print("\n3. Testing collection creation...")
    
    result = collections.post(json_data={'name': 'Debug Test Collection'})
    print(f"   ✅ Success: {type(result)}")
    print(f"   Result: {result}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    print(f"   Error type: {type(e)}")
    print("   Full traceback:")
    traceback.print_exc()