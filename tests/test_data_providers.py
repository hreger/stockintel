import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np

from data_ingestion.data_providers import DataProviderManager

class TestDataProviders(unittest.TestCase):
    def setUp(self):
        # Create mock providers
        self.alpha_vantage_mock = MagicMock()
        self.polygon_mock = MagicMock()
        
        # Setup test data
        self.test_data = pd.DataFrame({
            'date': pd.date_range(start='2023-01-01', periods=10),
            'open': np.random.rand(10) * 100,
            'high': np.random.rand(10) * 100,
            'low': np.random.rand(10) * 100,
            'close': np.random.rand(10) * 100,
            'volume': np.random.randint(1000, 100000, 10)
        })
        
    @patch('data_ingestion.data_providers.AlphaVantageProvider')
    @patch('data_ingestion.data_providers.PolygonProvider')
    def test_provider_fallback(self, mock_polygon, mock_alpha):
        # Setup mocks
        mock_alpha.return_value.get_stock_data.side_effect = Exception("API limit reached")
        mock_polygon.return_value.get_stock_data.return_value = self.test_data
        
        # Create manager with mocked providers
        manager = DataProviderManager()
        manager.providers = {
            'alpha_vantage': mock_alpha.return_value,
            'polygon': mock_polygon.return_value
        }
        
        # Test fallback behavior
        result = manager.get_stock_data('AAPL')
        
        # Verify alpha_vantage was called first
        mock_alpha.return_value.get_stock_data.assert_called_once_with('AAPL')
        
        # Verify polygon was called as fallback
        mock_polygon.return_value.get_stock_data.assert_called_once_with('AAPL')
        
        # Verify we got the polygon data
        pd.testing.assert_frame_equal(result, self.test_data)