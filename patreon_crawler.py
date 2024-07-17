import argparse
import os

from patreon_crawler.cookie_extractor import get_cookies
from patreon_crawler.crawler import PatreonCrawler
from patreon_crawler.crawler_config import CrawlerConfig

PARSER = argparse.ArgumentParser(description="Crawl Patreon for creators")
PARSER.add_argument("--creator", type=str, help="The handle of the creator to crawl")
PARSER.add_argument("--cookie-file", type=str, help="The path to the cookies file")
PARSER.add_argument("--download-dir", type=str, help="The directory to download the posts to")


def parse_args() -> list[CrawlerConfig]:
    args = PARSER.parse_args()

    config_creator = args.creator
    cookies_file = args.cookie_file
    download_dir = args.download_dir or "./downloads"

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

    return [CrawlerConfig(creator, cookies, download_dir) for creator in parsed_creator]


def main() -> None:
    configs = parse_args()

    for config in configs:
        print("Crawling", config.creator)

        crawler = PatreonCrawler(config)
        crawler.run()

        print("\nDone\n")


if __name__ == "__main__":
    main()
