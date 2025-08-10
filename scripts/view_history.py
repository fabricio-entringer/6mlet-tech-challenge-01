#!/usr/bin/env python3
"""
Scraping History Viewer

This script provides utilities to view and analyze scraping history logs.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.history_logger import ScrapingHistoryLogger


def view_scraping_history():
    """Display scraping history in a formatted way."""
    logger = ScrapingHistoryLogger()
    summary = logger.get_history_summary()

    print("📊 Scraping History Summary")
    print("=" * 50)

    if "error" in summary:
        print(f"❌ Error: {summary['error']}")
        return

    if summary["total_executions"] == 0:
        print("📝 No scraping executions recorded yet.")
        return

    print(f"Total Executions: {summary['total_executions']}")
    print(f"✅ Successful: {summary['successful_executions']}")
    print(f"❌ Failed: {summary['failed_executions']}")
    print(f"⚠️  Partial: {summary['partial_executions']}")
    print(f"📚 Total Books Scraped: {summary['total_books_scraped']}")

    if summary.get("latest_execution"):
        latest = summary["latest_execution"]
        print("\n🕒 Latest Execution:")
        print(f"  Timestamp: {latest['timestamp']}")
        print(f"  Type: {latest['execution_type']}")
        print(f"  Duration: {latest['duration_seconds']}s")
        print(f"  Books: {latest['total_books_scraped']}")
        print(f"  Status: {latest['status']}")
        if latest["error_message"]:
            print(f"  Error: {latest['error_message']}")

    print(f"\n📄 History file: {summary['history_file']}")


def main():
    """Main function for command line usage."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python scripts/view_history.py")
        print("Display scraping execution history and statistics.")
        return

    view_scraping_history()


if __name__ == "__main__":
    main()
