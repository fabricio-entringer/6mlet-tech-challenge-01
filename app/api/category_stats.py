"""Category statistics API endpoints."""

import csv
import os
from typing import Dict, List, Optional, Set

from fastapi import HTTPException

from ..models.category_stats import (
    CategoryStatsResponse,
    CategoryStatsItem,
    CategoryStatistics,
    RatingDistribution,
    AvailabilityStats,
    StatsSummary
)
from ..utils import convert_price_to_float, convert_rating_to_float


class CategoryStatsService:
    """Service for handling category statistics operations."""

    def __init__(self):
        """Initialize the service with data file path."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        self.data_file = os.path.join(project_root, "data", "books_data.csv")

    def _create_slug(self, name: str) -> str:
        """Create a URL-friendly slug from category name."""
        return name.lower().replace(" ", "-").replace("&", "and")

    def _is_in_stock(self, availability: str) -> bool:
        """Determine if a book is in stock based on availability string."""
        return "in stock" in availability.lower()

    def _get_raw_category_data(self, filter_categories: Optional[Set[str]] = None) -> Dict:
        """
        Extract raw category data from CSV file.
        
        Args:
            filter_categories: Set of category names to filter by (case-insensitive)
            
        Returns:
            Dictionary with category data organized by category name
        """
        category_data = {}
        
        try:
            if not os.path.exists(self.data_file):
                raise HTTPException(
                    status_code=404,
                    detail="Book data not found. Please run the scraper first to collect data."
                )

            with open(self.data_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    category = row.get("category", "").strip()
                    
                    # Skip empty categories
                    if not category:
                        continue
                    
                    # Apply category filter if provided
                    if filter_categories and category.lower() not in filter_categories:
                        continue

                    # Initialize category data structure
                    if category not in category_data:
                        category_data[category] = {
                            "books": [],
                            "prices": [],
                            "ratings": [],
                            "availability": []
                        }

                    # Process and store book data
                    book_data = {
                        "title": row.get("title", ""),
                        "price_raw": row.get("price", ""),
                        "rating_numeric": row.get("rating_numeric", "0"),
                        "availability": row.get("availability", "")
                    }
                    
                    category_data[category]["books"].append(book_data)

                    # Process price
                    price = convert_price_to_float(row.get("price", ""))
                    if price is not None:
                        category_data[category]["prices"].append(price)

                    # Process rating
                    rating = convert_rating_to_float(row.get("rating_numeric", "0"))
                    if rating is not None and 1 <= rating <= 5:
                        category_data[category]["ratings"].append(int(rating))

                    # Process availability
                    availability = row.get("availability", "").strip()
                    if availability:
                        category_data[category]["availability"].append(availability)

        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail="Book data not found. Please run the scraper first to collect data."
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error reading books data: {str(e)}"
            )

        return category_data

    def _calculate_rating_distribution(self, ratings: List[int]) -> RatingDistribution:
        """Calculate rating distribution from list of ratings."""
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for rating in ratings:
            if 1 <= rating <= 5:
                distribution[rating] += 1
        
        return RatingDistribution(
            one=distribution[1],
            two=distribution[2],
            three=distribution[3],
            four=distribution[4],
            five=distribution[5]
        )

    def _calculate_availability_stats(self, availability_list: List[str]) -> AvailabilityStats:
        """Calculate availability statistics from list of availability strings."""
        in_stock = 0
        out_of_stock = 0
        
        for availability in availability_list:
            if self._is_in_stock(availability):
                in_stock += 1
            else:
                out_of_stock += 1
        
        return AvailabilityStats(in_stock=in_stock, out_of_stock=out_of_stock)

    def _calculate_category_statistics(self, category_name: str, data: Dict) -> CategoryStatsItem:
        """Calculate statistics for a single category."""
        books = data["books"]
        prices = data["prices"]
        ratings = data["ratings"]
        availability = data["availability"]

        # Basic statistics
        book_count = len(books)
        avg_price = round(sum(prices) / len(prices), 2) if prices else None
        avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else None
        
        # Price range
        price_range = None
        if prices:
            price_range = {
                "min": round(min(prices), 2),
                "max": round(max(prices), 2)
            }

        # Rating distribution
        rating_distribution = self._calculate_rating_distribution(ratings) if ratings else None

        # Availability statistics
        availability_stats = self._calculate_availability_stats(availability) if availability else None

        statistics = CategoryStatistics(
            book_count=book_count,
            avg_price=avg_price,
            price_range=price_range,
            avg_rating=avg_rating,
            rating_distribution=rating_distribution,
            availability=availability_stats
        )

        return CategoryStatsItem(
            name=category_name,
            slug=self._create_slug(category_name),
            stats=statistics
        )

    def get_category_statistics(
        self,
        categories: Optional[List[str]] = None,
        include_distribution: bool = True
    ) -> CategoryStatsResponse:
        """
        Get detailed statistics for categories.
        
        Args:
            categories: List of category names to include (None for all)
            include_distribution: Whether to include rating distribution
            
        Returns:
            CategoryStatsResponse with statistics for requested categories
        """
        # Convert category filter to lowercase set for case-insensitive matching
        filter_categories = None
        if categories:
            filter_categories = {cat.lower() for cat in categories}

        # Get raw data
        category_data = self._get_raw_category_data(filter_categories)
        
        if not category_data:
            return CategoryStatsResponse(
                categories=[],
                summary=StatsSummary(total_categories=0, categories_analyzed=0)
            )

        # Calculate statistics for each category
        category_stats = []
        for category_name, data in category_data.items():
            try:
                stats_item = self._calculate_category_statistics(category_name, data)
                
                # Remove rating distribution if not requested
                if not include_distribution:
                    stats_item.stats.rating_distribution = None
                
                category_stats.append(stats_item)
            except Exception as e:
                # Log error but continue with other categories
                print(f"Error calculating statistics for category {category_name}: {e}")
                continue

        # Sort by category name for consistent output
        category_stats.sort(key=lambda x: x.name.lower())

        # Get total categories count (all categories in database)
        all_category_data = self._get_raw_category_data()
        total_categories = len(all_category_data)

        summary = StatsSummary(
            total_categories=total_categories,
            categories_analyzed=len(category_stats)
        )

        return CategoryStatsResponse(categories=category_stats, summary=summary)


# Initialize the service
category_stats_service = CategoryStatsService()


async def get_category_statistics(
    categories: Optional[str] = None,
    include_distribution: bool = True
) -> CategoryStatsResponse:
    """
    Get detailed statistics for book categories.
    
    Args:
        categories: Comma-separated list of category names to include
        include_distribution: Whether to include rating distribution
        
    Returns:
        CategoryStatsResponse with statistics for requested categories
    """
    # Parse categories parameter
    category_list = None
    if categories:
        category_list = [cat.strip() for cat in categories.split(",") if cat.strip()]

    return category_stats_service.get_category_statistics(
        categories=category_list,
        include_distribution=include_distribution
    )
