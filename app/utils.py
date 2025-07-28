import os
import tomllib
from typing import Optional


def convert_price_to_float(price_str: str) -> Optional[float]:
    """
    Convert price string to float value.
    
    Removes currency symbols (£) and commas, then converts to float.
    Only returns positive values, None for invalid or non-positive prices.
    
    Args:
        price_str: Price string to convert (e.g., "£12.99", "£1,234.56")
        
    Returns:
        Float value if conversion successful and positive, None otherwise
        
    Examples:
        >>> convert_price_to_float("£12.99")
        12.99
        >>> convert_price_to_float("£1,234.56")
        1234.56
        >>> convert_price_to_float("invalid")
        None
        >>> convert_price_to_float("£0")
        None
    """
    if not price_str:
        return None
        
    try:
        # Remove currency symbols and commas, then strip whitespace
        cleaned_price = price_str.replace('£', '').replace(',', '').strip()
        price = float(cleaned_price)
        
        # Only return positive prices
        if price > 0:
            return price
        return None
    except (ValueError, TypeError):
        return None


def convert_rating_to_float(rating_str: str, default_value: float = 0) -> Optional[float]:
    """
    Convert rating string to float value.
    
    Validates that the rating is within the valid range (1-5).
    Returns None for invalid ratings or ratings outside the valid range.
    
    Args:
        rating_str: Rating string to convert (e.g., "4.5", "3", "invalid")
        default_value: Default value to use if rating_str is empty or None
        
    Returns:
        Float value if conversion successful and within valid range (1-5), None otherwise
        
    Examples:
        >>> convert_rating_to_float("4.5")
        4.5
        >>> convert_rating_to_float("3")
        3.0
        >>> convert_rating_to_float("0")
        None
        >>> convert_rating_to_float("6")
        None
        >>> convert_rating_to_float("invalid")
        None
    """
    try:
        rating = float(rating_str or default_value)
        # Valid rating range is 1-5
        if 1 <= rating <= 5:
            return rating
        return None
    except (ValueError, TypeError):
        return None


def get_version() -> str:
    """Get version from pyproject.toml file."""
    try:
        # Get the project root directory (parent of app directory)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        pyproject_path = os.path.join(project_root, "pyproject.toml")

        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
            return pyproject_data.get("project", {}).get("version", "0.1.0")
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError):
        # Fallback version if file is not found or version is not in file
        return "0.1.0"
