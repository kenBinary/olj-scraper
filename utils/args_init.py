import argparse


def init_cli_args():
    parser = argparse.ArgumentParser(description="OLJ Web Scraper")
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    parser.add_argument("--prod", action="store_true", help="Run in production mode")
    parser.add_argument(
        "--test", action="store_true", help="Run in test mode (scrape only 3 jobs)"
    )

    args = parser.parse_args()

    if args.dev and args.prod:
        parser.error("Cannot specify both --dev and --prod")

    return args
