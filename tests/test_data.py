"""
Tests for data management functionality
"""

import unittest
import pandas as pd
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from src.pacs_map.config import Config
from src.pacs_map.data import DataManager


class TestDataManager(unittest.TestCase):
    """Test data management functionality"""
    
    def setUp(self):
        # Create temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test config
        self.config = Config()
        self.config.DATA_DIR = self.temp_dir
        
        self.data_manager = DataManager(self.config)
        
        # Sample test data
        self.sample_data = pd.DataFrame({
            'Language': ['English', 'Thai'],
            'Dog/Cat': ['Dog', 'Cat'],
            'No. of Animals': [1, 2],
            'Sex': ['Female', 'Both'],
            'Pregnant?': ['Yes', 'No'],
            'Age': ['Adult', 'Kitten'],
            'Temperament': ['Wild', 'Friendly'],
            'Location (Area)': ['Thong Sala', 'Chaloklum'],
            'Location Link': ['http://maps.google.com/@9.7282,99.9915251', 'http://maps.google.com/@9.7869,100.0026251'],
            'Contact Name': ['Alaska', 'John'],
            'Contact Phone #': ['0622355014', '0887654321'],
            'Latitude': [9.7282, 9.7869],
            'Longitude': [99.9915251, 100.0026251]
        })
    
    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_clean_data(self):
        """Test data cleaning functionality"""
        # Remove Status column to test addition
        test_data = self.sample_data.copy()
        
        cleaned_data = self.data_manager._clean_data(test_data)
        
        # Check Status column was added
        self.assertIn('Status', cleaned_data.columns)
        self.assertTrue(all(cleaned_data['Status'] == 'Pending'))
        
        # Check Priority_Score column was added
        self.assertIn('Priority_Score', cleaned_data.columns)
        
        # Check coordinates are numeric
        self.assertTrue(pd.api.types.is_numeric_dtype(cleaned_data['Latitude']))
        self.assertTrue(pd.api.types.is_numeric_dtype(cleaned_data['Longitude']))
    
    def test_calculate_priority(self):
        """Test priority calculation"""
        # Test pregnant animal (highest priority)
        pregnant_row = pd.Series({
            'Pregnant?': 'Yes',
            'Temperament': 'Friendly',
            'Sex': 'Female',
            'Location Details ': 'Normal location'
        })
        priority = self.data_manager._calculate_priority(pregnant_row)
        self.assertEqual(priority, self.config.PRIORITY_WEIGHTS['pregnant'])
        
        # Test wild animal
        wild_row = pd.Series({
            'Pregnant?': 'No',
            'Temperament': 'Wild',
            'Sex': 'Male',
            'Location Details ': 'Normal location'
        })
        priority = self.data_manager._calculate_priority(wild_row)
        self.assertEqual(priority, self.config.PRIORITY_WEIGHTS['wild'])
        
        # Test multiple animals + chained
        multiple_chained_row = pd.Series({
            'Pregnant?': 'No',
            'Temperament': 'Friendly',
            'Sex': 'Both',
            'Location Details ': 'Chained in yard'
        })
        priority = self.data_manager._calculate_priority(multiple_chained_row)
        expected = self.config.PRIORITY_WEIGHTS['multiple'] + self.config.PRIORITY_WEIGHTS['chained']
        self.assertEqual(priority, expected)
    
    def test_get_statistics(self):
        """Test statistics calculation"""
        test_data = self.sample_data.copy()
        test_data['Status'] = ['Pending', 'Completed']
        
        stats = self.data_manager.get_statistics(test_data)
        
        self.assertEqual(stats['total_animals'], 2)
        self.assertEqual(stats['animals_with_coords'], 2)
        self.assertEqual(stats['pending'], 1)
        self.assertEqual(stats['completed'], 1)
        self.assertEqual(stats['pregnant'], 1)
        self.assertEqual(stats['wild'], 1)
        self.assertEqual(stats['friendly'], 1)
    
    def test_save_processed_data(self):
        """Test saving processed data"""
        output_path = self.data_manager.save_processed_data(self.sample_data)
        
        # Check file was created
        self.assertTrue(os.path.exists(output_path))
        
        # Check data can be loaded back
        loaded_data = pd.read_csv(output_path)
        self.assertEqual(len(loaded_data), len(self.sample_data))
    
    @patch('requests.get')
    def test_sync_from_google_sheets_success(self, mock_get):
        """Test successful Google Sheets sync"""
        # Mock response
        mock_response = MagicMock()
        mock_response.text = self.sample_data.to_csv(index=False)
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.data_manager.sync_from_google_sheets()
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        
        # Check file was saved
        expected_path = self.config.get_data_path(self.config.SHEETS_DATA_FILE)
        self.assertTrue(os.path.exists(expected_path))
    
    @patch('requests.get')
    def test_sync_from_google_sheets_failure(self, mock_get):
        """Test Google Sheets sync failure"""
        mock_get.side_effect = Exception("Network error")
        
        result = self.data_manager.sync_from_google_sheets()
        
        self.assertIsNone(result)
    
    def test_load_data_file_priority(self):
        """Test data loading priority order"""
        # Create test files in different locations
        processed_path = self.config.get_data_path(self.config.PROCESSED_DATA_FILE)
        sheets_path = self.config.get_data_path(self.config.SHEETS_DATA_FILE)
        
        # Save different data to each file
        data1 = pd.DataFrame({'test': [1]})
        data2 = pd.DataFrame({'test': [2]})
        
        data1.to_csv(processed_path, index=False)
        data2.to_csv(sheets_path, index=False)
        
        # Should load processed data first
        loaded = self.data_manager.load_data()
        self.assertEqual(loaded.iloc[0]['test'], 1)


if __name__ == '__main__':
    unittest.main()