#!/usr/bin/env python3
"""
Comprehensive system test for the new PACS Dog Map structure
"""

import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

def test_project_structure():
    """Test that all required directories and files exist"""
    print("🔍 Testing project structure...")
    
    required_paths = [
        "src/pacs_map/__init__.py",
        "src/pacs_map/cli.py", 
        "src/pacs_map/config.py",
        "src/pacs_map/core.py",
        "src/pacs_map/data.py",
        "src/pacs_map/coordinates.py",
        "src/pacs_map/operations.py",
        "tests/test_coordinates.py",
        "tests/test_data.py", 
        "tests/test_cli.py",
        "tests/test_integration.py",
        "pacs-map",
        "pyproject.toml",
        "Makefile",
        "README.md",
        "data/",
        "web/",
        "scripts/",
        ".github/workflows/update-map.yml"
    ]
    
    missing = []
    for path in required_paths:
        if not os.path.exists(path):
            missing.append(path)
    
    if missing:
        print(f"❌ Missing paths: {missing}")
        return False
    
    print("✅ Project structure is complete")
    return True

def test_cli_executable():
    """Test that CLI is executable and functional"""
    print("🔍 Testing CLI executable...")
    
    try:
        # Test help command
        result = subprocess.run(["./pacs-map", "--help"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"❌ CLI help failed: {result.stderr}")
            return False
        
        if "PACS Dog Map" not in result.stdout:
            print("❌ CLI help output incorrect")
            return False
        
        print("✅ CLI is executable and functional")
        return True
        
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def test_package_imports():
    """Test that all package imports work"""
    print("🔍 Testing package imports...")
    
    try:
        sys.path.insert(0, 'src')
        
        from pacs_map import PacsMapGenerator, DataManager, CoordinateExtractor
        from pacs_map.config import Config
        from pacs_map.cli import CLI
        
        print("✅ All package imports successful")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_coordinate_extraction():
    """Test coordinate extraction functionality"""
    print("🔍 Testing coordinate extraction...")
    
    try:
        sys.path.insert(0, 'src')
        from pacs_map.coordinates import CoordinateExtractor
        
        extractor = CoordinateExtractor()
        
        # Test various URL formats
        test_urls = [
            ("https://www.google.com/maps/@9.7282,99.9915251,17z", (9.7282, 99.9915251)),
            ("https://www.google.com/maps/search/9.748065,+99.975760", (9.748065, 99.975760)),
            ("invalid_url", (None, None))
        ]
        
        for url, expected in test_urls:
            lat, lng = extractor.extract_from_url(url)
            if expected == (None, None):
                if lat is not None or lng is not None:
                    print(f"❌ Expected None for invalid URL, got {lat}, {lng}")
                    return False
            else:
                if abs(lat - expected[0]) > 0.001 or abs(lng - expected[1]) > 0.001:
                    print(f"❌ Coordinate extraction failed for {url}")
                    return False
        
        print("✅ Coordinate extraction working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Coordinate extraction test failed: {e}")
        return False

def test_data_processing():
    """Test data processing with actual files"""
    print("🔍 Testing data processing...")
    
    try:
        sys.path.insert(0, 'src')
        from pacs_map.config import Config
        from pacs_map.data import DataManager
        
        config = Config()
        data_manager = DataManager(config)
        
        # Test loading existing data
        df = data_manager.load_data()
        if df is None:
            print("❌ Could not load any data")
            return False
        
        if len(df) == 0:
            print("❌ Loaded empty dataset")
            return False
        
        # Test statistics
        stats = data_manager.get_statistics(df)
        expected_keys = ['total_animals', 'animals_with_coords', 'pending', 'completed']
        
        for key in expected_keys:
            if key not in stats:
                print(f"❌ Missing statistic: {key}")
                return False
        
        print(f"✅ Data processing working - {stats['total_animals']} animals loaded")
        return True
        
    except Exception as e:
        print(f"❌ Data processing test failed: {e}")
        return False

def test_map_generation():
    """Test map generation functionality"""
    print("🔍 Testing map generation...")
    
    try:
        sys.path.insert(0, 'src')
        from pacs_map.config import Config
        from pacs_map.core import PacsMapGenerator
        
        # Use temporary directory for test
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config()
            config.WEB_DIR = temp_dir
            
            map_generator = PacsMapGenerator(config)
            
            # Generate map
            map_path = map_generator.generate_map()
            
            if not os.path.exists(map_path):
                print("❌ Map file was not created")
                return False
            
            # Check map content
            with open(map_path, 'r') as f:
                content = f.read()
                
            required_elements = ['PACS Statistics', 'folium', 'Leaflet']
            for element in required_elements:
                if element not in content:
                    print(f"❌ Map missing required element: {element}")
                    return False
        
        print("✅ Map generation working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Map generation test failed: {e}")
        return False

def test_full_workflow():
    """Test complete end-to-end workflow"""
    print("🔍 Testing complete workflow...")
    
    try:
        # Test CLI commands
        commands = [
            ["./pacs-map", "stats"],
            ["./pacs-map", "list", "--pending"],
            ["./pacs-map", "generate"]
        ]
        
        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print(f"❌ Command failed: {' '.join(cmd)}")
                print(f"Error: {result.stderr}")
                return False
        
        # Check that map was generated
        if not os.path.exists("web/index.html"):
            print("❌ Map was not generated in workflow test")
            return False
        
        print("✅ Complete workflow functioning correctly")
        return True
        
    except Exception as e:
        print(f"❌ Full workflow test failed: {e}")
        return False

def main():
    """Run all system tests"""
    print("🧪 PACS Dog Map - Comprehensive System Test")
    print("=" * 50)
    
    tests = [
        ("Project Structure", test_project_structure),
        ("CLI Executable", test_cli_executable),
        ("Package Imports", test_package_imports), 
        ("Coordinate Extraction", test_coordinate_extraction),
        ("Data Processing", test_data_processing),
        ("Map Generation", test_map_generation),
        ("Full Workflow", test_full_workflow)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 SYSTEM TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✨ Your PACS Dog Map system is fully operational and production-ready!")
        print("\n📋 Ready for:")
        print("  ✅ Real-world deployment")
        print("  ✅ Team collaboration") 
        print("  ✅ Scaling to other regions")
        print("  ✅ Professional rescue operations")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review and fix issues.")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())