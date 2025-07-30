"""
Integration tests for PACS Dog Map
"""

import unittest
import tempfile
import shutil
import os
import pandas as pd

from src.pacs_map.config import Config
from src.pacs_map.core import PacsMapGenerator
from src.pacs_map.data import DataManager
from src.pacs_map.operations import BatchOperations


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, 'data')
        self.web_dir = os.path.join(self.temp_dir, 'web')
        os.makedirs(self.data_dir)
        os.makedirs(self.web_dir)
        
        # Create test configuration
        self.config = Config()
        self.config.DATA_DIR = self.data_dir
        self.config.WEB_DIR = self.web_dir
        
        # Create comprehensive test data
        self.test_data = pd.DataFrame({
            'Language': ['English', 'Thai', 'English', 'English'],
            'Pop-Up Info': ['Spay/Neuter'] * 4,
            'Dog/Cat': ['Dog', 'Cat', 'Dog', 'Dog'],
            'No. of Animals': [1, 2, 1, 3],
            'Sex': ['Female', 'Both', 'Male', 'Female'],
            'Pregnant?': ['Yes', 'No', 'No', 'No'],
            'Age': ['Adult', 'Kitten', 'Senior', 'Young'],
            'Temperament': ['Wild', 'Friendly', 'Friendly', 'Wild'],
            'Location (Area)': ['Thong Sala', 'Chaloklum', 'Haad Rin', 'Ban Tai'],
            'Location Link': [
                'https://maps.app.goo.gl/test1',
                'https://maps.app.goo.gl/test2',
                'https://maps.app.goo.gl/test3',
                'https://maps.app.goo.gl/test4'
            ],
            'Location Details ': [
                'Near market',
                'On beach',
                'Behind restaurant',
                'Chained in yard'
            ],
            'Contact Name': ['Alaska', 'John', 'Mary', 'Tom'],
            'Contact Phone #': ['0622355014', '0887654321', '0856789012', '0834567890'],
            'Photo': ['', '', '', ''],
            'Unshortened Link': [
                'https://www.google.com/maps/@9.7282,99.9915251,17z',
                'https://www.google.com/maps/@9.7869,100.0026251,17z',
                'https://www.google.com/maps/@9.6664,100.0735,17z',
                'https://www.google.com/maps/@9.7108,99.9876,17z'
            ],
            'Latitude': [9.7282, 9.7869, 9.6664, 9.7108],
            'Longitude': [99.9915251, 100.0026251, 100.0735, 99.9876],
            'Status': ['Pending', 'Completed', 'Pending', 'Pending']
        })
        
        # Save test data
        self.data_path = os.path.join(self.data_dir, 'processed_data.csv')
        self.test_data.to_csv(self.data_path, index=False)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_complete_workflow(self):
        """Test complete end-to-end workflow"""
        # Initialize components
        data_manager = DataManager(self.config)
        map_generator = PacsMapGenerator(self.config)
        operations = BatchOperations(self.config)
        
        # 1. Load data
        df = data_manager.load_data()
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 4)
        
        # 2. Check statistics
        stats = data_manager.get_statistics(df)
        self.assertEqual(stats['total_animals'], 4)
        self.assertEqual(stats['pending'], 3)
        self.assertEqual(stats['completed'], 1)
        self.assertEqual(stats['pregnant'], 1)
        
        # 3. Generate priority list
        priority_list = operations.generate_priority_list()
        self.assertIsNotNone(priority_list)
        
        # Check that pregnant animal is highest priority
        first_animal = priority_list.iloc[0]
        self.assertEqual(first_animal['Pregnant?'], 'Yes')
        
        # 4. Generate map
        map_path = map_generator.generate_map(df)
        self.assertTrue(os.path.exists(map_path))
        
        # Check map file has content
        with open(map_path, 'r') as f:
            map_content = f.read()
            self.assertIn('PACS Statistics', map_content)
            self.assertIn('Thong Sala', map_content)
            self.assertIn('folium', map_content)
        
        # 5. Mark an animal as completed
        initial_pending = len(df[df['Status'] != 'Completed'])
        updated_count = operations.mark_completed([0])  # Mark first animal as completed
        self.assertEqual(updated_count, 1)
        
        # Reload data and check status changed
        df_updated = data_manager.load_data()
        new_pending = len(df_updated[df_updated['Status'] != 'Completed'])
        self.assertEqual(new_pending, initial_pending - 1)
        
        # 6. Generate field report
        report_path = operations.export_field_report()
        self.assertTrue(os.path.exists(report_path))
        
        # Check report content
        report_df = pd.read_csv(report_path)
        self.assertGreater(len(report_df), 0)
        self.assertIn('Priority_Score', report_df.columns)
    
    def test_data_cleaning_and_processing(self):
        """Test data cleaning and processing pipeline"""
        data_manager = DataManager(self.config)
        
        # Create messy data
        messy_data = pd.DataFrame({
            'Dog/Cat': ['Dog', '', 'Cat', 'Dog'],
            'Location (Area)': ['Location1', None, 'Location3', 'Location4'],
            'Latitude': ['9.7282', 'invalid', '9.6664', '9.7108'],
            'Longitude': [99.9915251, None, '100.0735', 99.9876],
            'Sex': ['Both', 'Male', 'Female', 'Both'],
            'Temperament': ['Wild', 'Wild', 'Friendly', 'Wild'],
            'Pregnant?': ['No', 'Yes', 'No', 'No']
        })
        
        cleaned_data = data_manager._clean_data(messy_data)
        
        # Check Status column was added
        self.assertIn('Status', cleaned_data.columns)
        
        # Check Priority_Score was calculated
        self.assertIn('Priority_Score', cleaned_data.columns)
        
        # Check coordinates are numeric
        self.assertTrue(pd.api.types.is_numeric_dtype(cleaned_data['Latitude']))
        self.assertTrue(pd.api.types.is_numeric_dtype(cleaned_data['Longitude']))
        
        # Check empty rows were removed
        valid_animals = cleaned_data.dropna(subset=['Dog/Cat', 'Location (Area)'], how='all')
        self.assertEqual(len(valid_animals), 3)  # One row should be removed
    
    def test_priority_calculation_integration(self):
        """Test priority calculation in real workflow"""
        data_manager = DataManager(self.config)
        operations = BatchOperations(self.config)
        
        df = data_manager.load_data()
        priority_list = operations.generate_priority_list()
        
        # Verify priority ordering
        priorities = priority_list['Priority_Score'].tolist()
        self.assertEqual(priorities, sorted(priorities, reverse=True))
        
        # Check specific priority cases
        pregnant_animals = priority_list[priority_list['Pregnant?'] == 'Yes']
        if len(pregnant_animals) > 0:
            # Pregnant animals should have highest scores
            max_score = priority_list['Priority_Score'].max()
            self.assertTrue(any(pregnant_animals['Priority_Score'] == max_score))
    
    def test_location_filtering(self):
        """Test location-based filtering"""
        operations = BatchOperations(self.config)
        
        # Test existing location
        thong_sala_animals = operations.get_animals_by_location('Thong Sala')
        self.assertIsNotNone(thong_sala_animals)
        self.assertEqual(len(thong_sala_animals), 1)
        
        # Test partial match
        animals_with_sala = operations.get_animals_by_location('Sala')
        self.assertIsNotNone(animals_with_sala)
        self.assertGreaterEqual(len(animals_with_sala), 1)
        
        # Test non-existent location
        no_animals = operations.get_animals_by_location('NonExistentPlace')
        self.assertIsNone(no_animals)
    
    def test_map_generation_with_various_data(self):
        """Test map generation with different data scenarios"""
        map_generator = PacsMapGenerator(self.config)
        
        # Test with full data
        map_path = map_generator.generate_map(self.test_data)
        self.assertTrue(os.path.exists(map_path))
        
        # Test with minimal data
        minimal_data = pd.DataFrame({
            'Dog/Cat': ['Dog'],
            'Location (Area)': ['Test Location'],
            'Status': ['Pending'],
            'Temperament': ['Friendly'],
            'Sex': ['Male'],
            'Age': ['Adult'],
            'Contact Name': ['Test Contact'],
            'Contact Phone #': ['123456'],
            'Location Link': ['http://test.com'],
            'Location Details ': ['Test details'],
            'No. of Animals': [1],
            'Pregnant?': ['No'],
            'Latitude': [9.7282],
            'Longitude': [99.9915251]
        })
        
        map_path_minimal = map_generator.generate_map(minimal_data)
        self.assertTrue(os.path.exists(map_path_minimal))
        
        # Verify map contains expected elements
        with open(map_path_minimal, 'r') as f:
            content = f.read()
            self.assertIn('Test Location', content)
            self.assertIn('Test Contact', content)


if __name__ == '__main__':
    unittest.main()