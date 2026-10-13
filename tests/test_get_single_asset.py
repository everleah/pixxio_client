#!/usr/bin/env python3
"""
Test script to retrieve metadata of a single asset from PIXXIO.
Gets asset with ID: 1376045043
Credentials are read from the environment (see tests/credentials.py).
"""

import sys
import os

# Add project root to path to use local development code
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from pixxio_client import Client
from pixxio_client.files import File

# Test configuration
try:  # direct execution: python tests/<script>.py
    from credentials import require_api_key, require_test_host
except ImportError:  # module execution: python -m tests.<module>
    from tests.credentials import require_api_key, require_test_host

TEST_HOST = require_test_host()
TEST_API_KEY = require_api_key()

# Asset ID to retrieve
ASSET_ID = 1376045043


def test_get_single_asset_metadata() -> bool:
    """Test retrieving metadata of a single asset."""
    try:
        # Create client
        client = Client.create_client(TEST_API_KEY, TEST_HOST)
        files = File(client)
        
        print(f"\n🔍 Retrieving metadata for asset ID: {ASSET_ID}")
        
        #files.set_response_fields(['id',"metadata","metadataFields"])  
        
        # Get single asset metadata
        asset = files.get(ASSET_ID)
        
        if asset is None:
            print(f"❌ Asset not found")
            return False
        
        print(f"\n✅ Asset retrieved successfully!")
        print(f"\n📊 Asset Metadata:")
        print(f"{'─' * 60}")
        
        # Display available attributes
        if hasattr(asset, '__dict__'):
            # If it's a SimpleNamespace or similar object
            asset_dict = vars(asset)
        else:
            # If it's a dict
            asset_dict = asset if isinstance(asset, dict) else {}
        
        # Pretty print the metadata
        for key, value in sorted(asset_dict.items()):
            # Handle nested objects/dicts
            if isinstance(value, dict):
                print(f"  {key}: [dict with {len(value)} items]")
                for sub_key, sub_value in sorted(value.items()):
                    print(f"    - {sub_key}: {sub_value}")
            elif isinstance(value, (list, tuple)):
                if len(value) > 5:
                    print(f"  {key}: [{', '.join(str(v) for v in value[:5])}...] ({len(value)} items)")
                else:
                    print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value}")
        
        print(f"{'─' * 60}")
        
        # Display specific common fields
        # Extract file data - may be wrapped in 'file' attribute
        file_data = getattr(asset, 'file', asset)
        
        print(f"\n📋 Key Fields:")
        print(f"  ID: {getattr(file_data, 'id', 'N/A')}")
        print(f"  File Name: {getattr(file_data, 'fileName', 'N/A')}")
        print(f"  File Type: {getattr(file_data, 'fileType', 'N/A')}")
        print(f"  Subject: {getattr(file_data, 'subject', 'N/A')}")
        print(f"  Description: {getattr(file_data, 'description', 'N/A')}")
        print(f"  File Size: {getattr(file_data, 'fileSize', 'N/A')} bytes")
        print(f"  Keywords: {getattr(file_data, 'keywords', 'N/A')}")
        print(f"  Rating: {getattr(file_data, 'rating', 'N/A')}")
        print(f"  Create Date: {getattr(file_data, 'createDate', 'N/A')}")
        print(f"  Modify Date: {getattr(file_data, 'modifyDate', 'N/A')}")
        print(f"  Upload Date: {getattr(file_data, 'uploadDate', 'N/A')}")
        print(f"  File State: {getattr(file_data, 'fileState', 'N/A')}")
        print(f"  Creator: {getattr(file_data, 'creator', 'N/A')}")
        print(f"  User: {getattr(file_data, 'user', 'N/A')}")
        print(f"  Location: {getattr(file_data, 'location', 'N/A')}")
        print(f"  Directory: {getattr(file_data, 'directory', 'N/A')}")
        print(f"  Language Codes: {getattr(file_data, 'languageCodes', 'N/A')}")
        
        # Check for extended fields (GET_SINGLE only)
        print(f"\n🔧 Extended Fields (GET_SINGLE):")
        extended_fields = ['importantMetadata', 'metadata', 'metadataFields', 'unimportantMetadata', 'usePanoramaViewer']
        for field in extended_fields:
            value = getattr(file_data, field, None)
            if value is not None:
                if isinstance(value, dict):
                    print(f"  {field}: ✅ present [{len(value)} items]")
                elif isinstance(value, list):
                    print(f"  {field}: ✅ present [{len(value)} items]")
                else:
                    print(f"  {field}: ✅ {value}")
            else:
                print(f"  {field}: ⚠️  not present")
        
        return True
        
    except Exception as e:
        print(f"❌ Error retrieving asset: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("PIXXIO Single Asset Metadata Test")
    print("=" * 60)
    
    success = test_get_single_asset_metadata()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed!")
    print("=" * 60)
