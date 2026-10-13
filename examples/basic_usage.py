#!/usr/bin/env python3
"""
Basic usage examples for PIXXIO Python client library.
Demonstrates core functionality with the test environment.
"""

import tempfile
import os
from pixxio_client import Client
from pixxio_client.files import File
from pixxio_client.collections import Collection, CollectionCreateBuilder, CollectionUpdateBuilder
from pixxio_client.exceptions import PIXXIOException, NotFoundException

# Test environment configuration
# Credentials are read from the environment; see .env.example and docs/TEST_ENVIRONMENT.md.
TEST_HOST = os.environ.get("PIXXIO_TEST_HOST", "hoerl-demo.px.media")
TEST_API_KEY = os.environ.get("PIXXIO_TEST_API_KEY", "")
if not TEST_API_KEY:
    raise SystemExit("PIXXIO_TEST_API_KEY is not set; see docs/TEST_ENVIRONMENT.md.")

def example_1_basic_setup():
    """Example 1: Basic client setup and connection."""
    print("\n📋 Example 1: Basic Client Setup")
    print("-" * 40)
    
    # Create client
    client = Client.create_client(TEST_API_KEY, TEST_HOST)
    print(f"✅ Client created with base URL: {client.location_base}")
    
    # You can also create client manually for more control
    from pixxio_client import Authentication
    auth = Authentication(TEST_API_KEY)
    manual_client = Client(auth, TEST_HOST)
    print(f"✅ Manual client created: {manual_client.location_base}")
    
    return client

def example_2_file_operations(client):
    """Example 2: File upload, retrieval, and listing."""
    print("\n📁 Example 2: File Operations")
    print("-" * 40)
    
    files = File(client)
    
    # Create a test file
    test_content = "Hello from PIXXIO Python client!\nThis is a test file."
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        test_file_path = f.name
    
    try:
        # Upload file
        print("📤 Uploading file...")
        upload_result = files.upload(
            test_file_path,
            description="Example Upload - Python Client Demo",
            subject="Python Client Demo",
            keywords="python,client,example,demo"
        )
        
        file_id = getattr(upload_result, 'id')
        print(f"✅ File uploaded successfully! ID: {file_id}")
        
        # Get file information
        print("📄 Retrieving file information...")
        file_info = files.get(file_id)
        file_name = getattr(file_info, 'fileName', 'Unknown')
        file_size = getattr(file_info, 'fileSize', 'Unknown')
        print(f"✅ File info: {file_name} ({file_size} bytes)")
        
        # List recent files
        print("📋 Listing files...")
        all_files = files.get()
        print(f"✅ File listing retrieved")
        
        return file_id
        
    except Exception as e:
        print(f"❌ File operations failed: {e}")
        return None
    finally:
        # Clean up local test file
        os.unlink(test_file_path)

def example_3_collections(client):
    """Example 3: Working with collections."""
    print("\n📂 Example 3: Collection Operations")
    print("-" * 40)
    
    collections = Collection(client)
    
    try:
        # Create a new collection using the builder
        print("📂 Creating collection...")
        new_collection = collections.create(
            **CollectionCreateBuilder()
                .name(f'Python Client Example {int(os.getpid())}')
                .description('Collection created by Python client example')
                .build()
        )
        collection_id = getattr(new_collection, 'id')
        print(f"✅ Collection created! ID: {collection_id}")
        
        # Retrieve collection information
        print("📖 Retrieving collection...")
        collection_info = collections.get(collection_id)
        collection_name = getattr(collection_info, 'name', 'Unknown')
        print(f"✅ Collection retrieved: {collection_name}")
        
        # Update collection using the builder
        print("📝 Updating collection...")
        collections.update(
            collection_id,
            **CollectionUpdateBuilder()
                .description('Updated by Python client example')
                .build()
        )
        print(f"✅ Collection updated successfully")
        
        # List all collections
        print("📋 Listing collections...")
        all_collections = collections.list()
        print(f"✅ Collection listing retrieved")
        
        return collection_id
        
    except Exception as e:
        print(f"❌ Collection operations failed: {e}")
        return None

def example_4_error_handling(client):
    """Example 4: Proper error handling."""
    print("\n🛡️ Example 4: Error Handling")
    print("-" * 40)
    
    files = File(client)
    
    # Example 1: Handle not found error
    try:
        print("🔍 Attempting to get non-existent file...")
        files.get(999999999)  # This should fail
        
    except NotFoundException:
        print("✅ NotFoundException handled correctly")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Example 2: Handle file not found error
    try:
        print("📁 Attempting to upload non-existent file...")
        files.upload("/this/file/does/not/exist.txt")
        
    except FileNotFoundError:
        print("✅ FileNotFoundError handled correctly")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Example 3: Generic PIXXIO error handling
    try:
        # This demonstrates how to catch any PIXXIO API error
        result = files.get()  # This should work
        print("✅ API call successful")
        
    except PIXXIOException as e:
        print(f"❌ PIXXIO API Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def example_5_response_filtering(client):
    """Example 5: Response field filtering for performance."""
    print("\n🔍 Example 5: Response Field Filtering")
    print("-" * 40)
    
    files = File(client)
    
    # Set specific fields to reduce bandwidth and improve performance
    print("⚙️ Setting response fields...")
    files.set_response_fields(['id', 'fileName', 'fileSize'])
    
    # Now API calls will only return these fields
    print("📋 Getting files with filtering...")
    filtered_files = files.get()
    print("✅ Filtered response received (only requested fields)")
    
    # Add another field
    files.set_response_field('subject')
    print("➕ Added 'subject' to response fields")
    
    # Reset filtering to get all fields
    files.set_response_fields([])
    print("🔄 Reset filtering to get all fields")
    
    full_files = files.get()
    print("✅ Full response received (all fields)")

def example_6_job_tracking(client):
    """Example 6: Job tracking for long-running operations."""
    print("\n⚡ Example 6: Job Tracking")
    print("-" * 40)
    
    files = File(client)
    
    # Create a test file that might trigger processing
    test_content = "X" * (50 * 1024)  # 50KB file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        test_file_path = f.name
    
    try:
        print("⚡ Uploading with job tracking...")
        
        # Upload file with job tracking
        result = files.upload_and_wait(
            test_file_path,
            description="Job Tracking Example",
            timeout=60,  # Wait up to 1 minute
            poll_interval=2.0  # Check every 2 seconds
        )
        
        result_id = getattr(result, 'id')
        print(f"✅ Upload with job tracking completed! File ID: {result_id}")
        
    except Exception as e:
        print(f"❌ Job tracking upload failed: {e}")
        
    finally:
        os.unlink(test_file_path)

def main():
    """Run all examples."""
    print("🎯 PIXXIO Python Client - Basic Examples")
    print("=" * 50)
    print("This demonstrates core functionality using the test environment.")
    
    try:
        # Setup
        client = example_1_basic_setup()
        
        # File operations
        file_id = example_2_file_operations(client)
        
        # Collection operations
        collection_id = example_3_collections(client)
        
        # Error handling
        example_4_error_handling(client)
        
        # Response filtering
        example_5_response_filtering(client)
        
        # Job tracking
        example_6_job_tracking(client)
        
        print("\n🎉 All examples completed successfully!")
        print("=" * 50)
        print("Summary of what was demonstrated:")
        print("  ✅ Client creation and authentication")
        print("  ✅ File upload, retrieval, and listing")
        print("  ✅ Collection CRUD operations")
        print("  ✅ Proper error handling patterns")
        print("  ✅ Response field filtering for performance")
        print("  ✅ Job tracking for long-running operations")
        
        if file_id:
            print(f"\n📄 Test file uploaded: ID {file_id}")
        if collection_id:
            print(f"📂 Test collection created: ID {collection_id}")
            
        print("\nNext steps:")
        print("  • Try modifying these examples")
        print("  • Run the full integration test suite")
        print("  • Check out advanced examples")
        print("  • Build your own PIXXIO integration!")
        
    except Exception as e:
        print(f"\n💥 Example execution failed: {e}")
        print("Check your connection and API credentials.")

if __name__ == "__main__":
    main()