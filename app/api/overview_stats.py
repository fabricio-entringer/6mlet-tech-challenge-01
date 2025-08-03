"""Overview statistics API endpoints."""

import csv
import os
import statistics
from datetime import datetime
from typing import List, Set

from fastapi import HTTPException

from ..models.overview_stats import (
    OverviewStatsResponse,
    PriceStats,
    RatingDistributionStats,
    AvailabilityOverview
)
from ..utils import convert_price_to_float, convert_rating_to_float


class OverviewStatsService:
    """Service for handling overview statistics operations."""

    def __init__(self):
        """Initialize the service with data file path."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        self.data_file = os.path.join(project_root, "data", "books_data.csv")

    def _is_in_stock(self, availability: str) -> bool:
        """Determine if a book is in stock based on availability string."""
        return "in stock" in availability.lower()

    def _get_file_last_modified(self) -> str:
        """Get the last modified timestamp of the data file."""
        try:
            if os.path.exists(self.data_file):
                timestamp = os.path.getmtime(self.data_file)
                return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%SZ')
            else:
                return datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        except Exception:
            return datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

    def _calculate_price_stats(self, prices: List[float]) -> PriceStats:
        """Calculate comprehensive price statistics."""
        if not prices:
            return PriceStats(average=0.0, min=0.0, max=0.0, median=0.0)

        return PriceStats(
            average=round(statistics.mean(prices), 2),
            min=round(min(prices), 2),
            max=round(max(prices), 2),
            median=round(statistics.median(prices), 2)
        )

    def _calculate_rating_distribution(self, ratings: List[int]) -> RatingDistributionStats:
        """Calculate rating distribution from list of ratings."""
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for rating in ratings:
            if 1 <= rating <= 5:
                distribution[rating] += 1
        
        return RatingDistributionStats(
            one=distribution[1],
            two=distribution[2],
            three=distribution[3],
            four=distribution[4],
            five=distribution[5]
        )

    def _calculate_availability_stats(self, availability_list: List[str]) -> AvailabilityOverview:
        """Calculate availability statistics from list of availability strings."""
        in_stock = 0
        out_of_stock = 0
        
        for availability in availability_list:
            if self._is_in_stock(availability):
                in_stock += 1
            else:
                out_of_stock += 1
        
        return AvailabilityOverview(in_stock=in_stock, out_of_stock=out_of_stock)

    def get_overview_statistics(self) -> OverviewStatsResponse:
        """
        Get comprehensive overview statistics for the entire book catalog.
        
        Returns:
            OverviewStatsResponse with complete overview metrics
        """
        try:
            if not os.path.exists(self.data_file):
                raise HTTPException(
                    status_code=404,
                    detail="Book data not found. Please run the scraper first to collect data."
                )

            # Data collection lists
            prices = []
            ratings = []
            availability_list = []
            categories: Set[str] = set()
            total_books = 0

            with open(self.data_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    total_books += 1

                    # Process price
                    price_raw = row.get("price", "")
                    price = convert_price_to_float(price_raw)
                    if price is not None:
                        prices.append(price)

                    # Process rating
                    rating_raw = row.get("rating_numeric", "0")
                    rating = convert_rating_to_float(rating_raw)
                    if rating is not None and 1 <= rating <= 5:
                        ratings.append(int(rating))

                    # Process availability
                    availability = row.get("availability", "").strip()
                    if availability:
                        availability_list.append(availability)

                    # Process category
                    category = row.get("category", "").strip()
                    if category:
                        categories.add(category)

            # Calculate statistics
            price_stats = self._calculate_price_stats(prices)
            rating_distribution = self._calculate_rating_distribution(ratings)
            availability_stats = self._calculate_availability_stats(availability_list)
            last_updated = self._get_file_last_modified()

            return OverviewStatsResponse(
                total_books=total_books,
                price_stats=price_stats,
                rating_distribution=rating_distribution,
                availability=availability_stats,
                categories=len(categories),
                last_updated=last_updated
            )

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


# Initialize the service
overview_stats_service = OverviewStatsService()


async def get_overview_statistics() -> OverviewStatsResponse:
    """
    Get comprehensive overview statistics for the book catalog.
    
    Returns complete metrics including total counts, price statistics,
    rating distribution, availability stats, category count, and data freshness.
    
    Returns:
        OverviewStatsResponse with comprehensive overview metrics
    """
    return overview_stats_service.get_overview_statistics()
