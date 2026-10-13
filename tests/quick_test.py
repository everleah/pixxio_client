#!/usr/bin/env python3
"""
Quick test script to verify PIXXIO Python client works with test environment.
Run this to do a basic connection and functionality test.
"""

from pixxio_client import Client
from pixxio_client.files import File
from pixxio_client.users import User
from pixxio_client.exceptions import PIXXIOException

# Test environment configuration
try:  # direct execution: python tests/<script>.py
    from credentials import require_api_key, test_host
except ImportError:  # module execution: python -m tests.<module>
    from tests.credentials import require_api_key, test_host

TEST_HOST = test_host()
TEST_API_KEY = require_api_key()

def main():
    """Quick connection and functionality test."""
    print("🚀 PIXXIO Python Client - Quick Test")
    print("=" * 40)
    
    try:
        # Test 1: Client creation
        print("1️⃣  Creating client...")
        client = Client.create_client(TEST_API_KEY, TEST_HOST)
        print(f"   ✅ Client created successfully")
        print(f"   📍 Base URL: {client.location_base}")
        
        # Test 2: Authentication test
        print("\n2️⃣  Testing authentication...")
        users = User(client)
        user_data = users.get()
        print(f"   ✅ Authentication successful")
        
        # Test 3: File listing test
        print("\n3️⃣  Testing file operations...")
        files = File(client)
        file_list = files.get()
        print(f"   ✅ File listing successful")
        
        # Test 4: Response field filtering
        print("\n4️⃣  Testing response filtering...")
        files.set_response_fields(['id', 'fileName'])
        filtered_files = files.get()
        print(f"   ✅ Response filtering successful")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("   The PIXXIO Python client is working correctly.")
        print("   Ready to run full integration tests or use in your applications.")
        
        return True
        
    except PIXXIOException as e:
        print(f"\n❌ PIXXIO API Error: {e}")
        print("   Check your API key and network connection.")
        return False
        
    except Exception as e:
        print(f"\n💥 Unexpected Error: {e}")
        print("   There may be an issue with the client library.")
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 40)
    
    if success:
        print("✅ Quick test completed successfully!")
        print("\nNext steps:")
        print("  • Run full integration tests: python integration_tests.py")
        print("  • Check out examples in the documentation")
        print("  • Start building your PIXXIO integration!")
    else:
        print("❌ Quick test failed!")
        print("\nTroubleshooting:")
        print("  • Check your internet connection")
        print("  • Verify the test environment is accessible")
        print("  • Review any error messages above")
    
    exit(0 if success else 1)