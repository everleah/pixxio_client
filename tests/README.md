# PIXXIO Client Test Suite

This directory contains various test files for the PIXXIO Python client library.

## Integration Tests

### `integration_tests.py`
**Main comprehensive test suite** - Run this to verify all client functionality works correctly.
- Tests all major API endpoints (files, collections, users, etc.)
- Validates CRUD operations, file uploads, job tracking
- Uses live test environment (<your-test-host>)
- Returns detailed test results with pass/fail status

**Usage:**
```bash
python tests/integration_tests.py
```

### `quick_test.py`
**Quick functionality test** - Fast verification that basic operations work.
- Basic connection test
- Simple file and user operations
- Good for quick smoke testing

**Usage:**
```bash
python tests/quick_test.py
```

## Debug Tests

### `debug_test.py`
**Basic debug test** - Minimal test to identify connection issues.
- Tests client creation
- Validates basic API connectivity
- Useful for troubleshooting setup problems

### `debug_integration.py`
**Debug version of integration tests** - Shows detailed response structure.
- Similar to integration_tests.py but with verbose output
- Displays raw API responses for debugging
- Helps understand API response formats

## Specific Feature Tests

### `test_auth_error.py`
**Authentication testing** - Tests invalid API key handling.
- Verifies proper exception types for auth failures
- Tests error response parsing

### `test_upload_params.py`
**File upload parameter testing** - Tests file upload functionality.
- Validates upload parameter handling
- Tests file upload with various options
- Temporary file creation and cleanup

### `test_upload_with_metadata.py`
**Upload with metadata** - Exercises standard/custom metadata handling during upload.

### `test_get_single_asset.py`
**Single asset lookup** - Retrieves the metadata of one asset by ID.

### `test_metadata_standard_requests.py`
**Raw standard-metadata probe** - Uses `requests` directly against the standard metadata endpoint to compare `responseFields` encodings.

## Offline Unit Tests

These do not need network access or credentials:

### `response_fields_injection_checks.py`
**Response field injection** - Verifies `responseFields` injection and the opt-out behavior for endpoints that do not support it.

### `test_webhook_parser_generalized.py`
**Webhook parser** - Verifies the generalized parser against real payload shapes.

```bash
python -m unittest tests.response_fields_injection_checks tests.test_webhook_parser_generalized -v
```

## Test Configuration

Credentials are read from the environment and are never stored in the repository
(see [credentials.py](credentials.py)):

- **Host:** `PIXXIO_TEST_HOST`, defaults to `<your-test-host>`
- **API Key:** `PIXXIO_TEST_API_KEY`, required — ask a maintainer for access
- **Environment:** Live PIXXIO test system

```bash
# Windows PowerShell
$env:PIXXIO_TEST_API_KEY = "<key>"

# bash
export PIXXIO_TEST_API_KEY="<key>"
```

See [../docs/TEST_ENVIRONMENT.md](../docs/TEST_ENVIRONMENT.md) for details about the
shared system.

## Running Tests

### Run All Integration Tests
```bash
# From project root
python tests/integration_tests.py
```

### Run Quick Test
```bash
python tests/quick_test.py
```

### Run Specific Tests
```bash
python tests/debug_test.py
python tests/test_auth_error.py
python tests/test_upload_params.py
```

## Test Results

Integration tests provide structured output:
- ✅ Pass: Operation completed successfully  
- ❌ Fail: Operation failed with error details
- 🕒 Timeout: Operation timed out (may still be processing)

## Notes

- Tests use live API endpoints - require valid network connection
- Some tests create temporary files that are automatically cleaned up
- Upload tests may take longer due to file processing time
- All tests are designed to be non-destructive to the test environment

For examples of how to use the PIXXIO client library, see the `examples/` directory.