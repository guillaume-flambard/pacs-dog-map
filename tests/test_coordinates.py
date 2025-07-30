"""
Tests for coordinate extraction functionality
"""

import unittest
import pandas as pd
from src.pacs_map.coordinates import CoordinateExtractor


class TestCoordinateExtractor(unittest.TestCase):
    """Test coordinate extraction from Google Maps URLs"""
    
    def setUp(self):
        self.extractor = CoordinateExtractor()
    
    def test_extract_at_coordinates(self):
        """Test extraction from @lat,lng format"""
        url = "https://www.google.com/maps/@9.7282,99.9915251,17z"
        lat, lng = self.extractor.extract_from_url(url)
        self.assertAlmostEqual(lat, 9.7282, places=4)
        self.assertAlmostEqual(lng, 99.9915251, places=4)
    
    def test_extract_3d_coordinates(self):
        """Test extraction from 3d format"""
        url = "https://www.google.com/maps/place/@9.7282,99.9915251,17z/data=!3d9.7282!4d99.9941"
        lat, lng = self.extractor.extract_from_url(url)
        self.assertAlmostEqual(lat, 9.7282, places=4)
        self.assertAlmostEqual(lng, 99.9915251, places=4)
    
    def test_extract_search_coordinates(self):
        """Test extraction from search format"""
        url = "https://www.google.com/maps/search/9.748065,+99.975760"
        lat, lng = self.extractor.extract_from_url(url)
        self.assertAlmostEqual(lat, 9.748065, places=6)
        self.assertAlmostEqual(lng, 99.975760, places=6)
    
    def test_extract_degree_coordinates(self):
        """Test extraction from degree format"""
        url = "https://www.google.com/maps/place/9°43'41.5\"N+99°59'38.8\"E/@9.7282,99.9915251"
        lat, lng = self.extractor.extract_from_url(url)
        self.assertAlmostEqual(lat, 9.7282, places=4)
        self.assertAlmostEqual(lng, 99.9915251, places=4)
    
    def test_invalid_url(self):
        """Test handling of invalid URLs"""
        lat, lng = self.extractor.extract_from_url("not_a_url")
        self.assertIsNone(lat)
        self.assertIsNone(lng)
    
    def test_empty_url(self):
        """Test handling of empty/None URLs"""
        lat, lng = self.extractor.extract_from_url(None)
        self.assertIsNone(lat)
        self.assertIsNone(lng)
        
        lat, lng = self.extractor.extract_from_url("")
        self.assertIsNone(lat)
        self.assertIsNone(lng)
    
    def test_process_dataframe(self):
        """Test processing entire dataframe"""
        data = {
            'Location Link': [
                'https://www.google.com/maps/@9.7282,99.9915251,17z',
                'https://maps.app.goo.gl/invalid_link',
                'https://www.google.com/maps/search/9.748065,+99.975760'
            ],
            'Unshortened Link': [
                None,
                'https://www.google.com/maps/@9.7869,100.0026251,17z',
                None
            ],
            'Latitude': [None, None, None],
            'Longitude': [None, None, None]
        }
        
        df = pd.DataFrame(data)
        df_processed, fixed_count = self.extractor.process_dataframe(df)
        
        self.assertEqual(fixed_count, 3)
        self.assertAlmostEqual(df_processed.at[0, 'Latitude'], 9.7282, places=4)
        self.assertAlmostEqual(df_processed.at[1, 'Latitude'], 9.7869, places=4)
        self.assertAlmostEqual(df_processed.at[2, 'Latitude'], 9.748065, places=6)


if __name__ == '__main__':
    unittest.main()