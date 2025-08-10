"""Tests for overview statistics API endpoints."""

import json
import os
import pytest
from unittest.mock import patch, mock_open

from app.api.overview_stats import OverviewStatsService
from app.models.overview_stats import OverviewStatsResponse


class TestOverviewStatsService:
    """Test cases for OverviewStatsService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = OverviewStatsService()

    def test_is_in_stock(self):
        """Test the _is_in_stock method."""
        assert self.service._is_in_stock("In stock") is True
        assert self.service._is_in_stock("in stock") is True
        assert self.service._is_in_stock("IN STOCK") is True
        assert self.service._is_in_stock("Out of stock") is False
        assert self.service._is_in_stock("Unavailable") is False
        assert self.service._is_in_stock("") is False

    def test_get_file_last_modified_file_exists(self):
        """Test _get_file_last_modified when file exists."""
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getmtime', return_value=1640995200.0):  # 2022-01-01 00:00:00
            result = self.service._get_file_last_modified()
            assert result.startswith("2022-01-01T")

    def test_get_file_last_modified_file_not_exists(self):
        """Test _get_file_last_modified when file doesn't exist."""
        with patch('os.path.exists', return_value=False):
            result = self.service._get_file_last_modified()
            assert result.endswith("Z")
            assert "T" in result

    def test_calculate_price_stats_empty_list(self):
        """Test _calculate_price_stats with empty list."""
        result = self.service._calculate_price_stats([])
        assert result.average == 0.0
        assert result.min == 0.0
        assert result.max == 0.0
        assert result.median == 0.0

    def test_calculate_price_stats_with_data(self):
        """Test _calculate_price_stats with sample data."""
        prices = [10.0, 15.0, 20.0, 25.0, 30.0]
        result = self.service._calculate_price_stats(prices)
        assert result.average == 20.0
        assert result.min == 10.0
        assert result.max == 30.0
        assert result.median == 20.0

    def test_calculate_price_stats_with_even_count(self):
        """Test _calculate_price_stats with even number of prices."""
        prices = [10.0, 20.0, 30.0, 40.0]
        result = self.service._calculate_price_stats(prices)
        assert result.average == 25.0
        assert result.min == 10.0
        assert result.max == 40.0
        assert result.median == 25.0  # (20 + 30) / 2

    def test_calculate_rating_distribution_empty(self):
        """Test _calculate_rating_distribution with empty list."""
        result = self.service._calculate_rating_distribution([])
        assert result.one == 0
        assert result.two == 0
        assert result.three == 0
        assert result.four == 0
        assert result.five == 0

    def test_calculate_rating_distribution_with_data(self):
        """Test _calculate_rating_distribution with sample data."""
        ratings = [1, 2, 2, 3, 3, 3, 4, 4, 5]
        result = self.service._calculate_rating_distribution(ratings)
        assert result.one == 1
        assert result.two == 2
        assert result.three == 3
        assert result.four == 2
        assert result.five == 1

    def test_calculate_availability_stats(self):
        """Test _calculate_availability_stats method."""
        availability_list = ["In stock", "in stock", "Out of stock", "Unavailable"]
        result = self.service._calculate_availability_stats(availability_list)
        assert result.in_stock == 2
        assert result.out_of_stock == 2

    @patch('os.path.exists')
    def test_get_overview_statistics_file_not_found(self, mock_exists):
        """Test get_overview_statistics when data file doesn't exist."""
        mock_exists.return_value = False
        
        with pytest.raises(Exception) as exc_info:
            self.service.get_overview_statistics()
        
        assert "Book data not found" in str(exc_info.value.detail)

    @patch('builtins.open', new_callable=mock_open, read_data="""id,title,price,rating_text,rating_numeric,availability,category,image_url
1,Book 1,£25.99,Four,4,In stock,Fiction,url1
2,Book 2,£15.50,Three,3,Out of stock,Mystery,url2
3,Book 3,£35.75,Five,5,In stock,Science,url3""")
    @patch('os.path.exists')
    @patch('os.path.getmtime')
    def test_get_overview_statistics_success(self, mock_getmtime, mock_exists, mock_file):
        """Test successful get_overview_statistics call."""
        mock_exists.return_value = True
        mock_getmtime.return_value = 1640995200.0  # 2022-01-01 00:00:00
        
        result = self.service.get_overview_statistics()
        
        assert isinstance(result, OverviewStatsResponse)
        assert result.total_books == 3
        assert result.categories == 3  # Fiction, Mystery, Science
        assert result.price_stats.average == 25.75  # (25.99 + 15.50 + 35.75) / 3
        assert result.price_stats.min == 15.50
        assert result.price_stats.max == 35.75
        assert result.rating_distribution.three == 1
        assert result.rating_distribution.four == 1
        assert result.rating_distribution.five == 1
        assert result.availability.in_stock == 2
        assert result.availability.out_of_stock == 1
        assert result.last_updated.startswith("2022-01-01T")

    @patch('builtins.open', new_callable=mock_open, read_data="""id,title,price,rating_text,rating_numeric,availability,category,image_url
1,Book 1,Invalid Price,Invalid Rating,0,In stock,Fiction,url1
2,Book 2,,,,Out of stock,,url2""")
    @patch('os.path.exists')
    @patch('os.path.getmtime')
    def test_get_overview_statistics_with_invalid_data(self, mock_getmtime, mock_exists, mock_file):
        """Test get_overview_statistics with invalid/missing data."""
        mock_exists.return_value = True
        mock_getmtime.return_value = 1640995200.0
        
        result = self.service.get_overview_statistics()
        
        assert isinstance(result, OverviewStatsResponse)
        assert result.total_books == 2
        assert result.categories == 1  # Only Fiction (empty category ignored)
        # No valid prices, so should return 0s
        assert result.price_stats.average == 0.0
        assert result.price_stats.min == 0.0
        assert result.price_stats.max == 0.0
        assert result.price_stats.median == 0.0
        # No valid ratings
        assert result.rating_distribution.one == 0
        assert result.rating_distribution.two == 0
        assert result.rating_distribution.three == 0
        assert result.rating_distribution.four == 0
        assert result.rating_distribution.five == 0
        # Availability should still work
        assert result.availability.in_stock == 1
        assert result.availability.out_of_stock == 1

    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    @patch('os.path.exists')
    def test_get_overview_statistics_file_permission_error(self, mock_exists, mock_file):
        """Test get_overview_statistics when file can't be read due to permissions."""
        mock_exists.return_value = True
        
        with pytest.raises(Exception) as exc_info:
            self.service.get_overview_statistics()
        
        assert "Error reading books data" in str(exc_info.value.detail)

    @patch('builtins.open', new_callable=mock_open, read_data="")  # Empty file
    @patch('os.path.exists')
    @patch('os.path.getmtime')
    def test_get_overview_statistics_empty_file(self, mock_getmtime, mock_exists, mock_file):
        """Test get_overview_statistics with empty CSV file."""
        mock_exists.return_value = True
        mock_getmtime.return_value = 1640995200.0
        
        result = self.service.get_overview_statistics()
        
        assert isinstance(result, OverviewStatsResponse)
        assert result.total_books == 0
        assert result.categories == 0
        assert result.price_stats.average == 0.0
        assert result.availability.in_stock == 0
        assert result.availability.out_of_stock == 0


@pytest.mark.asyncio
class TestOverviewStatsEndpoint:
    """Test cases for overview stats API endpoint."""

    @patch('app.api.overview_stats.overview_stats_service.get_overview_statistics')
    async def test_get_overview_statistics_endpoint(self, mock_service):
        """Test the get_overview_statistics endpoint function."""
        from app.api.overview_stats import get_overview_statistics
        from app.models.overview_stats import (
            OverviewStatsResponse,
            PriceStats,
            RatingDistributionStats,
            AvailabilityOverview
        )
        
        # Mock the service response
        mock_response = OverviewStatsResponse(
            total_books=100,
            price_stats=PriceStats(average=25.99, min=9.99, max=59.99, median=19.99),
            rating_distribution=RatingDistributionStats(one=10, two=15, three=30, four=25, five=20),
            availability=AvailabilityOverview(in_stock=85, out_of_stock=15),
            categories=10,
            last_updated="2025-08-03T12:00:00Z"
        )
        mock_service.return_value = mock_response
        
        result = await get_overview_statistics()
        
        assert isinstance(result, OverviewStatsResponse)
        assert result.total_books == 100
        assert result.price_stats.average == 25.99
        assert result.categories == 10
        assert result.last_updated == "2025-08-03T12:00:00Z"
        mock_service.assert_called_once()

    @patch('app.api.overview_stats.overview_stats_service.get_overview_statistics')
    async def test_get_overview_statistics_endpoint_service_error(self, mock_service):
        """Test the endpoint when service raises an exception."""
        from app.api.overview_stats import get_overview_statistics
        from fastapi import HTTPException
        
        # Mock the service to raise an exception
        mock_service.side_effect = HTTPException(status_code=500, detail="Internal server error")
        
        with pytest.raises(HTTPException) as exc_info:
            await get_overview_statistics()
        
        assert exc_info.value.status_code == 500
        assert "Internal server error" in str(exc_info.value.detail)
