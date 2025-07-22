#!/usr/bin/env python3
"""
Scraping History Logger Module

This module provides functionality to log scraping process metadata
to a CSV file for historical tracking and analysis.
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

from scripts.config import SCRAPER_CONFIG, HISTORY_LOG_HEADERS


class ScrapingHistoryLogger:
    """
    Logger for tracking scraping process metadata and performance.
    
    Records information about each scraping execution including timing,
    data volume, configuration, and status for audit and analysis purposes.
    """
    
    def __init__(self, output_dir: str = None) -> None:
        """
        Initialize the history logger.
        
        Args:
            output_dir: Directory where history log file will be stored
        """
        self.output_dir = output_dir or SCRAPER_CONFIG["output_directory"]
        self.history_file = os.path.join(
            self.output_dir, 
            SCRAPER_CONFIG["history_log_filename"]
        )
        self._ensure_output_directory()
        self._initialize_history_file()
    
    def _ensure_output_directory(self) -> None:
        """Create output directory if it doesn't exist."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def _initialize_history_file(self) -> None:
        """Initialize history CSV file with headers if it doesn't exist."""
        if not os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=HISTORY_LOG_HEADERS)
                    writer.writeheader()
            except Exception as e:
                print(f"Warning: Could not initialize history file: {e}")
    
    def log_scraping_execution(
        self,
        execution_type: str,
        duration_seconds: float,
        total_books_scraped: int,
        total_categories: int,
        output_file: str,
        status: str,
        error_message: Optional[str] = None,
        configuration: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a scraping execution to the history file.
        
        Args:
            execution_type: Type of execution ("API" or "CLI")
            duration_seconds: Total execution time in seconds
            total_books_scraped: Number of books successfully scraped
            total_categories: Number of categories processed
            output_file: Path to the output CSV file
            status: Execution status ("SUCCESS", "PARTIAL", "FAILED")
            error_message: Error message if any (optional)
            configuration: Scraper configuration used (optional)
        """
        timestamp = datetime.now().isoformat()
        
        # Prepare configuration as JSON string
        config_json = ""
        if configuration:
            try:
                config_json = json.dumps(configuration, sort_keys=True)
            except Exception:
                config_json = str(configuration)
        
        # Prepare log entry
        log_entry = {
            "timestamp": timestamp,
            "execution_type": execution_type,
            "duration_seconds": f"{duration_seconds:.2f}",
            "total_books_scraped": str(total_books_scraped),
            "total_categories": str(total_categories),
            "output_file": output_file,
            "status": status,
            "error_message": error_message or "",
            "configuration": config_json
        }
        
        # Write to history file
        try:
            with open(self.history_file, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=HISTORY_LOG_HEADERS)
                writer.writerow(log_entry)
        except Exception as e:
            print(f"Warning: Could not write to history file: {e}")
    
    def get_history_summary(self) -> Dict[str, Any]:
        """
        Get a summary of scraping history.
        
        Returns:
            Dictionary with history statistics
        """
        if not os.path.exists(self.history_file):
            return {"total_executions": 0, "message": "No history file found"}
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
            
            if not rows:
                return {"total_executions": 0, "message": "No executions recorded"}
            
            total_executions = len(rows)
            successful_executions = sum(1 for row in rows if row["status"] == "SUCCESS")
            failed_executions = sum(1 for row in rows if row["status"] == "FAILED")
            total_books = sum(int(row["total_books_scraped"]) for row in rows if row["total_books_scraped"].isdigit())
            
            latest_execution = rows[-1] if rows else None
            
            return {
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "failed_executions": failed_executions,
                "partial_executions": total_executions - successful_executions - failed_executions,
                "total_books_scraped": total_books,
                "latest_execution": latest_execution,
                "history_file": self.history_file
            }
            
        except Exception as e:
            return {"error": f"Could not read history file: {e}"}


def create_configuration_snapshot(
    delay: float,
    max_retries: int,
    timeout: int,
    base_url: str = None
) -> Dict[str, Any]:
    """
    Create a configuration snapshot for history logging.
    
    Args:
        delay: Request delay in seconds
        max_retries: Maximum retry attempts
        timeout: Request timeout in seconds
        base_url: Base URL being scraped
        
    Returns:
        Configuration dictionary
    """
    return {
        "delay": delay,
        "max_retries": max_retries,
        "timeout": timeout,
        "base_url": base_url or SCRAPER_CONFIG["base_url"]
    }
