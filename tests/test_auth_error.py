#!/usr/bin/env python3
"""
Test what type of exception is raised for invalid authentication
"""

import traceback
from pixxio_client import Client
from pixxio_client.users import User

try:  # direct execution: python tests/<script>.py
    from credentials import require_test_host
except ImportError:  # module execution: python -m tests.<module>
    from tests.credentials import require_test_host

# Only the host is needed; this test intentionally uses an invalid key.
TEST_HOST = require_test_host()

print("🔍 Testing Invalid Authentication")
print("=" * 40)

try:
    invalid_client = Client.create_client("invalid-key-12345", TEST_HOST)
    
    # Let's make a manual request to see the status code
    response = invalid_client.session.get(f"{invalid_client.location_base}/users", 
                                         params={'page': 1, 'pageSize': 10})
    print(f"Manual request status: {response.status_code}")
    print(f"Manual request text: {response.text[:200]}...")
    
    users = User(invalid_client)
    result = users.get()
    print(f"❌ Unexpected success: {result}")
except Exception as e:
    print(f"✅ Exception caught: {type(e)}")
    print(f"   Message: {e}")
    print(f"   Has response: {hasattr(e, 'response')}")
    if hasattr(e, 'response') and getattr(e, 'response', None):
        response = getattr(e, 'response')
        print(f"   Status code: {response.status_code}")
        print(f"   Response text: {response.text[:100]}...")
    print("   Full traceback:")
    traceback.print_exc()