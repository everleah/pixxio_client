#!/usr/bin/env python3
"""
Debug test to identify issues with the PIXXIO client.
"""

import traceback
from pixxio_client import Client

# Test environment configuration
try:  # direct execution: python tests/<script>.py
    from credentials import require_api_key, test_host
except ImportError:  # module execution: python -m tests.<module>
    from tests.credentials import require_api_key, test_host

TEST_HOST = test_host()
TEST_API_KEY = require_api_key()

print("🔍 PIXXIO Debug Test")
print("=" * 40)

try:
    print("1. Creating client...")
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    print(f"   ✅ Client created: {client}")
    print(f"   📍 Base URL: {client.location_base}")
    print(f"   🔑 Has auth: {client.authentication is not None}")
    
    print("\n2. Testing direct session access...")
    print(f"   Session: {client.session}")
    print(f"   Session headers: {client.session.headers}")
    
    print("\n3. Testing simple files access...")
    from pixxio_client.files import File
    files = File(client)
    print(f"   Files object: {files}")
    print(f"   Endpoint base: {files.endpoint_base}")
    
    print("\n4. Making a simple GET request...")
    # Try to make the simplest possible request with required parameters  
    response = client.session.get(f"{client.location_base}/files", params={"page": 1, "pageSize": 10})
    print(f"   Raw response: {response}")
    print(f"   Status code: {response.status_code}")
    print(f"   Response headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("   ✅ Basic API access working!")
        
        print("\n5. Testing Files.get() method...")
        try:
            result = files.get()
            print(f"   ✅ Files.get() worked: {type(result)}")
            print(f"   Result: {result}")
        except Exception as files_error:
            print(f"   ❌ Files.get() failed: {files_error}")
            import traceback
            traceback.print_exc()
    else:
        print(f"   ❌ API returned status {response.status_code}")
        print(f"   Response text: {response.text[:200]}...")
        
except Exception as e:
    print(f"\n💥 Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()