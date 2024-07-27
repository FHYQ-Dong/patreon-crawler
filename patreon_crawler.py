import argparse
import os

from patreon_crawler.cookie_extractor import get_cookies
from patreon_crawler.crawler import PatreonCrawler
from patreon_crawler.crawler_config import CrawlerConfig

PARSER = argparse.ArgumentParser(description="A media crawler for Patreon")
PARSER.add_argument("--creator", type=str, help="The handle of the creator to crawl")
PARSER.add_argument("--cookie-file", type=str, help="The path to the cookies file")
PARSER.add_argument("--download-dir", type=str, help="The base directory to download the posts to")
PARSER.add_argument("--max-posts", type=int, help="Limit the maximum number of posts to download")
PARSER.add_argument("--download-inaccessible", action="store_true", default=False,
                    help="Download inaccessible posts (blurred)")
PARSER.add_argument("--max-parallel-downloads", type=int, default=10,
                    help="The maximum number of parallel downloads to run at once")


def parse_args() -> list[CrawlerConfig]:
    args = PARSER.parse_args()

    config_creator = args.creator
    cookies_file = args.cookie_file
    download_dir = args.download_dir or "./downloads"
    max_posts = args.max_posts or 0
    download_inaccessible = args.download_inaccessible
    max_parallel_downloads = args.max_parallel_downloads

    if not config_creator:
        config_creator = input("Enter creator name (multiple comma-separated): ")
    if not cookies_file:
        cookies_file = input("Enter path to cookies file: ")

    if not config_creator:
        raise ValueError("Creator name is required")
    if cookies_file != "auto" and not os.path.exists(cookies_file):
        raise FileNotFoundError("Cookies file not found")

    if not os.path.exists(download_dir):
        os.mkdir(download_dir)

    parsed_creator = config_creator.split(",")

    cookies = get_cookies(cookies_file, 'patreon.com')

    if cookies is None:
        raise ValueError(f"Failed to extract cookies from {cookies_file}")

    return [
        CrawlerConfig(
            creator,
            cookies,
            download_dir,
            max_posts=max_posts,
            download_inaccessible=download_inaccessible,
            max_parallel_downloads=max_parallel_downloads
        ) for creator in parsed_creator
    ]


def main() -> None:
    configs = parse_args()

    for config in configs:
        print("Crawling", config.creator)

        crawler = PatreonCrawler(config)
        crawler.run()

        print("\nDone\n")


if __name__ == "__main__":
    main()
