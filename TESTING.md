# 🧪 Testing Guide

## Running Tests

### Quick Test
```bash
# Run all tests
make test

# Run only unit tests
make test-unit

# Run only integration tests  
make test-integration
```

### Detailed Testing
```bash
# Run with coverage report
python -m pytest tests/ -v --cov=src/pacs_map --cov-report=html

# Run specific test file
python -m pytest tests/test_coordinates.py -v

# Run specific test
python -m pytest tests/test_cli.py::TestCLI::test_stats_command -v
```

## Test Structure

### Unit Tests
- `test_coordinates.py` - Coordinate extraction from Google Maps URLs
- `test_data.py` - Data management and processing
- `test_cli.py` - Command-line interface functionality

### Integration Tests
- `test_integration.py` - End-to-end workflow testing

## Test Coverage

Current test coverage includes:
- ✅ Coordinate extraction from all URL formats
- ✅ Data loading and processing
- ✅ Priority calculation algorithms
- ✅ CLI command functionality
- ✅ Map generation pipeline
- ✅ Batch operations
- ✅ Statistics calculation
- ✅ Complete end-to-end workflows

## Adding New Tests

### For New Features
1. Add unit tests in appropriate `test_*.py` file
2. Add integration test if feature affects workflow
3. Run tests locally before committing
4. Ensure coverage remains above 80%

### Test Data
- Use temporary directories for file operations
- Mock external API calls (Google Sheets)
- Clean up test artifacts in `tearDown()`

## Continuous Integration

Tests run automatically on:
- Every pull request
- Every push to main branch
- Daily scheduled runs

See `.github/workflows/` for CI configuration.