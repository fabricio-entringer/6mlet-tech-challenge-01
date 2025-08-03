"""Data validation utilities for CSV data processing."""

import logging
import re
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timezone

from ..models.book import Book
from ..utils import convert_price_to_float


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for data validation errors."""
    pass


class ValidationResult:
    """Result of data validation with details about errors and warnings."""
    
    def __init__(self):
        self.is_valid: bool = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.corrected_rows: int = 0
        self.invalid_rows: int = 0
        self.total_rows: int = 0
    
    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "corrected_rows": self.corrected_rows,
            "invalid_rows": self.invalid_rows,
            "total_rows": self.total_rows,
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
        }


class DataValidator:
    """Validates CSV data integrity and handles corrupted records."""
    
    # Required CSV columns
    REQUIRED_COLUMNS = [
        "id", "title", "price", "rating_text", "rating_numeric", 
        "availability", "category", "image_url"
    ]
    
    # Optional CSV columns
    OPTIONAL_COLUMNS = ["description", "upc", "reviews"]
    
    # Valid rating range
    VALID_RATING_RANGE = (1, 5)
    
    # Common price patterns
    PRICE_PATTERN = re.compile(r'[£$€¥]?\d+\.?\d*')
    
    def __init__(self):
        """Initialize the data validator."""
        self.reset_stats()
    
    def reset_stats(self) -> None:
        """Reset validation statistics."""
        self._validation_stats = {
            "total_validated": 0,
            "valid_records": 0,
            "invalid_records": 0,
            "corrected_records": 0,
            "common_errors": {},
        }
    
    def validate_csv_structure(self, raw_data: List[Dict[str, str]]) -> ValidationResult:
        """
        Validate the overall structure of CSV data.
        
        Args:
            raw_data: List of dictionaries representing CSV rows
            
        Returns:
            ValidationResult with structure validation details
        """
        result = ValidationResult()
        result.total_rows = len(raw_data)
        
        if not raw_data:
            result.add_error("CSV data is empty")
            return result
        
        # Check if all required columns are present
        first_row = raw_data[0]
        missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in first_row]
        
        if missing_columns:
            result.add_error(f"Missing required columns: {missing_columns}")
        
        # Check for unexpected columns (warning only)
        all_expected_columns = set(self.REQUIRED_COLUMNS + self.OPTIONAL_COLUMNS)
        unexpected_columns = [col for col in first_row.keys() if col not in all_expected_columns]
        
        if unexpected_columns:
            result.add_warning(f"Unexpected columns found: {unexpected_columns}")
        
        return result
    
    def validate_row(self, row: Dict[str, str], row_index: int) -> Tuple[Optional[Dict[str, str]], List[str]]:
        """
        Validate and potentially correct a single CSV row.
        
        Args:
            row: Dictionary representing a CSV row
            row_index: Row index for error reporting
            
        Returns:
            Tuple of (corrected_row_or_None, list_of_errors)
        """
        errors = []
        corrected_row = row.copy()
        
        # Validate ID
        if not row.get("id") or not str(row["id"]).strip():
            corrected_row["id"] = str(row_index)
            errors.append(f"Row {row_index}: Missing ID, using row index")
        else:
            try:
                int(row["id"])
            except ValueError:
                corrected_row["id"] = str(row_index)
                errors.append(f"Row {row_index}: Invalid ID format, using row index")
        
        # Validate title (required)
        if not row.get("title") or not row["title"].strip():
            errors.append(f"Row {row_index}: Missing or empty title")
            return None, errors
        
        corrected_row["title"] = row["title"].strip()
        
        # Validate price
        if not row.get("price"):
            corrected_row["price"] = "£0.00"
            errors.append(f"Row {row_index}: Missing price, defaulting to £0.00")
        else:
            # Try to validate price format
            price_value = convert_price_to_float(row["price"])
            if price_value is None:
                corrected_row["price"] = "£0.00"
                errors.append(f"Row {row_index}: Invalid price format '{row['price']}', defaulting to £0.00")
        
        # Validate rating_numeric
        if not row.get("rating_numeric"):
            corrected_row["rating_numeric"] = "0"
            errors.append(f"Row {row_index}: Missing rating_numeric, defaulting to 0")
        else:
            try:
                rating = int(row["rating_numeric"])
                if not (self.VALID_RATING_RANGE[0] <= rating <= self.VALID_RATING_RANGE[1]):
                    corrected_row["rating_numeric"] = "0"
                    errors.append(f"Row {row_index}: Rating {rating} out of valid range, defaulting to 0")
            except ValueError:
                corrected_row["rating_numeric"] = "0"
                errors.append(f"Row {row_index}: Invalid rating format, defaulting to 0")
        
        # Validate rating_text
        if not row.get("rating_text"):
            corrected_row["rating_text"] = ""
            errors.append(f"Row {row_index}: Missing rating_text")
        
        # Validate category
        if not row.get("category") or not row["category"].strip():
            corrected_row["category"] = "Unknown"
            errors.append(f"Row {row_index}: Missing category, defaulting to 'Unknown'")
        else:
            # Handle known problematic categories
            category = row["category"].strip()
            if category == "Add a comment":
                corrected_row["category"] = "Default"
                errors.append(f"Row {row_index}: Invalid category 'Add a comment' changed to 'Default'")
            else:
                corrected_row["category"] = category
        
        # Validate availability
        if not row.get("availability"):
            corrected_row["availability"] = "Unknown"
            errors.append(f"Row {row_index}: Missing availability, defaulting to 'Unknown'")
        
        # Validate image_url
        if not row.get("image_url"):
            corrected_row["image_url"] = ""
            errors.append(f"Row {row_index}: Missing image_url")
        
        # Clean optional fields
        for field in self.OPTIONAL_COLUMNS:
            if field in corrected_row and corrected_row[field]:
                corrected_row[field] = corrected_row[field].strip()
        
        return corrected_row, errors
    
    def validate_book_object(self, book: Book) -> List[str]:
        """
        Validate a Book object for consistency.
        
        Args:
            book: Book object to validate
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        if not book.title or not book.title.strip():
            errors.append("Book title is empty")
        
        if book.price < 0:
            errors.append(f"Book price is negative: {book.price}")
        
        if book.rating_numeric < 0 or book.rating_numeric > 5:
            errors.append(f"Book rating out of range: {book.rating_numeric}")
        
        if not book.category or not book.category.strip():
            errors.append("Book category is empty")
        
        return errors
    
    def validate_data_integrity(self, raw_data: List[Dict[str, str]]) -> ValidationResult:
        """
        Validate data integrity and handle corrupted records.
        
        Args:
            raw_data: List of dictionaries representing CSV rows
            
        Returns:
            ValidationResult with detailed validation information
        """
        result = ValidationResult()
        result.total_rows = len(raw_data)
        
        self._validation_stats["total_validated"] += len(raw_data)
        
        # First validate structure
        structure_result = self.validate_csv_structure(raw_data)
        if not structure_result.is_valid:
            result.errors.extend(structure_result.errors)
            result.warnings.extend(structure_result.warnings)
            return result
        
        # Validate each row
        valid_rows = 0
        corrupted_rows = 0
        corrected_rows = 0
        
        error_counts = {}
        
        for index, row in enumerate(raw_data, start=1):
            corrected_row, row_errors = self.validate_row(row, index)
            
            if corrected_row is None:
                # Row is too corrupted to fix
                corrupted_rows += 1
                result.add_error(f"Row {index} is too corrupted to process")
                continue
            
            if row_errors:
                # Row had issues but was corrected
                corrected_rows += 1
                for error in row_errors:
                    # Count error types for statistics
                    error_type = error.split(":")[1].strip() if ":" in error else error
                    error_counts[error_type] = error_counts.get(error_type, 0) + 1
                    result.add_warning(error)
            else:
                valid_rows += 1
        
        # Update statistics
        result.corrected_rows = corrected_rows
        result.invalid_rows = corrupted_rows
        
        self._validation_stats["valid_records"] += valid_rows
        self._validation_stats["invalid_records"] += corrupted_rows
        self._validation_stats["corrected_records"] += corrected_rows
        self._validation_stats["common_errors"].update(error_counts)
        
        # Summary
        if corrupted_rows > 0:
            result.add_error(f"Found {corrupted_rows} corrupted rows that cannot be processed")
        
        if corrected_rows > 0:
            result.add_warning(f"Corrected {corrected_rows} rows with data issues")
        
        logger.info(f"Validation complete: {valid_rows} valid, {corrected_rows} corrected, {corrupted_rows} corrupted")
        
        return result
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        return self._validation_stats.copy()
    
    def validate_file_integrity(self, file_path: str) -> ValidationResult:
        """
        Validate file integrity (size, permissions, etc.).
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            ValidationResult with file validation details
        """
        result = ValidationResult()
        
        try:
            import os
            from pathlib import Path
            
            path = Path(file_path)
            
            if not path.exists():
                result.add_error(f"File does not exist: {file_path}")
                return result
            
            if not path.is_file():
                result.add_error(f"Path is not a file: {file_path}")
                return result
            
            # Check file size
            file_size = path.stat().st_size
            if file_size == 0:
                result.add_error("File is empty")
                return result
            
            if file_size > 100 * 1024 * 1024:  # 100MB
                result.add_warning(f"Large file detected: {file_size / (1024*1024):.1f}MB")
            
            # Check file permissions
            if not os.access(file_path, os.R_OK):
                result.add_error("File is not readable")
                return result
            
            # Try to read first line to check encoding
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.readline()
            except UnicodeDecodeError:
                result.add_error("File encoding is not UTF-8")
                return result
            
        except Exception as e:
            result.add_error(f"Error validating file: {str(e)}")
        
        return result
