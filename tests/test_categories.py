"""Tests for the categories endpoint."""

import pytest
from unittest.mock import patch, mock_open
from app.api.categories import BookDataService, get_categories


class TestBookDataService:
    """Test the BookDataService class."""
    
    def test_is_valid_category(self):
        """Test category validation."""
        service = BookDataService()
        
        # Valid categories
        assert service._is_valid_category("Fiction")
        assert service._is_valid_category("Science Fiction")
        assert service._is_valid_category("Young Adult")
        
        # Invalid categories
        assert not service._is_valid_category("Default")
        assert not service._is_valid_category("In stock")
        assert not service._is_valid_category("1")
        assert not service._is_valid_category("One")
        assert not service._is_valid_category("")
        assert not service._is_valid_category("abc")  # too short
    
    def test_create_slug(self):
        """Test slug creation."""
        service = BookDataService()
        
        assert service._create_slug("Fiction") == "fiction"
        assert service._create_slug("Science Fiction") == "science-fiction"
        assert service._create_slug("Food & Drink") == "food-and-drink"
        assert service._create_slug("Young Adult") == "young-adult"


@pytest.mark.asyncio
async def test_get_categories():
    """Test the get_categories function."""
    # Mock CSV data
    csv_data = """title,price,rating_text,rating_numeric,availability,category,image_url
Book 1,£25.99,Four,4,In stock,Fiction,http://example.com/1.jpg
Book 2,£35.50,Three,3,In stock,Fiction,http://example.com/2.jpg
Book 3,£15.99,Five,5,In stock,Science Fiction,http://example.com/3.jpg
Book 4,£45.00,Two,2,In stock,Default,http://example.com/4.jpg
Book 5,£20.00,Four,4,In stock,Romance,http://example.com/5.jpg"""
    
    with patch("builtins.open", mock_open(read_data=csv_data)):
        result = await get_categories()
        
        assert result.total_categories == 3  # Fiction, Science Fiction, Romance (Default filtered out)
        assert len(result.categories) == 3
        
        # Check categories are sorted by name by default
        category_names = [cat.name for cat in result.categories]
        assert category_names == sorted(category_names)
        
        # Check Fiction category details
        fiction_cat = next(cat for cat in result.categories if cat.name == "Fiction")
        assert fiction_cat.book_count == 2
        assert fiction_cat.slug == "fiction"
        assert fiction_cat.avg_price == 30.74  # (25.99 + 35.50) / 2 rounded
        assert fiction_cat.avg_rating == 3.5  # (4 + 3) / 2
        assert fiction_cat.price_range.min == 25.99
        assert fiction_cat.price_range.max == 35.5


@pytest.mark.asyncio
async def test_get_categories_sort_by_count():
    """Test sorting categories by count."""
    csv_data = """title,price,rating_text,rating_numeric,availability,category,image_url
Book 1,£25.99,Four,4,In stock,Fiction,http://example.com/1.jpg
Book 2,£35.50,Three,3,In stock,Fiction,http://example.com/2.jpg
Book 3,£15.99,Five,5,In stock,Fiction,http://example.com/3.jpg
Book 4,£20.00,Four,4,In stock,Romance,http://example.com/4.jpg"""
    
    with patch("builtins.open", mock_open(read_data=csv_data)):
        result = await get_categories(sort="count", order="desc")
        
        assert result.total_categories == 2
        # Fiction should be first (3 books), then Romance (1 book)
        assert result.categories[0].name == "Fiction"
        assert result.categories[0].book_count == 3
        assert result.categories[1].name == "Romance"
        assert result.categories[1].book_count == 1


@pytest.mark.asyncio
async def test_get_categories_without_stats():
    """Test getting categories without statistics."""
    csv_data = """title,price,rating_text,rating_numeric,availability,category,image_url
Book 1,£25.99,Four,4,In stock,Fiction,http://example.com/1.jpg"""
    
    with patch("builtins.open", mock_open(read_data=csv_data)):
        result = await get_categories(include_stats=False)
        
        assert result.total_categories == 1
        fiction_cat = result.categories[0]
        assert fiction_cat.name == "Fiction"
        assert fiction_cat.book_count == 1
        assert fiction_cat.avg_price is None
        assert fiction_cat.avg_rating is None
        assert fiction_cat.price_range is None
