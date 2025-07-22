#!/usr/bin/env python3
"""
Command-line interface for the books scraper.

Usage:
    python run_scraper.py [options]

Options:
    --delay SECONDS     Delay between requests (default: 1.0)
    --output DIR        Output directory for CSV file (default: data)
    --filename NAME     CSV filename (default: books_data.csv)
    --help             Show this help message
"""

import argparse
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.books_scraper import BooksScraper
from scripts.config import SCRAPER_CONFIG


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Scrape books data from books.toscrape.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--delay",
        type=float,
        default=SCRAPER_CONFIG["delay"],
        help=f"Delay between requests in seconds (default: {SCRAPER_CONFIG['delay']})"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=SCRAPER_CONFIG["output_directory"],
        help=f"Output directory for CSV file (default: {SCRAPER_CONFIG['output_directory']})"
    )
    
    parser.add_argument(
        "--filename",
        type=str,
        default=SCRAPER_CONFIG["default_csv_filename"],
        help=f"CSV filename (default: {SCRAPER_CONFIG['default_csv_filename']})"
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        default=SCRAPER_CONFIG["max_retries"],
        help=f"Maximum retry attempts (default: {SCRAPER_CONFIG['max_retries']})"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=SCRAPER_CONFIG["timeout"],
        help=f"Request timeout in seconds (default: {SCRAPER_CONFIG['timeout']})"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()


def main() -> None:
    """Main function for the CLI."""
    args = parse_arguments()
    
    print("Books Scraper CLI")
    print("================")
    print(f"Target URL: {SCRAPER_CONFIG['base_url']}")
    print(f"Delay: {args.delay}s")
    print(f"Output: {args.output}/{args.filename}")
    print(f"Max retries: {args.max_retries}")
    print(f"Timeout: {args.timeout}s")
    print("-" * 40)
    
    try:
        # Initialize scraper with command-line options
        scraper = BooksScraper(
            delay=args.delay,
            max_retries=args.max_retries,
            timeout=args.timeout
        )
        
        # Run the scraping process
        print("Starting scraping process...")
        books = scraper.scrape_all_books(execution_type="CLI")
        
        if books:
            # Save results
            print("Saving results to CSV...")
            output_file = scraper.save_to_csv(
                filename=args.filename,
                output_dir=args.output
            )
            
            # Show statistics
            stats = scraper.get_statistics()
            print("\n" + "="*50)
            print("SCRAPING COMPLETED SUCCESSFULLY")
            print("="*50)
            print(f"Total books scraped: {stats['total_books']}")
            print(f"Total categories: {stats['total_categories']}")
            print(f"Data saved to: {output_file}")
            
            if args.verbose:
                print("\nCategories breakdown:")
                for category, count in stats['categories_breakdown'].items():
                    print(f"  {category}: {count} books")
                
                print("\nRatings breakdown:")
                for rating, count in stats['ratings_breakdown'].items():
                    print(f"  {rating}: {count} books")
            
            print("\nScraping process completed successfully! 🎉")
            
        else:
            print("❌ No books were scraped. Please check the logs for errors.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Scraping interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
