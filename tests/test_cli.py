"""
Tests for CLI functionality
"""

import unittest
import tempfile
import shutil
import os
from unittest.mock import patch, MagicMock
import pandas as pd

from src.pacs_map.cli import CLI
from src.pacs_map.config import Config


class TestCLI(unittest.TestCase):
    """Test CLI functionality"""
    
    def setUp(self):
        # Create temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock config to use temp directory
        patcher = patch('src.pacs_map.cli.Config.from_env')
        mock_config_cls = patcher.start()
        self.addCleanup(patcher.stop)
        
        config = Config()
        config.DATA_DIR = self.temp_dir
        config.WEB_DIR = self.temp_dir
        mock_config_cls.return_value = config
        
        self.cli = CLI()
        
        # Create sample data file
        sample_data = pd.DataFrame({
            'Dog/Cat': ['Dog', 'Cat'],
            'Location (Area)': ['Thong Sala', 'Chaloklum'],
            'Status': ['Pending', 'Completed'],
            'Pregnant?': ['No', 'No'],
            'Temperament': ['Friendly', 'Wild'],
            'Sex': ['Male', 'Female'],
            'Age': ['Adult', 'Kitten'],
            'Contact Name': ['Alaska', 'John'],
            'Contact Phone #': ['123', '456'],
            'Location Link': ['http://test1.com', 'http://test2.com'],
            'Location Details ': ['Detail 1', 'Detail 2'],
            'No. of Animals': [1, 2],
            'Latitude': [9.7282, 9.7869],
            'Longitude': [99.9915251, 100.0026251],
            'Priority_Score': [0, 5]
        })
        
        data_path = os.path.join(self.temp_dir, 'processed_data.csv')
        sample_data.to_csv(data_path, index=False)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_parser_creation(self):
        """Test argument parser creation"""
        parser = self.cli.create_parser()
        
        # Test that all expected subcommands exist
        actions = parser._subparsers._actions
        subparser_action = next(action for action in actions if hasattr(action, 'choices'))
        
        expected_commands = ['sync', 'generate', 'list', 'complete', 'report', 'stats']
        for command in expected_commands:
            self.assertIn(command, subparser_action.choices)
    
    def test_stats_command(self):
        """Test stats command"""
        result = self.cli.run(['stats'])
        self.assertEqual(result, 0)
    
    def test_list_command(self):
        """Test list command variations"""
        # Test basic list
        result = self.cli.run(['list'])
        self.assertEqual(result, 0)
        
        # Test priority list
        result = self.cli.run(['list', '--priority'])
        self.assertEqual(result, 0)
        
        # Test location filter
        result = self.cli.run(['list', '--location', 'Thong'])
        self.assertEqual(result, 0)
    
    def test_complete_command(self):
        """Test complete command"""
        result = self.cli.run(['complete', '0'])
        self.assertEqual(result, 0)
    
    def test_report_command(self):
        """Test report command"""
        result = self.cli.run(['report'])
        self.assertEqual(result, 0)
    
    @patch('src.pacs_map.data.DataManager.sync_from_google_sheets')
    def test_sync_command(self, mock_sync):
        """Test sync command"""
        mock_sync.return_value = pd.DataFrame({'test': [1]})
        
        result = self.cli.run(['sync'])
        self.assertEqual(result, 0)
        mock_sync.assert_called_once()
    
    @patch('src.pacs_map.data.DataManager.sync_from_google_sheets')
    def test_sync_command_with_generate(self, mock_sync):
        """Test sync command with generate flag"""
        mock_sync.return_value = pd.DataFrame({
            'Dog/Cat': ['Dog'],
            'Location (Area)': ['Test'],
            'Status': ['Pending'],
            'Latitude': [9.7282],
            'Longitude': [99.9915251]
        })
        
        with patch('src.pacs_map.core.PacsMapGenerator.generate_map') as mock_generate:
            result = self.cli.run(['sync', '--generate'])
            self.assertEqual(result, 0)
            mock_generate.assert_called_once()
    
    def test_generate_command(self):
        """Test generate command"""
        with patch('src.pacs_map.core.PacsMapGenerator.generate_map') as mock_generate:
            mock_generate.return_value = os.path.join(self.temp_dir, 'index.html')
            
            result = self.cli.run(['generate'])
            self.assertEqual(result, 0)
            mock_generate.assert_called_once()
    
    def test_invalid_command(self):
        """Test handling of invalid commands"""
        result = self.cli.run(['invalid_command'])
        self.assertEqual(result, 1)
    
    def test_no_arguments(self):
        """Test running with no arguments"""
        result = self.cli.run([])
        self.assertEqual(result, 0)  # Should show help
    
    @patch('src.pacs_map.data.DataManager.sync_from_google_sheets')
    def test_sync_failure(self, mock_sync):
        """Test sync command failure"""
        mock_sync.return_value = None
        
        result = self.cli.run(['sync'])
        self.assertEqual(result, 1)


if __name__ == '__main__':
    unittest.main()