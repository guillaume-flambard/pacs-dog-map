#!/usr/bin/env python3
"""
Test script for PACS Dog Map system
Verifies all components are working correctly
"""

import os
import sys

def test_file_exists(filepath, description):
    """Test if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def test_dependencies():
    """Test Python dependencies"""
    print("\n🔍 Testing Python Dependencies:")
    try:
        import pandas
        print("✅ pandas: OK")
    except ImportError:
        print("❌ pandas: MISSING")
        return False
    
    try:
        import folium
        print("✅ folium: OK") 
    except ImportError:
        print("❌ folium: MISSING")
        return False
        
    try:
        import requests
        print("✅ requests: OK")
    except ImportError:
        print("❌ requests: MISSING")
        return False
        
    return True

def test_data_files():
    """Test data files"""
    print("\n📊 Testing Data Files:")
    
    data_files = [
        ("sample_data.csv", "Sample data"),
        ("PACS_Test_1_List_v2.csv", "Original data"),
    ]
    
    found_data = False
    for filepath, desc in data_files:
        if test_file_exists(filepath, desc):
            found_data = True
    
    if not found_data:
        print("⚠️  No data files found - system will use sample data")
    
    return True

def test_scripts():
    """Test core scripts"""
    print("\n🐍 Testing Core Scripts:")
    
    scripts = [
        ("generate_enhanced_map.py", "Enhanced map generator"),
        ("google_sheets_sync.py", "Google Sheets sync"),
        ("batch_operations.py", "Batch operations"),
        ("fix_coordinates.py", "Coordinate fixer"),
    ]
    
    all_found = True
    for filepath, desc in scripts:
        if not test_file_exists(filepath, desc):
            all_found = False
    
    return all_found

def test_workflows():
    """Test GitHub workflows"""
    print("\n⚡ Testing GitHub Workflows:")
    return test_file_exists(".github/workflows/update-map.yml", "Auto-update workflow")

def test_documentation():
    """Test documentation"""
    print("\n📚 Testing Documentation:")
    
    docs = [
        ("README.md", "Main documentation"),
        ("whatsapp_integration.md", "WhatsApp integration guide"),
        ("requirements.txt", "Python requirements"),
    ]
    
    all_found = True
    for filepath, desc in docs:
        if not test_file_exists(filepath, desc):
            all_found = False
    
    return all_found

def run_map_generation_test():
    """Test map generation"""
    print("\n🗺️ Testing Map Generation:")
    
    try:
        print("Attempting to generate map...")
        import subprocess
        result = subprocess.run([sys.executable, "generate_enhanced_map.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Map generation: SUCCESS")
            if os.path.exists("index.html"):
                print("✅ Map file created: index.html")
                return True
            else:
                print("❌ Map file not created")
                return False
        else:
            print(f"❌ Map generation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Map generation error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 PACS Dog Map System Test")
    print("=" * 40)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Data Files", test_data_files),
        ("Core Scripts", test_scripts),
        ("GitHub Workflows", test_workflows),
        ("Documentation", test_documentation),
        ("Map Generation", run_map_generation_test),
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "=" * 40)
    print("📋 TEST SUMMARY:")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All systems ready! Your PACS Dog Map is fully operational.")
        print("\n📋 Next Steps:")
        print("  1. Update Google Sheets link in google_sheets_sync.py")
        print("  2. Enable GitHub Pages in repository settings")
        print("  3. Share the map link with rescue volunteers")
        print("  4. Set up WhatsApp integration if needed")
    else:
        print("\n⚠️  Some issues detected. Please review the failed tests above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)