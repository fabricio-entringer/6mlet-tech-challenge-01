"""Data service for handling book data operations."""

import csv
import os
from typing import Dict, List, Optional, Tuple

from ..models.category import CategoriesResponse, Category, PriceRange
from ..utils import convert_price_to_float, convert_rating_to_float


class BookDataService:
    """Service for handling book data operations."""

    def __init__(self):
        """Initialize the service with data file path."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        self.data_file = os.path.join(project_root, "data", "books_data.csv")

    def _create_slug(self, name: str) -> str:
        """Create a URL-friendly slug from category name."""
        return name.lower().replace(" ", "-").replace("&", "and")

    def get_categories_data(self) -> Tuple[Dict, Dict, Dict, Dict]:
        """
        Extract categories data from CSV file.

        Returns:
            Tuple of (categories_count, prices_by_category, ratings_by_category, price_ranges)
        """
        categories_count = {}
        prices_by_category = {}
        ratings_by_category = {}

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    category = row.get("category", "").strip()

                    # Initialize category data structures
                    if category not in categories_count:
                        categories_count[category] = 0
                        prices_by_category[category] = []
                        ratings_by_category[category] = []

                    categories_count[category] += 1

                    # Process price
                    price = convert_price_to_float(row.get("price", ""))
                    if price is not None:
                        prices_by_category[category].append(price)

                    # Process rating
                    rating = convert_rating_to_float(row.get("rating_numeric", "0"))
                    if rating is not None:
                        ratings_by_category[category].append(rating)

        except FileNotFoundError:
            # Return empty data if file not found
            pass

        # Calculate price ranges
        price_ranges = {}
        for category, prices in prices_by_category.items():
            if prices:
                price_ranges[category] = {"min": min(prices), "max": max(prices)}

        return categories_count, prices_by_category, ratings_by_category, price_ranges

    def get_categories(
        self, sort: str = "name", order: str = "asc", include_stats: bool = True
    ) -> List[Category]:
        """
        Get all categories with optional statistics.

        Args:
            sort: Sort by 'name' or 'count'
            order: Sort order 'asc' or 'desc'
            include_stats: Whether to include price and rating statistics

        Returns:
            List of Category objects
        """
        categories_count, prices_by_category, ratings_by_category, price_ranges = (
            self.get_categories_data()
        )

        categories = []

        for category_name, book_count in categories_count.items():
            # Calculate statistics if requested
            avg_price = None
            avg_rating = None
            price_range = None

            if include_stats:
                # Calculate average price
                if (
                    category_name in prices_by_category
                    and prices_by_category[category_name]
                ):
                    avg_price = sum(prices_by_category[category_name]) / len(
                        prices_by_category[category_name]
                    )

                # Calculate average rating
                if (
                    category_name in ratings_by_category
                    and ratings_by_category[category_name]
                ):
                    avg_rating = sum(ratings_by_category[category_name]) / len(
                        ratings_by_category[category_name]
                    )

                # Set price range
                if category_name in price_ranges:
                    price_range = PriceRange(
                        min=price_ranges[category_name]["min"],
                        max=price_ranges[category_name]["max"],
                    )

            category = Category(
                name=category_name,
                slug=self._create_slug(category_name),
                book_count=book_count,
                avg_price=round(avg_price, 2) if avg_price else None,
                avg_rating=round(avg_rating, 1) if avg_rating else None,
                price_range=price_range,
            )

            categories.append(category)

        # Sort categories
        if sort == "count":
            categories.sort(key=lambda x: x.book_count, reverse=(order == "desc"))
        else:  # sort by name
            categories.sort(key=lambda x: x.name.lower(), reverse=(order == "desc"))

        return categories


# Initialize the data service
book_data_service = BookDataService()


async def get_categories(
    sort: str = "name", order: str = "asc", include_stats: bool = True
) -> CategoriesResponse:
    """
    Get all book categories with optional statistics.

    Args:
        sort: Sort by 'name' or 'count'
        order: Sort order 'asc' or 'desc'
        include_stats: Whether to include price and rating statistics

    Returns:
        CategoriesResponse with list of categories and total count
    """
    # Validate sort parameter
    if sort not in ["name", "count"]:
        sort = "name"

    # Validate order parameter
    if order not in ["asc", "desc"]:
        order = "asc"

    categories = book_data_service.get_categories(sort, order, include_stats)

    return CategoriesResponse(categories=categories, total_categories=len(categories))
