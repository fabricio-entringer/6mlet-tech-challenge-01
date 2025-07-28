import os
import tomllib
from typing import Optional


def convert_price_to_float(price_str: str) -> Optional[float]:
    """
    Convert price string to float.

    This function converts price strings in various formats to float values.
    It handles currencies like £ and removes common characters.

    Args:
        price_str: Price string to convert (e.g., "£12.99", "In stock", etc.)

    Returns:
        Float value of the price, or None if conversion fails

    Examples:
        >>> convert_price_to_float("£12.99")
        12.99
        >>> convert_price_to_float("In stock")
        None
        >>> convert_price_to_float("$25.50")
        25.50
    """
    if not price_str or not isinstance(price_str, str):
        return None

    try:
        # Clean the string: remove currency symbols, spaces, and common non-numeric text
        cleaned = price_str.strip()

        # Remove common currency symbols and characters
        for char in ["£", "$", "€", "¥", ",", " "]:
            cleaned = cleaned.replace(char, "")

        # If the cleaned string is empty or contains non-numeric characters
        # (except for decimal point), return None
        if not cleaned or any(
            c not in "0123456789." for c in cleaned
        ):  # Allow digits and decimal point
            return None

        # Convert to float
        price_float = float(cleaned)

        # Validate that the price is positive
        if price_float < 0:
            return None

        return price_float

    except (ValueError, TypeError):
        return None


def convert_rating_to_float(rating_str: str) -> Optional[float]:
    """
    Convert rating string to float.

    This function converts rating strings to float values, handling various formats
    and validating that ratings are within expected range (0-5).

    Args:
        rating_str: Rating string to convert (e.g., "4.5", "Three", etc.)

    Returns:
        Float value of the rating, or None if conversion fails or out of range

    Examples:
        >>> convert_rating_to_float("4.5")
        4.5
        >>> convert_rating_to_float("Three")
        None
        >>> convert_rating_to_float("6.0")  # Out of range
        None
    """
    if not rating_str or not isinstance(rating_str, str):
        return None

    try:
        # Clean the string
        cleaned = rating_str.strip()

        # Convert to float
        rating_float = float(cleaned)

        # Validate rating range (typically 0-5 for star ratings)
        if rating_float < 0 or rating_float > 5:
            return None

        return rating_float

    except (ValueError, TypeError):
        return None


def convert_rating_to_float(
    rating_str: str, default_value: float = 0
) -> Optional[float]:
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
